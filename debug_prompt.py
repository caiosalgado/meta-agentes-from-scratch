#!/usr/bin/env python3
"""
Debug Meta Agent Prompts - Mostra system e user prompts completos
"""

from llm_meta_agent import LLM_Meta_Agent

def debug_meta_prompts(task_explicacao: str, 
                      model: str = "ollama:gemma3:4b", 
                      temperatura: float = 0.3):
    """
    Mostra os prompts do meta-agente sem enviar para o modelo.
    
    Args:
        task_explicacao: Descrição da tarefa para o agente
        model: Modelo LLM a ser usado
        temperatura: Temperatura para geração
    """
    print("🔍 DEBUG META AGENT PROMPTS")
    print("=" * 60)
    
    # Criar meta-agente com parâmetros
    meta_agent = LLM_Meta_Agent(model=model, temperatura=temperatura)
    
    print(f"📝 TAREFA: {task_explicacao}")
    print(f"🎯 MODELO: {model}")
    print(f"🌡️ TEMPERATURA: {temperatura}")
    
    # Construir prompts
    user_prompt = meta_agent._build_meta_prompt(task_explicacao)
    
    # PEGAR O SYSTEM PROMPT DA CONSTANTE DA CLASSE
    system_prompt = meta_agent.SYSTEM_PROMPT
    
    print("\n" + "=" * 60)
    print("🤖 SYSTEM PROMPT:")
    print("=" * 60)
    print(system_prompt)
    
    print("\n" + "=" * 60)
    print(f"👤 USER PROMPT ({len(user_prompt)} caracteres):")
    print("=" * 60)
    print(user_prompt)
    print("=" * 60)
    
    return system_prompt, user_prompt

if __name__ == "__main__":
    # Exemplo de uso
    task = "Criar um agente especialista em problemas de palíndromos e strings"
    
    system, user = debug_meta_prompts(
        task_explicacao=task,
        model="ollama:qwen3:32b", 
        temperatura=0.6
    )
