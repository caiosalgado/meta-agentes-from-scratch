from smolagents import CodeAgent, LiteLLMModel

model = LiteLLMModel(
    model_id="ollama/qwen3:4b",  # modelo do Ollama
    api_base="http://localhost:11434",  # endpoint padrão do Ollama local
    num_ctx=8192,  # contexto maior para evitar erros
)

agent = CodeAgent(tools=[], model=model, )

result = agent.run("Hello, world! Say hi in English.")
print(result) 