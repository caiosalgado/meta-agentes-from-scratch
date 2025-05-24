#!/usr/bin/env python3
"""
Criador de Agentes Manuais - Cria histórico inicial para o meta-agente
"""

import json
import time
from datetime import datetime
from llm_meta_agent import LLM_Meta_Agent
from llm_agent import LLM_Agent

def log_step(step: str, details: str = ""):
    """Log detalhado com timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🔍 {step}")
    if details:
        print(f"    ℹ️  {details}")

def test_agent_with_logs(agent_name: str, agent_code: str, description: str):
    """
    Testa um agente com logs detalhados de cada passo - EXECUTA 5 VEZES.
    
    Args:
        agent_name: Nome do agente
        agent_code: Código Python do agente
        description: Descrição do que o agente faz
        
    Returns:
        Dict com resultados consolidados de 5 execuções
    """
    print("\n" + "="*80)
    log_step(f"TESTANDO AGENTE: {agent_name}")
    log_step("Descrição", description)
    print("="*80)
    
    # Carregar problemas
    log_step("Carregando problemas LeetCode...")
    try:
        with open("leetcode_problems.json", encoding="utf-8") as f:
            problems = json.load(f)["problems"]
        log_step(f"✅ {len(problems)} problemas carregados")
    except Exception as e:
        log_step(f"❌ Erro ao carregar problemas: {e}")
        return None
    
    # Executar código do agente
    log_step("Executando código do agente...")
    try:
        local_vars = {}
        exec(agent_code, globals(), local_vars)
        
        if 'solve_problem' not in local_vars:
            log_step("❌ Função solve_problem não encontrada no código")
            return None
            
        solve_function = local_vars['solve_problem']
        log_step("✅ Função solve_problem carregada com sucesso")
        
    except Exception as e:
        log_step(f"❌ Erro ao executar código: {e}")
        return None
    
    # EXECUTAR 5 VEZES PARA MÉTRICAS CONFIÁVEIS
    log_step("🔄 INICIANDO 5 EXECUÇÕES PARA MÉTRICAS CONFIÁVEIS...")
    
    all_runs = []
    successful_runs = 0
    
    for run_num in range(1, 6):  # 5 execuções
        log_step(f"🏃 EXECUÇÃO {run_num}/5")
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
                    
                    if accuracy > 50:  # Considera correto se > 50% dos testes passaram
                        correct_count += 1
                        log_step(f"    🎯 SUCESSO - Acurácia: {accuracy:.1f}%")
                    else:
                        log_step(f"    ❌ FALHOU - Acurácia: {accuracy:.1f}%")
                    
                    problem_results.append({
                        "problem": problem_name,
                        "success": accuracy > 50,
                        "accuracy": accuracy,
                        "execution_time": execution_time,
                        "details": details
                    })
                    
                else:
                    log_step(f"    ❌ Resultado inválido: {type(result)}")
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
                run_errors.append(f"{problem_name}: {error_msg}")
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
        return None
    
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
    log_step(f"  ✅ Execuções Bem-sucedidas: {successful_runs}/5")
    
    return {
        "name": agent_name,
        "description": description,
        "accuracy": final_accuracy,
        "accuracy_std": accuracy_std,
        "accuracy_range": [min_accuracy, max_accuracy],
        "avg_execution_time": final_avg_time,
        "time_std": time_std,
        "time_range": [min_time, max_time],
        "successful_runs": successful_runs,
        "total_runs": 5,
        "all_runs": all_runs,
        "code": agent_code
    }

def create_agent_1_simple():
    """Agente 1: Simples e eficiente - esperado alta performance."""
    return """
# AGENTE 1: Simple Expert Solver
from llm_agent import LLM_Agent

def solve_problem(problem_data):
    '''Agente simples com foco em eficiência e precisão.'''
    
    # Criar agente especializado
    agent = LLM_Agent(
        role="Python Coding Expert",
        instruction=f'''Você é um especialista em Python. 
        
        Resolva este problema de programação:
        {problem_data.get("description", "")}
        
        Retorne apenas código Python limpo e eficiente.''',
        arquitetura_resposta={"code": "Código Python completo"},
        model="ollama:qwen3:32b",
        temperatura=0.2  # Baixa para precisão
    )
    
    # Executar e retornar resultado
    return agent.generate_response(problem_data)
