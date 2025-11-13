"""
LangGraph Implementation for NovaCRM Assistant

Architecture:
- Router: Classifies query intent (FAQ / DataLookup / Escalation)
- Retrieve: RAG retrieval for FAQ queries
- Tools: MCP tool calls for DataLookup queries
- Synthesize: Composes final answer from evidence
- Escalate: Handles escalation cases with helpful fallback
"""

from typing import Literal
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .state import AssistantState
from .retriever import get_retriever
from .mcp_client import get_mcp_tools, call_mcp_tool
from .validation import get_validator, get_safety_guardrails

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"

def load_prompt(name: str) -> str:
    """Load prompt template from prompts directory"""
    with open(PROMPTS_DIR / f"{name}.md", 'r', encoding='utf-8') as f:
        return f.read()

SYSTEM_PROMPT = load_prompt("system")
ROUTER_PROMPT = load_prompt("router")
RAG_SYNTH_PROMPT = load_prompt("rag_synth")
TOOL_CHECK_PROMPT = load_prompt("tool_check")

class NovaCRMGraph:
    """
    LangGraph-based assistant for NovaCRM operations and intelligence
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        """
        Initialize the graph with LLM configuration
        
        Args:
            model_name: OpenAI model to use
            temperature: Temperature for LLM calls
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.retriever = None
        self.validator = get_validator()
        self.safety = get_safety_guardrails()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow
        
        Returns:
            Compiled StateGraph
        """
        graph = StateGraph(AssistantState)
        
        # Add nodes
        graph.add_node("safety_check", self._safety_check_node)
        graph.add_node("router", self._router_node)
        graph.add_node("retrieve", self._retrieve_node)
        graph.add_node("tools", self._tools_node)
        graph.add_node("synthesize", self._synthesize_node)
        graph.add_node("validate", self._validate_node)
        graph.add_node("escalate", self._escalate_node)
        
        # Add edges
        graph.add_edge(START, "safety_check")
        graph.add_edge("safety_check", "router")
        
        # Conditional routing based on intent
        graph.add_conditional_edges(
            "router",
            self._route_query,
            {
                "FAQ": "retrieve",
                "DataLookup": "tools",
                "Escalation": "escalate"
            }
        )
        
        # Flow to synthesize, validate, then end
        graph.add_edge("retrieve", "synthesize")
        graph.add_edge("tools", "synthesize")
        graph.add_edge("synthesize", "validate")
        graph.add_edge("validate", END)
        graph.add_edge("escalate", END)
        
        return graph.compile()
    
    def _safety_check_node(self, state: AssistantState) -> AssistantState:
        """
        Safety Check Node: Pre-process query for sensitive content
        
        Checks for PII, sensitive topics, and applies initial guardrails
        """
        query = state["query"]
        
        # Check for sensitive content
        sensitivity_check = self.safety.check_sensitive_content(query)
        if sensitivity_check["is_sensitive"] and sensitivity_check["should_escalate"]:
            state["intent"] = "Escalation"
            state["evidence"].append(f"safety:sensitive_topic_detected:{','.join(sensitivity_check['matched_topics'])}")
            print(f"[Safety] Sensitive topic detected: {sensitivity_check['matched_topics']}")
        
        # Check for PII
        pii_check = self.safety.check_pii_exposure(query)
        if pii_check["has_pii"]:
            state["query"] = pii_check["redacted_text"]
            state["evidence"].append(f"safety:pii_redacted:{','.join(pii_check['pii_types'])}")
            print(f"[Safety] PII redacted: {pii_check['pii_types']}")
        
        print(f"[Safety] Query passed safety checks")
        return state
    
    def _router_node(self, state: AssistantState) -> AssistantState:
        """
        Router Node: Classify query intent
        
        Uses few-shot prompting to determine: FAQ, DataLookup, or Escalation
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", ROUTER_PROMPT)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({"query": state["query"]})
            intent = result.strip()
            
            # Validate intent
            if intent not in ["FAQ", "DataLookup", "Escalation"]:
                intent = "Escalation"
            
            state["intent"] = intent
            print(f"[Router] Classified intent: {intent}")
            
        except Exception as e:
            state["errors"].append(f"Router error: {str(e)}")
            state["intent"] = "Escalation"
            print(f"[Router] Error: {e}")
        
        return state
    
    def _retrieve_node(self, state: AssistantState) -> AssistantState:
        """
        Retrieve Node: RAG retrieval from knowledge base
        
        Uses FAISS vector store to find relevant documentation
        """
        try:
            if self.retriever is None:
                self.retriever = get_retriever()
            
            documents = self.retriever.retrieve(state["query"], k=5)
            
            # Track evidence
            for i, doc in enumerate(documents, 1):
                source = doc.metadata.get('source', 'unknown')
                state["evidence"].append(f"doc:{Path(source).name}")
            
            # Format results
            formatted = self.retriever.format_results(documents)
            state["answer"] = formatted["context"]
            
            print(f"[Retrieve] Retrieved {len(documents)} documents")
            
        except Exception as e:
            state["errors"].append(f"Retrieval error: {str(e)}")
            state["answer"] = "Knowledge base retrieval failed. Please try rephrasing your question."
            print(f"[Retrieve] Error: {e}")
        
        return state
    
    def _tools_node(self, state: AssistantState) -> AssistantState:
        """
        Tools Node: Call MCP tools for data lookup
        
        Determines which tools to call based on query and executes them
        """
        query = state["query"]
        account_context = state.get("account_context")
        
        try:
            # Get tool justification
            justification_prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("user", TOOL_CHECK_PROMPT)
            ])
            
            justification_chain = justification_prompt | self.llm | StrOutputParser()
            justification = justification_chain.invoke({
                "query": query,
                "account_context": account_context or "None specified"
            })
            
            state["evidence"].append(f"tool_justification:{justification[:100]}")
            
            # Determine which tools to call
            tool_calls = self._determine_tool_calls(query, account_context)
            
            # Execute tool calls with validation
            results = []
            for tool_name, params in tool_calls:
                # Validate tool parameters
                param_validation = self.safety.validate_tool_params(tool_name, params)
                
                if not param_validation["is_valid"]:
                    print(f"[Tools] Invalid params for {tool_name}: {param_validation['errors']}")
                    results.append({
                        "tool": tool_name,
                        "params": params,
                        "result": {"error": f"Invalid parameters: {', '.join(param_validation['errors'])}"}
                    })
                    continue
                
                # Call tool if params are valid
                result = call_mcp_tool(tool_name, params)
                results.append({
                    "tool": tool_name,
                    "params": params,
                    "result": result
                })
                state["evidence"].append(f"tool:{tool_name}:{list(params.keys())}")
            
            # Format results
            state["answer"] = self._format_tool_results(results)
            print(f"[Tools] Called {len(tool_calls)} tools")
            
        except Exception as e:
            state["errors"].append(f"Tools error: {str(e)}")
            state["answer"] = "Unable to retrieve data. Please verify account information."
            print(f"[Tools] Error: {e}")
        
        return state
    
    def _determine_tool_calls(self, query: str, account_context: str = None) -> list:
        """
        Determine which MCP tools to call based on query
        
        Args:
            query: User query
            account_context: Optional account ID
            
        Returns:
            List of (tool_name, params) tuples
        """
        query_lower = query.lower()
        tools = []
        
        # Invoice queries
        if "invoice" in query_lower or "payment" in query_lower or "billing" in query_lower:
            if account_context:
                params = {"account_id": account_context}
                # Check for period mentions
                if "2025-10" in query or "october" in query_lower:
                    params["period"] = "2025-10"
                elif "2025-09" in query or "september" in query_lower:
                    params["period"] = "2025-09"
                tools.append(("invoice_status", params))
        
        # Ticket queries
        if "ticket" in query_lower or "support" in query_lower:
            if account_context:
                tools.append(("ticket_summary", {"account_id": account_context}))
        
        # Usage queries
        if "usage" in query_lower or "api" in query_lower or "storage" in query_lower:
            if account_context:
                month = "2025-10"  # Default to current month
                if "2025-09" in query or "september" in query_lower:
                    month = "2025-09"
                elif "2025-08" in query or "august" in query_lower:
                    month = "2025-08"
                tools.append(("usage_report", {"account_id": account_context, "month": month}))
        
        # Account queries
        if "account" in query_lower or "plan" in query_lower or "tier" in query_lower:
            if account_context:
                tools.append(("account_lookup", {"account_id": account_context}))
            else:
                # Try to extract account ID from query
                for word in query.split():
                    if word.startswith("A") and word[1:].isdigit():
                        tools.append(("account_lookup", {"account_id": word}))
                        break
                    elif "company" in query_lower:
                        import re
                        match = re.search(r"Company[_\s](\d+)", query, re.I)
                        if match:
                            tools.append(("account_lookup", {"company": f"Company_{match.group(1).zfill(3)}"}))
                            break
        
        # Fallback: if account context provided but no specific tool matched, get account info
        if not tools and account_context:
            tools.append(("account_lookup", {"account_id": account_context}))
        
        return tools
    
    def _format_tool_results(self, results: list) -> str:
        """Format tool call results into readable text"""
        output = []
        
        for item in results:
            tool = item["tool"]
            result = item["result"]
            
            output.append(f"\n## {tool.replace('_', ' ').title()}\n")
            
            if "error" in result:
                output.append(f"Error: {result['error']}\n")
            else:
                # Format based on tool type
                if tool == "account_lookup":
                    output.append(f"- Company: {result.get('company', 'N/A')}\n")
                    output.append(f"- Plan: {result.get('plan', 'N/A')} ({result.get('tier', 'N/A')} tier)\n")
                    output.append(f"- Billing: {result.get('billing_cycle', 'N/A')}\n")
                    output.append(f"- CSM: {result.get('csm', 'N/A')}\n")
                    output.append(f"- Renewal: {result.get('renewal_date', 'N/A')}\n")
                
                elif tool == "invoice_status":
                    summary = result.get('summary', {})
                    output.append(f"- Total Invoices: {result.get('invoice_count', 0)}\n")
                    output.append(f"- Total Amount: ${summary.get('total', 0):.2f}\n")
                    output.append(f"- Paid: ${summary.get('paid', 0):.2f}\n")
                    output.append(f"- Overdue: ${summary.get('overdue', 0):.2f}\n")
                    output.append(f"- Pending: ${summary.get('pending', 0):.2f}\n")
                
                elif tool == "ticket_summary":
                    output.append(f"- Total Tickets: {result.get('total_tickets', 0)}\n")
                    output.append(f"- Open: {result.get('open_tickets', 0)}\n")
                    output.append(f"- High Priority Open: {result.get('high_priority_open', 0)}\n")
                    sla_risks = result.get('sla_risks', [])
                    if sla_risks:
                        output.append(f"- SLA Risks: {len(sla_risks)} ticket(s)\n")
                
                elif tool == "usage_report":
                    output.append(f"- Month: {result.get('month', 'N/A')}\n")
                    output.append(f"- API Calls: {result.get('api_calls', 0):,}\n")
                    output.append(f"- Email Sends: {result.get('email_sends', 0):,}\n")
                    output.append(f"- Storage: {result.get('storage_gb', 0):.2f} GB\n")
                    warnings = result.get('warnings', [])
                    if warnings:
                        output.append(f"\nWarnings:\n")
                        for warning in warnings:
                            output.append(f"  - {warning}\n")
        
        return "".join(output)
    
    def _synthesize_node(self, state: AssistantState) -> AssistantState:
        """
        Synthesize Node: Compose final answer from evidence
        
        Uses RAG synthesis prompt for FAQ, formats tool results for DataLookup
        """
        try:
            if state["intent"] == "FAQ":
                # Use RAG synthesis for FAQ queries
                prompt = ChatPromptTemplate.from_messages([
                    ("system", SYSTEM_PROMPT),
                    ("user", RAG_SYNTH_PROMPT)
                ])
                
                chain = prompt | self.llm | StrOutputParser()
                
                answer = chain.invoke({
                    "context": state.get("answer", ""),
                    "question": state["query"]
                })
                
                state["answer"] = answer
            
            # Add evidence section
            evidence_list = "\n".join([f"- {e}" for e in state["evidence"]])
            state["answer"] = f"{state.get('answer', '')}\n\n**Evidence:**\n{evidence_list}"
            
            print(f"[Synthesize] Generated final answer")
            
        except Exception as e:
            state["errors"].append(f"Synthesis error: {str(e)}")
            print(f"[Synthesize] Error: {e}")
        
        return state
    
    def _escalate_node(self, state: AssistantState) -> AssistantState:
        """
        Escalate Node: Handle queries that need human intervention
        
        Provides helpful fallback message with next steps
        """
        escalation_message = f"""
I understand you need assistance with: "{state['query']}"

This request requires specialized support from our team. Here's what you can do:

**Immediate Actions:**
- Email: support@novacrm.com
- Phone: 1-800-NOVA-CRM
- Submit a ticket through your account portal

**What to Include:**
- Your account ID or company name
- Detailed description of your request
- Any relevant dates or transaction IDs
- Preferred contact method

**Expected Response Time:**
- High priority: 2 hours
- Standard: 24 hours

Our team will reach out shortly to assist you further.
"""
        
        state["answer"] = escalation_message
        state["evidence"].append("escalated:human_support_required")
        
        print(f"[Escalate] Query escalated to human support")
        
        return state
    
    def _validate_node(self, state: AssistantState) -> AssistantState:
        """
        Validate Node: Validate output quality and apply final guardrails
        
        Checks for hallucination indicators, evidence quality, and answer completeness
        """
        answer = state.get("answer", "")
        intent = state.get("intent", "")
        evidence = state.get("evidence", [])
        
        # Validate answer
        validation = self.validator.validate_answer(answer, intent, evidence)
        
        if not validation["is_valid"]:
            print(f"[Validate] Answer failed validation: {validation['warnings']}")
            state["errors"].extend(validation["warnings"])
            # Add validation warning to answer
            state["answer"] = f"{answer}\n\n*Note: This response may be incomplete. Please contact support for assistance.*"
        
        # Validate evidence quality
        evidence_validation = self.validator.validate_evidence(evidence)
        if not evidence_validation["is_valid"]:
            print(f"[Validate] Evidence failed validation: {evidence_validation['warnings']}")
            state["errors"].extend(evidence_validation["warnings"])
        
        # Check intent-answer match
        intent_match = self.validator.check_intent_answer_match(intent, answer, evidence)
        if not intent_match:
            print(f"[Validate] Answer does not match intent: {intent}")
            state["errors"].append(f"Answer-intent mismatch detected")
        
        # Sanitize output
        state["answer"] = self.validator.sanitize_output(state["answer"])
        
        # Log validation metrics
        print(f"[Validate] Validation complete - Valid: {validation['is_valid']}, Warnings: {len(validation['warnings'])}")
        
        return state
    
    def _route_query(self, state: AssistantState) -> Literal["FAQ", "DataLookup", "Escalation"]:
        """
        Conditional routing function
        
        Returns the next node based on classified intent
        """
        intent = state.get("intent", "Escalation")
        return intent
    
    def invoke(self, query: str, account_context: str = None) -> dict:
        """
        Invoke the graph with a query
        
        Args:
            query: User query
            account_context: Optional account ID for scoping
            
        Returns:
            Final state dict with answer and evidence
        """
        initial_state = {
            "history": [],
            "intent": None,
            "query": query,
            "answer": None,
            "evidence": [],
            "errors": [],
            "account_context": account_context
        }
        
        result = self.graph.invoke(initial_state)
        
        return {
            "query": result["query"],
            "intent": result["intent"],
            "answer": result["answer"],
            "evidence": result["evidence"],
            "errors": result["errors"]
        }

def get_graph(model_name: str = "gpt-4o-mini", temperature: float = 0.0) -> NovaCRMGraph:
    """
    Factory function to create graph instance
    
    Args:
        model_name: OpenAI model name
        temperature: LLM temperature
        
        Returns:
        NovaCRMGraph instance
    """
    return NovaCRMGraph(model_name=model_name, temperature=temperature)

