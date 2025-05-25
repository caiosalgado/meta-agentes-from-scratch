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
    
    # CONFIGURAÇÕES CENTRALIZADAS
    DEFAULT_TEST_RUNS = 3  # Número padrão de execuções para teste de agentes
    
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
            "ollama:gemma3:1b",
            "ollama:qwen3:1.7b",
            "ollama:qwen3:4b", 
            "ollama:qwen3:14b", 
            "ollama:qwen3:30b", 
            "ollama:qwen3:32b",
            "ollama:devstral",
            "ollama:deepseek-r1:1.5b",
            "ollama:deepseek-r1:8b",
            "ollama:deepseek-r1:14b"
        ]
        
        # Cliente AI para o meta-agente
        self.client = ai.Client()
        self.client.configure({
            "ollama": {"timeout": 500}
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
    
    def _extract_detailed_errors(self, agent: Dict[str, Any]) -> str:
        """
        Extrai erros detalhados de um agente para incluir no prompt do meta-agente.
        
        Args:
            agent: Dicionário com dados do agente
            
        Returns:
            String formatada com erros detalhados
        """
        error_details = ""
        detailed_results = agent.get("detailed_results", [])
        
        if not detailed_results:
            return error_details
        
        # Coletar erros de diferentes fontes
        all_errors = []
        
        # 1. Erros gerais do run (se existir)
        for run_result in detailed_results:
            if "errors" in run_result and run_result["errors"]:
                all_errors.extend(run_result["errors"])
            
            # 2. Erros específicos de problemas
            problem_results = run_result.get("problem_results", [])
            for problem in problem_results:
                if "error" in problem and problem["error"]:
                    all_errors.append(f"Problema '{problem.get('problem', 'Unknown')}': {problem['error']}")
                
                # 3. Erros de test cases específicos
                if "details" in problem:
                    for detail in problem["details"]:
                        if "error" in detail and detail["error"]:
                            # Extrair apenas a parte mais relevante do erro
                            error_msg = detail['error']
                            if "Traceback" in error_msg:
                                # Pegar apenas a última linha do traceback
                                lines = error_msg.strip().split('\n')
                                error_msg = lines[-1] if lines else error_msg
                            all_errors.append(f"Test case: {error_msg}")
        
        # Remover duplicatas mantendo ordem
        unique_errors = []
        seen = set()
        for error in all_errors:
            if error not in seen:
                unique_errors.append(error)
                seen.add(error)
        
        # Limitar a 5 erros mais representativos
        if unique_errors:
            error_details = "\n\n**ERROS ESPECÍFICOS ENCONTRADOS:**\n"
            for i, error in enumerate(unique_errors[:5], 1):
                error_details += f"{i}. {error}\n"
            
            if len(unique_errors) > 5:
                error_details += f"... e mais {len(unique_errors) - 5} erros similares\n"
        
        return error_details

    def get_non_functional_examples(self, max_n: int = 5) -> str:
        """
        Retorna exemplos de agentes não funcionais para evitar padrões problemáticos.
        Inclui erros detalhados para melhor aprendizado do meta-agente.
        """
        if not self.agent_history:
            return "Nenhum histórico disponível."
        
        # Filtrar agentes com baixa performance (< 30% acurácia) OU com erros de execução
        non_functional_agents = []
        for agent in self.agent_history:
            accuracy = agent.get("performance", {}).get("accuracy", 0)
            detailed_results = agent.get("detailed_results", [])
            has_execution_error = (detailed_results and len(detailed_results) > 0 and 
                                 "raw_error_details" in detailed_results[0])
            
            if accuracy < 30 or has_execution_error:
                non_functional_agents.append(agent)
        
        if not non_functional_agents:
            return "Nenhum exemplo de baixa performance encontrado."
        
        # Pegar até max_n exemplos
        selected_agents = non_functional_agents[:max_n]
        
        # Formatar exemplos com erros detalhados
        examples = []
        for agent in selected_agents:
            error_type = self._identify_error_type(agent)
            
            # Extrair erros detalhados usando nova função
            error_details = self._extract_detailed_errors(agent)
            
            # Verificar se há erro bruto disponível (código original)
            raw_error_details = ""
            detailed_results = agent.get("detailed_results", [])
            if detailed_results and len(detailed_results) > 0 and "raw_error_details" in detailed_results[0]:
                error_info = detailed_results[0]["raw_error_details"]
                raw_error_details = f"""

**CÓDIGO PROBLEMÁTICO GERADO PELO META-AGENTE:**
```python
{error_info["problematic_code"]}
```

**ERRO BRUTO QUE ACONTECEU:**
```
{error_info["error_message"]}
```"""
            
            example = f"""
## {agent['name']} (ID: {agent['agent_id']}) - PROBLEMÁTICO
**Performance:** Acurácia: {agent['performance']['accuracy']:.1f}%
**Tipo de Erro:** {error_type}{error_details}{raw_error_details}
**Problema Identificado:** {agent['thinking']}
**Configuração que NÃO funcionou:** {json.dumps(agent['config'], indent=2, ensure_ascii=False)}
"""
            examples.append(example)
        
        return "\n".join(examples)
    
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
    
    def test_agent_pipeline(self, agent_code: str, agent_name: str, runs: int = None) -> Dict[str, Any]:
        """
        FUNÇÃO ÚNICA para testar pipelines de agentes com logs detalhados.
        
        Args:
            agent_code: Código Python do pipeline
            agent_name: Nome do agente/pipeline
            runs: Número de execuções para teste (usa DEFAULT_TEST_RUNS se None)
            
        Returns:
            Dict com resultados consolidados e estatísticas
        """
        # Usar valor padrão se não especificado
        if runs is None:
            runs = self.DEFAULT_TEST_RUNS
        
        def log_step(step: str, details: str = ""):
            """Log detalhado com timestamp."""
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🔍 {step}")
            if details:
                print(f"    ℹ️  {details}")
        
        print("\n" + "="*80)
        log_step(f"TESTANDO PIPELINE: {agent_name}")
        print("="*80)
        
        # Carregar problemas LeetCode
        log_step("Carregando problemas LeetCode...")
        try:
            with open("leetcode_problems.json", encoding="utf-8") as f:
                problems = json.load(f)["problems"]
            log_step(f"✅ {len(problems)} problemas carregados")
        except Exception as e:
            log_step(f"❌ Erro ao carregar problemas: {e}")
            return {
                "name": agent_name,
                "accuracy": 0.0,
                "avg_execution_time": 0.0,
                "error": f"Erro ao carregar problemas: {str(e)}"
            }
        
        # Executar código do agente
        log_step("Executando código do agente...")
        try:
            local_vars = {}
            exec(agent_code, globals(), local_vars)
            
            if 'solve_problem' not in local_vars:
                log_step("❌ Função solve_problem não encontrada no código")
                return {
                    "name": agent_name,
                    "accuracy": 0.0,
                    "avg_execution_time": 0.0,
                    "error": "Função solve_problem não encontrada"
                }
                
            solve_function = local_vars['solve_problem']
            log_step("✅ Função solve_problem carregada com sucesso")
            
        except Exception as e:
            log_step(f"❌ Erro ao executar código: {e}")
            return {
                "name": agent_name,
                "accuracy": 0.0,
                "avg_execution_time": 0.0,
                "error": f"Erro ao executar código: {str(e)}",
                "raw_error_details": {
                    "error_message": str(e),
                    "problematic_code": agent_code,
                    "error_type": type(e).__name__
                }
            }
        
        # EXECUTAR MÚLTIPLAS VEZES PARA MÉTRICAS CONFIÁVEIS
        log_step(f"🔄 INICIANDO {runs} EXECUÇÕES PARA MÉTRICAS CONFIÁVEIS...")
        
        all_runs = []
        successful_runs = 0
        
        for run_num in range(1, runs + 1):
            log_step(f"🏃 EXECUÇÃO {run_num}/{runs}")
            print("-" * 60)
            
            # Testar cada problema nesta execução
            correct_count = 0
            total_problems = len(problems)
            total_time = 0
            problem_results = []
            run_errors = []
            
            for i, problem in enumerate(problems):
                problem_name = problem.get('title', f'Problem {i+1}')
                log_step(f"  Problema {i+1}/{total_problems}: {problem_name}")
                
                start_time = time.time()
                
                try:
                    # Executar agente no problema
                    result = solve_function(problem)
                    execution_time = time.time() - start_time
                    total_time += execution_time
                    
                    log_step(f"    ⏱️  Tempo: {execution_time:.2f}s")
                    
                    # Verificar se resultado é válido
                    if isinstance(result, dict) and 'code' in result:
                        log_step(f"    ✅ Resultado válido")
                        
                        # Testar código gerado
                        temp_agent = LLM_Agent(
                            role="Test Agent",
                            instruction="Test",
                            arquitetura_resposta={"code": "code"}
                        )
                        
                        accuracy, details = temp_agent.test_code_accuracy(
                            result['code'], 
                            problem.get('tests', [])
                        )
                        
                        if accuracy == 100:  # Considera correto apenas se 100% dos testes passaram
                            correct_count += 1
                            log_step(f"    🎯 SUCESSO - Acurácia: {accuracy:.1f}%")
                        else:
                            log_step(f"    ❌ FALHOU - Acurácia: {accuracy:.1f}%")
                            run_errors.append(f"{agent_name}: Código falhou em {100-accuracy:.1f}% dos testes (acurácia: {accuracy:.1f}%)")
                        
                        problem_results.append({
                            "problem": problem_name,
                            "success": accuracy == 100,
                            "accuracy": accuracy,
                            "execution_time": execution_time,
                            "details": details
                        })
                        
                    else:
                        log_step(f"    ❌ Resultado inválido: {type(result)}")
                        run_errors.append(f"{agent_name}: Resultado inválido - retornou {type(result)} ao invés de dict com 'code'")
                        problem_results.append({
                            "problem": problem_name,
                            "success": False,
                            "accuracy": 0,
                            "execution_time": execution_time,
                            "error": "Resultado inválido"
                        })
                        
                except Exception as e:
                    execution_time = time.time() - start_time
                    total_time += execution_time
                    error_msg = str(e)
                    log_step(f"    💥 ERRO: {error_msg}")
                    run_errors.append(f"{agent_name}: {error_msg}")
                    problem_results.append({
                        "problem": problem_name,
                        "success": False,
                        "accuracy": 0,
                        "execution_time": execution_time,
                        "error": error_msg
                    })
            
            # Calcular métricas desta execução
            run_accuracy = (correct_count / total_problems) * 100 if total_problems > 0 else 0
            run_avg_time = total_time / total_problems if total_problems > 0 else 0
            
            run_result = {
                "run_number": run_num,
                "accuracy": run_accuracy,
                "avg_execution_time": run_avg_time,
                "total_time": total_time,
                "correct_count": correct_count,
                "total_problems": total_problems,
                "problem_results": problem_results,
                "errors": run_errors
            }
            
            all_runs.append(run_result)
            
            if len(run_errors) == 0:  # Execução sem erros
                successful_runs += 1
            
            print("-" * 60)
            log_step(f"  📊 Run {run_num}: {run_accuracy:.1f}% acurácia, {run_avg_time:.2f}s tempo médio")
            
            if run_errors:
                log_step(f"  ⚠️  {len(run_errors)} erros nesta execução")
        
        # CALCULAR ESTATÍSTICAS CONSOLIDADAS
        log_step("📈 CALCULANDO ESTATÍSTICAS CONSOLIDADAS...")
        
        if not all_runs:
            log_step("❌ Nenhuma execução válida")
            return {
                "name": agent_name,
                "accuracy": 0.0,
                "avg_execution_time": 0.0,
                "error": "Nenhuma execução válida"
            }
        
        # Métricas médias
        accuracies = [run['accuracy'] for run in all_runs]
        avg_times = [run['avg_execution_time'] for run in all_runs]
        
        final_accuracy = sum(accuracies) / len(accuracies)
        final_avg_time = sum(avg_times) / len(avg_times)
        
        # Estatísticas adicionais
        accuracy_std = (sum([(acc - final_accuracy)**2 for acc in accuracies]) / len(accuracies)) ** 0.5
        time_std = (sum([(t - final_avg_time)**2 for t in avg_times]) / len(avg_times)) ** 0.5
        
        min_accuracy = min(accuracies)
        max_accuracy = max(accuracies)
        min_time = min(avg_times)
        max_time = max(avg_times)
        
        # Logs das estatísticas finais
        log_step("🎯 RESULTADOS FINAIS CONSOLIDADOS:")
        log_step(f"  📊 Acurácia Média: {final_accuracy:.1f}% (±{accuracy_std:.1f})")
        log_step(f"  📊 Acurácia Range: {min_accuracy:.1f}% - {max_accuracy:.1f}%")
        log_step(f"  ⏱️  Tempo Médio: {final_avg_time:.2f}s (±{time_std:.2f})")
        log_step(f"  ⏱️  Tempo Range: {min_time:.2f}s - {max_time:.2f}s")
        log_step(f"  ✅ Execuções Bem-sucedidas: {successful_runs}/{runs}")
        
        return {
            "name": agent_name,
            "accuracy": final_accuracy,
            "accuracy_std": accuracy_std,
            "accuracy_range": [min_accuracy, max_accuracy],
            "avg_execution_time": final_avg_time,
            "time_std": time_std,
            "time_range": [min_time, max_time],
            "successful_runs": successful_runs,
            "total_runs": runs,
            "all_runs": all_runs
        }
    
    def create_and_evaluate_agent(self, task_explicacao: str) -> Dict[str, Any]:
        """
        Fluxo completo: gera agente → testa → salva no histórico.
        
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
        
        # Testar agente usando função centralizada
        print("🧪 Testando agente...")
        test_results = self.test_agent_pipeline(
            agent_code=agent_spec['code'],
            agent_name=agent_spec['name']
        )
        
        # Adicionar ao histórico usando função centralizada
        agent_entry = self.add_agent_to_history(
            agent_name=agent_spec['name'],
            agent_code=agent_spec['code'],
            description=agent_spec['pensamento'],
            test_results=test_results,
            agent_type="generated_pipeline"
        )
        
        print(f"📊 Performance: {test_results['accuracy']:.1f}% acurácia, {test_results['avg_execution_time']:.2f}s tempo médio")
        
        return {
            "success": True,
            "agent": agent_entry,
            "performance": test_results
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
    
    def add_agent_to_history(self, 
                           agent_name: str,
                           agent_code: str, 
                           description: str,
                           test_results: Dict[str, Any],
                           agent_type: str = "pipeline") -> Dict[str, Any]:
        """
        Adiciona agente testado ao histórico de forma padronizada.
        
        Args:
            agent_name: Nome do agente
            agent_code: Código do agente
            description: Descrição do agente
            test_results: Resultados do test_agent_pipeline()
            agent_type: Tipo do agente (pipeline, manual_pipeline, etc.)
            
        Returns:
            Dict com entrada do histórico criada
        """
        agent_entry = {
            "agent_id": self._generate_agent_id(),
            "name": agent_name,
            "creation_timestamp": datetime.now().isoformat(),
            "config": {
                "type": agent_type,
                "code": agent_code,
                "description": description
            },
            "performance": {
                "accuracy": test_results.get('accuracy', 0.0),
                "accuracy_std": test_results.get('accuracy_std', 0.0),
                "accuracy_range": test_results.get('accuracy_range', [0.0, 0.0]),
                "avg_execution_time": test_results.get('avg_execution_time', 0.0),
                "time_std": test_results.get('time_std', 0.0),
                "time_range": test_results.get('time_range', [0.0, 0.0])
            },
            "testing_stats": {
                "successful_runs": test_results.get('successful_runs', 0),
                "total_runs": test_results.get('total_runs', 0),
                "all_runs_summary": [
                    {
                        "run": run['run_number'],
                        "accuracy": run['accuracy'],
                        "avg_time": run['avg_execution_time'],
                        "errors": len(run['errors'])
                    } for run in test_results.get('all_runs', [])
                ]
            },
            "thinking": f"Agente testado. {description}. Testado {test_results.get('total_runs', 0)} vezes com {test_results.get('successful_runs', 0)} execuções bem-sucedidas. Acurácia média: {test_results.get('accuracy', 0):.1f}%.",
            "task_explanation": f"Teste de {agent_name}",
            "detailed_results": test_results.get('all_runs', [])
        }
        
        # Adicionar ao histórico
        self.agent_history.append(agent_entry)
        self._save_history()
        
        print(f"💾 Agente {agent_name} salvo no histórico com ID: {agent_entry['agent_id']}")
        
        return agent_entry


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