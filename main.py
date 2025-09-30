#!/usr/bin/env python3
"""
MediSyn Labs Healthcare Research Assistant
Main application entry point

This file serves as the primary entry point for the Healthcare Research Assistant,
integrating all components and providing a unified interface for medical professionals.
"""

import os
import sys
import argparse
import logging
from typing import Optional

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config, get_logger
from healthcare_schema import create_initial_state
from state_management import HealthcareStateManager
from memory_manager import HealthcareMemoryManager
from medical_query_handler import MedicalQueryHandler
from message_filter import MessageFilter
from human_loop_integration import HumanInTheLoopManager
from report_generator import HealthcareReportGenerator

class HealthcareResearchAssistant:
    """
    Main Healthcare Research Assistant Application
    Orchestrates all components for medical research workflow
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        # Initialize components
        self.memory_manager = HealthcareMemoryManager()
        self.query_handler = MedicalQueryHandler(self.config.GOOGLE_API_KEY)
        self.message_filter = MessageFilter(self.config.MAX_SHORT_TERM_QUERIES)
        self.state_manager = HealthcareStateManager()
        self.hitl_manager = HumanInTheLoopManager()
        self.report_generator = HealthcareReportGenerator()
        
        self.logger.info(f"Healthcare Research Assistant initialized - Version {self.config.APP_VERSION}")
    
    def start_research_session(
        self, 
        researcher_id: str, 
        project_id: str, 
        disease_focus: str
    ) -> str:
        """Start a new research session"""
        
        try:
            # Create initial state
            state = create_initial_state(researcher_id, project_id, disease_focus)
            
            # Save session
            if self.memory_manager.save_session(state):
                self.logger.info(f"New research session started: {state['session_id']}")
                return state['session_id']
            else:
                raise Exception("Failed to save initial session state")
                
        except Exception as e:
            self.logger.error(f"Error starting research session: {str(e)}")
            raise
    
    def process_query(
        self, 
        session_id: str, 
        query_text: str, 
        query_type: str = "clinical_question",
        priority: str = "medium"
    ) -> dict:
        """Process a medical research query"""
        
        try:
            # Load session state
            session_data = self.memory_manager.load_session(session_id)
            if not session_data:
                raise ValueError(f"Session {session_id} not found")
            
            # Filter query
            is_valid, cleaned_text, filter_info = self.message_filter.filter_query(query_text)
            
            if not is_valid:
                return {
                    'status': 'filtered',
                    'reason': filter_info['reason'],
                    'filter_info': filter_info
                }
            
            # Create query
            from healthcare_schema import create_query
            query = create_query(cleaned_text, query_type, priority)
            
            # Process query
            response = self.query_handler.process_medical_query(query)
            
            # Check if approval needed
            if self.hitl_manager.requires_approval(response, query_type):
                approval_request = self.hitl_manager.create_approval_request(
                    response, query_type, session_data.get('researcher_id', 'unknown')
                )
                response['approval_request'] = approval_request
            
            self.logger.info(f"Query processed successfully: {query['query_id']}")
            
            return {
                'status': 'success',
                'query_id': query['query_id'],
                'response': response,
                'requires_approval': response.get('requires_approval', False)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_report(
        self, 
        session_id: str, 
        report_type: str = "session_summary"
    ) -> str:
        """Generate research report"""
        
        try:
            # Load session data
            session_data = self.memory_manager.load_session(session_id)
            if not session_data:
                raise ValueError(f"Session {session_id} not found")
            
            # Generate report based on type
            if report_type == "session_summary":
                report = self.report_generator.generate_session_summary_report(
                    session_data, [], []  # Would load actual query history and responses
                )
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            self.logger.info(f"Report generated: {report_type} for session {session_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
    
    def get_session_status(self, session_id: str) -> dict:
        """Get session status and statistics"""
        
        try:
            session_data = self.memory_manager.load_session(session_id)
            if not session_data:
                return {'status': 'not_found'}
            
            return {
                'status': 'active',
                'session_id': session_id,
                'created_at': session_data.get('timestamp'),
                'query_count': session_data.get('message_count', 0),
                'memory_trimmed': session_data.get('memory_trimmed', False)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting session status: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def cleanup_old_sessions(self, days_old: int = None) -> int:
        """Clean up old sessions"""
        
        days_old = days_old or self.config.MEMORY_CLEANUP_DAYS
        
        try:
            cleaned_count = self.memory_manager.cleanup_old_sessions(days_old)
            self.logger.info(f"Cleaned up {cleaned_count} old sessions")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {str(e)}")
            return 0

def run_streamlit_app():
    """Run the Streamlit web application"""
    import subprocess
    import sys
    
    try:
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", str(get_config().STREAMLIT_SERVER_PORT),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Healthcare Research Assistant stopped by user")
    except Exception as e:
        print(f"❌ Error running Streamlit app: {e}")

def run_cli_interface():
    """Run command-line interface"""
    
    assistant = HealthcareResearchAssistant()
    
    print(f"🔬 {assistant.config.APP_NAME}")
    print(f"Version {assistant.config.APP_VERSION}")
    print("=" * 50)
    
    # Start interactive session
    researcher_id = input("Enter Researcher ID: ").strip()
    project_id = input("Enter Project ID: ").strip()
    disease_focus = input("Enter Disease Focus: ").strip()
    
    try:
        session_id = assistant.start_research_session(researcher_id, project_id, disease_focus)
        print(f"✅ Session started: {session_id[:8]}...")
        
        print("\n💡 Enter your medical research queries (type 'quit' to exit, 'help' for commands)")
        
        while True:
            query = input("\n🔍 Query: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'help':
                print_help()
                continue
            elif query.lower().startswith('report'):
                report = assistant.generate_report(session_id)
                print("\n📋 Report:")
                print("-" * 30)
                print(report[:500] + "..." if len(report) > 500 else report)
                continue
            elif query.lower().startswith('status'):
                status = assistant.get_session_status(session_id)
                print(f"\n📊 Session Status: {status}")
                continue
            
            if query:
                result = assistant.process_query(session_id, query)
                
                if result['status'] == 'success':
                    response = result['response']
                    print(f"\n✅ Query processed (ID: {result['query_id'][:8]}...)")
                    print(f"Type: {response.get('response_type', 'unknown')}")
                    print(f"Confidence: {response.get('confidence_score', 0):.1%}")
                    
                    if result.get('requires_approval'):
                        print("⚠️  This response requires approval")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print("\n👋 Healthcare Research Assistant stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def print_help():
    """Print help information"""
    print("""
