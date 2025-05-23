# %%
import json
import aisuite as ai
from typing import Dict, List, Any, Optional

# Carrega o JSON completo
with open("leetcode_problems.json", encoding="utf-8") as f:
    problems = json.load(f)["problems"]

# Escolhe um problema (por índice ou id)
problem = problems[0]   # por exemplo, o primeiro
# Ou: problem = next(p for p in problems if p["id"] == "twoSum")

# Converte o dicionário inteiro em string JSON indentada
task_str = json.dumps(problem, indent=2, ensure_ascii=False)

print(task_str)

class LLM_Agent:
    def __init__(
        self,
        role: str,
        instruction: str,
        arquitetura_resposta: Dict[str, str],
        temperatura: float = 0.7,
        arquitetura_respostas_anteriores: Optional[List[Dict[str, str]]] = None,
        model: str = "ollama:qwen3:4b"
    ):
        """
        Inicializa um agente LLM para resolver problemas.
        
        Args:
            role: O papel/função do agente (ex: "Especialista em Python")
            instruction: Instruções específicas para o agente
            arquitetura_resposta: Estrutura JSON esperada na resposta
            temperatura: Temperatura para o modelo (0.0 a 1.0)
            arquitetura_respostas_anteriores: Lista de dicionários com respostas anteriores
            model: Modelo LLM a ser usado (default: "ollama:qwen3:4b")
        """
        self.role = role
        self.instruction = instruction
        self.arquitetura_resposta = arquitetura_resposta
        self.temperatura = temperatura
        self.arquitetura_respostas_anteriores = arquitetura_respostas_anteriores or []
        
        # Configurar cliente AI
        self.client = ai.Client()
        self.client.configure({
            "ollama": {
                "timeout": 600,
            }
        })
        self.model = model
    
    def create_prompt(self, task: str) -> tuple[str, str]:
        """
        Cria system_prompt e user_prompt separados.
        
        Args:
            task: Descrição da tarefa a ser resolvida
            
        Returns:
            tuple[str, str]: (system_prompt, user_prompt)
        """
        # Processar info_section se houver respostas anteriores
        info_section = ""
        if self.arquitetura_respostas_anteriores:
            for idx, resposta in enumerate(self.arquitetura_respostas_anteriores):
                agent_id = f"{idx:02d}"
                for key, value in resposta.items():
                    info_section += f"## {key.title()} do Agente {agent_id}:\n{value}\n\n"
        
        system_prompt = (
            "Você é um {role}.\n\n"
            "Responda exatamente no formato JSON abaixo:\n"
            "{json_string}\n"
            "NAO ESQUEÇA NENHUM CAMPO!\n\n"
        ).format(
            role=self.role,
            json_string=json.dumps(self.arquitetura_resposta, indent=2, ensure_ascii=False)
        )
        
        user_prompt = (
            "# Sua Tarefa\n"
            "{task}\n\n"
            "{info_section}"
            "# Instrução\n"
            "{instruction}\n"
        ).format(
            task=task,
            info_section=info_section,
            instruction=self.instruction
        )
        
        return system_prompt, user_prompt
    
    def solve(self, task: str) -> str:
        """
        Resolve uma tarefa usando o agente configurado.
        
        Args:
            task: Descrição da tarefa a ser resolvida
            
        Returns:
            str: Resposta do modelo
        """
        system_prompt, user_prompt = self.create_prompt(task)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperatura
        )
        
        return response.choices[0].message.content

# %%
# Criar agente para resolver problemas de algoritmos
agente = LLM_Agent(
    role="Especialista em Algoritmos Python",
    instruction="Implemente uma solução eficiente para o problema",
    arquitetura_resposta={
        "analysis": "Análise detalhada do problema",
        "explanation": "Explicação da solução",
        "code": "Código Python completo",
    },
    temperatura=0.3,
    # model="ollama:qwen3:4b"
    model="ollama:gemma3:4b"
)

# Testar o agente
system_prompt, user_prompt = agente.create_prompt(task_str)
print("=== SYSTEM PROMPT ===")
print(system_prompt)
print("\n=== USER PROMPT ===")
print(user_prompt)
# %%
print("\n=== RESPOSTA DO MODELO ===")
print(agente.solve(task_str))

    # # Criar outro agente com respostas anteriores
    # agente_com_historico = LLM_Agent(
    #     role="Especialista em Algoritmos Python",
    #     instruction="Analise as soluções anteriores e proponha uma solução otimizada",
    #     arquitetura_resposta={
    #         "previous_solutions_analysis": "Análise das soluções anteriores",
    #         "optimization_proposal": "Proposta de otimização",
    #         "improved_code": "Código Python otimizado",
    #         "performance_comparison": "Comparação de performance"
    #     },
    #     temperatura=0.2,
    #     arquitetura_respostas_anteriores=[
    #         {
    #             "analysis": "A solução atual usa conversão para string, podemos otimizar",
    #             "explanation": "A abordagem atual converte o número para string para fazer a comparação",
    #             "code": "def isPalindrome(x: int) -> bool:\n    return str(x) == str(x)[::-1]"
    #         },
    #         {
    #             "analysis": "Otimize a função que verifica se um número é palindromo evitando conversão para string",
    #             "explanation": "A abordagem atual converte o número para string para fazer a comparação",
    #             "code": "def isPalindrome(x: int) -> bool:\n    return str(x) == str(x)[::-1]"
    #         },
    #     ],
    #     model="ollama:qwen3:4b"
    # )
    
    # # Testar o segundo agente
    # task_2 = "Otimize a função que verifica se um número é palindromo evitando conversão para string"
    # system_prompt_2, user_prompt_2 = agente_com_historico.create_prompt(task_2)
    # print("\n=== SYSTEM PROMPT (AGENTE COM HISTÓRICO) ===")
    # print(system_prompt_2)
    # print("\n=== USER PROMPT (AGENTE COM HISTÓRICO) ===")
    # print(user_prompt_2)
    # # print("\n=== RESPOSTA DO MODELO ===")
    # # print(agente_com_historico.solve(task_2))
# %%
