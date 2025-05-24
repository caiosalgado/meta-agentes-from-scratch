#!/usr/bin/env python3
"""
Teste do LLM Meta Agent
Demonstra como usar o meta-agente para criar e avaliar novos agentes
"""

from llm_meta_agent import LLM_Meta_Agent
import json

def test_meta_agent_basic():
    """Teste básico do meta-agente."""
    print("🚀 TESTE BÁSICO DO META-AGENTE")
    print("=" * 50)
    
    # Criar meta-agente
    meta_agent = LLM_Meta_Agent(
        model="ollama:gemma3:4b",  # Modelo menor para teste
        temperatura=0.3
    )
    
    # Ver estatísticas iniciais
    stats = meta_agent.get_agent_statistics()
    print(f"📊 Estatísticas iniciais: {stats}")
    
    # Criar primeiro agente
    task1 = """
    Criar um agente especialista em problemas de palíndromos e strings.
    O agente deve ser excelente em:
    - Verificar se strings/números são palíndromos
    - Manipular e processar strings
    - Problemas de inversão de texto
    
    Use técnicas de análise step-by-step para maximizar acurácia.
    """
    
    print(f"\n🎯 Criando agente para: {task1[:100]}...")
    result1 = meta_agent.create_and_evaluate_agent(task1)
    
    if result1["success"]:
        print("✅ Primeiro agente criado com sucesso!")
        agent1 = result1["agent"]
        print(f"   Nome: {agent1['name']}")
        print(f"   Acurácia: {agent1['performance']['accuracy']:.1f}%")
        print(f"   Tempo: {agent1['performance']['avg_execution_time']:.2f}s")
    else:
        print(f"❌ Erro no primeiro agente: {result1['error']}")
        return
    
    # Criar segundo agente (agora com histórico)
    task2 = """
    Criar um agente que combine múltiplas técnicas para resolver problemas matemáticos.
    Deve ser capaz de:
    - Conversão entre diferentes bases numéricas
    - Problemas de soma e manipulação de arrays
    - Lógica matemática complexa
    
    Use pipeline com múltiplos agentes especializados se necessário.
    """
    
    print(f"\n🎯 Criando segundo agente...")
    result2 = meta_agent.create_and_evaluate_agent(task2)
    
    if result2["success"]:
        print("✅ Segundo agente criado com sucesso!")
        agent2 = result2["agent"]
        print(f"   Nome: {agent2['name']}")
        print(f"   Acurácia: {agent2['performance']['accuracy']:.1f}%")
        print(f"   Tempo: {agent2['performance']['avg_execution_time']:.2f}s")
    else:
        print(f"❌ Erro no segundo agente: {result2['error']}")
    
    # Estatísticas finais
    final_stats = meta_agent.get_agent_statistics()
    print(f"\n📊 Estatísticas finais:")
    print(f"   Total de agentes: {final_stats['total_agents']}")
    print(f"   Acurácia média: {final_stats.get('avg_accuracy', 0):.1f}%")
    print(f"   Agentes funcionais: {final_stats.get('functional_agents', 0)}")
    print(f"   Agentes alta performance: {final_stats.get('high_performance_agents', 0)}")
    
    # Top agentes
    top_agents = meta_agent.list_top_agents(3)
    print(f"\n🏆 Top agentes:")
    for i, agent in enumerate(top_agents, 1):
        print(f"   {i}. {agent['name']}: {agent['performance']['accuracy']:.1f}%")

def test_generate_agent_only():
    """Teste apenas a geração de código (sem execução completa)."""
    print("\n🧪 TESTE DE GERAÇÃO DE CÓDIGO")
    print("=" * 50)
    
    meta_agent = LLM_Meta_Agent(model="ollama:gemma3:4b")
    
    task = """
    Criar um agente inovador que use técnicas de debate entre múltiplos especialistas.
    O pipeline deve ter:
    1. Agente analisador que identifica o tipo de problema
    2. 3 agentes especialistas com diferentes abordagens
    3. Agente decisor final que sintetiza as respostas
    
    Use diferentes modelos e temperaturas estrategicamente.
    """
    
    print("🤖 Gerando código de agente...")
    agent_spec = meta_agent.generate_agent_code(task)
    
    print(f"✅ Agente gerado:")
    print(f"   Nome: {agent_spec['name']}")
    print(f"   Pensamento: {agent_spec['pensamento'][:200]}...")
    print(f"\n💻 Código gerado:")
    print("-" * 40)
    print(agent_spec['code'][:500] + "...")
    print("-" * 40)

def test_load_existing_history():
    """Teste carregamento de histórico existente."""
    print("\n📂 TESTE DE HISTÓRICO")
    print("=" * 50)
    
    meta_agent = LLM_Meta_Agent()
    
    if meta_agent.agent_history:
        print(f"📚 Histórico carregado: {len(meta_agent.agent_history)} agentes")
        
        # Mostrar exemplos funcionais
        print("\n✅ Exemplos funcionais:")
        functional = meta_agent.get_functional_examples(2)
        print(functional[:300] + "..." if len(functional) > 300 else functional)
        
        # Mostrar exemplos não funcionais
        print("\n❌ Exemplos não funcionais:")
        non_functional = meta_agent.get_non_functional_examples(2)
        print(non_functional[:300] + "..." if len(non_functional) > 300 else non_functional)
        
    else:
        print("📭 Nenhum histórico encontrado. Execute teste_meta_agent_basic() primeiro.")

def main():
    """Executa todos os testes."""
    print("🧪 TESTES DO LLM META AGENT")
    print("=" * 60)
    
    try:
        # Teste básico (cria agentes)
        test_meta_agent_basic()
        
        # Teste só geração
        test_generate_agent_only()
        
        # Teste histórico
        test_load_existing_history()
        
        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES CONCLUÍDOS!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante testes: {str(e)}")

if __name__ == "__main__":
    main() 