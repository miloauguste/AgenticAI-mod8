import sqlite3
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from healthcare_schema import (
    HealthcareAgentState, 
    LiteratureSummarySchema, 
    TreatmentComparisonSchema
)

class HealthcareMemoryManager:
    """
    Memory Management System for Healthcare Research Assistant
    Handles both short-term (session) and long-term (persistent) memory storage
    """
    
    def __init__(self, db_path: str = "healthcare_memory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for long-term memory storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for long-term memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS literature_summaries (
                summary_id TEXT PRIMARY KEY,
                researcher_id TEXT,
                project_id TEXT,
                title TEXT,
                authors TEXT,
                publication_date TEXT,
                journal TEXT,
                abstract TEXT,
                key_findings TEXT,
                treatment_focus TEXT,
                population_studied TEXT,
                confidence_score REAL,
                researcher_notes TEXT,
                approved BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS treatment_comparisons (
                comparison_id TEXT PRIMARY KEY,
                researcher_id TEXT,
                project_id TEXT,
                treatments TEXT,
                disease_condition TEXT,
                efficacy_metrics TEXT,
                side_effects TEXT,
                population_differences TEXT,
                recommendation TEXT,
                confidence_level TEXT,
                sources TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_sessions (
                session_id TEXT PRIMARY KEY,
                researcher_id TEXT,
                project_id TEXT,
                disease_focus TEXT,
                session_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS researcher_projects (
                project_id TEXT PRIMARY KEY,
                researcher_id TEXT,
                project_name TEXT,
                disease_focus TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_session(self, state: HealthcareAgentState) -> bool:
        """Save current session to long-term memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            session_data = {
                'current_queries': state['current_queries'],
                'session_responses': state['session_responses'],
                'active_conversation': state['active_conversation'],
                'message_count': state['message_count'],
                'memory_trimmed': state['memory_trimmed']
            }
            
            cursor.execute('''
                INSERT OR REPLACE INTO research_sessions 
                (session_id, researcher_id, project_id, disease_focus, session_data, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                state['session_id'],
                state['researcher_id'],
                state['project_id'],
                state['disease_focus'],
                json.dumps(session_data),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session from long-term memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_data FROM research_sessions WHERE session_id = ?
            ''', (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def save_literature_summary(self, summary: LiteratureSummarySchema, researcher_id: str, project_id: str) -> bool:
        """Save literature summary to long-term memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO literature_summaries 
                (summary_id, researcher_id, project_id, title, authors, publication_date, 
                 journal, abstract, key_findings, treatment_focus, population_studied, 
                 confidence_score, researcher_notes, approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                summary['summary_id'],
                researcher_id,
                project_id,
                summary['title'],
                json.dumps(summary['authors']),
                summary['publication_date'],
                summary['journal'],
                summary['abstract'],
                json.dumps(summary['key_findings']),
                summary['treatment_focus'],
                summary['population_studied'],
                summary['confidence_score'],
                summary['researcher_notes'],
                summary['approved']
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving literature summary: {e}")
            return False
    
    def get_literature_summaries(self, researcher_id: str, project_id: str = None, disease_focus: str = None) -> List[LiteratureSummarySchema]:
        """Retrieve literature summaries from long-term memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM literature_summaries WHERE researcher_id = ?"
            params = [researcher_id]
            
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            
            if disease_focus:
                query += " AND treatment_focus LIKE ?"
                params.append(f"%{disease_focus}%")
            
            query += " ORDER BY created_at DESC LIMIT 10"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            summaries = []
            for row in results:
                summary = LiteratureSummarySchema(
                    summary_id=row[0],
                    title=row[3],
                    authors=json.loads(row[4]),
                    publication_date=row[5],
                    journal=row[6],
                    abstract=row[7],
                    key_findings=json.loads(row[8]),
                    treatment_focus=row[9],
                    population_studied=row[10],
                    confidence_score=row[11],
                    researcher_notes=row[12],
                    approved=bool(row[13])
                )
                summaries.append(summary)
            
            return summaries
        except Exception as e:
            print(f"Error retrieving literature summaries: {e}")
            return []
    
    def save_treatment_comparison(self, comparison: TreatmentComparisonSchema, researcher_id: str, project_id: str) -> bool:
        """Save treatment comparison to long-term memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO treatment_comparisons 
                (comparison_id, researcher_id, project_id, treatments, disease_condition, 
                 efficacy_metrics, side_effects, population_differences, recommendation, 
                 confidence_level, sources)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                comparison['comparison_id'],
                researcher_id,
                project_id,
                json.dumps(comparison['treatments']),
                comparison['disease_condition'],
                json.dumps(comparison['efficacy_metrics']),
                json.dumps(comparison['side_effects']),
                json.dumps(comparison['population_differences']),
                comparison['recommendation'],
                comparison['confidence_level'],
                json.dumps(comparison['sources'])
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving treatment comparison: {e}")
            return False
    
    def get_treatment_comparisons(self, researcher_id: str, project_id: str = None, disease_condition: str = None) -> List[TreatmentComparisonSchema]:
        """Retrieve treatment comparisons from long-term memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM treatment_comparisons WHERE researcher_id = ?"
            params = [researcher_id]
            
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            
            if disease_condition:
                query += " AND disease_condition LIKE ?"
                params.append(f"%{disease_condition}%")
            
            query += " ORDER BY created_at DESC LIMIT 10"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            comparisons = []
            for row in results:
                comparison = TreatmentComparisonSchema(
                    comparison_id=row[0],
                    treatments=json.loads(row[3]),
                    disease_condition=row[4],
                    efficacy_metrics=json.loads(row[5]),
                    side_effects=json.loads(row[6]),
                    population_differences=json.loads(row[7]),
                    recommendation=row[8],
                    confidence_level=row[9],
                    sources=json.loads(row[10])
                )
                comparisons.append(comparison)
            
            return comparisons
        except Exception as e:
            print(f"Error retrieving treatment comparisons: {e}")
            return []
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old sessions from memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            cursor.execute('''
                DELETE FROM research_sessions WHERE last_updated < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
        except Exception as e:
            print(f"Error cleaning up old sessions: {e}")
            return 0
    
    def get_researcher_stats(self, researcher_id: str) -> Dict[str, Any]:
        """Get statistics for a researcher"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count literature summaries
            cursor.execute('''
                SELECT COUNT(*) FROM literature_summaries WHERE researcher_id = ?
            ''', (researcher_id,))
            literature_count = cursor.fetchone()[0]
            
            # Count treatment comparisons
            cursor.execute('''
                SELECT COUNT(*) FROM treatment_comparisons WHERE researcher_id = ?
            ''', (researcher_id,))
            comparison_count = cursor.fetchone()[0]
            
            # Count sessions
            cursor.execute('''
                SELECT COUNT(*) FROM research_sessions WHERE researcher_id = ?
            ''', (researcher_id,))
            session_count = cursor.fetchone()[0]
            
            # Get most recent activity
            cursor.execute('''
                SELECT MAX(last_updated) FROM research_sessions WHERE researcher_id = ?
            ''', (researcher_id,))
            last_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'researcher_id': researcher_id,
                'literature_summaries': literature_count,
                'treatment_comparisons': comparison_count,
                'total_sessions': session_count,
                'last_activity': last_activity
            }
        except Exception as e:
            print(f"Error getting researcher stats: {e}")
            return {}
    
    def trim_short_term_memory(self, state: HealthcareAgentState, max_items: int = 7) -> HealthcareAgentState:
        """Trim short-term memory to improve performance"""
        # Trim session responses
        if len(state['session_responses']) > max_items:
            state['session_responses'] = state['session_responses'][-max_items:]
            state['memory_trimmed'] = True
        
        # Trim active conversation
        if len(state['active_conversation']) > max_items:
            state['active_conversation'] = state['active_conversation'][-max_items:]
            state['memory_trimmed'] = True
        
        # Trim current queries if too many
        if len(state['current_queries']) > max_items:
            state['current_queries'] = state['current_queries'][-max_items:]
            state['memory_trimmed'] = True
        
        return state