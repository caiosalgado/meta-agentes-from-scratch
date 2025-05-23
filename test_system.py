#!/usr/bin/env python3
"""
Teste simples do sistema de agentes LLM reformatado.
"""

import json
from llm_agent import LLM_Agent

def test_json_format():
    """Testa se o JSON reformatado está sendo carregado corretamente."""
    print("=== TESTE 1: Carregamento do JSON ===")
    
    with open("leetcode_problems.json", encoding="utf-8") as f:
        problems = json.load(f)["problems"]
    
    print(f"✅ JSON carregado: {len(problems)} problemas")
    
    for problem in problems:
        print(f"   - {problem['id']}: {len(problem['tests'])} casos de teste")
        
        # Verificar estrutura
        required_fields = ['id', 'title', 'description', 'function_signature', 'tests']
        for field in required_fields:
            assert field in problem, f"Campo '{field}' ausente em {problem['id']}"
        
        # Verificar formato dos testes
        for test in problem['tests']:
            assert 'input' in test and 'expected' in test, f"Teste inválido em {problem['id']}"
            assert isinstance(test['input'], list), f"Input deve ser lista em {problem['id']}"
    
    print("✅ Estrutura do JSON validada")
    return problems

def test_code_execution():
    """Testa execução de código simples."""
    print("\n=== TESTE 2: Execução de Código ===")
    
    # Criar agente de teste
    agente = LLM_Agent(
        role="Testador Python",
        instruction="Crie código Python simples",
        arquitetura_resposta={
            "code": "Código Python",
        },
        temperatura=0.1,
        model="ollama:gemma3:4b"
    )
    
    # Código de teste simples
    test_code = """
def isPalindrome(x: int) -> bool:
    return str(x) == str(x)[::-1]
"""
    
    test_cases = [
        {"input": [121], "expected": True},
        {"input": [-121], "expected": False},
        {"input": [10], "expected": False}
    ]
    
    print("Testando execução de código...")
    accuracy, results = agente.test_code_accuracy(test_code, test_cases)
    
    print(f"✅ Acurácia: {accuracy:.1f}%")
    for result in results:
        status = "✅" if result['correct'] else "❌"
        print(f"   {status} Teste {result['test_case']}: {result['input']} → {result['actual']} (esperado: {result['expected']})")
    
    return accuracy > 0

def test_full_system():
    """Testa o sistema completo com um problema real."""
    print("\n=== TESTE 3: Sistema Completo ===")
    
    # Carregar problemas
    with open("leetcode_problems.json", encoding="utf-8") as f:
        problems = json.load(f)["problems"]
    
    # Criar agente
    agente = LLM_Agent(
        role="Especialista em Algoritmos Python",
        instruction="Implemente uma solução eficiente. Use apenas funções standalone.",
        arquitetura_resposta={
            "analysis": "Análise do problema",
            "code": "Código Python completo",
        },
        temperatura=0.2,
        model="ollama:gemma3:4b"
    )
    
    # Testar problema mais simples (isPalindrome)
    problem = problems[0]  # isPalindrome
    print(f"Testando problema: {problem['title']}")
    
    try:
        result = agente.run_leetcode_test(problem)
        accuracy = result['evaluation']['code_accuracy']
        
        print(f"✅ Teste executado com sucesso")
        print(f"   Acurácia: {accuracy:.1f}%")
        print(f"   Feedback: {result['evaluation']['feedback']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

def main():
    """Executa todos os testes."""
    print("TESTANDO SISTEMA DE AGENTES LLM REFORMATADO")
    print("=" * 50)
    
    try:
        # Teste 1: JSON
        problems = test_json_format()
        
        # Teste 2: Execução de código
        code_works = test_code_execution()
        
        # Teste 3: Sistema completo (apenas se os anteriores passaram)
        if code_works:
            system_works = test_full_system()
        else:
            print("\n❌ Pulando teste completo devido a falhas anteriores")
            system_works = False
        
        # Resultado final
        print("\n" + "=" * 50)
        print("RESULTADO FINAL")
        print("=" * 50)
        
        if code_works and system_works:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("   O sistema está funcionando corretamente.")
        else:
            print("⚠️  ALGUNS TESTES FALHARAM")
            print("   Verifique os erros acima.")
            
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        print("   O sistema não está funcionando.")

if __name__ == "__main__":
    main() 