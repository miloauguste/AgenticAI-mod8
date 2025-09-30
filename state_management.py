from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from healthcare_schema import (
    HealthcareAgentState, 
    QuerySchema, 
    LiteratureSummarySchema,
    create_query,
    validate_state
)
import json
from datetime import datetime

class HealthcareStateManager:
    """
    State Management System for Healthcare Research Assistant
    Manages state transitions and memory updates using LangGraph StateGraph
    """
    
    def __init__(self, memory_saver: SqliteSaver = None):
        self.memory_saver = memory_saver or SqliteSaver.from_conn_string(":memory:")
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the StateGraph for healthcare research workflow"""
        workflow = StateGraph(HealthcareAgentState)
        
        # Add nodes for different states
        workflow.add_node("process_query", self.process_query_node)
        workflow.add_node("retrieve_memory", self.retrieve_memory_node)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("update_memory", self.update_memory_node)
        workflow.add_node("trim_memory", self.trim_memory_node)
        workflow.add_node("human_approval", self.human_approval_node)
        workflow.add_node("filter_input", self.filter_input_node)
        
        # Define the workflow flow
        workflow.set_entry_point("filter_input")
        
        workflow.add_edge("filter_input", "process_query")
        workflow.add_edge("process_query", "retrieve_memory")
        workflow.add_edge("retrieve_memory", "generate_response")
        workflow.add_edge("generate_response", "human_approval")
        workflow.add_edge("human_approval", "update_memory")
        workflow.add_edge("update_memory", "trim_memory")
        workflow.add_edge("trim_memory", END)
        
        return workflow.compile(checkpointer=self.memory_saver)
    
    def filter_input_node(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Filter out non-informational inputs and validate queries"""
        if not state.get("current_queries"):
            return state
        
        filtered_queries = []
        for query in state["current_queries"]:
            query_text = query.get("query_text", "").lower().strip()
            
            # Filter out greetings and vague queries
            if self._is_informational_query(query_text):
                filtered_queries.append(query)
        
        state["current_queries"] = filtered_queries
        return state
    
    def _is_informational_query(self, query_text: str) -> bool:
        """Check if query is informational and relevant for medical research"""
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
        vague_terms = ["help", "what can you do", "how are you"]
        
        # Filter out greetings
        if any(greeting in query_text for greeting in greetings):
            return False
        
        # Filter out vague queries
        if any(vague in query_text for vague in vague_terms):
            return False
        
        # Check for medical/research keywords
        medical_keywords = [
            "treatment", "therapy", "drug", "medication", "clinical", "trial",
            "disease", "diagnosis", "patient", "efficacy", "side effects",
            "literature", "research", "study", "pubmed", "journal"
        ]
        
        return any(keyword in query_text for keyword in medical_keywords)
    
    def process_query_node(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Process incoming queries and categorize them"""
        if not state["current_queries"]:
            return state
        
        processed_queries = []
        for query in state["current_queries"]:
            query_text = query["query_text"].lower()
            
            # Categorize query type
            if any(term in query_text for term in ["compare", "versus", "vs", "difference"]):
                query["query_type"] = "treatment_comparison"
            elif any(term in query_text for term in ["literature", "research", "studies", "papers"]):
                query["query_type"] = "literature_search"
            else:
                query["query_type"] = "clinical_question"
            
            # Set priority based on urgency keywords
            if any(term in query_text for term in ["urgent", "critical", "emergency"]):
                query["priority"] = "critical"
            elif any(term in query_text for term in ["important", "priority"]):
                query["priority"] = "high"
            else:
                query["priority"] = "medium"
            
            query["status"] = "processing"
            processed_queries.append(query)
        
        state["current_queries"] = processed_queries
        state["message_count"] += len(processed_queries)
        return state
    
    def retrieve_memory_node(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Retrieve relevant information from long-term memory"""
        if not state["current_queries"]:
            return state
        
        relevant_summaries = []
        relevant_comparisons = []
        
        for query in state["current_queries"]:
            query_text = query["query_text"].lower()
            disease_focus = state["disease_focus"].lower()
            
            # Retrieve relevant literature summaries
            for summary in state["literature_summaries"]:
                if (disease_focus in summary["treatment_focus"].lower() or 
                    any(term in summary["key_findings"][0].lower() 
                        for term in query_text.split() if len(term) > 3)):
                    relevant_summaries.append(summary)
            
            # Retrieve relevant comparative findings
            for comparison in state["comparative_findings"]:
                if (disease_focus in comparison["disease_condition"].lower() or
                    any(treatment.lower() in query_text 
                        for treatment in comparison["treatments"])):
                    relevant_comparisons.append(comparison)
        
        # Add retrieved information to session responses for context
        if relevant_summaries or relevant_comparisons:
            retrieval_context = {
                "type": "memory_retrieval",
                "summaries": relevant_summaries[:3],  # Limit to top 3
                "comparisons": relevant_comparisons[:2],  # Limit to top 2
                "timestamp": datetime.now().isoformat()
            }
            state["session_responses"].append(retrieval_context)
        
        return state
    
    def generate_response_node(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Generate responses to medical queries (placeholder for LLM integration)"""
        if not state["current_queries"]:
            return state
        
        responses = []
        for query in state["current_queries"]:
            response = {
                "query_id": query["query_id"],
                "response_type": query["query_type"],
                "generated_content": f"Generated response for {query['query_type']}: {query['query_text']}",
                "confidence_score": 0.85,
                "requires_approval": query["priority"] in ["high", "critical"],
                "timestamp": datetime.now().isoformat()
            }
            responses.append(response)
        
        state["session_responses"].extend(responses)
        return state
    
    def human_approval_node(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Handle human-in-the-loop approval for critical responses"""
        pending_approvals = []
        
        for response in state["session_responses"]:
            if response.get("requires_approval", False):
                approval_request = {
                    "approval_id": f"approval_{response.get('query_id', 'unknown')}",
                    "content": response["generated_content"],
                    "type": response["response_type"],
                    "timestamp": datetime.now().isoformat(),
                    "status": "pending_approval"
                }
                pending_approvals.append(approval_request)
        
        state["pending_approvals"].extend(pending_approvals)
        return state
    
    def update_memory_node(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Update long-term memory with new findings and responses"""
        # Update research projects
        current_project = {
            "project_id": state["project_id"],
            "researcher_id": state["researcher_id"],
            "disease_focus": state["disease_focus"],
            "last_updated": datetime.now().isoformat(),
            "query_count": len(state["current_queries"]),
            "session_id": state["session_id"]
        }
        
        # Check if project already exists, update or add
        project_exists = False
        for i, project in enumerate(state["research_projects"]):
            if project["project_id"] == state["project_id"]:
                state["research_projects"][i] = current_project
                project_exists = True
                break
        
        if not project_exists:
            state["research_projects"].append(current_project)
        
        # Clear current queries after processing
        state["current_queries"] = []
        
        return state
    
    def trim_memory_node(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Trim short-term memory to maintain performance"""
        max_session_responses = 7
        max_active_conversation = 10
        
        # Trim session responses
        if len(state["session_responses"]) > max_session_responses:
            state["session_responses"] = state["session_responses"][-max_session_responses:]
            state["memory_trimmed"] = True
        
        # Trim active conversation
        if len(state["active_conversation"]) > max_active_conversation:
            state["active_conversation"] = state["active_conversation"][-max_active_conversation:]
            state["memory_trimmed"] = True
        
        return state
    
    def state_reducer(self, current_state: HealthcareAgentState, update: Dict[str, Any]) -> HealthcareAgentState:
        """Reduce state updates with current state"""
        for key, value in update.items():
            if key in current_state:
                if isinstance(current_state[key], list) and isinstance(value, list):
                    current_state[key].extend(value)
                else:
                    current_state[key] = value
        
        # Update timestamp
        current_state["timestamp"] = datetime.now().isoformat()
        
        # Validate state after update
        if not validate_state(current_state):
            raise ValueError("Invalid state after update")
        
        return current_state
    
    def add_query(self, state: HealthcareAgentState, query_text: str, query_type: str = "clinical_question") -> HealthcareAgentState:
        """Add a new query to the current state"""
        new_query = create_query(query_text, query_type)
        state["current_queries"].append(new_query)
        return state
    
    def process_state_update(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Process a complete state update through the workflow"""
        thread_config = {"configurable": {"thread_id": state["session_id"]}}
        result = self.graph.invoke(state, thread_config)
        return result