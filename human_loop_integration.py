from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import uuid
from healthcare_schema import HealthcareAgentState, LiteratureSummarySchema, TreatmentComparisonSchema

class HumanInTheLoopManager:
    """
    Human-in-the-Loop Integration for Healthcare Research Assistant
    Manages approval workflows, feedback collection, and quality control
    """
    
    def __init__(self):
        self.approval_callbacks = {}
        self.feedback_handlers = {}
        self.quality_thresholds = {
            'confidence_threshold': 0.7,
            'medical_relevance_threshold': 0.8,
            'critical_priority_auto_approve': False
        }
    
    def register_approval_callback(self, content_type: str, callback: Callable):
        """Register a callback function for specific content type approvals"""
        self.approval_callbacks[content_type] = callback
    
    def register_feedback_handler(self, feedback_type: str, handler: Callable):
        """Register a handler for specific feedback types"""
        self.feedback_handlers[feedback_type] = handler
    
    def requires_approval(self, content: Dict[str, Any], content_type: str) -> bool:
        """Determine if content requires human approval"""
        
        # Always require approval for critical priority items
        if content.get('priority') == 'critical':
            return True
        
        # Check confidence score
        confidence = content.get('confidence_score', 0)
        if confidence < self.quality_thresholds['confidence_threshold']:
            return True
        
        # Treatment comparisons always require approval
        if content_type == 'treatment_comparison':
            return True
        
        # Literature summaries with high impact require approval
        if content_type == 'literature_summary':
            if self._is_high_impact_literature(content):
                return True
        
        # Check for sensitive medical content
        if self._contains_sensitive_content(content):
            return True
        
        return False
    
    def _is_high_impact_literature(self, content: Dict[str, Any]) -> bool:
        """Check if literature summary is high impact and requires approval"""
        high_impact_journals = [
            "new england journal of medicine", "the lancet", "jama", "nature medicine",
            "science", "cell", "british medical journal", "annals of internal medicine"
        ]
        
        journal = content.get('journal', '').lower()
        return any(journal_name in journal for journal_name in high_impact_journals)
    
    def _contains_sensitive_content(self, content: Dict[str, Any]) -> bool:
        """Check if content contains sensitive medical information"""
        sensitive_keywords = [
            'contraindicated', 'black box warning', 'fatal', 'mortality',
            'severe adverse', 'emergency', 'toxic', 'overdose'
        ]
        
        content_text = json.dumps(content).lower()
        return any(keyword in content_text for keyword in sensitive_keywords)
    
    def create_approval_request(
        self, 
        content: Dict[str, Any], 
        content_type: str, 
        researcher_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create an approval request for human review"""
        
        approval_request = {
            'approval_id': str(uuid.uuid4()),
            'content': content,
            'content_type': content_type,
            'researcher_id': researcher_id,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'context': context or {},
            'priority': self._determine_approval_priority(content, content_type),
            'approval_criteria': self._get_approval_criteria(content_type),
            'estimated_review_time': self._estimate_review_time(content_type)
        }
        
        return approval_request
    
    def _determine_approval_priority(self, content: Dict[str, Any], content_type: str) -> str:
        """Determine the priority level for approval"""
        
        # Critical content gets highest priority
        if content.get('priority') == 'critical':
            return 'urgent'
        
        # Treatment comparisons get high priority
        if content_type == 'treatment_comparison':
            return 'high'
        
        # High confidence content gets lower priority
        confidence = content.get('confidence_score', 0)
        if confidence > 0.9:
            return 'low'
        elif confidence > 0.7:
            return 'medium'
        else:
            return 'high'
    
    def _get_approval_criteria(self, content_type: str) -> List[str]:
        """Get approval criteria for different content types"""
        criteria_map = {
            'literature_summary': [
                'Verify accuracy of key findings',
                'Check for potential bias in interpretation',
                'Validate treatment focus alignment',
                'Confirm population relevance',
                'Review confidence score justification'
            ],
            'treatment_comparison': [
                'Verify treatment efficacy claims',
                'Check for contraindications and warnings',
                'Validate population-specific considerations',
                'Review recommendation appropriateness',
                'Confirm source reliability'
            ],
            'clinical_question': [
                'Verify medical accuracy',
                'Check for appropriate disclaimers',
                'Validate evidence-based content',
                'Review recommendation safety'
            ]
        }
        
        return criteria_map.get(content_type, ['General medical accuracy check'])
    
    def _estimate_review_time(self, content_type: str) -> int:
        """Estimate review time in minutes"""
        time_estimates = {
            'literature_summary': 10,
            'treatment_comparison': 15,
            'clinical_question': 5,
            'general_medical': 3
        }
        
        return time_estimates.get(content_type, 5)
    
    def process_approval_response(
        self, 
        approval_id: str, 
        decision: str, 
        feedback: str = None,
        reviewer_id: str = None
    ) -> Dict[str, Any]:
        """Process human approval response"""
        
        response = {
            'approval_id': approval_id,
            'decision': decision,  # 'approved', 'rejected', 'revision_requested'
            'feedback': feedback,
            'reviewer_id': reviewer_id,
            'reviewed_at': datetime.now().isoformat(),
            'review_duration': None  # Could be calculated if we track start time
        }
        
        # Execute appropriate callback based on decision
        if decision == 'approved':
            self._handle_approval(approval_id, response)
        elif decision == 'rejected':
            self._handle_rejection(approval_id, response)
        elif decision == 'revision_requested':
            self._handle_revision_request(approval_id, response)
        
        return response
    
    def _handle_approval(self, approval_id: str, response: Dict[str, Any]):
        """Handle approved content"""
        callback = self.approval_callbacks.get('approved')
        if callback:
            callback(approval_id, response)
    
    def _handle_rejection(self, approval_id: str, response: Dict[str, Any]):
        """Handle rejected content"""
        callback = self.approval_callbacks.get('rejected')
        if callback:
            callback(approval_id, response)
    
    def _handle_revision_request(self, approval_id: str, response: Dict[str, Any]):
        """Handle revision requests"""
        callback = self.approval_callbacks.get('revision_requested')
        if callback:
            callback(approval_id, response)
    
    def create_feedback_prompt(self, content_type: str, content: Dict[str, Any]) -> str:
        """Create contextual feedback prompts for reviewers"""
        
        prompts = {
            'literature_summary': f"""
                Please review this literature summary for accuracy and relevance:
                
                **Title:** {content.get('title', 'N/A')}
                **Key Findings:** {content.get('key_findings', [])}
                **Confidence Score:** {content.get('confidence_score', 0):.2%}
                
                Consider:
                - Are the key findings accurately represented?
                - Is the confidence score appropriate?
                - Are there any missing critical details?
                - Does this align with current medical knowledge?
            """,
            
            'treatment_comparison': f"""
                Please review this treatment comparison for clinical accuracy:
                
                **Treatments:** {content.get('treatments', [])}
                **Recommendation:** {content.get('recommendation', 'N/A')}
                
                Consider:
                - Are the efficacy claims supported by evidence?
                - Are important contraindications mentioned?
                - Is the recommendation clinically appropriate?
                - Are population-specific factors addressed?
            """,
            
            'clinical_question': f"""
                Please review this clinical response for accuracy and safety:
                
                **Response:** {content.get('clinical_response', 'N/A')[:200]}...
                
                Consider:
                - Is the medical information accurate?
                - Are appropriate disclaimers included?
                - Is the advice safe for general guidance?
                - Should patients be directed to healthcare providers?
            """
        }
        
        return prompts.get(content_type, "Please review this content for medical accuracy and appropriateness.")
    
    def generate_approval_summary(self, approvals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of approval activities"""
        
        total_approvals = len(approvals)
        approved = sum(1 for a in approvals if a.get('decision') == 'approved')
        rejected = sum(1 for a in approvals if a.get('decision') == 'rejected')
        revision_requested = sum(1 for a in approvals if a.get('decision') == 'revision_requested')
        pending = sum(1 for a in approvals if a.get('decision') == 'pending')
        
        # Calculate average review times
        completed_reviews = [a for a in approvals if a.get('reviewed_at')]
        avg_review_time = self._calculate_average_review_time(completed_reviews)
        
        # Content type breakdown
        content_types = {}
        for approval in approvals:
            content_type = approval.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        return {
            'total_approvals': total_approvals,
            'approved': approved,
            'rejected': rejected,
            'revision_requested': revision_requested,
            'pending': pending,
            'approval_rate': approved / total_approvals if total_approvals > 0 else 0,
            'average_review_time_minutes': avg_review_time,
            'content_type_breakdown': content_types,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_average_review_time(self, completed_reviews: List[Dict[str, Any]]) -> float:
        """Calculate average review time in minutes"""
        if not completed_reviews:
            return 0.0
        
        total_time = 0
        count = 0
        
        for review in completed_reviews:
            if review.get('review_duration'):
                total_time += review['review_duration']
                count += 1
        
        return total_time / count if count > 0 else 0.0
    
    def update_quality_thresholds(self, new_thresholds: Dict[str, Any]):
        """Update quality control thresholds"""
        self.quality_thresholds.update(new_thresholds)
    
    def get_pending_approvals(self, researcher_id: str = None) -> List[Dict[str, Any]]:
        """Get pending approvals, optionally filtered by researcher"""
        # This would integrate with the actual storage system
        # For now, return empty list as placeholder
        return []
    
    def escalate_approval(self, approval_id: str, reason: str) -> Dict[str, Any]:
        """Escalate approval to higher authority"""
        escalation = {
            'escalation_id': str(uuid.uuid4()),
            'original_approval_id': approval_id,
            'reason': reason,
            'escalated_at': datetime.now().isoformat(),
            'status': 'escalated',
            'priority': 'urgent'
        }
        
        return escalation
    
    def create_approval_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create custom approval workflow"""
        workflow = {
            'workflow_id': str(uuid.uuid4()),
            'name': workflow_name,
            'steps': steps,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        
        return workflow
    
    def auto_approve_based_on_criteria(self, content: Dict[str, Any], content_type: str) -> bool:
        """Determine if content can be auto-approved based on criteria"""
        
        # Never auto-approve critical content
        if content.get('priority') == 'critical':
            return False
        
        # High confidence and low risk content can be auto-approved
        confidence = content.get('confidence_score', 0)
        if confidence > 0.95 and not self._contains_sensitive_content(content):
            return True
        
        # Auto-approve simple clinical questions with disclaimers
        if content_type == 'clinical_question':
            response_text = content.get('clinical_response', '').lower()
            has_disclaimer = any(phrase in response_text for phrase in [
                'consult your doctor', 'speak with your healthcare provider',
                'this is not medical advice', 'for educational purposes'
            ])
            if confidence > 0.8 and has_disclaimer:
                return True
        
        return False
    
    def generate_quality_report(self, period_days: int = 30) -> Dict[str, Any]:
        """Generate quality control report"""
        # This would integrate with actual data storage
        # Placeholder implementation
        return {
            'period_days': period_days,
            'total_content_reviewed': 0,
            'auto_approved': 0,
            'human_approved': 0,
            'rejected': 0,
            'quality_score': 0.0,
            'improvement_suggestions': [
                'Increase confidence thresholds for auto-approval',
                'Add more specific medical domain checks',
                'Implement reviewer training recommendations'
            ],
            'generated_at': datetime.now().isoformat()
        }