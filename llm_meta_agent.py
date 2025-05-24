#!/usr/bin/env python3
"""
LLM Meta Agent - Agente que cria outros agentes
Gera pipelines inteligentes de agentes LLM para maximizar performance
"""

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import aisuite as ai
from llm_agent import LLM_Agent


class LLM_Meta_Agent:
    """
    Meta-agente que cria outros agentes LLM especializados.
    
    Aprende com histórico de performance e cria pipelines inteligentes
    combinando múltiplos agentes para maximizar acurácia.
    """
    
    # SYSTEM PROMPT ÚNICO - SOURCE OF TRUTH
    SYSTEM_PROMPT = """Você é um especialista em engenharia de agentes de IA.

RESPONDA EXCLUSIVAMENTE EM JSON com esta estrutura:
{
  "name": "Nome descritivo do pipeline",
  "pensamento": "Por que esta arquitetura vai funcionar melhor...", 
  "code": "Código Python executável que cria e orquestra os agentes"
}"""

    def __init__(self, 
                 model: str = "ollama:qwen3:32b",
                 history_file: str = "agent_history.json",
                 temperatura: float = 0.3):
        """
        Inicializa o Meta-Agente que cria outros agentes.
        
        Args:
            model: Modelo LLM para o meta-agente
            history_file: Arquivo para persistir histórico de agentes
            temperatura: Temperatura para geração de novos agentes
        """
        self.model = model
        self.temperatura = temperatura
        self.history_file = Path(history_file)
        self.agent_history = self._load_history()
        
        # Modelos disponíveis para criação de agentes
        self.available_models = [
            "ollama:phi4:latest", 
            "ollama:gemma3:4b", 
            "ollama:gemma3:12b", 
            "ollama:gemma3:27b", 
            "ollama:qwen3:4b", 
            "ollama:qwen3:14b", 
            "ollama:qwen3:30b", 
            "ollama:qwen3:32b"
        ]
        
        # Cliente AI para o meta-agente
        self.client = ai.Client()
        self.client.configure({
            "ollama": {"timeout": 600}
        })
        
        # Arquitetura de resposta do meta-agente
        self.arquitetura_resposta = {
            "name": "Nome descritivo do agente/pipeline",
            "pensamento": "Raciocínio sobre por que esta arquitetura vai funcionar",
            "code": "Código Python executável para criar e executar o(s) agente(s)"
        }
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Carrega histórico de agentes do arquivo JSON."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar histórico: {e}")
                return []
        return []
    
    def _save_history(self):
        """Salva histórico de agentes no arquivo JSON."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.agent_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def _generate_agent_id(self) -> str:
        """Gera ID único para novo agente."""
        if not self.agent_history:
            return "001"
        
        last_id = max([int(agent.get("agent_id", "0")) for agent in self.agent_history])
        return f"{last_id + 1:03d}"
    
    def get_functional_examples(self, top_n: int = 3) -> str:
        """
        Retorna exemplos de agentes funcionais (top 3 por acurácia + 1 aleatório).
        Em caso de empate na acurácia, usa avg_execution_time como critério.
        """
        if not self.agent_history:
            return "Nenhum histórico de agentes funcionais disponível."
        
        # Filtrar agentes com performance válida
        functional_agents = [
            agent for agent in self.agent_history 
            if agent.get("performance", {}).get("accuracy", 0) > 0
        ]
        
        if not functional_agents:
            return "Nenhum agente funcional encontrado no histórico."
        
        # Ordenar por acurácia (desc) e tempo de execução (asc)
        functional_agents.sort(
            key=lambda x: (
                -x.get("performance", {}).get("accuracy", 0),
                x.get("performance", {}).get("avg_execution_time", float('inf'))
            )
        )
        
        # Top N agentes
        top_agents = functional_agents[:top_n]
        
        # Adicionar 1 agente aleatório (se houver mais)
        remaining_agents = functional_agents[top_n:]
        if remaining_agents:
            random_agent = random.choice(remaining_agents)
            top_agents.append(random_agent)
        
        # Formatar exemplos
        examples = []
        for agent in top_agents:
            example = f"""
