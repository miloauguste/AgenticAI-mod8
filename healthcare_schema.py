from typing import List, Dict, Optional, Any
from typing_extensions import TypedDict
from datetime import datetime
import uuid

class HealthcareAgentState(TypedDict):
    """
    Healthcare Memory Schema for MediSyn Labs Research Assistant
    
    This state tracks both short-term session data and long-term research history
    to support medical professionals in literature review and treatment comparisons.
    """
    
    # Short-term memory: Active session queries and responses
    current_queries: List[Dict[str, Any]]
    session_responses: List[Dict[str, Any]]
    active_conversation: List[Dict[str, str]]
    
    # Long-term memory: Stored literature summaries and research history
    literature_summaries: List[Dict[str, Any]]
    comparative_findings: List[Dict[str, Any]]
    case_history: List[Dict[str, Any]]
    research_projects: List[Dict[str, Any]]
    
    # Metadata fields
    researcher_id: str
    project_id: str
    disease_focus: str
    session_id: str
    timestamp: str
    
    # Memory management
    memory_trimmed: bool
    message_count: int
    
    # Human-in-the-loop tracking
    pending_approvals: List[Dict[str, Any]]
    approved_summaries: List[Dict[str, Any]]
    flagged_content: List[Dict[str, Any]]

class QuerySchema(TypedDict):
    """Schema for individual medical queries"""
    query_id: str
    query_text: str
    query_type: str  # "literature_search", "treatment_comparison", "clinical_question"
    timestamp: str
    priority: str    # "low", "medium", "high", "critical"
    status: str      # "pending", "processing", "completed", "requires_approval"

class LiteratureSummarySchema(TypedDict):
    """Schema for literature summaries"""
    summary_id: str
    title: str
    authors: List[str]
    publication_date: str
    journal: str
    abstract: str
    key_findings: List[str]
    treatment_focus: str
    population_studied: str
    confidence_score: float
    researcher_notes: str
    approved: bool

class TreatmentComparisonSchema(TypedDict):
    """Schema for treatment comparisons"""
    comparison_id: str
    treatments: List[str]
    disease_condition: str
    efficacy_metrics: Dict[str, Any]
    side_effects: Dict[str, List[str]]
    population_differences: Dict[str, Any]
    recommendation: str
    confidence_level: str
    sources: List[str]

def create_initial_state(researcher_id: str, project_id: str, disease_focus: str) -> HealthcareAgentState:
    """Create initial healthcare agent state"""
    session_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    return HealthcareAgentState(
        # Short-term memory
        current_queries=[],
        session_responses=[],
        active_conversation=[],
        
        # Long-term memory
        literature_summaries=[],
        comparative_findings=[],
        case_history=[],
        research_projects=[],
        
        # Metadata
        researcher_id=researcher_id,
        project_id=project_id,
        disease_focus=disease_focus,
        session_id=session_id,
        timestamp=timestamp,
        
        # Memory management
        memory_trimmed=False,
        message_count=0,
        
        # Human-in-the-loop
        pending_approvals=[],
        approved_summaries=[],
        flagged_content=[]
    )

def validate_state(state: HealthcareAgentState) -> bool:
    """Validate the healthcare agent state"""
    required_fields = [
        'researcher_id', 'project_id', 'disease_focus', 
        'session_id', 'timestamp'
    ]
    
    for field in required_fields:
        if not state.get(field):
            return False
    
    # Validate disease_focus is a string
    if not isinstance(state['disease_focus'], str):
        return False
    
    # Validate current_queries is a list
    if not isinstance(state['current_queries'], list):
        return False
    
    return True

def create_query(query_text: str, query_type: str, priority: str = "medium") -> QuerySchema:
    """Create a new query schema"""
    return QuerySchema(
        query_id=str(uuid.uuid4()),
        query_text=query_text,
        query_type=query_type,
        timestamp=datetime.now().isoformat(),
        priority=priority,
        status="pending"
    )

def create_literature_summary(
    title: str, 
    authors: List[str], 
    publication_date: str,
    journal: str,
    abstract: str,
    key_findings: List[str],
    treatment_focus: str,
    population_studied: str,
    confidence_score: float = 0.8
) -> LiteratureSummarySchema:
    """Create a literature summary schema"""
    return LiteratureSummarySchema(
        summary_id=str(uuid.uuid4()),
        title=title,
        authors=authors,
        publication_date=publication_date,
        journal=journal,
        abstract=abstract,
        key_findings=key_findings,
        treatment_focus=treatment_focus,
        population_studied=population_studied,
        confidence_score=confidence_score,
        researcher_notes="",
        approved=False
    )