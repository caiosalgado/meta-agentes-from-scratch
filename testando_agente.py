# %%

import os
import json
import aisuite as ai
from leetcode_solver import create_leetcode_prompt

# Either set the environment variables or define the parameters below.
# Setting the parameters in ai.Client() will override the environment variable values.
client = ai.Client()
client.configure({
  "ollama" : {
    "timeout": 600,
  }
})

model = "ollama:qwen3:4b"  
# model = "ollama:gemma3:27b"  

# Carregar o problema do JSON
with open("leetcode_problems.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

problem = data['problems'][0]  # Primeiro problema (Palindrome Number)

role = "Especialista em Algoritmos Python e LeetCode"

# Definir parâmetros
expected_json = {
    "analysis": "Análise detalhada do problema e estratégia de solução",
    "solution": "Código Python completo da solução",
}

instructions = """
1. Analise cuidadosamente o problema e identifique a abordagem mais eficiente
2. Complete o código inicial fornecido com sua implementação
3. Considere os edge cases e constraints mencionados
4. Otimize para complexidade de tempo e espaço quando possível
5. Explique claramente sua estratégia e raciocínio
6. Verifique se sua solução funciona com todos os exemplos fornecidos
"""

# Obter system_prompt e prompt usando create_leetcode_prompt
system_prompt, prompt = create_leetcode_prompt(
    leetcode_problem=problem,
    expected_json=expected_json,
    instructions=instructions,
    role=role,
    info_list=None
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": prompt},
]

response = client.chat.completions.create(
    model=model,
    messages=messages,
)

print(response.choices[0].message.content)

# %%