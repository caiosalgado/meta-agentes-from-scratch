from langchain_core.prompts import PromptTemplate
from typing import Optional

def prompt_meta_agente(
    arquiteturas_agentes: str,
    exemplos_funcionais: str,
    exemplos_nao_funcionais: str,
    task_explicacao: str
) -> str:
    """
    Gera um prompt otimizado para um meta-agente especialista em criação de novos agentes.
    
    Args:
        arquiteturas_agentes: Documentação das arquiteturas disponíveis
        exemplos_funcionais: Exemplos de agentes que funcionaram bem
        exemplos_nao_funcionais: Exemplos de agentes que não funcionaram
        task_explicacao: Descrição detalhada da nova tarefa/problema
    
    Returns:
        str: Prompt formatado para o meta-agente
    """
    
    PROMPT_TEMPLATE = (
        "Você é um especialista mundial em engenharia de prompts e arquitetura de agentes de IA.\n\n"
        "Seu objetivo é projetar agentes de alta performance que maximizem as métricas de desempenho "
        "através de técnicas avançadas de prompt engineering e design de arquitetura.\n\n"
        "Pense em diferentes paradigmas: agentes reflexivos, colaborativos, especialistas, "
        "multi-step reasoning, chain-of-thought, tree-of-thought, entre outros.\n\n"
        "# Arquivo de Arquiteturas de Agentes Disponíveis\n"
        "{arquiteturas_agentes}\n\n"
        "# Exemplos de Agentes de Alto Desempenho (FUNCIONAIS)\n"
        "Analise estes exemplos que demonstraram excelente performance:\n"
        "{exemplos_funcionais}\n\n"
        "# Exemplos de Agentes com Baixo Desempenho (NÃO FUNCIONAIS)\n"
        "Evite os padrões presentes nestes exemplos problemáticos:\n"
        "{exemplos_nao_funcionais}\n\n"
        "# Instrução do Output\n"
        "Responda EXCLUSIVAMENTE em formato JSON com esta estrutura exata:\n"
        "{{\n"
        '  "name": "Nome do agente",\n'
        '  "pensamento": "Seu pensamento sobre o design do agente",\n'
        '  "code": "Código para criar o agente"\n'
        "}}\n\n"
        "# Sua Tarefa Específica\n"
        "{task_explicacao}\n\n"
        "## Diretrizes Importantes:\n"
        "- INOVE: Crie soluções únicas que combinem diferentes técnicas\n"
        "- OTIMIZE: Foque em máxima eficiência e precisão\n"
        "- ADAPTE: Personalize a solução para o problema específico\n"
        "- TESTE MENTALMENTE: Antecipe edge cases e limitações\n\n"
        "PENSE FORA DA CAIXA E CRIE UM AGENTE REVOLUCIONÁRIO!"
    )
    
    prompt = PromptTemplate(
        input_variables=["arquiteturas_agentes", "exemplos_funcionais", "exemplos_nao_funcionais", "task_explicacao"],
        template=PROMPT_TEMPLATE,
    )
    
    prompt_vars = {
        "arquiteturas_agentes": arquiteturas_agentes,
        "exemplos_funcionais": exemplos_funcionais,
        "exemplos_nao_funcionais": exemplos_nao_funcionais,
        "task_explicacao": task_explicacao,
    }
    
    return prompt.format(**prompt_vars)


def prompt_meta_agente_simples(task_explicacao: str) -> str:
    """
    Versão simplificada para uso rápido quando não há exemplos ou arquiteturas específicas.
    
    Args:
        task_explicacao: Descrição da tarefa/problema
        
    Returns:
        str: Prompt formatado simplificado
    """
    return prompt_meta_agente(
        arquiteturas_agentes="Utilize as melhores práticas de arquitetura de agentes disponíveis.",
        exemplos_funcionais="Baseie-se em agentes que demonstram raciocínio claro e resultados precisos.",
        exemplos_nao_funcionais="Evite agentes que produzem respostas vagas ou inconsistentes.",
        task_explicacao=task_explicacao
    )

