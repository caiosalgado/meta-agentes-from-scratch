# LLM Meta Agent 🤖

Sistema avançado de criação automática de agentes LLM especializados com pipelines inteligentes.

## 📋 Visão Geral

O `LLM_Meta_Agent` é um agente de IA que cria outros agentes de IA. Ele usa técnicas avançadas de engenharia de prompts e aprendizado por experiência para gerar pipelines de agentes que maximizam a acurácia em tarefas específicas.

### 🎯 Características Principais

- **Criação Automática**: Gera código executável para novos agentes
- **Pipelines Inteligentes**: Suporta múltiplas arquiteturas (Sequential, Debate, Reflection, etc.)
- **Aprendizado Contínuo**: Mantém histórico de performance e aprende com sucessos/falhas
- **Teste Automatizado**: Executa 10 testes por agente para estatísticas confiáveis
- **Múltiplos Modelos**: Suporta 8 modelos diferentes (phi4, gemma3, qwen3)

## 🚀 Instalação

```bash
# Instalar dependências
uv add aisuite langchain langchain-core

# Verificar se ollama está rodando
ollama list
```

## 💡 Como Funciona

### 1. Arquiteturas Suportadas

- **Single Agent**: Um agente especializado
- **Sequential Pipeline**: Agente1 → Agente2 → ... → AgentN
- **Debate Pipeline**: Múltiplos especialistas → Decisão final
- **Reflection Pipeline**: Agente principal ↔ Agente revisor
- **Hierarchical**: Agente coordenador + agentes especializados

### 2. Sistema de Aprendizado

O meta-agente mantém um histórico permanente (`agent_history.json`) com:
- Performance de cada agente (acurácia + tempo)
- Configurações que funcionaram/falharam
- Padrões de erro identificados
- Exemplos funcionais para inspiração

### 3. Critérios de Seleção

1. **Acurácia** (prioridade máxima)
2. **Tempo de execução** (critério de desempate)
3. **Robustez** (consistência entre múltiplos testes)

## 📖 Uso Básico

### Exemplo Simples

```python
from llm_meta_agent import LLM_Meta_Agent

# Criar meta-agente
meta_agent = LLM_Meta_Agent(
    model="ollama:gemma3:4b",
    temperatura=0.3
)

# Definir tarefa
task = """
Criar um agente especialista em problemas de strings.
Deve ser excelente em:
- Verificação de palíndromos
- Manipulação de texto
- Análise de padrões
"""

# Gerar código do agente
agent_spec = meta_agent.generate_agent_code(task)
print(f"Nome: {agent_spec['name']}")
print(f"Código: {agent_spec['code']}")
```

### Exemplo Completo (com Teste)

```python
# Criar e testar agente completo
result = meta_agent.create_and_evaluate_agent(task)

if result["success"]:
    agent = result["agent"]
    print(f"Acurácia: {agent['performance']['accuracy']:.1f}%")
    print(f"Tempo: {agent['performance']['avg_execution_time']:.2f}s")
```

## 🔧 API Completa

### Métodos Principais

```python
# Criar meta-agente
meta_agent = LLM_Meta_Agent(
    model="ollama:qwen3:32b",      # Modelo para o meta-agente
    history_file="agent_history.json",  # Arquivo de histórico
    temperatura=0.3                 # Temperatura para geração
)

# Gerar código de agente
agent_spec = meta_agent.generate_agent_code(task_explicacao)

# Testar pipeline múltiplas vezes
performance = meta_agent.test_pipeline_multiple_times(code, runs=10)

# Fluxo completo: gerar → testar → salvar
result = meta_agent.create_and_evaluate_agent(task_explicacao)

# Estatísticas do histórico
stats = meta_agent.get_agent_statistics()

# Top agentes por performance
top_agents = meta_agent.list_top_agents(5)
```

### Estrutura de Resposta

```python
# agent_spec (generate_agent_code)
{
    "name": "Nome do agente/pipeline",
    "pensamento": "Raciocínio sobre a arquitetura",
    "code": "Código Python executável"
}

# performance (test_pipeline_multiple_times)
{
    "accuracy": 85.5,              # Acurácia média (%)
    "avg_execution_time": 2.3,     # Tempo médio (segundos)
    "successful_runs": 8,          # Runs bem-sucedidos
    "total_runs": 10,              # Total de runs
    "all_accuracies": [80, 90, ...], # Todas as acurácias
    "all_execution_times": [2.1, 2.5, ...] # Todos os tempos
}
```

## 🧪 Exemplos de Uso

### 1. Executar Exemplo Simples

```bash
python exemplo_meta_agent.py
```

### 2. Executar Testes Completos

```bash
python teste_meta_agent.py
```

### 3. Criar Agente Personalizado

```python
task = """
Criar um pipeline de debate com 3 especialistas:
1. Especialista em algoritmos
2. Especialista em estruturas de dados  
3. Especialista em otimização

Use diferentes modelos e temperaturas para cada especialista.
"""

result = meta_agent.create_and_evaluate_agent(task)
```

## 📊 Monitoramento

### Verificar Histórico

```python
# Estatísticas gerais
stats = meta_agent.get_agent_statistics()
print(f"Total: {stats['total_agents']}")
print(f"Funcionais: {stats['functional_agents']}")
print(f"Alta performance: {stats['high_performance_agents']}")

# Top performers
for i, agent in enumerate(meta_agent.list_top_agents(3), 1):
    print(f"{i}. {agent['name']}: {agent['performance']['accuracy']:.1f}%")
```

### Exemplos de Aprendizado

```python
# Ver exemplos funcionais (para inspiração)
functional = meta_agent.get_functional_examples(3)

# Ver exemplos problemáticos (para evitar)
problematic = meta_agent.get_non_functional_examples(3)
```

## 🎛️ Configurações Avançadas

### Modelos Disponíveis

```python
available_models = [
    "ollama:phi4:latest",
    "ollama:gemma3:4b",
    "ollama:gemma3:12b", 
    "ollama:gemma3:27b",
    "ollama:qwen3:4b",
    "ollama:qwen3:14b",
    "ollama:qwen3:30b",
    "ollama:qwen3:32b"
]
```

### Estratégias de Temperatura

- **Baixa (0.1-0.3)**: Para precisão e consistência
- **Média (0.4-0.6)**: Para equilíbrio
- **Alta (0.7-0.9)**: Para criatividade e exploração

### Critérios de Performance

- **Funcional**: Acurácia ≥ 30%
- **Alta Performance**: Acurácia ≥ 70%
- **Tempo Aceitável**: < 10 segundos por problema

## 🔍 Troubleshooting

### Problemas Comuns

1. **Erro de importação**: Verificar se `llm_agent.py` existe
2. **Modelo não encontrado**: Verificar se ollama está rodando
3. **Timeout**: Aumentar timeout no cliente aisuite
4. **JSON inválido**: Meta-agente tentará extrair JSON automaticamente

### Debug

```python
# Testar só geração (sem execução)
agent_spec = meta_agent.generate_agent_code(task)
print(agent_spec['code'])

# Testar execução manual
exec(agent_spec['code'])
```

## 📈 Roadmap

- [ ] Suporte a mais tipos de problemas (não só LeetCode)
- [ ] Interface web para visualização
- [ ] Métricas avançadas de performance
- [ ] Auto-tuning de hiperparâmetros
- [ ] Integração com mais modelos LLM

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido com ❤️ para maximizar a inteligência artificial através de colaboração entre agentes.** 