"""

def create_agent_2_complex():
    """Agente 2: Pipeline complexo - esperado problemas de performance."""
    return """
# AGENTE 2: Over-engineered Complex Pipeline  
from llm_agent import LLM_Agent

def solve_problem(problem_data):
    '''Pipeline complexo com múltiplos agentes - pode ter overhead.'''
    
    # AGENTE 1: Analista
    analyst = LLM_Agent(
        role="Problem Analyst", 
        instruction=f'''Analise este problema de programação em detalhes:
        {problem_data.get("description", "")}
        
        Identifique padrões, edge cases e estratégias de solução.''',
        arquitetura_resposta={"analysis": "Análise detalhada do problema"},
        model="ollama:gemma3:27b",
        temperatura=0.4
    )
    
    analysis_result = analyst.generate_response(problem_data)
    
    # AGENTE 2: Arquiteto
    architect = LLM_Agent(
        role="Solution Architect",
        instruction=f'''Baseado nesta análise: {analysis_result.get("analysis", "")}
        
        Crie uma arquitetura de solução detalhada.''',
        arquitetura_resposta={"architecture": "Arquitetura da solução"},
        model="ollama:qwen3:14b", 
        temperatura=0.5,
        arquitetura_respostas_anteriores=[analysis_result]
    )
    
    architecture_result = architect.generate_response(problem_data)
    
    # AGENTE 3: Implementador
    implementer = LLM_Agent(
        role="Code Implementer",
        instruction=f'''Implemente esta solução:
        Análise: {analysis_result.get("analysis", "")}
        Arquitetura: {architecture_result.get("architecture", "")}
        
        Código Python final:''',
        arquitetura_resposta={"code": "Código Python implementado"},
        model="ollama:qwen3:32b",
        temperatura=0.3,
        arquitetura_respostas_anteriores=[analysis_result, architecture_result]
    )
    
    return implementer.generate_response(problem_data)
"""

def create_agent_3_debate():
    """Agente 3: Debate entre experts - esperado performance média."""
    return """
# AGENTE 3: Expert Debate Solver
from llm_agent import LLM_Agent

def solve_problem(problem_data):
    '''Dois experts debatem, um terceiro decide - abordagem intermediária.'''
    
    # EXPERT 1: Abordagem Algorítmica
    expert1 = LLM_Agent(
        role="Algorithm Expert",
        instruction=f'''Você é um especialista em algoritmos. 
        
        Resolva este problema focando em eficiência algorítmica:
        {problem_data.get("description", "")}
        
        Priorize complexidade temporal e espacial.''',
        arquitetura_resposta={"solution": "Solução algorítmica", "reasoning": "Raciocínio"},
        model="ollama:qwen3:30b",
        temperatura=0.3
    )
    
    # EXPERT 2: Abordagem Prática  
    expert2 = LLM_Agent(
        role="Practical Coder",
        instruction=f'''Você é um programador prático.
        
        Resolva este problema focando em simplicidade e legibilidade:
        {problem_data.get("description", "")}
        
        Priorize código limpo e funcionais.''',
        arquitetura_resposta={"solution": "Solução prática", "reasoning": "Raciocínio"},
        model="ollama:gemma3:12b", 
        temperatura=0.4
    )
    
    # Executar ambos experts
    solution1 = expert1.generate_response(problem_data)
    solution2 = expert2.generate_response(problem_data)
    
    # JUIZ: Decide entre as duas soluções
    judge = LLM_Agent(
        role="Technical Judge",
        instruction=f'''Avalie estas duas soluções e escolha/combine a melhor:
        
        Solução Algorítmica: {solution1.get("solution", "")}
        Raciocínio 1: {solution1.get("reasoning", "")}
        
        Solução Prática: {solution2.get("solution", "")}  
        Raciocínio 2: {solution2.get("reasoning", "")}
        
        Retorne a melhor solução final.''',
        arquitetura_resposta={"code": "Código Python final escolhido"},
        model="ollama:qwen3:32b",
        temperatura=0.2,
        arquitetura_respostas_anteriores=[solution1, solution2]
    )
    
    return judge.generate_response(problem_data)
