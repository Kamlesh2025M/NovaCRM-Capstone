"""
NovaCRM Assistant CLI

Command-line interface for interacting with the NovaCRM Assistant
Supports:
- Model selection (--model)
- Temperature control (--temperature)
- Account context (--account)
- Markdown output with evidence and notes sections
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from .graph import get_graph
from .mcp_client import test_mcp_connection

def format_markdown_output(result: dict) -> str:
    """
    Format result as markdown with sections
    
    Args:
        result: Graph execution result
        
    Returns:
        Formatted markdown string
    """
    output = []
    
    output.append("=" * 80)
    output.append(f"NovaCRM Assistant Response")
    output.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Intent: {result.get('intent', 'Unknown')}")
    output.append("=" * 80)
    output.append("")
    
    output.append("## Answer")
    output.append("")
    output.append(result.get('answer', 'No answer generated'))
    output.append("")
    
    if result.get('evidence'):
        output.append("## Evidence")
        output.append("")
        for evidence in result['evidence']:
            output.append(f"- {evidence}")
        output.append("")
    
    if result.get('errors'):
        output.append("## Notes")
        output.append("")
        output.append("The following issues occurred during processing:")
        for error in result['errors']:
            output.append(f"- {error}")
        output.append("")
    
    output.append("=" * 80)
    
    return "\n".join(output)

def interactive_mode(graph, account_context: str = None):
    """
    Run interactive CLI session
    
    Args:
        graph: NovaCRMGraph instance
        account_context: Optional account ID for all queries
    """
    print("\n" + "=" * 80)
    print("NovaCRM Assistant - Interactive Mode")
    print("=" * 80)
    print(f"Model: {graph.llm.model_name}")
    print(f"Temperature: {graph.llm.temperature}")
    if account_context:
        print(f"Account Context: {account_context}")
    print("\nType 'exit' or 'quit' to end session")
    print("Type 'account <id>' to set account context")
    print("=" * 80 + "\n")
    
    current_account = account_context
    
    while True:
        try:
            query = input("You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            if query.lower().startswith('account '):
                parts = query.split(maxsplit=1)
                if len(parts) == 2:
                    current_account = parts[1].strip()
                    print(f"Account context set to: {current_account}\n")
                else:
                    current_account = None
                    print("Account context cleared\n")
                continue
            
            print("\nProcessing...\n")
            
            result = graph.invoke(query, account_context=current_account)
            
            print(format_markdown_output(result))
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")

def single_query_mode(graph, query: str, account_context: str = None):
    """
    Process a single query and exit
    
    Args:
        graph: NovaCRMGraph instance
        query: User query
        account_context: Optional account ID
    """
    result = graph.invoke(query, account_context=account_context)
    print(format_markdown_output(result))

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="NovaCRM Assistant - Customer Intelligence & Ops CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python -m app.cli
  
  # Single query
  python -m app.cli --query "What is NovaCRM?"
  
  # With account context
  python -m app.cli --account A001 --query "Show my invoices"
  
  # Custom model and temperature
  python -m app.cli --model gpt-4 --temperature 0.3
        """
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Single query to process (omit for interactive mode)'
    )
    
    parser.add_argument(
        '--account', '-a',
        type=str,
        help='Account ID for scoping queries (e.g., A001)'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='gpt-4o-mini',
        help='OpenAI model to use (default: gpt-4o-mini)'
    )
    
    parser.add_argument(
        '--temperature', '-t',
        type=float,
        default=0.0,
        help='LLM temperature (0.0-1.0, default: 0.0)'
    )
    
    args = parser.parse_args()
    
    print("\nChecking MCP server connection...")
    if not test_mcp_connection():
        print("\nWARNING: MCP server not reachable at http://127.0.0.1:3001")
        print("DataLookup queries will fail. Please start the MCP server first.")
        print("Run: python servers/mcp_nova/server.py\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("MCP server is running [OK]\n")
    
    print("Initializing NovaCRM Assistant...")
    graph = get_graph(model_name=args.model, temperature=args.temperature)
    print("Ready!\n")
    
    if args.query:
        single_query_mode(graph, args.query, args.account)
    else:
        interactive_mode(graph, args.account)

if __name__ == "__main__":
    main()

