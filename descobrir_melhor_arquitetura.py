#!/usr/bin/env python3
from llm_meta_agent import LLM_Meta_Agent

def main():
    TENTATIVAS = 100

    meta_agent = LLM_Meta_Agent(model="ollama:qwen3:32b", temperatura=0.6)
    
    tarefa = "Descubra a arquitetura de agentes ou pipeline com multiplos agentes que resolve o maior numero de desafios do leetcode que estão no json no menor tempo possível"
    
    for i in range(TENTATIVAS):
        print(f"Tentativa {i+1}/{TENTATIVAS}")
        result = meta_agent.create_and_evaluate_agent(tarefa)
        if result["success"]:
            print(f"✅ {result['agent']['name']}: {result['performance']['accuracy']:.1f}% - {result['performance']['avg_execution_time']:.1f}s")
        else:
            print(f"❌ Falhou: {result['error']}")

if __name__ == "__main__":
    main()