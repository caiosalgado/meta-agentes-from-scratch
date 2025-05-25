#!/usr/bin/env python3
"""
Teste de acesso concorrente ao histórico de agentes
"""

import time
import os
import multiprocessing
from llm_meta_agent import LLM_Meta_Agent

def test_concurrent_save(process_id: int, num_agents: int = 3):
    """
    Simula um processo criando e salvando agentes.
    
    Args:
        process_id: ID único do processo
        num_agents: Número de agentes a criar
    """
    print(f"🔄 Processo {process_id} iniciado (PID: {os.getpid()})")
    
    # Criar meta-agente com arquivo de teste
    meta_agent = LLM_Meta_Agent(
        model="ollama:gemma3:4b",  # Modelo mais leve para teste
        history_file=f"test_history_concurrent.json",
        temperatura=0.3
    )
    
    for i in range(num_agents):
        try:
            print(f"📝 Processo {process_id}: Criando agente {i+1}/{num_agents}")
            
            # Simular criação de agente
            test_results = {
                "accuracy": 50.0 + (i * 10),
                "accuracy_std": 5.0,
                "accuracy_range": [45.0, 55.0],
                "avg_execution_time": 2.0 + i,
                "time_std": 0.5,
                "time_range": [1.5, 2.5],
                "successful_runs": 2,
                "total_runs": 3,
                "all_runs": [
                    {
                        "run_number": 1,
                        "accuracy": 50.0,
                        "avg_execution_time": 2.0,
                        "errors": []
                    }
                ]
            }
            
            # Adicionar ao histórico (vai usar file locking)
            agent_entry = meta_agent.add_agent_to_history(
                agent_name=f"Test Agent P{process_id}-A{i+1}",
                agent_code=f"# Test code from process {process_id}, agent {i+1}",
                description=f"Agente de teste do processo {process_id}",
                test_results=test_results,
                agent_type="test_agent"
            )
            
            print(f"✅ Processo {process_id}: Agente {agent_entry['agent_id']} salvo")
            
            # Pequena pausa para simular processamento
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Processo {process_id}: Erro no agente {i+1}: {e}")
    
    print(f"🏁 Processo {process_id} concluído")

def main():
    """Teste principal de concorrência."""
    print("🧪 TESTE DE ACESSO CONCORRENTE")
    print("=" * 50)
    
    # Limpar arquivo de teste anterior
    test_file = "test_history_concurrent.json"
    if os.path.exists(test_file):
        os.remove(test_file)
        print("🗑️ Arquivo de teste anterior removido")
    
    # Configurações do teste
    num_processes = 3
    agents_per_process = 2
    
    print(f"📊 Configuração:")
    print(f"   - Processos: {num_processes}")
    print(f"   - Agentes por processo: {agents_per_process}")
    print(f"   - Total esperado: {num_processes * agents_per_process} agentes")
    print()
    
    # Criar e iniciar processos
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        p = multiprocessing.Process(
            target=test_concurrent_save,
            args=(i+1, agents_per_process)
        )
        processes.append(p)
        p.start()
        print(f"🚀 Processo {i+1} iniciado")
    
    # Aguardar todos os processos terminarem
    for i, p in enumerate(processes):
        p.join()
        print(f"✅ Processo {i+1} finalizado")
    
    end_time = time.time()
    
    # Verificar resultados
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DO TESTE")
    print("=" * 50)
    
    if os.path.exists(test_file):
        try:
            import json
            with open(test_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            print(f"✅ Arquivo criado com sucesso")
            print(f"📈 Agentes salvos: {len(history)}")
            print(f"⏱️ Tempo total: {end_time - start_time:.2f}s")
            
            # Verificar IDs únicos
            agent_ids = [agent.get('agent_id') for agent in history]
            unique_ids = set(agent_ids)
            
            if len(agent_ids) == len(unique_ids):
                print("✅ Todos os IDs são únicos")
            else:
                print(f"❌ IDs duplicados encontrados: {len(agent_ids)} total, {len(unique_ids)} únicos")
            
            # Mostrar agentes por processo
            print("\n📋 Agentes por processo:")
            for i in range(1, num_processes + 1):
                process_agents = [a for a in history if f"P{i}" in a.get('name', '')]
                print(f"   Processo {i}: {len(process_agents)} agentes")
            
            # Verificar integridade do JSON
            print("✅ JSON válido e bem formado")
            
        except Exception as e:
            print(f"❌ Erro ao verificar resultados: {e}")
    else:
        print("❌ Arquivo de teste não foi criado")
    
    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    main() 