📚 Available Commands:
- Enter any medical query to process
- 'report' - Generate session report
- 'status' - Show session status
- 'help' - Show this help
- 'quit' - Exit the application

🔍 Example Queries:
- "What are the latest findings on COVID-19 treatments?"
- "Compare efficacy of Drug A vs Drug B for diabetes"
- "Literature review on hypertension management"
    """)

def main():
    """Main application entry point"""
    
    parser = argparse.ArgumentParser(
        description="MediSyn Labs Healthcare Research Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --web                 # Run Streamlit web interface
  python main.py --cli                 # Run command-line interface
  python main.py --cleanup             # Clean up old sessions
  python main.py --config              # Show configuration
        """
    )
    
    parser.add_argument('--web', action='store_true', help='Run Streamlit web interface')
    parser.add_argument('--cli', action='store_true', help='Run command-line interface')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old sessions')
    parser.add_argument('--config', action='store_true', help='Show configuration')
    parser.add_argument('--version', action='store_true', help='Show version information')
    
    args = parser.parse_args()
    
    # Show version
    if args.version:
        config = get_config()
        print(f"{config.APP_NAME} v{config.APP_VERSION}")
        return
    
    # Show configuration
    if args.config:
        config = get_config()
        print("Configuration:")
        print("=" * 30)
        for key, value in config.export_config().items():
            print(f"{key}: {value}")
        return
    
    # Clean up old sessions
    if args.cleanup:
        assistant = HealthcareResearchAssistant()
        cleaned = assistant.cleanup_old_sessions()
        print(f"✅ Cleaned up {cleaned} old sessions")
        return
    
    # Run web interface
    if args.web:
        print("🌐 Starting Healthcare Research Assistant Web Interface...")
        run_streamlit_app()
        return
    
    # Run CLI interface
    if args.cli:
        run_cli_interface()
        return
    
    # Default: show help and run web interface
    parser.print_help()
    print("\n🌐 Starting web interface by default...")
    run_streamlit_app()

if __name__ == "__main__":
    main()