#!/usr/bin/env python3
"""
Debug Agent Prompts - Mostra apenas system e user prompts
"""

from llm_agent import LLM_Agent
import json
import re

def load_leetcode_problems():
    """Carrega problemas do leetcode_problems.json"""
    try:
        with open("leetcode_problems.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("problems", [])
    except:
        return []

def load_agent_history():
    """Carrega histórico de agentes"""
    try:
        with open("agent_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def extract_agent_config():
    """Extrai configuração de um agente funcional"""
    history = load_agent_history()
    if not history:
        return None
    
    # Pegar primeiro agente funcional
    functional_agents = [a for a in history if a.get("performance", {}).get("accuracy", 0) >= 30]
    agent = functional_agents[0] if functional_agents else history[0]
    
    code = agent.get("config", {}).get("code", "")
    
    # Extrair configurações
    role_match = re.search(r'role\s*=\s*["\']([^"\']+)["\']', code)
    instruction_match = re.search(r'instruction\s*=\s*["\']([^"\']*)["\']', code, re.DOTALL)
    model_match = re.search(r'model\s*=\s*["\']([^"\']+)["\']', code)
    temp_match = re.search(r'temperatura\s*=\s*([0-9.]+)', code)
    
    return {
        "role": role_match.group(1) if role_match else "Especialista em Python",
        "instruction": instruction_match.group(1) if instruction_match else "Resolva este problema",
        "model": model_match.group(1) if model_match else "ollama:qwen3:4b",
        "temperatura": float(temp_match.group(1)) if temp_match else 0.7
    }

def debug_agent_prompts():
    """Mostra system e user prompts de um agente"""
    
    # Carregar dados
    problems = load_leetcode_problems()
    agent_config = extract_agent_config()
    
    if not problems or not agent_config:
        return
    
    # Usar primeiro problema
    problem = problems[0]
    
    # Construir tarefa
    task = f"""
Problema: {problem['title']}
Descrição: {problem['description']}
Assinatura: {problem['function_signature']}
Testes: {json.dumps(problem['tests'], indent=2)}
    """
    
    # Criar agente
    agent = LLM_Agent(
        role=agent_config['role'],
        instruction=agent_config['instruction'],
        arquitetura_resposta={"code": "Código Python completo"},
        temperatura=agent_config['temperatura'],
        model=agent_config['model']
    )
    
    # Construir prompts
    system_prompt, user_prompt = agent.create_prompt(task)
    
    print("SYSTEM PROMPT:")
    print("=" * 50)
    print(system_prompt)
    
    print("\n\nUSER PROMPT:")
    print("=" * 50)
    print(user_prompt)

if __name__ == "__main__":
    debug_agent_prompts() 