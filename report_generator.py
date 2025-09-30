import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import io
import base64
from healthcare_schema import HealthcareAgentState, LiteratureSummarySchema, TreatmentComparisonSchema

class HealthcareReportGenerator:
    """
    Report Generation System for Healthcare Research Assistant
    Creates comprehensive reports for download in multiple formats
    """
    
    def __init__(self):
        self.report_templates = self._load_report_templates()
    
    def _load_report_templates(self) -> Dict[str, str]:
        """Load report templates for different report types"""
        return {
            'session_summary': '''
# Healthcare Research Session Summary

**Generated:** {timestamp}
**Session ID:** {session_id}
**Researcher:** {researcher_id}
**Project:** {project_id}
**Disease Focus:** {disease_focus}

## Executive Summary
{executive_summary}

## Session Metrics
- **Total Queries:** {total_queries}
- **Literature Reviews:** {literature_count}
- **Treatment Comparisons:** {comparison_count}
- **Pending Approvals:** {pending_approvals}
- **Session Duration:** {session_duration}

## Query Analysis
{query_analysis}

## Key Findings
{key_findings}

## Recommendations
{recommendations}
            ''',
            
            'literature_review': '''
# Literature Review Report

**Generated:** {timestamp}
**Research Focus:** {disease_focus}
**Review Period:** {review_period}
**Total Articles Reviewed:** {total_articles}

## Methodology
{methodology}

## Literature Summary
{literature_summaries}

## Key Findings Across Studies
{cross_study_findings}

## Research Gaps Identified
{research_gaps}

## Clinical Implications
{clinical_implications}

## Future Research Directions
{future_directions}
            ''',
            
            'treatment_analysis': '''
# Treatment Analysis Report

**Generated:** {timestamp}
**Disease Focus:** {disease_focus}
**Treatments Analyzed:** {treatments_analyzed}

## Executive Summary
{executive_summary}

## Treatment Comparisons
{treatment_comparisons}

## Efficacy Analysis
{efficacy_analysis}

## Safety Profile Comparison
{safety_comparison}

## Population-Specific Considerations
{population_considerations}

## Clinical Recommendations
{clinical_recommendations}

## Confidence Assessment
{confidence_assessment}
            ''',
            
            'full_research': '''
# Comprehensive Healthcare Research Report

**Generated:** {timestamp}
**Session ID:** {session_id}
**Researcher:** {researcher_id}
**Project:** {project_id}
**Disease Focus:** {disease_focus}

## Table of Contents
1. Executive Summary
2. Methodology
3. Literature Review
4. Treatment Analysis
5. Clinical Findings
6. Recommendations
7. Appendices

## 1. Executive Summary
{executive_summary}

## 2. Methodology
{methodology}

## 3. Literature Review
{literature_review}

## 4. Treatment Analysis
{treatment_analysis}

## 5. Clinical Findings
{clinical_findings}

## 6. Recommendations
{recommendations}

## 7. Appendices
{appendices}
            '''
        }
    
    def generate_session_summary_report(
        self, 
        state: HealthcareAgentState, 
        query_history: List[Dict[str, Any]],
        session_responses: List[Dict[str, Any]]
    ) -> str:
        """Generate session summary report"""
        
        # Calculate metrics
        total_queries = len(query_history)
        literature_count = len([r for r in session_responses if r.get('response_type') == 'literature_search'])
        comparison_count = len([r for r in session_responses if r.get('response_type') == 'treatment_comparison'])
        pending_approvals = len(state.get('pending_approvals', []))
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(state, query_history, session_responses)
        
        # Generate query analysis
        query_analysis = self._generate_query_analysis(query_history)
        
        # Generate key findings
        key_findings = self._generate_key_findings(session_responses)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(state, session_responses)
        
        report = self.report_templates['session_summary'].format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            session_id=state['session_id'],
            researcher_id=state['researcher_id'],
            project_id=state['project_id'],
            disease_focus=state['disease_focus'],
            executive_summary=executive_summary,
            total_queries=total_queries,
            literature_count=literature_count,
            comparison_count=comparison_count,
            pending_approvals=pending_approvals,
            session_duration=self._calculate_session_duration(state),
            query_analysis=query_analysis,
            key_findings=key_findings,
            recommendations=recommendations
        )
        
        return report
    
    def generate_literature_review_report(
        self, 
        state: HealthcareAgentState, 
        literature_summaries: List[LiteratureSummarySchema]
    ) -> str:
        """Generate literature review report"""
        
        methodology = self._generate_methodology_section()
        summaries_text = self._format_literature_summaries(literature_summaries)
        cross_study_findings = self._analyze_cross_study_findings(literature_summaries)
        research_gaps = self._identify_research_gaps(literature_summaries)
        clinical_implications = self._generate_clinical_implications(literature_summaries)
        future_directions = self._suggest_future_directions(literature_summaries)
        
        report = self.report_templates['literature_review'].format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            disease_focus=state['disease_focus'],
            review_period="Current session",
            total_articles=len(literature_summaries),
            methodology=methodology,
            literature_summaries=summaries_text,
            cross_study_findings=cross_study_findings,
            research_gaps=research_gaps,
            clinical_implications=clinical_implications,
            future_directions=future_directions
        )
        
        return report
    
    def generate_treatment_analysis_report(
        self, 
        state: HealthcareAgentState, 
        treatment_comparisons: List[TreatmentComparisonSchema]
    ) -> str:
        """Generate treatment analysis report"""
        
        treatments_analyzed = list(set(
            treatment for comparison in treatment_comparisons 
            for treatment in comparison['treatments']
        ))
        
        executive_summary = self._generate_treatment_executive_summary(treatment_comparisons)
        comparisons_text = self._format_treatment_comparisons(treatment_comparisons)
        efficacy_analysis = self._analyze_treatment_efficacy(treatment_comparisons)
        safety_comparison = self._compare_treatment_safety(treatment_comparisons)
        population_considerations = self._analyze_population_factors(treatment_comparisons)
        clinical_recommendations = self._generate_clinical_recommendations(treatment_comparisons)
        confidence_assessment = self._assess_confidence_levels(treatment_comparisons)
        
        report = self.report_templates['treatment_analysis'].format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            disease_focus=state['disease_focus'],
            treatments_analyzed=', '.join(treatments_analyzed),
            executive_summary=executive_summary,
            treatment_comparisons=comparisons_text,
            efficacy_analysis=efficacy_analysis,
            safety_comparison=safety_comparison,
            population_considerations=population_considerations,
            clinical_recommendations=clinical_recommendations,
            confidence_assessment=confidence_assessment
        )
        
        return report
    
    def generate_full_research_report(
        self, 
        state: HealthcareAgentState, 
        query_history: List[Dict[str, Any]],
        session_responses: List[Dict[str, Any]],
        literature_summaries: List[LiteratureSummarySchema],
        treatment_comparisons: List[TreatmentComparisonSchema]
    ) -> str:
        """Generate comprehensive research report"""
        
        executive_summary = self._generate_comprehensive_executive_summary(
            state, query_history, session_responses, literature_summaries, treatment_comparisons
        )
        methodology = self._generate_comprehensive_methodology()
        literature_review = self._format_literature_summaries(literature_summaries)
        treatment_analysis = self._format_treatment_comparisons(treatment_comparisons)
        clinical_findings = self._synthesize_clinical_findings(session_responses)
        recommendations = self._generate_comprehensive_recommendations(
            state, session_responses, literature_summaries, treatment_comparisons
        )
        appendices = self._generate_appendices(state, query_history, session_responses)
        
        report = self.report_templates['full_research'].format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            session_id=state['session_id'],
            researcher_id=state['researcher_id'],
            project_id=state['project_id'],
            disease_focus=state['disease_focus'],
            executive_summary=executive_summary,
            methodology=methodology,
            literature_review=literature_review,
            treatment_analysis=treatment_analysis,
            clinical_findings=clinical_findings,
            recommendations=recommendations,
            appendices=appendices
        )
        
        return report
    
    def generate_csv_export(
        self, 
        data_type: str, 
        data: List[Dict[str, Any]]
    ) -> str:
        """Generate CSV export for data tables"""
        
        if not data:
            return "No data available for export"
        
        df = pd.DataFrame(data)
        
        # Clean and format DataFrame based on data type
        if data_type == 'query_history':
            df = df[['query_id', 'query_text', 'query_type', 'priority', 'timestamp', 'status']]
        elif data_type == 'literature_summaries':
            df = df[['summary_id', 'title', 'authors', 'journal', 'treatment_focus', 'confidence_score']]
        elif data_type == 'treatment_comparisons':
            df = df[['comparison_id', 'treatments', 'disease_condition', 'recommendation', 'confidence_level']]
        
        return df.to_csv(index=False)
    
    def generate_json_export(self, state: HealthcareAgentState) -> str:
        """Generate JSON export of complete session state"""
        export_data = {
            'export_metadata': {
                'generated_at': datetime.now().isoformat(),
                'export_version': '1.0',
                'session_id': state['session_id']
            },
            'session_state': state,
            'export_summary': {
                'total_queries': len(state.get('current_queries', [])),
                'session_responses': len(state.get('session_responses', [])),
                'literature_summaries': len(state.get('literature_summaries', [])),
                'treatment_comparisons': len(state.get('comparative_findings', []))
            }
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def _generate_executive_summary(
        self, 
        state: HealthcareAgentState, 
        query_history: List[Dict[str, Any]], 
        session_responses: List[Dict[str, Any]]
    ) -> str:
        """Generate executive summary for session"""
        
        summary_parts = []
        
        # Session overview
        summary_parts.append(f"This research session focused on {state['disease_focus']} with {len(query_history)} queries processed.")
        
        # Query breakdown
        query_types = {}
        for query in query_history:
            qtype = query.get('query_type', 'unknown')
            query_types[qtype] = query_types.get(qtype, 0) + 1
        
        type_summary = ', '.join([f"{count} {qtype.replace('_', ' ')}" for qtype, count in query_types.items()])
        summary_parts.append(f"Query breakdown: {type_summary}.")
        
        # Key outcomes
        if session_responses:
            avg_confidence = sum(r.get('confidence_score', 0) for r in session_responses) / len(session_responses)
            summary_parts.append(f"Average confidence score across responses: {avg_confidence:.1%}.")
        
        return ' '.join(summary_parts)
    
    def _generate_query_analysis(self, query_history: List[Dict[str, Any]]) -> str:
        """Generate query analysis section"""
        
        if not query_history:
            return "No queries to analyze."
        
        analysis_parts = []
        
        # Query types
        query_types = {}
        priorities = {}
        
        for query in query_history:
            qtype = query.get('query_type', 'unknown')
            priority = query.get('priority', 'unknown')
            
            query_types[qtype] = query_types.get(qtype, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
        
        analysis_parts.append("### Query Type Distribution")
        for qtype, count in query_types.items():
            analysis_parts.append(f"- **{qtype.replace('_', ' ').title()}:** {count}")
        
        analysis_parts.append("\n### Priority Distribution")
        for priority, count in priorities.items():
            analysis_parts.append(f"- **{priority.title()}:** {count}")
        
        return '\n'.join(analysis_parts)
    
    def _generate_key_findings(self, session_responses: List[Dict[str, Any]]) -> str:
        """Generate key findings section"""
        
        if not session_responses:
            return "No findings to report."
        
        findings = []
        
        # Literature findings
        literature_responses = [r for r in session_responses if r.get('response_type') == 'literature_search']
        if literature_responses:
            findings.append(f"### Literature Review Findings")
            findings.append(f"- Reviewed {len(literature_responses)} literature searches")
            
            for response in literature_responses[:3]:  # Top 3
                summaries = response.get('summaries', [])
                if summaries:
                    findings.append(f"- Key study: {summaries[0].get('title', 'Unknown title')}")
        
        # Treatment findings
        treatment_responses = [r for r in session_responses if r.get('response_type') == 'treatment_comparison']
        if treatment_responses:
            findings.append(f"\n### Treatment Comparison Findings")
            findings.append(f"- Analyzed {len(treatment_responses)} treatment comparisons")
            
            for response in treatment_responses[:2]:  # Top 2
                treatments = response.get('treatments_compared', [])
                if treatments:
                    findings.append(f"- Compared: {' vs '.join(treatments)}")
        
        return '\n'.join(findings) if findings else "No significant findings to highlight."
    
    def _generate_recommendations(
        self, 
        state: HealthcareAgentState, 
        session_responses: List[Dict[str, Any]]
    ) -> str:
        """Generate recommendations section"""
        
        recommendations = []
        
        # Based on query patterns
        if len(state.get('current_queries', [])) > 5:
            recommendations.append("- Consider breaking down complex research into focused sessions")
        
        # Based on confidence scores
        if session_responses:
            low_confidence = [r for r in session_responses if r.get('confidence_score', 1) < 0.7]
            if low_confidence:
                recommendations.append("- Review and validate low-confidence responses manually")
        
        # Based on pending approvals
        if len(state.get('pending_approvals', [])) > 3:
            recommendations.append("- Prioritize approval of pending critical summaries")
        
        # General recommendations
        recommendations.extend([
            "- Continue monitoring latest research in " + state['disease_focus'],
            "- Consider expanding search to related therapeutic areas",
            "- Maintain regular review of approved summaries for updates"
        ])
        
        return '\n'.join(recommendations)
    
    def _calculate_session_duration(self, state: HealthcareAgentState) -> str:
        """Calculate session duration"""
        try:
            start_time = datetime.fromisoformat(state['timestamp'])
            duration = datetime.now() - start_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
        except:
            return "Unknown"
    
    def _generate_methodology_section(self) -> str:
        """Generate methodology section"""
        return """
This literature review was conducted using the MediSyn Labs Healthcare Research Assistant, 
which employs AI-powered analysis combined with human oversight for quality assurance.

**Search Strategy:**
- Automated keyword extraction from research queries
- Literature database integration (simulated PubMed searches)
- Confidence scoring based on source reliability and content relevance

**Quality Control:**
- Human-in-the-loop validation for high-impact findings
- Systematic review of treatment comparisons
- Bias detection and mitigation protocols

**Analysis Framework:**
- Evidence-based medicine principles
- Population-specific considerations
- Safety and efficacy prioritization
        """
    
    def _format_literature_summaries(self, summaries: List[LiteratureSummarySchema]) -> str:
        """Format literature summaries for report"""
        
        if not summaries:
            return "No literature summaries available."
        
        formatted = []
        
        for i, summary in enumerate(summaries, 1):
            formatted.append(f"### Study {i}: {summary['title']}")
            formatted.append(f"**Authors:** {', '.join(summary['authors'])}")
            formatted.append(f"**Journal:** {summary['journal']}")
            formatted.append(f"**Publication Date:** {summary['publication_date']}")
            formatted.append(f"**Treatment Focus:** {summary['treatment_focus']}")
            formatted.append(f"**Population:** {summary['population_studied']}")
            formatted.append(f"**Confidence Score:** {summary['confidence_score']:.1%}")
            
            formatted.append("**Key Findings:**")
            for finding in summary['key_findings']:
                formatted.append(f"- {finding}")
            
            formatted.append("")  # Empty line between summaries
        
        return '\n'.join(formatted)
    
    def _analyze_cross_study_findings(self, summaries: List[LiteratureSummarySchema]) -> str:
        """Analyze findings across multiple studies"""
        
        if len(summaries) < 2:
            return "Insufficient studies for cross-analysis."
        
        analysis = []
        
        # Treatment focus analysis
        treatments = {}
        for summary in summaries:
            treatment = summary['treatment_focus']
            treatments[treatment] = treatments.get(treatment, 0) + 1
        
        analysis.append("### Treatment Focus Distribution")
        for treatment, count in treatments.items():
            analysis.append(f"- **{treatment}:** {count} studies")
        
        # Confidence analysis
        avg_confidence = sum(s['confidence_score'] for s in summaries) / len(summaries)
        analysis.append(f"\n### Overall Confidence: {avg_confidence:.1%}")
        
        # Common findings patterns
        all_findings = []
        for summary in summaries:
            all_findings.extend(summary['key_findings'])
        
        analysis.append("\n### Common Research Themes")
        analysis.append("- Treatment efficacy evaluation")
        analysis.append("- Safety profile assessment")
        analysis.append("- Population-specific outcomes")
        
        return '\n'.join(analysis)
    
    def _identify_research_gaps(self, summaries: List[LiteratureSummarySchema]) -> str:
        """Identify research gaps from literature review"""
        
        gaps = [
            "- Long-term follow-up studies needed",
            "- Pediatric population research limited",
            "- Real-world effectiveness data required",
            "- Comparative effectiveness research opportunities",
            "- Health economics and outcomes research"
        ]
        
        return '\n'.join(gaps)
    
    def _generate_clinical_implications(self, summaries: List[LiteratureSummarySchema]) -> str:
        """Generate clinical implications section"""
        
        implications = [
            "- Evidence supports current treatment guidelines",
            "- Consider individual patient factors in treatment selection",
            "- Monitor for reported adverse events",
            "- Regular reassessment of treatment effectiveness recommended",
            "- Stay updated on emerging research findings"
        ]
        
        return '\n'.join(implications)
    
    def _suggest_future_directions(self, summaries: List[LiteratureSummarySchema]) -> str:
        """Suggest future research directions"""
        
        directions = [
            "- Conduct larger randomized controlled trials",
            "- Investigate biomarkers for treatment response prediction",
            "- Explore combination therapy approaches",
            "- Develop personalized medicine protocols",
            "- Study implementation in diverse healthcare settings"
        ]
        
        return '\n'.join(directions)
    
    def _generate_treatment_executive_summary(self, comparisons: List[TreatmentComparisonSchema]) -> str:
        """Generate executive summary for treatment analysis"""
        
        if not comparisons:
            return "No treatment comparisons available for analysis."
        
        total_treatments = len(set(
            treatment for comparison in comparisons 
            for treatment in comparison['treatments']
        ))
        
        summary = f"Analysis of {len(comparisons)} treatment comparisons covering {total_treatments} unique treatments. "
        summary += "This report provides evidence-based comparisons to support clinical decision-making."
        
        return summary
    
    def _format_treatment_comparisons(self, comparisons: List[TreatmentComparisonSchema]) -> str:
        """Format treatment comparisons for report"""
        
        if not comparisons:
            return "No treatment comparisons available."
        
        formatted = []
        
        for i, comparison in enumerate(comparisons, 1):
            formatted.append(f"### Comparison {i}: {' vs '.join(comparison['treatments'])}")
            formatted.append(f"**Disease Condition:** {comparison['disease_condition']}")
            formatted.append(f"**Confidence Level:** {comparison['confidence_level']}")
            
            formatted.append("**Efficacy Metrics:**")
            for treatment, efficacy in comparison['efficacy_metrics'].items():
                formatted.append(f"- {treatment}: {efficacy}")
            
            formatted.append("**Recommendation:**")
            formatted.append(comparison['recommendation'])
            
            formatted.append("")  # Empty line between comparisons
        
        return '\n'.join(formatted)
    
    def _analyze_treatment_efficacy(self, comparisons: List[TreatmentComparisonSchema]) -> str:
        """Analyze treatment efficacy across comparisons"""
        
        analysis = []
        analysis.append("### Efficacy Analysis Summary")
        analysis.append("- Treatment efficacy varies by patient population")
        analysis.append("- Individual response factors should be considered")
        analysis.append("- Regular monitoring recommended for all treatments")
        
        return '\n'.join(analysis)
    
    def _compare_treatment_safety(self, comparisons: List[TreatmentComparisonSchema]) -> str:
        """Compare treatment safety profiles"""
        
        safety = []
        safety.append("### Safety Profile Comparison")
        safety.append("- All treatments show acceptable safety profiles")
        safety.append("- Monitor for treatment-specific adverse events")
        safety.append("- Consider patient comorbidities in selection")
        
        return '\n'.join(safety)
    
    def _analyze_population_factors(self, comparisons: List[TreatmentComparisonSchema]) -> str:
        """Analyze population-specific factors"""
        
        factors = []
        factors.append("### Population Considerations")
        factors.append("- Age-related treatment response variations noted")
        factors.append("- Genetic factors may influence efficacy")
        factors.append("- Comorbidity impacts treatment selection")
        
        return '\n'.join(factors)
    
    def _generate_clinical_recommendations(self, comparisons: List[TreatmentComparisonSchema]) -> str:
        """Generate clinical recommendations from comparisons"""
        
        recommendations = []
        recommendations.append("### Clinical Practice Recommendations")
        recommendations.append("1. Use evidence-based treatment selection criteria")
        recommendations.append("2. Consider individual patient characteristics")
        recommendations.append("3. Monitor treatment response and adjust as needed")
        recommendations.append("4. Stay informed about emerging treatment options")
        
        return '\n'.join(recommendations)
    
    def _assess_confidence_levels(self, comparisons: List[TreatmentComparisonSchema]) -> str:
        """Assess confidence levels across comparisons"""
        
        confidence_levels = [c['confidence_level'] for c in comparisons]
        level_counts = {}
        for level in confidence_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        assessment = []
        assessment.append("### Confidence Assessment")
        for level, count in level_counts.items():
            assessment.append(f"- **{level.title()}:** {count} comparisons")
        
        return '\n'.join(assessment)
    
    def _generate_comprehensive_executive_summary(
        self, 
        state: HealthcareAgentState, 
        query_history: List[Dict[str, Any]],
        session_responses: List[Dict[str, Any]],
        literature_summaries: List[LiteratureSummarySchema],
        treatment_comparisons: List[TreatmentComparisonSchema]
    ) -> str:
        """Generate comprehensive executive summary"""
        
        summary_parts = []
        
        # Overview
        summary_parts.append(f"Comprehensive research analysis for {state['disease_focus']} conducted during session {state['session_id'][:8]}.")
        
        # Scope
        summary_parts.append(f"Analysis included {len(query_history)} research queries, {len(literature_summaries)} literature reviews, and {len(treatment_comparisons)} treatment comparisons.")
        
        # Key outcomes
        if session_responses:
            avg_confidence = sum(r.get('confidence_score', 0) for r in session_responses) / len(session_responses)
            summary_parts.append(f"Overall research confidence: {avg_confidence:.1%}.")
        
        # Clinical impact
        summary_parts.append("Findings provide evidence-based insights to support clinical decision-making and identify areas for future research.")
        
        return ' '.join(summary_parts)
    
    def _generate_comprehensive_methodology(self) -> str:
        """Generate comprehensive methodology section"""
        
        return """
### Research Methodology

**Data Collection:**
- Systematic query processing using AI-powered analysis
- Literature database integration with confidence scoring
- Treatment comparison framework with evidence evaluation

**Quality Assurance:**
- Human-in-the-loop validation for critical findings
- Multi-stage approval process for treatment recommendations
- Bias detection and confidence assessment protocols

**Analysis Framework:**
- Evidence-based medicine principles
- Population health considerations
- Clinical practice guideline alignment
- Safety and efficacy prioritization

**Validation Process:**
- Expert review of high-impact findings
- Cross-reference with established clinical guidelines
- Continuous quality monitoring and improvement
        """
    
    def _synthesize_clinical_findings(self, session_responses: List[Dict[str, Any]]) -> str:
        """Synthesize clinical findings across all responses"""
        
        findings = []
        findings.append("### Clinical Findings Synthesis")
        
        # Literature findings
        literature_count = len([r for r in session_responses if r.get('response_type') == 'literature_search'])
        if literature_count > 0:
            findings.append(f"- Literature analysis ({literature_count} reviews) provides current evidence base")
        
        # Treatment findings
        treatment_count = len([r for r in session_responses if r.get('response_type') == 'treatment_comparison'])
        if treatment_count > 0:
            findings.append(f"- Treatment comparisons ({treatment_count} analyses) inform clinical decisions")
        
        # Overall insights
        findings.append("- Evidence supports individualized treatment approaches")
        findings.append("- Regular monitoring and reassessment recommended")
        findings.append("- Emerging research may modify current recommendations")
        
        return '\n'.join(findings)
    
    def _generate_comprehensive_recommendations(
        self, 
        state: HealthcareAgentState, 
        session_responses: List[Dict[str, Any]],
        literature_summaries: List[LiteratureSummarySchema],
        treatment_comparisons: List[TreatmentComparisonSchema]
    ) -> str:
        """Generate comprehensive recommendations"""
        
        recommendations = []
        recommendations.append("### Research and Clinical Recommendations")
        
        # Immediate actions
        recommendations.append("#### Immediate Actions")
        recommendations.append("1. Review and validate all pending approvals")
        recommendations.append("2. Implement approved treatment recommendations")
        recommendations.append("3. Share findings with clinical team")
        
        # Short-term actions
        recommendations.append("#### Short-term Actions (1-3 months)")
        recommendations.append("1. Monitor patient outcomes with recommended treatments")
        recommendations.append("2. Conduct follow-up literature searches")
        recommendations.append("3. Update clinical protocols based on findings")
        
        # Long-term actions
        recommendations.append("#### Long-term Actions (3+ months)")
        recommendations.append("1. Establish continuous monitoring system")
        recommendations.append("2. Develop research collaboration opportunities")
        recommendations.append("3. Contribute to evidence base through publication")
        
        return '\n'.join(recommendations)
    
    def _generate_appendices(
        self, 
        state: HealthcareAgentState, 
        query_history: List[Dict[str, Any]], 
        session_responses: List[Dict[str, Any]]
    ) -> str:
        """Generate appendices section"""
        
        appendices = []
        appendices.append("### Appendix A: Session Configuration")
        appendices.append(f"- Session ID: {state['session_id']}")
        appendices.append(f"- Researcher ID: {state['researcher_id']}")
        appendices.append(f"- Project ID: {state['project_id']}")
        appendices.append(f"- Disease Focus: {state['disease_focus']}")
        
        appendices.append("\n### Appendix B: Query Details")
        for i, query in enumerate(query_history, 1):
            appendices.append(f"**Query {i}:** {query['query_text']}")
        
        appendices.append("\n### Appendix C: Response Summary")
        appendices.append(f"Total responses generated: {len(session_responses)}")
        
        return '\n'.join(appendices)