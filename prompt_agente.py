from langchain_core.prompts import PromptTemplate
from typing import Optional, List
from collections import namedtuple

# Definição da namedtuple Info
Info = namedtuple('Info', ['tipo', 'agente', 'conteudo', 'numero'])

def prompt_agente(
    role: str,
    json_string: str,
    task: str,
    instruction: str,
    info_list: Optional[List[Info]] = None
) -> str:
    PROMPT_TEMPLATE = (
        "Você é um {role}.\n\n"
        "Responda exatamente no formato JSON abaixo:\n"
        "{json_string}\n"
        "NAO ESQUEÇA NENHUM CAMPO!\n\n"
        "# Sua Tarefa\n"
        "{task}\n\n"
        "{info_section}"
        "# Instrução\n"
        "{instruction}\n"
    )
    
    # Processar a lista de Info se fornecida
    info_section = ""
    if info_list:
        for info in info_list:
            if info.tipo == "thinking":
                info_section += f"## Análise do {info.agente}:\n{info.conteudo}\n\n"
            elif info.tipo == "code":
                info_section += f"## Código do {info.agente}:\n```\n{info.conteudo}\n```\n\n"
            else:
                info_section += f"## {info.tipo.title()} do {info.agente}:\n{info.conteudo}\n\n"
    
    prompt = PromptTemplate(
        input_variables=["role", "json_string", "task", "instruction"],
        partial_variables={
            "info_section": info_section
        },
        template=PROMPT_TEMPLATE,
    )
    prompt_vars = {
        "role": role,
        "json_string": json_string,
        "task": task,
        "instruction": instruction,
    }
    prompt_complete = prompt.format(**prompt_vars)
    
    # Adicionar nota sobre código se houver algum Info do tipo 'code'
    if info_list and any(info.tipo == 'code' for info in info_list):
        codigo_placeholder = f"\n# Tenha certeza que seu agente resolve handles all edges cases."
    else:
        codigo_placeholder = ""
    return prompt_complete + codigo_placeholder