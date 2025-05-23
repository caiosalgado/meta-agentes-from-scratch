# %%
import json
import aisuite as ai
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import tempfile
import os
import re

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
    
    def generate_response(self, task: str) -> Dict[str, Any]:
        """
        Gera uma resposta usando o agente configurado.
        
        Args:
            task: Descrição da tarefa a ser resolvida
            
        Returns:
            Dict[str, Any]: Resposta parseada como dicionário ou dicionário com erro
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
        
        # Aplicar parse JSON automaticamente
        raw_response = response.choices[0].message.content
        return self.parse_json_response(raw_response)
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Faz o parse da resposta JSON com tratamento de erros.
        
        Args:
            response: String de resposta do modelo
            
        Returns:
            Dict[str, Any]: Dicionário com a resposta parseada ou erro
        """
        try:
            # Tentar fazer parse direto
            return json.loads(response)
        except json.JSONDecodeError:
            try:
                # Tentar extrair JSON se estiver em markdown ou com texto extra
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx + 1]
                    return json.loads(json_str)
                else:
                    return {"erro": "JSON não encontrado na resposta"}
            except json.JSONDecodeError as e:
                return {"erro": f"Erro ao fazer parse do JSON: {str(e)}"}
            except Exception as e:
                return {"erro": f"Erro inesperado ao processar resposta: {str(e)}"}
    
    def _extract_function_name(self, code: str) -> str:
        """
        Extrai o nome da função do código de forma robusta.
        
        Args:
            code: Código Python
            
        Returns:
            str: Nome da função ou string vazia se não encontrar
        """
        # Buscar por definição de função
        match = re.search(r'def\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)
        return ""
    
    def test_code_accuracy(self, code: str, test_cases: List[Dict[str, Any]]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Testa a acurácia do código gerado contra casos de teste (versão simplificada).
        
        Args:
            code: Código Python para testar
            test_cases: Lista de casos de teste no formato {"input": [args...], "expected": result}
            
        Returns:
            Tuple[float, List[Dict[str, Any]]]: (porcentagem_acurácia, resultados_detalhados)
        """
        results = []
        correct_count = 0
        
        # Extrair nome da função
        function_name = self._extract_function_name(code)
        if not function_name:
            return 0.0, [{"error": "Não foi possível extrair nome da função"}]
        
        for i, test_case in enumerate(test_cases):
            try:
                # Criar arquivo temporário com o código
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    # Preparar código de teste - formato muito simples agora
                    test_code = f"""
{code}

# Caso de teste
input_args = {test_case['input']}
result = {function_name}(*input_args)
print(repr(result))
"""
                    f.write(test_code)
                    temp_file = f.name
                
                # Executar código
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    actual_output = result.stdout.strip()
                    try:
                        actual_value = eval(actual_output)
                        expected_value = test_case['expected']
                        is_correct = actual_value == expected_value
                        
                        if is_correct:
                            correct_count += 1
                        
                        results.append({
                            'test_case': i + 1,
                            'input': test_case['input'],
                            'expected': expected_value,
                            'actual': actual_value,
                            'correct': is_correct,
                            'error': None
                        })
                    except Exception as e:
                        results.append({
                            'test_case': i + 1,
                            'input': test_case['input'],
                            'expected': test_case['expected'],
                            'actual': actual_output,
                            'correct': False,
                            'error': f"Erro ao avaliar resultado: {str(e)}"
                        })
                else:
                    results.append({
                        'test_case': i + 1,
                        'input': test_case['input'],
                        'expected': test_case['expected'],
                        'actual': None,
                        'correct': False,
                        'error': result.stderr.strip()
                    })
                
                # Limpar arquivo temporário
                os.unlink(temp_file)
                
            except subprocess.TimeoutExpired:
                results.append({
                    'test_case': i + 1,
                    'input': test_case['input'],
                    'expected': test_case['expected'],
                    'actual': None,
                    'correct': False,
                    'error': "Timeout - código demorou mais de 10 segundos"
                })
                if 'temp_file' in locals():
                    os.unlink(temp_file)
            except Exception as e:
                results.append({
                    'test_case': i + 1,
                    'input': test_case['input'],
                    'expected': test_case['expected'],
                    'actual': None,
                    'correct': False,
                    'error': f"Erro inesperado: {str(e)}"
                })
        
        accuracy = (correct_count / len(test_cases)) * 100 if test_cases else 0
        return accuracy, results
    
    def evaluate_response(self, response: Dict[str, Any], test_cases: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Avalia a resposta do agente comparando valores esperados vs atuais.
        
        Args:
            response: Resposta do modelo já parseada como dicionário
            test_cases: Casos de teste opcionais para avaliar código
            
        Returns:
            Dict[str, Any]: Avaliação completa com feedback detalhado
        """
        evaluation = {
            'response_valid': True,
            'json_parse_successful': True,
            'parsed_response': {},
            'code_accuracy': None,
            'test_results': [],
            'feedback': []
        }
        
        # A resposta já vem parseada do generate_response
        parsed_response = response
        evaluation['parsed_response'] = parsed_response
        
        if 'erro' in parsed_response:
            evaluation['response_valid'] = False
            evaluation['json_parse_successful'] = False
            evaluation['feedback'].append(f"Erro no parse JSON: {parsed_response['erro']}")
        else:
            evaluation['feedback'].append("Resposta JSON válida")
            
            # Verificar se todos os campos obrigatórios estão presentes
            missing_fields = []
            for field in self.arquitetura_resposta.keys():
                if field not in parsed_response:
                    missing_fields.append(field)
            
            if missing_fields:
                evaluation['response_valid'] = False
                evaluation['feedback'].append(f"Campos obrigatórios ausentes: {missing_fields}")
            else:
                evaluation['feedback'].append("Todos os campos obrigatórios presentes")
            
            # Testar código se casos de teste foram fornecidos e há campo 'code'
            if test_cases and 'code' in parsed_response:
                try:
                    accuracy, test_results = self.test_code_accuracy(
                        parsed_response['code'], 
                        test_cases
                    )
                    evaluation['code_accuracy'] = accuracy
                    evaluation['test_results'] = test_results
                    evaluation['feedback'].append(f"Acurácia do código: {accuracy:.1f}%")
                except Exception as e:
                    evaluation['feedback'].append(f"Erro ao testar código: {str(e)}")
        
        return evaluation
    
    def load_leetcode_problem(self, problem_data: Dict[str, Any]) -> str:
        """
        Converte dados do problema LeetCode para string de tarefa.
        
        Args:
            problem_data: Dados do problema do JSON
            
        Returns:
            str: String formatada da tarefa
        """
        return json.dumps(problem_data, indent=2, ensure_ascii=False)
    
    def run_leetcode_test(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa teste completo de um problema LeetCode.
        
        Args:
            problem_data: Dados completos do problema
            
        Returns:
            Dict[str, Any]: Resultado da avaliação
        """
        # Gerar resposta para o problema (já retorna dicionário parseado)
        task_str = self.load_leetcode_problem(problem_data)
        response = self.generate_response(task_str)
        
        # Avaliar resposta com casos de teste
        test_cases = problem_data.get('tests', [])
        evaluation = self.evaluate_response(response, test_cases)
        
        return {
            'problem_id': problem_data.get('id'),
            'problem_title': problem_data.get('title'),
            'response': response,
            'evaluation': evaluation
        }

# %%
# Criar agente para resolver problemas de algoritmos
agente = LLM_Agent(
    role="Especialista em Algoritmos Python",
    instruction="Implemente uma solução eficiente para o problema. Use apenas funções standalone (não classes).",
    arquitetura_resposta={
        "analysis": "Análise detalhada do problema",
        "explanation": "Explicação da solução step-by-step",
        "code": "Código Python completo - apenas função standalone",
        "complexity": "Análise de complexidade temporal e espacial"
    },
    temperatura=0.3,
    # model="ollama:qwen3:4b"
    model="ollama:gemma3:4b"
)

# Testar o agente com o novo formato
print("=== TESTANDO PROBLEMA: isPalindrome ===")
palindrome_problem = problems[0]
result = agente.run_leetcode_test(palindrome_problem)

print(f"\nProblema: {result['problem_title']} ({result['problem_id']})")
accuracy = result['evaluation']['code_accuracy'] or 0
print(f"Acurácia: {accuracy:.1f}%")
print(f"Feedback: {result['evaluation']['feedback']}")

print("\n=== RESPOSTA COMPLETA ===")
print(json.dumps(result['response'], indent=2, ensure_ascii=False))

print("\n=== RESULTADOS DOS TESTES ===")
for test_result in result['evaluation']['test_results']:
    status = "✅" if test_result['correct'] else "❌"
    print(f"{status} Teste {test_result['test_case']}: input={test_result['input']}, expected={test_result['expected']}, actual={test_result['actual']}")
    if test_result['error']:
        print(f"   Erro: {test_result['error']}")

# %%
# Testar todos os problemas
print("\n" + "="*50)
print("TESTANDO TODOS OS PROBLEMAS")
print("="*50)

all_results = []
for problem in problems:
    print(f"\n--- {problem['title']} ---")
    result = agente.run_leetcode_test(problem)
    all_results.append(result)
    
    accuracy = result['evaluation']['code_accuracy'] or 0
    print(f"Acurácia: {accuracy:.1f}%")
    correct_count = sum(1 for test in result['evaluation']['test_results'] if test['correct'])
    total_count = len(result['evaluation']['test_results'])
    print(f"Testes corretos: {correct_count}/{total_count}")

# Resumo final
print(f"\n{'='*50}")
print("RESUMO FINAL")
print(f"{'='*50}")
total_accuracy = sum(r['evaluation']['code_accuracy'] or 0 for r in all_results) / len(all_results)
print(f"Acurácia média: {total_accuracy:.1f}%")

for result in all_results:
    accuracy = result['evaluation']['code_accuracy'] or 0
    status = "🎯" if accuracy >= 80 else "⚠️" if accuracy >= 50 else "❌"
    print(f"{status} {result['problem_title']}: {accuracy:.1f}%")

# %%
