# LLM Meta Agent 🤖

Sistema avançado de criação automática de agentes LLM especializados que **aprende a criar agentes melhores**.

## 🎯 O que é este projeto?

Este é um **agente de IA que cria outros agentes de IA**! É como ter um "arquiteto de agentes" que sabe como construir pipelines inteligentes para resolver problemas específicos, aprendendo com cada tentativa.

### 🚀 Script Principal

```bash
uv run descobrir_melhor_arquitetura.py
```

Este script executa 100 tentativas de criação de agentes, buscando descobrir a arquitetura que resolve o maior número de desafios do LeetCode no menor tempo possível.

## 🔧 Como Funciona

### Fluxo Completo:
1. **Você descreve** o que quer: "agente especialista em strings"
2. **Meta-agente analisa** o histórico de sucessos/fracassos 
3. **Gera código** de um pipeline inteligente
4. **Testa 3 vezes** nos problemas LeetCode
5. **Calcula performance** (acurácia + tempo)
6. **Salva no histórico** para aprender

### Arquiteturas Suportadas

- **Single Agent**: Um agente simples especializado
- **Sequential Pipeline**: Agente1 → Agente2 → Agente3 (cada um especializado)
- **Debate Pipeline**: 3 especialistas debatem → agente final decide
- **Reflection Pipeline**: Agente principal ↔ agente revisor (verificação)
- **Hierarchical**: Agente coordenador + múltiplos especialistas

## 📁 Estrutura do Projeto

### Arquivos Principais
- **`descobrir_melhor_arquitetura.py`** - Script principal que executa o sistema
- **`llm_meta_agent.py`** - Meta-agente que cria outros agentes
- **`llm_agent.py`** - Classe base para agentes individuais
- **`debug_meta_agent_prompt.py`** - Debug de prompts do meta-agente
- **`debug_agent_prompt.py`** - Debug de prompts de agentes individuais

### Arquivos de Dados
- **`agent_history.json`** - Histórico de agentes criados (gerado automaticamente)
- **`leetcode_problems.json`** - Problemas para teste dos agentes

## 🧠 Sistema de Aprendizado

### O Meta-Agente Aprende:
- **Quais modelos** funcionam melhor para cada tipo de tarefa
- **Quais temperaturas** usar (baixa para precisão, alta para criatividade)
- **Quais arquiteturas** de pipeline são mais eficazes
- **Quais padrões** evitar (baseado em falhas passadas)

### Histórico Permanente
```json
{
  "agent_id": "001",
  "name": "Palindrome Expert Pipeline", 
  "performance": {"accuracy": 85.5, "avg_execution_time": 2.3},
  "config": {"code": "código do agente"},
  "detailed_results": [...]
}
```

## 📊 Sistema de Performance

### Métricas Rastreadas:
- **Acurácia**: % de problemas resolvidos corretamente
- **Tempo**: Segundos médios por problema
- **Consistência**: Variação entre múltiplos testes
- **Robustez**: Performance em diferentes tipos de problema

### Critérios de Seleção:
1. **Acurácia** (prioridade máxima)
2. **Tempo de execução** (critério de desempate)
3. **Consistência** entre testes

## 💡 Uso Básico

### Exemplo Simples
```python
from llm_meta_agent import LLM_Meta_Agent

# Criar meta-agente
meta_agent = LLM_Meta_Agent(
    model="ollama:qwen3:32b",
    temperatura=0.6
)

# Definir tarefa
task = "Criar um agente especialista em problemas de strings"

# Criar e testar agente
result = meta_agent.create_and_evaluate_agent(task)

if result["success"]:
    print(f"✅ {result['agent']['name']}")
    print(f"📊 Acurácia: {result['performance']['accuracy']:.1f}%")
    print(f"⏱️ Tempo: {result['performance']['avg_execution_time']:.2f}s")
```

### Exemplo Real de Pipeline Gerado
```python
def solve_problem(problem_data):
    # Agente 1: Analisador (identifica tipo de problema)
    analyzer = LLM_Agent(model="gemma3:4b", temperatura=0.2)
    
    # Agente 2: Especialista matemático 
    math_expert = LLM_Agent(model="qwen3:14b", temperatura=0.1)
    
    # Agente 3: Revisor de código
    code_reviewer = LLM_Agent(model="phi4:latest", temperatura=0.3)
    
    # Pipeline: Análise → Solução → Revisão
    analysis = analyzer.generate_response(problem_data)
    solution = math_expert.generate_response(problem_data, analysis)
    final_code = code_reviewer.generate_response(problem_data, solution)
    
    return final_code
```

## 🛠️ Instalação e Configuração

### Pré-requisitos
```bash
# Instalar dependências
uv add aisuite

# Verificar se ollama está rodando
ollama list
```

### Modelos Disponíveis
- `ollama:phi4:latest`
- `ollama:gemma3:4b`, `ollama:gemma3:12b`
- `ollama:qwen3:1.7b`, `ollama:qwen3:4b`, `ollama:qwen3:14b`
- `ollama:deepseek-r1:1.5b`, `ollama:deepseek-r1:8b`, `ollama:deepseek-r1:14b`

## 🔍 Debug e Monitoramento

### Debug de Prompts do Meta-Agente
```python
from debug_meta_agent_prompt import debug_meta_agent_prompts

# Ver prompts do meta-agente sem executar
system, user = debug_meta_agent_prompts(
    "Criar agente para palíndromos",
    model="ollama:qwen3:32b"
)
```

### Debug de Prompts de Agentes Individuais
```python
from debug_agent_prompt import debug_agent_prompts

# Ver prompts de um agente específico
system, user = debug_agent_prompts(
    task="Resolva o problema Two Sum",
    role="Especialista em Algoritmos",
    model="ollama:qwen3:14b"
)
```

### Estatísticas do Histórico
```python
# Ver estatísticas gerais
stats = meta_agent.get_agent_statistics()
print(f"Total de agentes: {stats['total_agents']}")
print(f"Agentes funcionais: {stats['functional_agents']}")

# Ver top performers
for agent in meta_agent.list_top_agents(3):
    print(f"{agent['name']}: {agent['performance']['accuracy']:.1f}%")
```

## 🎉 O Diferencial

Este sistema é **revolucionário** porque:

1. **Autoevolução**: Cada agente criado melhora os próximos
2. **Especialização**: Cria soluções específicas para cada problema
3. **Colaboração**: Pipelines com múltiplos agentes especializados
4. **Aprendizado**: Mantém memória permanente de sucessos/falhas
5. **Otimização**: Maximiza acurácia através de testes múltiplos

### Conceitos Avançados

- **Meta-Learning**: Aprende como resolver problemas melhor
- **Ensemble Intelligence**: Inteligência coletiva que supera agentes individuais
- **Adaptive Architecture**: Adapta arquitetura baseado no histórico
- **Emergent Behavior**: Comportamentos inteligentes emergem da colaboração

## 🚀 Execução

### Descobrir Melhor Arquitetura
```bash
# Executa 100 tentativas buscando a melhor arquitetura
uv run descobrir_melhor_arquitetura.py
```

### Debug de Prompts
```bash
# Ver prompts do meta-agente
python debug_meta_agent_prompt.py

# Ver prompts de agentes individuais
python debug_agent_prompt.py
```

---

**Este é o futuro da IA: sistemas que se automelhoram e colaboram para resolver problemas complexos!** 🚀

É como ter um **laboratório de IA** que experimenta diferentes combinações e evolui automaticamente! 🔬✨