## {agent['name']} (ID: {agent['agent_id']})
**Performance:** Acurácia: {agent['performance']['accuracy']:.1f}%, Tempo: {agent['performance']['avg_execution_time']:.2f}s
**Pensamento:** {agent['thinking']}
**Configuração:** {json.dumps(agent['config'], indent=2, ensure_ascii=False)}
"""
            examples.append(example)
        
        return "\n".join(examples)
    
    def get_non_functional_examples(self, max_n: int = 5) -> str:
        """
        Retorna exemplos de agentes não funcionais para evitar padrões problemáticos.
        """
        if not self.agent_history:
            return "Nenhum histórico disponível."
        
        # Filtrar agentes com baixa performance (< 30% acurácia)
        non_functional_agents = [
            agent for agent in self.agent_history 
            if agent.get("performance", {}).get("accuracy", 0) < 30
        ]
        
        if not non_functional_agents:
            return "Nenhum exemplo de baixa performance encontrado."
        
        # Pegar até max_n exemplos
        selected_agents = non_functional_agents[:max_n]
        
        # Formatar exemplos com tipos de erro comuns
        examples = []
        for agent in selected_agents:
            error_type = self._identify_error_type(agent)
            example = f"""
## {agent['name']} (ID: {agent['agent_id']}) - PROBLEMÁTICO
**Performance:** Acurácia: {agent['performance']['accuracy']:.1f}%
**Tipo de Erro:** {error_type}
**Problema Identificado:** {agent['thinking']}
**Configuração que NÃO funcionou:** {json.dumps(agent['config'], indent=2, ensure_ascii=False)}
"""
            examples.append(example)
        
        return "\n".join(examples)
    
    def _identify_error_type(self, agent: Dict[str, Any]) -> str:
        """Identifica tipo de erro baseado na performance do agente."""
        accuracy = agent.get("performance", {}).get("accuracy", 0)
        execution_time = agent.get("performance", {}).get("avg_execution_time", 0)
        
        if accuracy == 0:
            return "Erro crítico - nenhuma resposta correta"
        elif accuracy < 10:
            return "Erro de lógica - respostas predominantemente incorretas"
        elif execution_time > 10:
            return "Erro de performance - tempo de execução excessivo"
        elif accuracy < 30:
            return "Erro de arquitetura - baixa acurácia geral"
        else:
            return "Erro não classificado"
    
    def _build_meta_prompt(self, task_explicacao: str) -> str:
        """Constrói prompt para o meta-agente."""
        arquiteturas_agentes = f"Modelos disponíveis: {', '.join(self.available_models)}"
        exemplos_funcionais = self.get_functional_examples()
        exemplos_nao_funcionais = self.get_non_functional_examples()
        
        prompt = f"""Seu objetivo é criar PIPELINES INTELIGENTES de agentes que MAXIMIZEM A ACURÁCIA e MINIMIZEM O TEMPO DE EXECUÇÃO através de colaboração, especialização e raciocínio distribuído.

Para melhorar a performance, você pode usar as seguintes técnicas:
- Usar diferentes modelos para diferentes funções
- Pipelines podem usar outputs anteriores via arquitetura_respostas_anteriores
- Pense em especialização: cada agente tem função específica
- Considere edge cases e robustez

Para minimizar o tempo de execução, você pode usar as seguintes técnicas:
- Usar modelos mais leves
- Usar pipelines mais simples
- Usar pipelines com menos agentes
- Usar pipelines com menos iterações

TÉCNICAS DISPONÍVEIS:
- Single Agent: Um agente especializado
- Sequential Pipeline: Agente1 → Agente2 → ... → AgentN  
- Debate Pipeline: Múltiplos especialistas → Decisão final
- Reflection Pipeline: Agente principal ↔ Agente revisor
- Hierarchical: Agente coordenador + agentes especializados

MODELOS DISPONÍVEIS:
{', '.join(self.available_models)}

# Histórico de Arquiteturas
{arquiteturas_agentes}

# Exemplos de ALTA Performance (FUNCIONAIS)
{exemplos_funcionais}

# Exemplos de BAIXA Performance (EVITAR)
{exemplos_nao_funcionais}

# Sua Missão
{task_explicacao}

RESPONDA EXCLUSIVAMENTE EM JSON com esta estrutura:
{{
  "name": "Nome descritivo do pipeline",
  "pensamento": "Por que esta arquitetura vai funcionar melhor...",
  "code": "Código Python executável que cria e orquestra os agentes"
}}

DIRETRIZES IMPORTANTES:
- Use diferentes modelos para diferentes funções
- Varie temperaturas: baixa (0.1-0.3) para precisão, media (0.4-0.6) para normalidade e alta (0.7-0.9) para criatividade
- Pipelines podem usar outputs anteriores via arquitetura_respostas_anteriores
- Pense em especialização: cada agente tem função específica
- Considere edge cases e robustez
- O código deve retornar um dicionário final com a resposta

