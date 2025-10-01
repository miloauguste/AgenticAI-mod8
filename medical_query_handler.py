import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    print("Warning: Google Generative AI not available. Please install langchain-google-genai")

from healthcare_schema import (
    HealthcareAgentState, 
    QuerySchema, 
    LiteratureSummarySchema,
    TreatmentComparisonSchema,
    create_literature_summary
)

class MedicalQueryHandler:
    """
    Medical Query Handler for Healthcare Research Assistant
    Handles medical literature summarization, treatment comparisons, and clinical question answering
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            
            # Use direct genai only to avoid LangChain model compatibility issues
            self.llm = None
            self.use_direct_genai = False
            
            # Try different model names for direct genai - using actually available models
            model_names = ['models/gemini-2.5-flash', 'models/gemini-2.5-pro', 'models/gemini-2.0-flash', 'models/gemini-flash-latest']
            
            for model_name in model_names:
                try:
                    self.genai_model = genai.GenerativeModel(model_name)
                    self.use_direct_genai = True
                    print(f"Successfully initialized direct genai with {model_name}")
                    break
                except Exception as e:
                    print(f"Failed to initialize direct genai with {model_name}: {e}")
                    continue
            
            if not self.use_direct_genai:
                print("Warning: Could not initialize any model. LLM features will be limited.")
        else:
            self.llm = None
            print("Warning: No Google API key provided. LLM features will be limited.")
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response using either LangChain or direct genai"""
        if self.use_direct_genai and hasattr(self, 'genai_model'):
            try:
                print(f"Using direct genai model for response generation")
                response = self.genai_model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Error with direct genai: {e}")
                return f"Error generating response: {e}"
        elif self.llm:
            try:
                print(f"Using LangChain model for response generation")
                response = self.llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                print(f"Error with LangChain: {e}")
                return f"Error generating response: {e}"
        else:
            print(f"No LLM available - use_direct_genai: {getattr(self, 'use_direct_genai', False)}, has genai_model: {hasattr(self, 'genai_model')}, has llm: {self.llm is not None}")
            return "LLM not available. Please check your API key configuration."
    
    def process_medical_query(self, query: QuerySchema, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a medical query and generate appropriate response"""
        query_type = query['query_type']
        
        if query_type == "literature_search":
            return self._handle_literature_search(query, context)
        elif query_type == "treatment_comparison":
            return self._handle_treatment_comparison(query, context)
        elif query_type == "clinical_question":
            return self._handle_clinical_question(query, context)
        else:
            return self._handle_general_medical_query(query, context)
    
    def _handle_literature_search(self, query: QuerySchema, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle literature search queries"""
        search_terms = self._extract_search_terms(query['query_text'])
        
        # Simulate PubMed search (in real implementation, integrate with actual PubMed API)
        mock_articles = self._mock_pubmed_search(search_terms)
        
        summaries = []
        for article in mock_articles:
            if self.llm:
                summary = self._generate_literature_summary(article, query['query_text'])
                summaries.append(summary)
        
        response = {
            "query_id": query['query_id'],
            "response_type": "literature_search",
            "search_terms": search_terms,
            "articles_found": len(mock_articles),
            "summaries": summaries,
            "confidence_score": 0.85,
            "requires_approval": len(summaries) > 3,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _handle_treatment_comparison(self, query: QuerySchema, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle treatment comparison queries"""
        treatments = self._extract_treatments_from_query(query['query_text'])
        
        if len(treatments) < 2:
            return {
                "query_id": query['query_id'],
                "response_type": "treatment_comparison",
                "error": "Please specify at least two treatments to compare",
                "timestamp": datetime.now().isoformat()
            }
        
        comparison_data = self._generate_treatment_comparison(treatments, query['query_text'])
        
        response = {
            "query_id": query['query_id'],
            "response_type": "treatment_comparison",
            "treatments_compared": treatments,
            "comparison_data": comparison_data,
            "confidence_score": 0.80,
            "requires_approval": True,  # Treatment comparisons always require approval
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _handle_clinical_question(self, query: QuerySchema, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle general clinical questions"""
        if self.llm or (self.use_direct_genai and hasattr(self, 'genai_model')):
            clinical_response = self._generate_clinical_response(query['query_text'], context)
        else:
            clinical_response = f"Clinical response for: {query['query_text']} (LLM not available)"
        
        response = {
            "query_id": query['query_id'],
            "response_type": "clinical_question",
            "clinical_response": clinical_response,
            "confidence_score": 0.75,
            "requires_approval": "critical" in query.get('priority', '').lower(),
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _handle_general_medical_query(self, query: QuerySchema, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle general medical queries"""
        if self.llm or (self.use_direct_genai and hasattr(self, 'genai_model')):
            general_response = self._generate_general_medical_response(query['query_text'], context)
        else:
            general_response = f"General medical response for: {query['query_text']} (LLM not available)"
        
        response = {
            "query_id": query['query_id'],
            "response_type": "general_medical",
            "medical_response": general_response,
            "confidence_score": 0.70,
            "requires_approval": False,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _extract_search_terms(self, query_text: str) -> List[str]:
        """Extract search terms from query text"""
        # Simple extraction - in real implementation, use NLP techniques
        medical_keywords = [
            "treatment", "therapy", "drug", "medication", "clinical trial",
            "efficacy", "safety", "side effects", "dosage", "administration",
            "diagnosis", "prognosis", "biomarker", "outcome", "mortality"
        ]
        
        query_lower = query_text.lower()
        extracted_terms = []
        
        for keyword in medical_keywords:
            if keyword in query_lower:
                extracted_terms.append(keyword)
        
        # Add quoted phrases
        words = query_text.split()
        for word in words:
            if len(word) > 4 and word.isalpha():
                extracted_terms.append(word.lower())
        
        return list(set(extracted_terms))[:5]  # Limit to 5 terms
    
    def _extract_treatments_from_query(self, query_text: str) -> List[str]:
        """Extract treatment names from comparison query"""
        # Common treatment indicators
        comparison_words = ["vs", "versus", "compared to", "compare", "between"]
        query_lower = query_text.lower()
        
        treatments = []
        
        # Look for drug names and treatments (simplified approach)
        common_drugs = [
            "aspirin", "ibuprofen", "acetaminophen", "metformin", "insulin",
            "penicillin", "amoxicillin", "warfarin", "simvastatin", "lisinopril",
            "remdesivir", "paxlovid", "hydroxychloroquine", "azithromycin"
        ]
        
        for drug in common_drugs:
            if drug in query_lower:
                treatments.append(drug.title())
        
        # If no specific drugs found, extract from context
        if not treatments:
            words = query_text.split()
            for i, word in enumerate(words):
                if word.lower() in comparison_words and i < len(words) - 1:
                    if i > 0:
                        treatments.append(words[i-1])
                    if i < len(words) - 1:
                        treatments.append(words[i+1])
        
        return list(set(treatments))
    
    def _mock_pubmed_search(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Mock PubMed search - replace with actual PubMed API integration"""
        mock_articles = [
            {
                "title": f"Efficacy of Novel Treatment for {search_terms[0] if search_terms else 'Medical Condition'}",
                "authors": ["Smith, J.", "Johnson, M.", "Brown, K."],
                "journal": "New England Journal of Medicine",
                "publication_date": "2023-09-15",
                "abstract": f"This randomized controlled trial evaluated the efficacy of novel treatment approaches for {search_terms[0] if search_terms else 'various medical conditions'}. Results showed significant improvement in patient outcomes.",
                "pmid": "12345678"
            },
            {
                "title": f"Comparative Analysis of {search_terms[0] if search_terms else 'Treatment'} Protocols",
                "authors": ["Davis, A.", "Wilson, R."],
                "journal": "The Lancet",
                "publication_date": "2023-08-22",
                "abstract": f"A comprehensive meta-analysis comparing different {search_terms[0] if search_terms else 'treatment'} protocols and their clinical outcomes across diverse patient populations.",
                "pmid": "12345679"
            }
        ]
        
        return mock_articles
    
    def _generate_literature_summary(self, article: Dict[str, Any], query_text: str) -> LiteratureSummarySchema:
        """Generate literature summary using LLM"""
        if not self.llm:
            # Fallback without LLM
            key_findings = [
                f"Study focuses on {query_text}",
                "Significant clinical outcomes observed",
                "Further research recommended"
            ]
        else:
            prompt = f"""
            Analyze this medical research article and provide key findings relevant to the query: "{query_text}"
            
            Article Title: {article['title']}
            Authors: {', '.join(article['authors'])}
            Journal: {article['journal']}
            Abstract: {article['abstract']}
            
            Please provide:
            1. 3-5 key findings
            2. Treatment focus
            3. Population studied
            4. Clinical significance
            
            Format as structured text.
            """
            
            try:
                response_text = self._generate_response(prompt)
                key_findings = self._parse_llm_findings(response_text)
            except Exception as e:
                print(f"Error generating summary: {e}")
                key_findings = ["Error generating detailed findings"]
        
        return create_literature_summary(
            title=article['title'],
            authors=article['authors'],
            publication_date=article['publication_date'],
            journal=article['journal'],
            abstract=article['abstract'],
            key_findings=key_findings,
            treatment_focus=query_text,
            population_studied="General population",
            confidence_score=0.85
        )
    
    def _generate_treatment_comparison(self, treatments: List[str], query_text: str) -> TreatmentComparisonSchema:
        """Generate treatment comparison using LLM"""
        if not self.llm:
            comparison_data = {
                "comparison_id": f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "treatments": treatments,
                "disease_condition": "General condition",
                "efficacy_metrics": {treatment: "Moderate efficacy" for treatment in treatments},
                "side_effects": {treatment: ["Mild side effects"] for treatment in treatments},
                "population_differences": {"all_populations": "Similar efficacy across groups"},
                "recommendation": f"Consider individual patient factors when choosing between {' and '.join(treatments)}",
                "confidence_level": "medium",
                "sources": ["Clinical guidelines", "Medical literature"]
            }
        else:
            prompt = f"""
            Compare the following treatments: {', '.join(treatments)}
            
            Query context: {query_text}
            
            Please provide a comprehensive comparison including:
            1. Efficacy metrics for each treatment
            2. Common side effects
            3. Population-specific considerations
            4. Clinical recommendations
            5. Confidence level of the comparison
            
            Base your response on current medical evidence and guidelines.
            """
            
            try:
                response_text = self._generate_response(prompt)
                comparison_data = self._parse_treatment_comparison(response_text, treatments)
            except Exception as e:
                print(f"Error generating comparison: {e}")
                comparison_data = {
                    "comparison_id": f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "treatments": treatments,
                    "disease_condition": "Unknown",
                    "efficacy_metrics": {},
                    "side_effects": {},
                    "population_differences": {},
                    "recommendation": "Unable to generate comparison",
                    "confidence_level": "low",
                    "sources": []
                }
        
        return comparison_data
    
    def _generate_clinical_response(self, query_text: str, context: Dict[str, Any] = None) -> str:
        """Generate clinical response using LLM"""
        if not self.llm and not (self.use_direct_genai and hasattr(self, 'genai_model')):
            return f"Clinical guidance for: {query_text}. Please consult current medical literature and guidelines."
        
        context_str = ""
        if context:
            context_str = f"Context: {json.dumps(context, indent=2)}\n\n"
        
        prompt = f"""
        {context_str}Clinical Question: {query_text}
        
        Please provide a comprehensive clinical response that includes:
        1. Evidence-based answer
        2. Clinical considerations
        3. Relevant guidelines or recommendations
        4. Any important warnings or contraindications
        
        Ensure the response is accurate and based on current medical knowledge.
        """
        
        try:
            response_text = self._generate_response(prompt)
            return response_text
        except Exception as e:
            print(f"Error generating clinical response: {e}")
            return f"Unable to generate detailed clinical response for: {query_text}"
    
    def _generate_general_medical_response(self, query_text: str, context: Dict[str, Any] = None) -> str:
        """Generate general medical response using LLM"""
        if not self.llm and not (self.use_direct_genai and hasattr(self, 'genai_model')):
            return f"General medical information for: {query_text}. Please consult healthcare providers for specific advice."
        
        prompt = f"""
        Medical Query: {query_text}
        
        Please provide helpful medical information while being careful to:
        1. Provide evidence-based information
        2. Avoid giving specific medical advice
        3. Recommend consulting healthcare providers when appropriate
        4. Include relevant disclaimers
        
        Keep the response informative but appropriate for general medical education.
        """
        
        try:
            response_text = self._generate_response(prompt)
            return response_text
        except Exception as e:
            print(f"Error generating general response: {e}")
            return f"Please consult medical literature or healthcare providers regarding: {query_text}"
    
    def _parse_llm_findings(self, llm_response: str) -> List[str]:
        """Parse LLM response to extract key findings"""
        # Simple parsing - in real implementation, use more sophisticated NLP
        lines = llm_response.split('\n')
        findings = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('2.')):
                findings.append(line.lstrip('-•123456789. '))
        
        return findings[:5] if findings else ["Key findings extracted from literature"]
    
    def _parse_treatment_comparison(self, llm_response: str, treatments: List[str]) -> TreatmentComparisonSchema:
        """Parse LLM response to create treatment comparison schema"""
        # Simplified parsing - in real implementation, use structured output
        return TreatmentComparisonSchema(
            comparison_id=f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            treatments=treatments,
            disease_condition="Extracted from query",
            efficacy_metrics={treatment: "Based on LLM analysis" for treatment in treatments},
            side_effects={treatment: ["Analyzed side effects"] for treatment in treatments},
            population_differences={"general": "Population analysis from LLM"},
            recommendation=llm_response[:200] + "..." if len(llm_response) > 200 else llm_response,
            confidence_level="medium",
            sources=["LLM analysis", "Medical literature"]
        )