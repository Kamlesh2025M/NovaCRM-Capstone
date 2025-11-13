"""
Simple Demo Script for NovaCRM Assistant

Interactive demo to test the assistant with different query types
"""

import os
from dotenv import load_dotenv
from app.graph import get_graph

# Load environment
load_dotenv()

def demo_faq():
    """Demo FAQ queries"""
    print("\n" + "="*80)
    print("DEMO 1: FAQ Queries (Knowledge Base)")
    print("="*80)
    
    graph = get_graph()
    
    queries = [
        "What is NovaCRM?",
        "What are the pricing plans?",
        "How does contact management work?",
    ]
    
    for query in queries:
        print(f"\n[Query] {query}")
        result = graph.invoke(query)
        print(f"[Intent] {result['intent']}")
        print(f"[Answer]\n{result['answer'][:500]}...")
        if result['errors']:
            print(f"[Warnings] {result['errors']}")

def demo_datalookup():
    """Demo DataLookup queries"""
    print("\n" + "="*80)
    print("DEMO 2: Data Lookup Queries (MCP Tools)")
    print("="*80)
    
    graph = get_graph()
    
    queries = [
        ("What plan is account A001 on?", "A001"),
        ("Show me invoices for Company_003", None),
        ("How many open tickets does A005 have?", "A005"),
    ]
    
    for query, account in queries:
        print(f"\n[Query] {query}")
        result = graph.invoke(query, account_context=account)
        print(f"[Intent] {result['intent']}")
        print(f"[Answer]\n{result['answer'][:500]}...")
        if result['errors']:
            print(f"[Warnings] {result['errors']}")

def demo_escalation():
    """Demo Escalation queries"""
    print("\n" + "="*80)
    print("DEMO 3: Escalation Queries (Human Support)")
    print("="*80)
    
    graph = get_graph()
    
    queries = [
        "I want to cancel my subscription",
        "There's a billing error on my account",
        "I need to speak with a manager",
    ]
    
    for query in queries:
        print(f"\n[Query] {query}")
        result = graph.invoke(query)
        print(f"[Intent] {result['intent']}")
        print(f"[Answer]\n{result['answer'][:300]}...")

def demo_safety():
    """Demo Safety & Validation"""
    print("\n" + "="*80)
    print("DEMO 4: Safety & Validation (Guardrails)")
    print("="*80)
    
    graph = get_graph()
    
    queries = [
        "My email is test@example.com, help me with account A001",
        "I think my account was hacked",
        "This is legal action against your company",
    ]
    
    for query in queries:
        print(f"\n[Query] {query}")
        result = graph.invoke(query)
        print(f"[Intent] {result['intent']}")
        print(f"[Safety Checks] {[e for e in result['evidence'] if 'safety:' in e]}")
        print(f"[Answer]\n{result['answer'][:300]}...")

def interactive_mode():
    """Interactive demo mode"""
    print("\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    print("Type your queries (or 'quit' to exit)")
    
    graph = get_graph()
    
    while True:
        query = input("\n[You] ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        if not query:
            continue
        
        account = input("[Account ID (optional)] ").strip() or None
        
        result = graph.invoke(query, account_context=account)
        
        print(f"\n[Intent] {result['intent']}")
        print(f"[Answer]\n{result['answer']}")
        print(f"\n[Evidence] {len(result['evidence'])} items")
        if result['errors']:
            print(f"[Warnings] {', '.join(result['errors'])}")

def main():
    """Main demo menu"""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        print("Please create a .env file with your OpenAI API key")
        return
    
    print("\n" + "="*80)
    print(" " * 25 + "NovaCRM ASSISTANT DEMO")
    print("="*80)
    print("\nSelect a demo:")
    print("1. FAQ Queries (Knowledge Base Retrieval)")
    print("2. Data Lookup Queries (MCP Tool Calls)")
    print("3. Escalation Queries (Human Support)")
    print("4. Safety & Validation (Guardrails)")
    print("5. Interactive Mode")
    print("6. Run All Demos")
    print("0. Exit")
    
    choice = input("\nEnter choice: ").strip()
    
    if choice == "1":
        demo_faq()
    elif choice == "2":
        demo_datalookup()
    elif choice == "3":
        demo_escalation()
    elif choice == "4":
        demo_safety()
    elif choice == "5":
        interactive_mode()
    elif choice == "6":
        demo_faq()
        demo_datalookup()
        demo_escalation()
        demo_safety()
    elif choice == "0":
        print("Goodbye!")
        return
    else:
        print("Invalid choice")
    
    print("\n" + "="*80)
    print("Demo complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

