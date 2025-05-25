#!/usr/bin/env python3
"""
Criador de Agentes Manuais - Cria histórico inicial para o meta-agente
"""

from llm_meta_agent import LLM_Meta_Agent

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
    """Função principal - cria e testa os 3 agentes manuais usando função centralizada."""
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
    
    # Criar meta-agente para usar função centralizada
    print("🔍 Inicializando meta-agente...")
    meta_agent = LLM_Meta_Agent()
    
    # Testar cada agente usando função centralizada
    results = []
    for i, agent_config in enumerate(agents):
        print(f"\n🔍 INICIANDO TESTE {i+1}/3: {agent_config['name']}")
        print(f"🔍 Expectativa: {agent_config['expected']}")
        
        # ✅ USA FUNÇÃO CENTRALIZADA DO META-AGENTE
        test_results = meta_agent.test_agent_pipeline(
            agent_code=agent_config['code'],
            agent_name=agent_config['name']
        )
        
        # ✅ USA FUNÇÃO CENTRALIZADA PARA SALVAR NO HISTÓRICO
        agent_entry = meta_agent.add_agent_to_history(
            agent_name=agent_config['name'],
            agent_code=agent_config['code'], 
            description=agent_config['description'],
            test_results=test_results,
            agent_type="manual_pipeline"
        )
        
        results.append(test_results)
        print(f"✅ Agente {agent_config['name']} adicionado ao histórico")
    
    # Resumo final
    print("\n" + "="*80)
    print(f"🔍 📊 RESUMO FINAL DOS TESTES ({meta_agent.DEFAULT_TEST_RUNS} EXECUÇÕES CADA)")
    print("="*80)
    
    for i, result in enumerate(results):
        agent_name = agents[i]['name']
        print(f"🤖 {agent_name}:")
        print(f"   🎯 Acurácia: {result['accuracy']:.1f}% (±{result.get('accuracy_std', 0):.1f})")
        print(f"   📊 Range Acurácia: {result.get('accuracy_range', [0, 0])[0]:.1f}% - {result.get('accuracy_range', [0, 0])[1]:.1f}%")
        print(f"   ⏱️  Tempo Médio: {result['avg_execution_time']:.2f}s (±{result.get('time_std', 0):.2f})")
        print(f"   📊 Range Tempo: {result.get('time_range', [0, 0])[0]:.2f}s - {result.get('time_range', [0, 0])[1]:.2f}s")
        print(f"   ✅ Execuções OK: {result['successful_runs']}/{result['total_runs']}")
        print()
    
    print(f"🔍 🎉 Processo concluído! {len(results)} agentes criados e testados {meta_agent.DEFAULT_TEST_RUNS} vezes cada.")
    print("🔍 📈 Agora o meta-agente tem histórico estatisticamente confiável para aprender!")

if __name__ == "__main__":
    main() 