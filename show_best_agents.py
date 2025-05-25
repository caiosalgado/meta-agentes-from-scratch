#!/usr/bin/env python3
"""
Script simples para mostrar os agentes com melhor performance
"""

import json
from pathlib import Path
from datetime import datetime


def load_agents(history_file="agent_history.json"):
    """Carrega dados dos agentes do arquivo JSON."""
    file_path = Path(history_file)
    
    if not file_path.exists():
        print(f"❌ Arquivo {history_file} não encontrado!")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Carregados {len(data)} agentes do histórico\n")
        return data
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return []


def show_best_agents(agents_data, top_n=5):
    """Mostra os melhores agentes ordenados por acurácia."""
    if not agents_data:
        print("❌ Nenhum dado de agente disponível!")
        return
    
    # Ordenar por acurácia (decrescente) e tempo (crescente)
    sorted_agents = sorted(
        agents_data,
        key=lambda x: (
            -x.get("performance", {}).get("accuracy", 0),
            x.get("performance", {}).get("avg_execution_time", float('inf'))
        )
    )
    
    print(f"🏆 TOP {top_n} AGENTES COM MELHOR ACURÁCIA")
    print("="*80)
    
    for i, agent in enumerate(sorted_agents[:top_n], 1):
        # Dados básicos
        agent_id = agent.get("agent_id", "N/A")
        name = agent.get("name", "Sem nome")
        
        # Performance
        performance = agent.get("performance", {})
        accuracy = performance.get("accuracy", 0)
        avg_time = performance.get("avg_execution_time", 0)
        accuracy_std = performance.get("accuracy_std", 0)
        
        # Estatísticas de teste
        testing_stats = agent.get("testing_stats", {})
        successful_runs = testing_stats.get("successful_runs", 0)
        total_runs = testing_stats.get("total_runs", 0)
        
        # Data de criação
        creation_time = agent.get("creation_timestamp", "")
        if creation_time:
            try:
                dt = datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
                creation_str = dt.strftime("%d/%m/%Y %H:%M")
            except:
                creation_str = creation_time
        else:
            creation_str = "N/A"
        
        # Score combinado (acurácia - penalização por tempo)
        combined_score = accuracy - (avg_time / 10)
        
        print(f"\n🥇 RANK #{i} - {name}")
        print(f"   🆔 ID: {agent_id}")
        print(f"   🎯 Acurácia: {accuracy:.1f}% (±{accuracy_std:.1f}%)")
        print(f"   ⏱️  Tempo Médio: {avg_time:.2f}s")
        print(f"   🏅 Score Combinado: {combined_score:.1f}")
        print(f"   ✅ Execuções Bem-sucedidas: {successful_runs}/{total_runs}")
        print(f"   📅 Criado em: {creation_str}")
        
        # Descrição resumida
        thinking = agent.get("thinking", "")
        if thinking:
            # Pegar apenas os primeiros 150 caracteres
            short_thinking = thinking[:150] + "..." if len(thinking) > 150 else thinking
            print(f"   💭 Descrição: {short_thinking}")
        
        # Tipo de agente
        config = agent.get("config", {})
        agent_type = config.get("type", "N/A")
        print(f"   🔧 Tipo: {agent_type}")
        
        print("-" * 80)


def show_general_stats(agents_data):
    """Mostra estatísticas gerais do histórico."""
    if not agents_data:
        return
    
    accuracies = [agent.get("performance", {}).get("accuracy", 0) for agent in agents_data]
    times = [agent.get("performance", {}).get("avg_execution_time", 0) for agent in agents_data]
    
    # Filtrar valores válidos
    valid_accuracies = [acc for acc in accuracies if acc > 0]
    valid_times = [t for t in times if t > 0]
    
    print(f"\n📊 ESTATÍSTICAS GERAIS")
    print("="*50)
    
    if valid_accuracies:
        avg_accuracy = sum(valid_accuracies) / len(valid_accuracies)
        max_accuracy = max(valid_accuracies)
        min_accuracy = min(valid_accuracies)
        print(f"🎯 Acurácia:")
        print(f"   Média: {avg_accuracy:.1f}%")
        print(f"   Máxima: {max_accuracy:.1f}%")
        print(f"   Mínima: {min_accuracy:.1f}%")
    
    if valid_times:
        avg_time = sum(valid_times) / len(valid_times)
        max_time = max(valid_times)
        min_time = min(valid_times)
        print(f"\n⏱️  Tempo de Execução:")
        print(f"   Médio: {avg_time:.2f}s")
        print(f"   Máximo: {max_time:.2f}s")
        print(f"   Mínimo: {min_time:.2f}s")
    
    # Contadores por performance
    high_perf = len([acc for acc in valid_accuracies if acc >= 70])
    medium_perf = len([acc for acc in valid_accuracies if 30 <= acc < 70])
    low_perf = len([acc for acc in valid_accuracies if acc < 30])
    
    print(f"\n🏆 Distribuição de Performance:")
    print(f"   Alta (≥70%): {high_perf} agentes")
    print(f"   Média (30-70%): {medium_perf} agentes")
    print(f"   Baixa (<30%): {low_perf} agentes")


def main():
    """Função principal."""
    print("🔍 ANÁLISE DE AGENTES - MELHORES PERFORMERS")
    print("="*60)
    
    # Carregar dados
    agents_data = load_agents()
    
    if not agents_data:
        return
    
    # Mostrar top 5 agentes
    show_best_agents(agents_data, top_n=5)
    
    # Mostrar estatísticas gerais
    show_general_stats(agents_data)
    
    print(f"\n✨ Análise concluída! Total de {len(agents_data)} agentes analisados.")


if __name__ == "__main__":
    main() 