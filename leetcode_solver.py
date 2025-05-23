import json
from typing import Dict, Any
from prompt_agente import prompt_agente, Info

def create_leetcode_prompt(
    leetcode_problem: Dict[str, Any],
    expected_json: Dict[str, str], 
    instructions: str,
    role: str,
    info_list: list[Info] | None = None
) -> tuple[str, str]:
    """
    Cria um prompt para resolver problemas do LeetCode.
    
    Args:
        leetcode_problem: Dicionário com as informações do problema do LeetCode
        expected_json: Dicionário com a estrutura JSON esperada na resposta
        instructions: Instruções para o agente
        role: Role/papel do agente
        info_list: Lista opcional de objetos Info
        
    Returns:
        tuple[str, str]: (system_prompt, prompt) - system_prompt até "NAO ESQUEÇA NENHUM CAMPO!", prompt é o resto
    """
    
    # Construir a descrição da tarefa
    task_description = f"""
Resolva o problema {leetcode_problem}

Complete o código Python fornecido para resolver este desafio algorítmico do LeetCode.
Sua solução deve ser eficiente, clara e seguir as melhores práticas de programação.
"""

    # Chamar a função prompt_agente
    full_prompt = prompt_agente(
        role=role,
        json_string=json.dumps(expected_json, indent=2, ensure_ascii=False),
        task=task_description.strip(),
        instruction=instructions.strip(),
        info_list=info_list
    )
    
    # Dividir o prompt no ponto "NAO ESQUEÇA NENHUM CAMPO!"
    split_point = "NAO ESQUEÇA NENHUM CAMPO!"
    if split_point in full_prompt:
        parts = full_prompt.split(split_point, 1)
        system_prompt = parts[0] + split_point
        prompt = parts[1].strip()
    else:
        # Fallback se não encontrar o texto
        system_prompt = full_prompt
        prompt = ""
    
    return system_prompt, prompt

def solve_leetcode_from_json_file(json_file_path: str, problem_id: int) -> str:
    """
    Carrega um arquivo JSON com problemas do LeetCode e cria o prompt para um problema específico.
    
    Args:
        json_file_path: Caminho para o arquivo JSON com os problemas
        problem_id: ID do problema que queremos resolver
        
    Returns:
        str: Prompt formatado para resolver o problema
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    problem = data['problems'][problem_id]
    
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
    
    return create_leetcode_prompt(
        leetcode_problem=problem,
        expected_json=expected_json,
        instructions=instructions,
        role="Especialista em Algoritmos Python e LeetCode",
        info_list=None
    )

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo: resolver o problema "Two Sum" (ID 1)
    problem_id = 0
    system_prompt, prompt = solve_leetcode_from_json_file("leetcode_problems.json", problem_id)
    print(f"=== PROMPT GERADO PARA LEETCODE SOLVER {problem_id} ===")
    print(system_prompt) 
    print(prompt) 
    print('########################################################')
    problem_id = 1
    system_prompt, prompt = solve_leetcode_from_json_file("leetcode_problems.json", problem_id)
    print(f"=== PROMPT GERADO PARA LEETCODE SOLVER {problem_id} ===")
    print(system_prompt) 
    print(prompt) 
    print('########################################################')
    problem_id = 2
    system_prompt, prompt = solve_leetcode_from_json_file("leetcode_problems.json", problem_id)
    print(f"=== PROMPT GERADO PARA LEETCODE SOLVER {problem_id} ===")
    print(system_prompt) 
    print(prompt) 
    print('########################################################')