IMPORTANTE: O código deve implementar uma função solve_problem(problem_data) que:
1. Recebe problem_data (dicionário do problema LeetCode)
2. Executa o pipeline de agentes
3. Retorna dicionário com a resposta final

CRIE UM PIPELINE REVOLUCIONÁRIO!"""
        
        return prompt
    
    def generate_agent_code(self, task_explicacao: str) -> Dict[str, Any]:
        """
        Gera código executável para novo(s) agente(s).
        
        Args:
            task_explicacao: Descrição da tarefa/objetivo do agente
            
        Returns:
            Dict com name, pensamento e code do agente gerado
        """
        prompt = self._build_meta_prompt(task_explicacao)
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperatura
            )
            
            raw_response = response.choices[0].message.content
            
            # Parse JSON da resposta
            try:
                # Tentar parse direto
                result = json.loads(raw_response)
            except json.JSONDecodeError:
                # Extrair JSON se estiver em markdown
                start_idx = raw_response.find('{')
                end_idx = raw_response.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = raw_response[start_idx:end_idx + 1]
                    result = json.loads(json_str)
                else:
                    return {
                        "name": "Erro de Parse",
                        "pensamento": "Erro ao fazer parse da resposta JSON",
                        "code": f"# Erro: resposta não é JSON válido\n# {raw_response}"
                    }
            
            return result
            
        except Exception as e:
            return {
                "name": "Erro de Geração",
                "pensamento": f"Erro ao gerar agente: {str(e)}",
                "code": f"# Erro na geração: {str(e)}"
            }
    
    def test_pipeline_multiple_times(self, pipeline_code: str, runs: int = 10) -> Dict[str, Any]:
        """
        Executa pipeline múltiplas vezes e retorna estatísticas consolidadas.
        
        Args:
            pipeline_code: Código Python do pipeline
            runs: Número de execuções para teste
            
        Returns:
            Dict com accuracy média e avg_execution_time
        """
        # Carregar problemas LeetCode
        try:
            with open("leetcode_problems.json", encoding="utf-8") as f:
                problems = json.load(f)["problems"]
        except Exception as e:
            return {
                "accuracy": 0.0,
                "avg_execution_time": 0.0,
                "error": f"Erro ao carregar problemas: {str(e)}"
            }
        
        all_accuracies = []
        all_execution_times = []
        successful_runs = 0
        
        for run in range(runs):
            print(f"Executando teste {run + 1}/{runs}...")
            
            try:
                # Executar código do pipeline
                local_vars = {}
                exec(pipeline_code, globals(), local_vars)
                
                if 'solve_problem' not in local_vars:
                    print(f"Run {run + 1}: Função solve_problem não encontrada")
                    continue
                
                solve_function = local_vars['solve_problem']
                
                # Testar cada problema
                correct_count = 0
                total_problems = len(problems)
                total_time = 0
                
                for problem in problems:
                    start_time = time.time()
                    
                    try:
                        # Executar função do pipeline
                        result = solve_function(problem)
                        execution_time = time.time() - start_time
                        total_time += execution_time
                        
                        # Verificar se resultado é válido
                        if isinstance(result, dict) and 'code' in result:
                            # Testar código gerado
                            from llm_agent import LLM_Agent
                            temp_agent = LLM_Agent(
                                role="Test Agent",
                                instruction="Test",
                                arquitetura_resposta={"code": "code"}
                            )
                            
                            accuracy, _ = temp_agent.test_code_accuracy(
                                result['code'], 
                                problem.get('tests', [])
                            )
                            
                            if accuracy > 50:  # Considera correto se > 50% dos testes passaram
                                correct_count += 1
                        
                    except Exception as e:
                        print(f"Erro no problema {problem['id']}: {str(e)}")
                        total_time += 1.0  # Penalty time
                
                # Calcular métricas do run
                run_accuracy = (correct_count / total_problems) * 100 if total_problems > 0 else 0
                run_avg_time = total_time / total_problems if total_problems > 0 else 0
                
                all_accuracies.append(run_accuracy)
                all_execution_times.append(run_avg_time)
                successful_runs += 1
                
                print(f"Run {run + 1}: Acurácia = {run_accuracy:.1f}%, Tempo = {run_avg_time:.2f}s")
                
            except Exception as e:
                print(f"Erro no run {run + 1}: {str(e)}")
                all_accuracies.append(0.0)
                all_execution_times.append(10.0)  # Penalty time
        
        # Calcular estatísticas finais
        if successful_runs > 0:
            final_accuracy = sum(all_accuracies) / len(all_accuracies)
            final_avg_time = sum(all_execution_times) / len(all_execution_times)
        else:
            final_accuracy = 0.0
            final_avg_time = 0.0
        
        return {
            "accuracy": final_accuracy,
            "avg_execution_time": final_avg_time,
            "successful_runs": successful_runs,
            "total_runs": runs,
            "all_accuracies": all_accuracies,
            "all_execution_times": all_execution_times
        }
    
    def create_and_evaluate_agent(self, task_explicacao: str) -> Dict[str, Any]:
        """
        Fluxo completo: gera agente → testa 10x → salva no histórico.
        
        Args:
            task_explicacao: Descrição da tarefa para o novo agente
            
        Returns:
            Dict com informações completas do agente criado e testado
        """
        print("🤖 Gerando novo agente...")
        
        # Gerar código do agente
        agent_spec = self.generate_agent_code(task_explicacao)
        
        if "Erro" in agent_spec.get("name", ""):
            return {
                "success": False,
                "error": "Erro na geração do agente",
                "details": agent_spec
            }
        
        print(f"✅ Agente gerado: {agent_spec['name']}")
        print(f"💭 Pensamento: {agent_spec['pensamento']}")
        
        # Testar agente múltiplas vezes
        print("🧪 Testando agente 10 vezes...")
        performance = self.test_pipeline_multiple_times(agent_spec['code'], runs=10)
        
        # Criar entrada do histórico
        agent_entry = {
            "agent_id": self._generate_agent_id(),
            "name": agent_spec['name'],
            "creation_timestamp": datetime.now().isoformat(),
            "config": {
                "type": "pipeline",  # Detectar automaticamente ou assumir pipeline
                "code": agent_spec['code']
            },
            "performance": {
                "accuracy": performance['accuracy'],
                "avg_execution_time": performance['avg_execution_time']
            },
            "thinking": agent_spec['pensamento'],
            "task_explanation": task_explicacao,
            "test_details": performance
        }
        
        # Adicionar ao histórico
        self.agent_history.append(agent_entry)
        self._save_history()
        
        print(f"📊 Performance: {performance['accuracy']:.1f}% acurácia, {performance['avg_execution_time']:.2f}s tempo médio")
        print(f"💾 Salvo no histórico com ID: {agent_entry['agent_id']}")
        
        return {
            "success": True,
            "agent": agent_entry,
            "performance": performance
        }
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do histórico de agentes."""
        if not self.agent_history:
            return {"total_agents": 0}
        
        accuracies = [agent.get("performance", {}).get("accuracy", 0) for agent in self.agent_history]
        execution_times = [agent.get("performance", {}).get("avg_execution_time", 0) for agent in self.agent_history]
        
        return {
            "total_agents": len(self.agent_history),
            "avg_accuracy": sum(accuracies) / len(accuracies),
            "max_accuracy": max(accuracies),
            "min_accuracy": min(accuracies),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "functional_agents": len([a for a in self.agent_history if a.get("performance", {}).get("accuracy", 0) >= 30]),
            "high_performance_agents": len([a for a in self.agent_history if a.get("performance", {}).get("accuracy", 0) >= 70])
        }
    
    def list_top_agents(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Lista os top N agentes por performance."""
        if not self.agent_history:
            return []
        
        sorted_agents = sorted(
            self.agent_history,
            key=lambda x: (
                -x.get("performance", {}).get("accuracy", 0),
                x.get("performance", {}).get("avg_execution_time", float('inf'))
            )
        )
        
        return sorted_agents[:top_n]


# Exemplo de uso
if __name__ == "__main__":
    # Criar meta-agente
    meta_agent = LLM_Meta_Agent(model="ollama:qwen3:32b", temperatura=0.3)
    
    # Exemplo de criação de agente
    task = """
    Criar um agente/pipeline que maximize a acurácia em problemas de algoritmos LeetCode.
    O agente deve ser capaz de resolver problemas de diferentes categorias como:
    - Problemas de arrays e listas
    - Problemas de strings e manipulação de texto  
    - Problemas de matemática e lógica
    - Problemas de estruturas de dados básicas
    
    Foque em crear uma solução robusta que combine diferentes técnicas de raciocínio.
    """
    
    print("🚀 Iniciando criação de novo agente...")
    result = meta_agent.create_and_evaluate_agent(task)
    
    if result["success"]:
        print("\n✅ Agente criado e testado com sucesso!")
        print(f"📊 Estatísticas: {meta_agent.get_agent_statistics()}")
    else:
        print(f"\n❌ Erro: {result['error']}") 