"""

def main():
    """Função principal - cria e testa os 3 agentes manuais."""
    print("🚀 CRIANDO AGENTES MANUAIS PARA HISTÓRICO INICIAL")
    print("="*80)
    
    # Definir os 3 agentes
    agents = [
        {
            "name": "Simple Expert Solver",
            "code": create_agent_1_simple(),
            "description": "Agente simples com foco em eficiência e precisão",
            "expected": "Alta performance"
        },
        {
            "name": "Complex Pipeline Solver", 
            "code": create_agent_2_complex(),
            "description": "Pipeline complexo com múltiplos agentes especializados",
            "expected": "Problemas de performance/overhead"
        },
        {
            "name": "Expert Debate Solver",
            "code": create_agent_3_debate(), 
            "description": "Dois experts debatem, um juiz decide",
            "expected": "Performance intermediária"
        }
    ]
    
    # Criar meta-agente para salvar histórico
    log_step("Inicializando meta-agente...")
    meta_agent = LLM_Meta_Agent()
    
    # Testar cada agente
    results = []
    for i, agent_config in enumerate(agents):
        log_step(f"INICIANDO TESTE {i+1}/3: {agent_config['name']}")
        log_step(f"Expectativa: {agent_config['expected']}")
        
        result = test_agent_with_logs(
            agent_config['name'],
            agent_config['code'], 
            agent_config['description']
        )
        
        if result:
            results.append(result)
            
            # Criar entrada do histórico com estatísticas consolidadas
            agent_entry = {
                "agent_id": f"manual_{i+1:03d}",
                "name": result['name'],
                "creation_timestamp": datetime.now().isoformat(),
                "config": {
                    "type": "manual_pipeline",
                    "code": result['code'],
                    "description": result['description']
                },
                "performance": {
                    "accuracy": result['accuracy'],
                    "accuracy_std": result['accuracy_std'],
                    "accuracy_range": result['accuracy_range'],
                    "avg_execution_time": result['avg_execution_time'],
                    "time_std": result['time_std'],
                    "time_range": result['time_range']
                },
                "testing_stats": {
                    "successful_runs": result['successful_runs'],
                    "total_runs": result['total_runs'],
                    "all_runs_summary": [
                        {
                            "run": run['run_number'],
                            "accuracy": run['accuracy'],
                            "avg_time": run['avg_execution_time'],
                            "errors": len(run['errors'])
                        } for run in result['all_runs']
                    ]
                },
                "thinking": f"Agente criado manualmente para teste. {result['description']}. Testado {result['total_runs']} vezes com {result['successful_runs']} execuções bem-sucedidas. Acurácia média: {result['accuracy']:.1f}%.",
                "task_explanation": f"Teste manual de {result['name']} - 5 execuções para métricas confiáveis",
                "detailed_results": result['all_runs']  # Todos os runs detalhados
            }
            
            # Adicionar ao histórico
            meta_agent.agent_history.append(agent_entry)
            log_step(f"✅ Agente {result['name']} adicionado ao histórico")
        else:
            log_step(f"❌ Falha no teste do agente {agent_config['name']}")
    
    # Salvar histórico
    log_step("Salvando histórico no arquivo...")
    meta_agent._save_history()
    log_step("✅ Histórico salvo em agent_history.json")
    
    # Resumo final com estatísticas detalhadas
    print("\n" + "="*80)
    log_step("📊 RESUMO FINAL DOS TESTES (5 EXECUÇÕES CADA)")
    print("="*80)
    
    for result in results:
        print(f"🤖 {result['name']}:")
        print(f"   🎯 Acurácia: {result['accuracy']:.1f}% (±{result['accuracy_std']:.1f})")
        print(f"   📊 Range Acurácia: {result['accuracy_range'][0]:.1f}% - {result['accuracy_range'][1]:.1f}%")
        print(f"   ⏱️  Tempo Médio: {result['avg_execution_time']:.2f}s (±{result['time_std']:.2f})")
        print(f"   📊 Range Tempo: {result['time_range'][0]:.2f}s - {result['time_range'][1]:.2f}s")
        print(f"   ✅ Execuções OK: {result['successful_runs']}/5")
        print()
    
    log_step(f"🎉 Processo concluído! {len(results)} agentes criados e testados 5 vezes cada.")
    log_step("📈 Agora o meta-agente tem histórico estatisticamente confiável para aprender!")

if __name__ == "__main__":
    main() 