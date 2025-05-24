#!/usr/bin/env python3
"""
Exemplo simples de uso do LLM Meta Agent
Demonstra como criar um agente especializado
"""

from llm_meta_agent import LLM_Meta_Agent

def exemplo_simples():
    """Exemplo básico de criação de agente."""
    print("🚀 EXEMPLO SIMPLES DO META-AGENTE")
    print("=" * 50)
    
    # Criar meta-agente com modelo menor para teste rápido
    meta_agent = LLM_Meta_Agent(
        model="ollama:gemma3:4b",
        temperatura=0.3
    )
    
    # Definir tarefa para o novo agente
    task = """
    Criar um agente especialista em problemas de strings e palíndromos.
    O agente deve:
    - Analisar strings de forma detalhada
    - Verificar palíndromos com alta precisão
    - Usar técnicas de análise step-by-step
    - Ser robusto contra edge cases
    
    Priorize acurácia sobre velocidade.
    """
    
    print("🎯 Tarefa definida:")
    print(task)
    
    # Gerar apenas o código (sem teste completo)
    print("\n🤖 Gerando código do agente...")
    agent_spec = meta_agent.generate_agent_code(task)
    
    print(f"\n✅ Agente gerado:")
    print(f"📝 Nome: {agent_spec['name']}")
    print(f"💭 Pensamento: {agent_spec['pensamento']}")
    print(f"\n💻 Código gerado:")
    print("-" * 60)
    print(agent_spec['code'])
    print("-" * 60)
    
    return agent_spec

def exemplo_com_teste():
    """Exemplo com teste completo do agente."""
    print("\n🧪 EXEMPLO COM TESTE COMPLETO")
    print("=" * 50)
    
    meta_agent = LLM_Meta_Agent(
        model="ollama:gemma3:4b",
        temperatura=0.2  # Temperatura mais baixa para precisão
    )
    
    task = """
    Criar um agente simples mas eficaz para problemas básicos de LeetCode.
    Foque em:
    - Problemas de arrays simples
    - Verificação de palíndromos
    - Operações matemáticas básicas
    
    Use uma abordagem direta e confiável.
    """
    
    print("🎯 Criando e testando agente completo...")
    result = meta_agent.create_and_evaluate_agent(task)
    
    if result["success"]:
        agent = result["agent"]
        print(f"\n✅ Agente criado com sucesso!")
        print(f"📝 Nome: {agent['name']}")
        print(f"🎯 ID: {agent['agent_id']}")
        print(f"📊 Acurácia: {agent['performance']['accuracy']:.1f}%")
        print(f"⏱️ Tempo médio: {agent['performance']['avg_execution_time']:.2f}s")
        print(f"💭 Pensamento: {agent['thinking'][:200]}...")
        
        # Mostrar estatísticas
        stats = meta_agent.get_agent_statistics()
        print(f"\n📈 Estatísticas do histórico:")
        print(f"   Total de agentes: {stats['total_agents']}")
        print(f"   Acurácia média: {stats.get('avg_accuracy', 0):.1f}%")
        
    else:
        print(f"❌ Erro: {result['error']}")
        print(f"Detalhes: {result.get('details', 'N/A')}")

def main():
    """Executa os exemplos."""
    try:
        # Exemplo simples (só geração)
        agent_spec = exemplo_simples()
        
        # Perguntar se quer continuar com teste completo
        print("\n" + "=" * 60)
        resposta = input("Deseja executar o teste completo? (s/n): ").lower().strip()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            exemplo_com_teste()
        else:
            print("✅ Exemplo concluído!")
            
    except KeyboardInterrupt:
        print("\n⚠️ Exemplo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main() 