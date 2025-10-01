import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
from healthcare_schema import HealthcareAgentState, QuerySchema

class MessageFilter:
    """
    Message Filtering System for Healthcare Research Assistant
    Filters and trims messages to optimize processing and maintain relevant context
    """
    
    def __init__(self, max_short_term_queries: int = 7):
        self.max_short_term_queries = max_short_term_queries
        self.medical_keywords = self._load_medical_keywords()
        self.non_informational_patterns = self._load_filtering_patterns()
    
    def _load_medical_keywords(self) -> List[str]:
        """Load medical and research-related keywords"""
        return [
            # Medical conditions
            "diabetes", "hypertension", "cancer", "covid", "pneumonia", "asthma",
            "arthritis", "depression", "anxiety", "migraine", "copd", "alzheimer",
            "disease", "syndrome", "disorder", "condition", "illness", "symptom",
            
            # Treatments and interventions
            "treatment", "therapy", "medication", "drug", "surgery", "procedure",
            "intervention", "protocol", "regimen", "dosage", "administration",
            "cure", "heal", "remedy", "medicine", "pharmaceutical",
            
            # Research terms
            "clinical trial", "study", "research", "meta-analysis", "systematic review",
            "randomized", "controlled", "placebo", "efficacy", "safety",
            "evidence", "data", "analysis", "findings", "results",
            
            # Medical outcomes
            "mortality", "morbidity", "outcome", "prognosis", "diagnosis", "biomarker",
            "side effects", "adverse events", "complications", "recovery",
            "symptoms", "pain", "relief", "improvement",
            
            # Healthcare systems
            "patient", "healthcare", "clinical", "hospital", "physician", "nurse",
            "pharmacist", "medical", "health", "medicine", "doctor", "clinic",
            
            # General medical/health terms
            "what", "how", "why", "when", "where", "can", "should", "compare",
            "effective", "best", "recommend", "suggest", "help", "information"
        ]
    
    def _load_filtering_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for filtering non-informational inputs"""
        return [
            {
                "pattern": r"^(hi|hello|hey|good morning|good afternoon|good evening)",
                "type": "greeting",
                "severity": "high"
            },
            {
                "pattern": r"^(thanks|thank you|thx)",
                "type": "acknowledgment",
                "severity": "medium"
            },
            {
                "pattern": r"^(what can you do|help|how are you|what is this)",
                "type": "vague_query",
                "severity": "high"
            },
            {
                "pattern": r"^(yes|no|ok|okay|sure)$",
                "type": "simple_response",
                "severity": "medium"
            },
            {
                "pattern": r"^.{1,3}$",
                "type": "too_short",
                "severity": "high"
            },
            {
                "pattern": r"^(.)\1{5,}",  # Repeated characters
                "type": "spam",
                "severity": "high"
            }
        ]
    
    def filter_query(self, query_text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Filter a single query to determine if it's informational
        Returns: (is_valid, cleaned_text, filter_info)
        """
        original_text = query_text
        cleaned_text = self._clean_text(query_text)
        
        # Check length
        if len(cleaned_text.strip()) < 5:
            return False, cleaned_text, {
                "reason": "too_short",
                "original_length": len(original_text),
                "cleaned_length": len(cleaned_text)
            }
        
        # Check against filtering patterns
        for pattern_info in self.non_informational_patterns:
            if re.search(pattern_info["pattern"], cleaned_text.lower(), re.IGNORECASE):
                if pattern_info["severity"] == "high":
                    return False, cleaned_text, {
                        "reason": pattern_info["type"],
                        "pattern": pattern_info["pattern"],
                        "severity": pattern_info["severity"]
                    }
        
        # Check for medical relevance
        medical_score = self._calculate_medical_relevance(cleaned_text)
        
        if medical_score < 0.01:  # Very low medical relevance - more permissive threshold
            return False, cleaned_text, {
                "reason": "low_medical_relevance",
                "medical_score": medical_score,
                "threshold": 0.01
            }
        
        return True, cleaned_text, {
            "reason": "valid",
            "medical_score": medical_score,
            "passed_filters": True
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep medical symbols
        text = re.sub(r'[^\w\s\-\+\/%\.\,\;\:\?\!]', '', text)
        
        # Normalize common medical abbreviations
        abbreviations = {
            'mg': 'milligrams',
            'ml': 'milliliters',
            'mcg': 'micrograms',
            'bid': 'twice daily',
            'tid': 'three times daily',
            'qd': 'once daily'
        }
        
        for abbr, full in abbreviations.items():
            text = re.sub(r'\b' + abbr + r'\b', full, text, flags=re.IGNORECASE)
        
        return text
    
    def _calculate_medical_relevance(self, text: str) -> float:
        """Calculate medical relevance score for text"""
        text_lower = text.lower()
        words = text_lower.split()
        
        if not words:
            return 0.0
        
        medical_word_count = 0
        for word in words:
            if any(keyword in word for keyword in self.medical_keywords):
                medical_word_count += 1
        
        # Additional scoring for medical patterns
        medical_patterns = [
            r'\d+\s*(mg|ml|mcg|units)',  # Dosage patterns
            r'(clinical|randomized|controlled)\s+(trial|study)',  # Study types
            r'(side\s+effects|adverse\s+events)',  # Safety terms
            r'(efficacy|effectiveness|outcome)',  # Outcome terms
        ]
        
        pattern_matches = 0
        for pattern in medical_patterns:
            if re.search(pattern, text_lower):
                pattern_matches += 1
        
        # Calculate score
        word_score = medical_word_count / len(words)
        pattern_score = pattern_matches * 0.1
        
        return min(1.0, word_score + pattern_score)
    
    def filter_queries_batch(self, queries: List[QuerySchema]) -> Tuple[List[QuerySchema], List[Dict[str, Any]]]:
        """Filter a batch of queries"""
        valid_queries = []
        filter_results = []
        
        for query in queries:
            is_valid, cleaned_text, filter_info = self.filter_query(query['query_text'])
            
            if is_valid:
                # Update query with cleaned text
                query['query_text'] = cleaned_text
                valid_queries.append(query)
            
            filter_results.append({
                "query_id": query['query_id'],
                "original_text": query['query_text'],
                "cleaned_text": cleaned_text,
                "is_valid": is_valid,
                "filter_info": filter_info,
                "timestamp": datetime.now().isoformat()
            })
        
        return valid_queries, filter_results
    
    def trim_short_term_memory(self, state: HealthcareAgentState) -> HealthcareAgentState:
        """Trim short-term memory to maintain performance"""
        # Trim current queries
        if len(state['current_queries']) > self.max_short_term_queries:
            # Keep the most recent queries
            state['current_queries'] = state['current_queries'][-self.max_short_term_queries:]
            state['memory_trimmed'] = True
        
        # Trim session responses
        if len(state['session_responses']) > self.max_short_term_queries:
            state['session_responses'] = state['session_responses'][-self.max_short_term_queries:]
            state['memory_trimmed'] = True
        
        # Trim active conversation
        if len(state['active_conversation']) > self.max_short_term_queries:
            state['active_conversation'] = state['active_conversation'][-self.max_short_term_queries:]
            state['memory_trimmed'] = True
        
        return state
    
    def prioritize_queries(self, queries: List[QuerySchema]) -> List[QuerySchema]:
        """Prioritize queries based on medical urgency and relevance"""
        def priority_score(query: QuerySchema) -> float:
            score = 0.0
            query_text = query['query_text'].lower()
            
            # Priority based on explicit priority field
            priority_map = {
                'critical': 1.0,
                'high': 0.8,
                'medium': 0.5,
                'low': 0.2
            }
            score += priority_map.get(query.get('priority', 'medium'), 0.5)
            
            # Additional scoring based on urgency keywords
            urgent_keywords = ['urgent', 'emergency', 'critical', 'severe', 'acute']
            for keyword in urgent_keywords:
                if keyword in query_text:
                    score += 0.2
            
            # Medical relevance score
            medical_score = self._calculate_medical_relevance(query['query_text'])
            score += medical_score * 0.3
            
            # Query type scoring
            type_scores = {
                'treatment_comparison': 0.3,
                'literature_search': 0.2,
                'clinical_question': 0.4
            }
            score += type_scores.get(query.get('query_type', 'clinical_question'), 0.1)
            
            return score
        
        # Sort queries by priority score (highest first)
        return sorted(queries, key=priority_score, reverse=True)
    
    def detect_duplicate_queries(self, queries: List[QuerySchema]) -> List[Tuple[int, int]]:
        """Detect duplicate or very similar queries"""
        duplicates = []
        
        for i, query1 in enumerate(queries):
            for j, query2 in enumerate(queries[i+1:], i+1):
                similarity = self._calculate_query_similarity(query1['query_text'], query2['query_text'])
                if similarity > 0.8:  # High similarity threshold
                    duplicates.append((i, j))
        
        return duplicates
    
    def _calculate_query_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two query texts"""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def generate_filter_report(self, filter_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a report on filtering results"""
        total_queries = len(filter_results)
        valid_queries = sum(1 for result in filter_results if result['is_valid'])
        filtered_queries = total_queries - valid_queries
        
        filter_reasons = {}
        for result in filter_results:
            if not result['is_valid']:
                reason = result['filter_info']['reason']
                filter_reasons[reason] = filter_reasons.get(reason, 0) + 1
        
        return {
            "total_queries": total_queries,
            "valid_queries": valid_queries,
            "filtered_queries": filtered_queries,
            "filter_rate": filtered_queries / total_queries if total_queries > 0 else 0,
            "filter_reasons": filter_reasons,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_filter_settings(self, settings: Dict[str, Any]) -> None:
        """Update filter settings dynamically"""
        if 'max_short_term_queries' in settings:
            self.max_short_term_queries = settings['max_short_term_queries']
        
        if 'medical_keywords' in settings:
            self.medical_keywords.extend(settings['medical_keywords'])
        
        if 'additional_patterns' in settings:
            self.non_informational_patterns.extend(settings['additional_patterns'])