import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import io
import os
from typing import Dict, List, Any

from healthcare_schema import (
    HealthcareAgentState, 
    create_initial_state, 
    create_query
)
from state_management import HealthcareStateManager
from memory_manager import HealthcareMemoryManager
from medical_query_handler import MedicalQueryHandler
from message_filter import MessageFilter
from config import get_config

class HealthcareResearchUI:
    """Streamlit UI for Healthcare Research Assistant"""
    
    def __init__(self):
        self.init_session_state()
        self.config = get_config()
        self.memory_manager = HealthcareMemoryManager()
        print(f"Streamlit: Creating MedicalQueryHandler with API key: {self.config.GOOGLE_API_KEY[:10] if self.config.GOOGLE_API_KEY else 'None'}...")
        self.query_handler = MedicalQueryHandler(self.config.GOOGLE_API_KEY)
        print(f"Streamlit: Query handler created. use_direct_genai: {getattr(self.query_handler, 'use_direct_genai', 'Not set')}")
        self.message_filter = MessageFilter()
        self.state_manager = HealthcareStateManager()
    
    def init_session_state(self):
        """Initialize Streamlit session state"""
        if 'healthcare_state' not in st.session_state:
            st.session_state.healthcare_state = create_initial_state(
                researcher_id="streamlit_user", 
                project_id="general_research", 
                disease_focus="general_medicine"
            )
        if 'current_session' not in st.session_state:
            st.session_state.current_session = None
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        if 'pending_approvals' not in st.session_state:
            st.session_state.pending_approvals = []
    
    def run(self):
        """Run the Streamlit application"""
        st.set_page_config(
            page_title="MediSyn Labs - Healthcare Research Assistant",
            page_icon="🔬",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown(self.get_custom_css(), unsafe_allow_html=True)
        
        # Main header
        st.title("🔬 MediSyn Labs Healthcare Research Assistant")
        st.markdown("*AI-Powered Medical Literature Analysis & Treatment Comparison*")
        
        # Sidebar
        self.render_sidebar()
        
        # Main content area
        if st.session_state.healthcare_state is None:
            self.render_welcome_page()
        else:
            self.render_main_interface()
    
    def get_custom_css(self) -> str:
        """Custom CSS for the application"""
        return """
        <style>
        .main-header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }
        .query-box {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #1e3c72;
            margin: 1rem 0;
        }
        .response-box {
            background-color: #e8f4fd;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #2a5298;
            margin: 1rem 0;
        }
        .approval-needed {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .success-box {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .error-box {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        </style>
        """
    
    def render_sidebar(self):
        """Render the sidebar with session management and settings"""
        st.sidebar.title("🏥 Session Management")
        
        # Session creation
        with st.sidebar.expander("🆕 New Research Session", expanded=False):
            researcher_id = st.text_input("Researcher ID", value="researcher_001")
            project_id = st.text_input("Project ID", value="project_" + datetime.now().strftime("%Y%m%d"))
            disease_focus = st.selectbox(
                "Disease Focus",
                ["COVID-19", "Diabetes", "Hypertension", "Cancer", "Cardiovascular", "Respiratory", "Neurological", "Other"]
            )
            
            if st.button("🚀 Start New Session"):
                state = create_initial_state(researcher_id, project_id, disease_focus)
                st.session_state.healthcare_state = state
                st.session_state.current_session = state['session_id']
                st.success(f"✅ Session started: {state['session_id'][:8]}...")
                st.rerun()
        
        # Current session info
        if st.session_state.healthcare_state:
            st.sidebar.markdown("### 📊 Current Session")
            state = st.session_state.healthcare_state
            st.sidebar.info(f"""
            **Session ID:** {state['session_id'][:8]}...
            **Researcher:** {state['researcher_id']}
            **Project:** {state['project_id']}
            **Focus:** {state['disease_focus']}
            **Queries:** {len(state['current_queries'])}
            """)
            
            if st.sidebar.button("💾 Save Session"):
                if self.memory_manager.save_session(state):
                    st.sidebar.success("✅ Session saved!")
                else:
                    st.sidebar.error("❌ Failed to save session")
        
        # Settings
        with st.sidebar.expander("⚙️ Settings", expanded=False):
            st.markdown("**Filter Settings**")
            max_queries = st.slider("Max Short-term Queries", 3, 15, 7)
            
            st.markdown("**LLM Settings**")
            api_key_input = st.text_input("Google API Key", type="password", help="Enter your Google Gemini API key")
            
            if api_key_input:
                os.environ['GOOGLE_API_KEY'] = api_key_input
                self.query_handler = MedicalQueryHandler(api_key_input)
    
    def render_welcome_page(self):
        """Render the welcome page"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class="main-header">
                <h2>🎯 Welcome to MediSyn Labs Research Assistant</h2>
                <p>Your AI-powered companion for medical literature analysis and treatment comparisons</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🌟 Key Features")
            
            features = [
                "📚 **Literature Summarization** - Analyze medical papers and extract key findings",
                "⚖️ **Treatment Comparison** - Compare therapies across diseases and populations",
                "🧠 **Clinical Q&A** - Get evidence-based answers to clinical questions",
                "🔄 **Session Memory** - Maintain context across research sessions",
                "👥 **Human-in-the-Loop** - Approve critical summaries and comparisons",
                "📊 **Report Generation** - Download comprehensive research reports"
            ]
            
            for feature in features:
                st.markdown(feature)
            
            st.markdown("### 🚀 Getting Started")
            st.info("👈 Create a new research session using the sidebar to begin your medical research journey!")
    
    def render_main_interface(self):
        """Render the main research interface"""
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 Query Interface", 
            "🔬 Research Results", 
            "✅ Approvals", 
            "📊 Analytics", 
            "📋 Reports"
        ])
        
        with tab1:
            self.render_query_interface()
        
        with tab2:
            self.render_research_results()
        
        with tab3:
            self.render_approval_interface()
        
        with tab4:
            self.render_analytics()
        
        with tab5:
            self.render_reports()
    
    def render_query_interface(self):
        """Render the main query interface"""
        st.header("💬 Medical Research Query Interface")
        
        # Query input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query_text = st.text_area(
                "Enter your medical research query:",
                height=100,
                placeholder="e.g., What are the latest findings on mRNA vaccine efficacy in elderly populations?"
            )
        
        with col2:
            query_type = st.selectbox(
                "Query Type",
                ["clinical_question", "literature_search", "treatment_comparison"]
            )
            priority = st.selectbox("Priority", ["medium", "high", "critical"])
        
        # Submit query
        if st.button("🔍 Submit Query", type="primary"):
            if query_text.strip():
                self.process_new_query(query_text, query_type, priority)
            else:
                st.error("Please enter a query before submitting.")
        
        # Display recent queries
        if st.session_state.query_history:
            st.subheader("🕒 Recent Queries")
            for i, query_info in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}: {query_info['query_text'][:60]}..."):
                    st.write(f"**Type:** {query_info['query_type']}")
                    st.write(f"**Priority:** {query_info['priority']}")
                    st.write(f"**Timestamp:** {query_info['timestamp']}")
                    st.write(f"**Status:** {query_info['status']}")
    
    def process_new_query(self, query_text: str, query_type: str, priority: str):
        """Process a new query through the system"""
        try:
            # Create new query
            new_query = create_query(query_text, query_type, priority)
            
            # Filter the query
            is_valid, cleaned_text, filter_info = self.message_filter.filter_query(query_text)
            
            if not is_valid:
                st.error(f"❌ Query filtered out: {filter_info['reason']}")
                return
            
            # Update query with cleaned text
            new_query['query_text'] = cleaned_text
            
            # Add to state
            state = st.session_state.healthcare_state
            state['current_queries'].append(new_query)
            
            # Show processing message
            with st.spinner("🔄 Processing your query..."):
                st.info("Query submitted successfully! Processing in progress...")
                
                # Process query
                response = self.query_handler.process_medical_query(new_query)
            
            # Add to session responses
            state['session_responses'].append(response)
            
            # Check if approval needed
            if response.get('requires_approval', False):
                st.session_state.pending_approvals.append({
                    'query_id': new_query['query_id'],
                    'query_text': query_text,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
                st.warning("⚠️ This response requires approval. Check the Approvals tab.")
            
            # Add to query history
            st.session_state.query_history.append({
                'query_id': new_query['query_id'],
                'query_text': query_text,
                'query_type': query_type,
                'priority': priority,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed' if not response.get('requires_approval') else 'pending_approval'
            })
            
            # Update state
            st.session_state.healthcare_state = state
            
            st.success("✅ Query processed successfully! Check the Research Results tab to view your results.")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error processing query: {str(e)}")
    
    def render_research_results(self):
        """Render research results and findings"""
        st.header("🔬 Research Results")
        
        state = st.session_state.healthcare_state
        
        # Check if there are queries being processed
        pending_queries = len(state.get('current_queries', [])) - len(state.get('session_responses', []))
        
        if pending_queries > 0:
            # Show loading spinner for pending queries
            with st.spinner(f"🔄 Processing {pending_queries} query(s)..."):
                st.info("Your queries are being processed in the background. Results will appear here shortly.")
        
        if not state['session_responses']:
            if pending_queries == 0:
                st.info("No research results yet. Submit queries in the Query Interface tab.")
            return
        
        # Display recent responses
        for response in reversed(state['session_responses'][-10:]):
            response_type = response.get('response_type', 'unknown')
            
            with st.expander(f"{self.get_response_icon(response_type)} {response_type.replace('_', ' ').title()}", expanded=True):
                if response_type == "literature_search":
                    self.render_literature_response(response)
                elif response_type == "treatment_comparison":
                    self.render_comparison_response(response)
                elif response_type == "clinical_question":
                    self.render_clinical_response(response)
                else:
                    st.json(response)
                
                # Confidence score
                confidence = response.get('confidence_score', 0)
                st.progress(confidence, text=f"Confidence: {confidence:.1%}")
    
    def get_response_icon(self, response_type: str) -> str:
        """Get icon for response type"""
        icons = {
            'literature_search': '📚',
            'treatment_comparison': '⚖️',
            'clinical_question': '🩺',
            'general_medical': '💊'
        }
        return icons.get(response_type, '🔍')
    
    def render_literature_response(self, response: Dict[str, Any]):
        """Render literature search response"""
        st.markdown(f"**Search Terms:** {', '.join(response.get('search_terms', []))}")
        st.markdown(f"**Articles Found:** {response.get('articles_found', 0)}")
        
        summaries = response.get('summaries', [])
        if summaries:
            for i, summary in enumerate(summaries):
                st.markdown(f"### 📄 Article {i+1}: {summary['title']}")
                st.markdown(f"**Authors:** {', '.join(summary['authors'])}")
                st.markdown(f"**Journal:** {summary['journal']}")
                st.markdown(f"**Key Findings:**")
                for finding in summary['key_findings']:
                    st.markdown(f"- {finding}")
    
    def render_comparison_response(self, response: Dict[str, Any]):
        """Render treatment comparison response"""
        treatments = response.get('treatments_compared', [])
        st.markdown(f"**Treatments Compared:** {', '.join(treatments)}")
        
        comparison_data = response.get('comparison_data', {})
        if comparison_data:
            st.markdown("### 📊 Comparison Results")
            
            # Create comparison table
            if 'efficacy_metrics' in comparison_data:
                efficacy_df = pd.DataFrame([
                    {'Treatment': treatment, 'Efficacy': comparison_data['efficacy_metrics'].get(treatment, 'N/A')}
                    for treatment in treatments
                ])
                st.dataframe(efficacy_df, use_container_width=True)
            
            if 'recommendation' in comparison_data:
                st.markdown(f"**Recommendation:** {comparison_data['recommendation']}")
    
    def render_clinical_response(self, response: Dict[str, Any]):
        """Render clinical question response"""
        clinical_response = response.get('clinical_response', '')
        st.markdown(clinical_response)
    
    def render_approval_interface(self):
        """Render human-in-the-loop approval interface"""
        st.header("✅ Approval Interface")
        
        if not st.session_state.pending_approvals:
            st.success("🎉 No pending approvals! All responses have been processed.")
            return
        
        st.warning(f"⚠️ {len(st.session_state.pending_approvals)} items pending approval")
        
        for i, approval_item in enumerate(st.session_state.pending_approvals):
            with st.expander(f"Approval {i+1}: {approval_item['query_text'][:60]}...", expanded=True):
                st.markdown("### Query")
                st.markdown(f"**Text:** {approval_item['query_text']}")
                
                st.markdown("### Response")
                response = approval_item['response']
                
                if response['response_type'] == 'literature_search':
                    self.render_literature_response(response)
                elif response['response_type'] == 'treatment_comparison':
                    self.render_comparison_response(response)
                else:
                    st.json(response)
                
                # Approval buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{i}"):
                        self.approve_response(i)
                
                with col2:
                    if st.button(f"❌ Reject", key=f"reject_{i}"):
                        self.reject_response(i)
                
                with col3:
                    if st.button(f"✏️ Request Revision", key=f"revise_{i}"):
                        self.request_revision(i)
    
    def approve_response(self, approval_index: int):
        """Approve a pending response"""
        approved_item = st.session_state.pending_approvals.pop(approval_index)
        
        # Add to approved summaries in state
        state = st.session_state.healthcare_state
        state['approved_summaries'].append({
            'approval_id': f"approved_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'query_id': approved_item['query_id'],
            'approved_at': datetime.now().isoformat(),
            'approved_by': state['researcher_id']
        })
        
        st.success("✅ Response approved!")
        st.rerun()
    
    def reject_response(self, approval_index: int):
        """Reject a pending response"""
        rejected_item = st.session_state.pending_approvals.pop(approval_index)
        
        # Add to flagged content
        state = st.session_state.healthcare_state
        state['flagged_content'].append({
            'flag_id': f"flagged_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'query_id': rejected_item['query_id'],
            'reason': 'rejected_by_researcher',
            'flagged_at': datetime.now().isoformat(),
            'flagged_by': state['researcher_id']
        })
        
        st.error("❌ Response rejected!")
        st.rerun()
    
    def request_revision(self, approval_index: int):
        """Request revision for a response"""
        revision_item = st.session_state.pending_approvals[approval_index]
        
        revision_notes = st.text_area(f"Revision notes for item {approval_index + 1}:")
        
        if st.button(f"Submit Revision Request", key=f"submit_revision_{approval_index}"):
            # Add revision request logic here
            st.info("📝 Revision requested! This feature will be implemented in the next version.")
    
    def render_analytics(self):
        """Render analytics dashboard"""
        st.header("📊 Research Analytics")
        
        state = st.session_state.healthcare_state
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", len(st.session_state.query_history))
        
        with col2:
            st.metric("Pending Approvals", len(st.session_state.pending_approvals))
        
        with col3:
            st.metric("Approved Items", len(state.get('approved_summaries', [])))
        
        with col4:
            st.metric("Session Responses", len(state.get('session_responses', [])))
        
        # Query type distribution
        if st.session_state.query_history:
            query_types = [q['query_type'] for q in st.session_state.query_history]
            type_counts = pd.Series(query_types).value_counts()
            
            fig = px.pie(values=type_counts.values, names=type_counts.index, 
                        title="Query Type Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Timeline of queries
        if st.session_state.query_history:
            df = pd.DataFrame(st.session_state.query_history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = px.line(df, x='timestamp', y=None, title="Query Timeline",
                         hover_data=['query_type', 'priority'])
            st.plotly_chart(fig, use_container_width=True)
    
    def render_reports(self):
        """Render report generation interface"""
        st.header("📋 Research Reports")
        
        state = st.session_state.healthcare_state
        
        # Report generation options
        st.subheader("📝 Generate Report")
        
        report_type = st.selectbox(
            "Report Type",
            ["Session Summary", "Literature Review", "Treatment Analysis", "Full Research Report"]
        )
        
        include_options = st.multiselect(
            "Include in Report",
            ["Query History", "Research Results", "Approved Summaries", "Analytics", "Recommendations"],
            default=["Query History", "Research Results"]
        )
        
        if st.button("📊 Generate Report"):
            report_content = self.generate_report(report_type, include_options)
            
            # Display report preview
            st.subheader("📄 Report Preview")
            st.markdown(report_content)
            
            # Download button
            st.download_button(
                label="💾 Download Report",
                data=report_content,
                file_name=f"medisyn_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    def generate_report(self, report_type: str, include_options: List[str]) -> str:
        """Generate research report"""
        state = st.session_state.healthcare_state
        report_lines = []
        
        # Header
        report_lines.append(f"# MediSyn Labs Research Report")
        report_lines.append(f"**Report Type:** {report_type}")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Session ID:** {state['session_id']}")
        report_lines.append(f"**Researcher:** {state['researcher_id']}")
        report_lines.append(f"**Project:** {state['project_id']}")
        report_lines.append(f"**Disease Focus:** {state['disease_focus']}")
        report_lines.append("")
        
        # Include selected sections
        if "Query History" in include_options:
            report_lines.append("## Query History")
            for i, query in enumerate(st.session_state.query_history):
                report_lines.append(f"### Query {i+1}")
                report_lines.append(f"**Text:** {query['query_text']}")
                report_lines.append(f"**Type:** {query['query_type']}")
                report_lines.append(f"**Priority:** {query['priority']}")
                report_lines.append(f"**Status:** {query['status']}")
                report_lines.append("")
        
        if "Research Results" in include_options:
            report_lines.append("## Research Results")
            for i, response in enumerate(state['session_responses']):
                report_lines.append(f"### Result {i+1}")
                report_lines.append(f"**Type:** {response.get('response_type', 'unknown')}")
                report_lines.append(f"**Confidence:** {response.get('confidence_score', 0):.1%}")
                if 'summaries' in response:
                    report_lines.append("**Literature Summaries:**")
                    for summary in response['summaries']:
                        report_lines.append(f"- {summary['title']}")
                report_lines.append("")
        
        if "Analytics" in include_options:
            report_lines.append("## Analytics")
            report_lines.append(f"**Total Queries:** {len(st.session_state.query_history)}")
            report_lines.append(f"**Pending Approvals:** {len(st.session_state.pending_approvals)}")
            report_lines.append(f"**Approved Items:** {len(state.get('approved_summaries', []))}")
            report_lines.append("")
        
        return "\n".join(report_lines)

def main():
    """Main function to run the Streamlit app"""
    app = HealthcareResearchUI()
    app.run()

if __name__ == "__main__":
    main()