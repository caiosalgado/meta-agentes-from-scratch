#!/usr/bin/env python3
"""
Debug Meta Agent - Simula uma execução completa do descobrir_melhor_arquitetura.py
Mostra todos os passos internos: prompts, resposta do LLM e execução
"""

from llm_meta_agent import LLM_Meta_Agent
import re

def extract_task_from_main_script():
    """Extrai a tarefa real do descobrir_melhor_arquitetura.py"""
    try:
        with open("descobrir_melhor_arquitetura.py", "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'tarefa\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else None
    except:
        return None

def extract_model_and_temp():
    """Extrai modelo e temperatura do descobrir_melhor_arquitetura.py"""
    try:
        with open("descobrir_melhor_arquitetura.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        model_match = re.search(r'model\s*=\s*["\']([^"\']+)["\']', content)
        temp_match = re.search(r'temperatura\s*=\s*([0-9.]+)', content)
        
        model = model_match.group(1) if model_match else "ollama:qwen3:32b"
        temperatura = float(temp_match.group(1)) if temp_match else 0.6
        
        return model, temperatura
    except:
        return "ollama:qwen3:32b", 0.6

def debug_meta_agent_execution():
    """Simula uma execução completa do descobrir_melhor_arquitetura.py"""
    
    print("🔍 SIMULANDO DESCOBRIR_MELHOR_ARQUITETURA.PY (1 TENTATIVA)")
    print("=" * 70)
    
    # 1. Extrair dados reais do script original
    tarefa = extract_task_from_main_script()
    model, temperatura = extract_model_and_temp()
    
    if not tarefa:
        print("❌ Não foi possível extrair a tarefa")
        return
    
    print(f"📝 TAREFA EXTRAÍDA: {tarefa}")
    print(f"🎯 MODELO: {model}")
    print(f"🌡️ TEMPERATURA: {temperatura}")
    
    # 2. Criar meta-agente (igual ao script original)
    meta_agent = LLM_Meta_Agent(model=model, temperatura=temperatura)
    
    # 3. Mostrar prompts que vão para o LLM
    print("\n" + "=" * 70)
    print("🤖 SYSTEM PROMPT QUE VAI PARA O LLM:")
    print("=" * 70)
    system_prompt = meta_agent.SYSTEM_PROMPT
    print(system_prompt)
    
    print("\n" + "=" * 70)
    print("👤 USER PROMPT QUE VAI PARA O LLM:")
    print("=" * 70)
    user_prompt = meta_agent._build_meta_prompt(tarefa)
    print(user_prompt)
    
    # 4. Executar o processo completo (igual ao script original)
    print("\n" + "=" * 70)
    print("🚀 ENVIANDO PARA O LLM E EXECUTANDO...")
    print("=" * 70)
    
    result = meta_agent.create_and_evaluate_agent(tarefa)
    
    # 5. Mostrar resposta do LLM
    if result["success"]:
        print("✅ LLM GEROU CÓDIGO COM SUCESSO!")
        print("\n📄 CÓDIGO GERADO PELO LLM:")
        print("-" * 50)
        agent_code = result["agent"]["config"]["code"]
        print(agent_code)
        
        # 6. Mostrar resultados da execução
        print("\n📊 RESULTADOS DOS TESTES:")
        print("-" * 50)
        performance = result["performance"]
        print(f"🎯 Acurácia: {performance['accuracy']:.1f}%")
        print(f"⏱️ Tempo médio: {performance['avg_execution_time']:.2f}s")
        print(f"📈 Nome do agente: {result['agent']['name']}")
        
    else:
        print("❌ FALHA NA EXECUÇÃO!")
        print(f"🚫 Erro: {result['error']}")

if __name__ == "__main__":
    debug_meta_agent_execution() 