import os
import aisuite as ai
from langchain_core.prompts import PromptTemplate
from typing import Optional
from prompt_agente import prompt_agente, Info
from prompt_meta_agente import prompt_meta_agente

# Either set the environment variables or define the parameters below.
# Setting the parameters in ai.Client() will override the environment variable values.
client = ai.Client()

# model = "ollama:qwen3:4b"  
model = "ollama:gemma3:27b"  

# Exemplo de uso da função prompt_agente
formatted_prompt = prompt_agente(
    role="agente de teste",
    json_string='{"campo": "valor1", "campo2": "valor2"}',
    task="Explique como usar o PromptTemplate do LangChain.",
    instruction="Seja detalhado e objetivo.",
    info_list=[
        Info('thinking', 'Debate Agent Expert abc1', 'Vou analisar o problema...', 0),
        Info('code', 'Debate Agent Expert abc1', 'def solve():\n    return 42', 0)
    ]  # Descomente para testar com lista de Info
)

print("\n--- Prompt formatado ---\n")
print(formatted_prompt)

# messages = [
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "What's the weather like today?"},
# ]

# response = client.chat.completions.create(
#     model=model,
#     messages=messages,
# )

# print(response.choices[0].message.content)

print('########################################################')

# Exemplo de uso da função prompt_meta_agente
formatted_prompt_meta = prompt_meta_agente(
    arquiteturas_agentes="Utilize as melhores práticas de arquitetura de agentes disponíveis.",
    exemplos_funcionais="Baseie-se em agentes que demonstram raciocínio claro e resultados precisos.",
    exemplos_nao_funcionais="Evite agentes que produzem respostas vagas ou inconsistentes.",
    task_explicacao="Crie um agente que resolva o problema de encontrar a raiz quadrada de um número."
)

print("\n--- Prompt formatado ---\n")
print(formatted_prompt_meta)