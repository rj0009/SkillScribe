import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import time
import re
from dataclasses import asdict

# Import our evaluation system (assuming evaluation_scoring.py is in the same directory)
try:
    from evaluation_scoring import (
        EvaluationGenerator, 
        RecommendationType, 
        EvaluationReport,
        ScoreBreakdown
    )
except ImportError:
    st.error("Please ensure evaluation_scoring.py is in the same directory")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="SkillScribe - AI-Powered Technical Assessment",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #1f77b4;
}

.success-card {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #28a745;
}

.warning-card {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #ffc107;
}

.danger-card {
    background-color: #f8d7da;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #dc3545;
}

.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)


class MockEvidenceItem:
    """Mock evidence item for demonstration"""
    def __init__(self, requirement_id: str, description: str, passed: bool, 
                 evidence_type: str = "correctness", file_path: str = "", line_number: int = 0):
        self.requirement_id = requirement_id
        self.description = description
        self.passed = passed
        self.evidence_type = evidence_type
        self.file_path = file_path
        self.line_number = line_number


def init_session_state():
    """Initialize session state variables"""
    if 'evaluations' not in st.session_state:
        st.session_state.evaluations = []
    
    if 'current_evaluation' not in st.session_state:
        st.session_state.current_evaluation = None
    
    if 'answer_keys' not in st.session_state:
        st.session_state.answer_keys = {}


def load_sample_data():
    """Load sample data for demonstration"""
    
    # Sample answer key for HDB case study
    sample_answer_key = {
        "problem_statement": "Using relevant data from 2017 onwards, quantify the business impact on agents of the HDB resale portal launch",
        "look_out_for": [
            "Clearly distinguishes between impact of portal on buyers' and sellers' reliance on property agents",
            "Uses appropriate statistical methods for time series analysis",
            "Provides clear visualization of trends before and after portal launch"
        ],
        "pitfalls": [
            "Sweeping conclusions using 'total' instead of ratio or percentages",
            "Ignoring seasonal patterns in real estate data",
            "Not accounting for other market factors affecting agent usage"
        ],
        "bonus": [
            "Further slicing by HDB towns - Are transactions in some areas more affected than others?",
            "Advanced statistical modeling (ARIMA, interrupted time series)",
            "Creative visualization showing impact magnitude"
        ]
    }
    
    # Sample stakeholder profile
    sample_stakeholder_profile = {
        "audience": "general_public",
        "technical_level": "basic",
        "decision_makers": ["HDB management", "Policy makers"],
        "communication_weight": 0.3
    }
    
    # Sample problem elements
    sample_problem_elements = {
        "hidden_dimensions": ["Buyer reliance", "Seller reliance", "Geographic variation"],
        "temporal_factors": ["Seasonality", "Market cycles", "Policy changes"],
        "complexity_level": "intermediate"
    }
    
    return sample_answer_key, sample_stakeholder_profile, sample_problem_elements


def create_sample_evidence_items(repo_url: str) -> List[MockEvidenceItem]:
    """Create sample evidence items for demonstration"""
    
    evidence_items = [
        # Existence checks
        MockEvidenceItem("existence_data_loading", "Data files are properly loaded", True, "existence", "data_loader.py", 15),
        MockEvidenceItem("existence_analysis_notebook", "Analysis notebook exists", True, "existence", "analysis.ipynb", 1),
        MockEvidenceItem("existence_visualization", "Visualization code exists", True, "existence", "visualizations.py", 45),
        
        # Correctness checks
        MockEvidenceItem("correctness_buyer_seller_split", "Correctly separates buyer and seller transactions", True, "correctness", "analysis.py", 128),
        MockEvidenceItem("correctness_time_series", "Proper time series analysis implementation", True, "correctness", "analysis.py", 245),
        MockEvidenceItem("correctness_statistical_test", "Appropriate statistical tests applied", False, "correctness", "analysis.py", 312),
        
        # Completeness checks
        MockEvidenceItem("completeness_edge_cases", "Handles edge cases and missing data", True, "completeness", "data_cleaning.py", 89),
        MockEvidenceItem("completeness_validation", "Includes result validation", False, "completeness", "validation.py", 23),
        
        # Pitfalls
        MockEvidenceItem("pitfall_absolute_numbers", "Uses ratios instead of absolute numbers", False, "correctness", "analysis.py", 187),
        
        # Bonuses
        MockEvidenceItem("bonus_geographic_analysis", "Geographic breakdown by HDB towns", True, "correctness", "geographic_analysis.py", 67),
    ]
    
    return evidence_items


def mock_github_analysis(repo_url: str) -> Dict[str, Any]:
    """Mock GitHub repository analysis"""
    
    return {
        "repository_info": {
            "name": repo_url.split("/")[-1],
            "url": repo_url,
            "files_analyzed": 12,
            "total_lines": 2847
        },
        "detailed_analysis": {
            "code_analysis": [
                {
                    "file_path": "analysis.py",
                    "imports": ["pandas", "numpy", "matplotlib", "seaborn", "scipy.stats"],
                    "functions": ["load_data", "clean_data", "analyze_trends", "statistical_test"],
                    "variables": ["buyer_data", "seller_data", "portal_launch_date", "trend_analysis"],
                    "visualization_calls": ["plt.plot", "sns.barplot", "plt.histogram"],
                    "function_calls": ["ttest_ind", "pearsonr", "describe"]
                }
            ],
            "notebook_analysis": [
                {
                    "file_path": "analysis.ipynb",
                    "markdown_cells": 8,
                    "code_cells": 15,
                    "has_visualizations": True,
                    "output_quality": "good"
                }
            ]
        },
        "documentation": [
            {"path": "README.md", "exists": True},
            {"path": "requirements.txt", "exists": True}
        ],
        "quality_metrics": {
            "code_complexity": "medium",
            "documentation_coverage": 0.7,
            "test_coverage": 0.3
        }
    }


def display_evaluation_form():
    """Display the main evaluation form"""
    
    st.header("🎯 New Technical Assessment")
    
    with st.form("evaluation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Basic Information")
            candidate_name = st.text_input("Candidate Name")
            repo_url = st.text_input(
                "GitHub Repository URL",
                placeholder="https://github.com/username/repository",
                help="Enter the candidate's GitHub repository URL for analysis"
            )
            position = st.selectbox(
                "Position Applied For",
                ["Data Scientist", "Software Engineer", "ML Engineer", "DevOps Engineer", "Other"]
            )
        
        with col2:
            st.subheader("🎨 Assessment Configuration")
            case_study = st.selectbox(
                "Case Study Type",
                ["HDB Resale Portal Impact", "COE Bidding Analysis", "Traffic Pattern Analysis", "Custom"]
            )
            
            stakeholder_audience = st.selectbox(
                "Target Audience",
                ["General Public", "Technical Team", "Senior Management", "Policy Makers"]
            )
            
            priority_weights = st.slider(
                "Communication Weight (%)",
                min_value=10,
                max_value=50,
                value=30,
                help="Adjust based on role requirements"
            )
        
        # Advanced settings in expandable section
        with st.expander("🔧 Advanced Settings"):
            st.subheader("Evaluation Criteria")
            
            col3, col4 = st.columns(2)
            with col3:
                technical_weight = st.slider("Technical Compliance Weight", 30, 60, 40)
                enable_pitfall_deductions = st.checkbox("Enable Pitfall Deductions", value=True)
                
            with col4:
                problem_solving_weight = st.slider("Problem Solving Weight", 20, 40, 30)
                enable_bonus_points = st.checkbox("Enable Bonus Points", value=True)
            
            # Ensure weights sum to 100
            comm_weight = 100 - technical_weight - problem_solving_weight
            st.info(f"Calculated weights: Technical ({technical_weight}%), Communication ({comm_weight}%), Problem Solving ({problem_solving_weight}%)")
        
        submitted = st.form_submit_button("🚀 Start Evaluation", type="primary")
        
        if submitted:
            if not repo_url or not candidate_name:
                st.error("Please fill in all required fields")
                return
            
            if not repo_url.startswith("https://github.com/"):
                st.error("Please enter a valid GitHub repository URL")
                return
            
            # Start the evaluation process
            start_evaluation(candidate_name, repo_url, case_study, stakeholder_audience)


def start_evaluation(candidate_name: str, repo_url: str, case_study: str, audience: str):
    """Start the evaluation process"""
    
    st.success(f"✅ Starting evaluation for {candidate_name}")
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Repository Analysis
    status_text.text("🔍 Step 1/4: Analyzing GitHub repository...")
    progress_bar.progress(25)
    time.sleep(1)  # Simulate processing time
    
    repo_analysis = mock_github_analysis(repo_url)
    
    # Step 2: Evidence Collection
    status_text.text("📊 Step 2/4: Collecting evidence items...")
    progress_bar.progress(50)
    time.sleep(1)
    
    evidence_items = create_sample_evidence_items(repo_url)
    
    # Step 3: Load Configuration
    status_text.text("⚙️ Step 3/4: Loading assessment configuration...")
    progress_bar.progress(75)
    time.sleep(1)
    
    answer_key, stakeholder_profile, problem_elements = load_sample_data()
    
    # Adjust stakeholder profile based on user input
    stakeholder_profile["audience"] = audience.lower().replace(" ", "_")
    
    # Step 4: Generate Evaluation
    status_text.text("🎯 Step 4/4: Generating evaluation report...")
    progress_bar.progress(100)
    time.sleep(1)
    
    # Generate the evaluation
    evaluator = EvaluationGenerator()
    evaluation_report = evaluator.generate_evaluation(
        candidate_repo_url=repo_url,
        evidence_items=evidence_items,
        repo_analysis=repo_analysis,
        answer_key=answer_key,
        problem_elements=problem_elements,
        stakeholder_profile=stakeholder_profile
    )
    
    # Add metadata
    evaluation_report.candidate_name = candidate_name
    evaluation_report.case_study = case_study
    evaluation_report.position = getattr(st.session_state, 'position', 'Data Scientist')
    
    # Store in session state
    st.session_state.current_evaluation = evaluation_report
    st.session_state.evaluations.append(evaluation_report)
    
    status_text.text("✅ Evaluation completed successfully!")
    time.sleep(1)
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    st.success("🎉 Evaluation completed! View results below.")
    st.rerun()


def display_evaluation_results():
    """Display the evaluation results"""
    
    if not st.session_state.current_evaluation:
        st.info("No evaluation results to display. Please run an assessment first.")
        return
    
    evaluation = st.session_state.current_evaluation
    
    st.header("📈 Evaluation Results")
    
    # Overall Score Display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Overall Score</h3>
            <h1>{evaluation.weighted_total_score:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        recommendation_color = {
            RecommendationType.STRONG_HIRE: "success",
            RecommendationType.TECH_INTERVIEW: "warning", 
            RecommendationType.REJECT: "danger"
        }
        color = recommendation_color.get(evaluation.final_recommendation, "info")
        
        st.markdown(f"""
        <div class="{color}-card">
            <h3>Recommendation</h3>
            <h2>{evaluation.final_recommendation.value}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        confidence_color = "success" if evaluation.evaluation_confidence > 0.7 else "warning"
        st.markdown(f"""
        <div class="{confidence_color}-card">
            <h3>Confidence</h3>
            <h2>{evaluation.evaluation_confidence*100:.0f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Evidence Items</h3>
            <h2>{sum(evaluation.evidence_summary.values())}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed Results in Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Score Breakdown", 
        "🔍 Evidence Analysis", 
        "💡 Insights & Recommendations", 
        "📋 Competency Framework",
        "📄 Full Report"
    ])
    
    with tab1:
        display_score_breakdown(evaluation)
    
    with tab2:
        display_evidence_analysis(evaluation)
    
    with tab3:
        display_insights_recommendations(evaluation)
    
    with tab4:
        display_competency_framework(evaluation)
    
    with tab5:
        display_full_report(evaluation)


def display_score_breakdown(evaluation: EvaluationReport):
    """Display detailed score breakdown"""
    
    st.subheader("📊 Score Breakdown Analysis")
    
    # Create score visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Overall Scores", "Component Breakdown", "Evidence Summary", "Confidence Levels"),
        specs=[[{"type": "indicator"}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Overall score gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=evaluation.weighted_total_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=1, col=1
    )
    
    # Component scores
    components = ['Technical Compliance', 'Communication Quality', 'Problem Solving']
    scores = [
        evaluation.technical_compliance_score,
        evaluation.communication_quality_score,
        evaluation.problem_solving_depth_score
    ]
    weights = [40, 30, 30]
    
    fig.add_trace(
        go.Bar(
            x=components,
            y=scores,
            text=[f"{score:.1f}% (Weight: {weight}%)" for score, weight in zip(scores, weights)],
            textposition='auto',
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
        ),
        row=1, col=2
    )
    
    # Evidence summary pie chart
    evidence_labels = list(evaluation.evidence_summary.keys())
    evidence_values = list(evaluation.evidence_summary.values())
    
    fig.add_trace(
        go.Pie(
            labels=evidence_labels,
            values=evidence_values,
            hole=0.3
        ),
        row=2, col=1
    )
    
    # Confidence levels
    confidence_data = [
        evaluation.technical_breakdown.confidence,
        evaluation.communication_breakdown.confidence,
        evaluation.problem_solving_breakdown.confidence,
        evaluation.evaluation_confidence
    ]
    confidence_labels = ['Technical', 'Communication', 'Problem Solving', 'Overall']
    
    fig.add_trace(
        go.Bar(
            x=confidence_labels,
            y=[c*100 for c in confidence_data],
            text=[f"{c*100:.1f}%" for c in confidence_data],
            textposition='auto',
            marker_color='orange'
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown table
    st.subheader("Detailed Score Components")
    
    breakdown_data = []
    for breakdown in [evaluation.technical_breakdown, evaluation.communication_breakdown, evaluation.problem_solving_breakdown]:
        breakdown_data.append({
            "Component": breakdown.component_name,
            "Raw Score": f"{breakdown.raw_score:.1f}%",
            "Weight": f"{breakdown.weight*100:.0f}%",
            "Weighted Score": f"{breakdown.weighted_score:.1f}",
            "Evidence Count": breakdown.evidence_count,
            "Confidence": f"{breakdown.confidence*100:.1f}%"
        })
    
    df = pd.DataFrame(breakdown_data)
    st.dataframe(df, use_container_width=True)


def display_evidence_analysis(evaluation: EvaluationReport):
    """Display evidence analysis"""
    
    st.subheader("🔍 Evidence Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Pitfalls & Deductions")
        if evaluation.pitfall_deductions:
            for pitfall in evaluation.pitfall_deductions:
                st.markdown(f"""
                <div class="danger-card">
                    <strong>⚠️ {pitfall['description']}</strong><br>
                    <small>Deduction: -{pitfall['deduction']}% | File: {pitfall['file_path']}:{pitfall.get('line_number', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
        else:
            st.success("No critical pitfalls detected!")
    
    with col2:
        st.markdown("### 🌟 Bonus Achievements")
        if evaluation.bonus_points:
            for bonus in evaluation.bonus_points:
                st.markdown(f"""
                <div class="success-card">
                    <strong>🎯 {bonus['description']}</strong><br>
                    <small>Bonus: +{bonus['points']}% | File: {bonus['file_path']}:{bonus.get('line_number', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
        else:
            st.info("No bonus achievements identified")
    
    # Evidence summary
    st.markdown("### 📊 Evidence Summary")
    
    evidence_df = pd.DataFrame([
        {"Type": "Existence Checks", "Count": evaluation.evidence_summary.get("existence_checks", 0)},
        {"Type": "Correctness Checks", "Count": evaluation.evidence_summary.get("correctness_checks", 0)},
        {"Type": "Completeness Checks", "Count": evaluation.evidence_summary.get("completeness_checks", 0)},
        {"Type": "Pitfalls Triggered", "Count": evaluation.evidence_summary.get("pitfalls_triggered", 0)},
        {"Type": "Bonuses Achieved", "Count": evaluation.evidence_summary.get("bonuses_achieved", 0)}
    ])
    
    fig = px.bar(evidence_df, x="Type", y="Count", 
                title="Evidence Item Distribution",
                color="Count",
                color_continuous_scale="viridis")
    
    st.plotly_chart(fig, use_container_width=True)


def display_insights_recommendations(evaluation: EvaluationReport):
    """Display insights and recommendations"""
    
    st.subheader("💡 Critical Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💪 Critical Strengths")
        if evaluation.critical_strengths:
            for strength in evaluation.critical_strengths:
                st.markdown(f"""
                <div class="success-card">
                    <strong>✅ {strength}</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
        else:
            st.info("No specific strengths identified")
    
    with col2:
        st.markdown("### 🎯 Areas for Growth")
        if evaluation.critical_gaps:
            for gap in evaluation.critical_gaps:
                st.markdown(f"""
                <div class="warning-card">
                    <strong>📈 {gap}</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
        else:
            st.success("No significant gaps identified")
    
    with col3:
        st.markdown("### 🚨 Red Flags")
        if evaluation.red_flags:
            for flag in evaluation.red_flags:
                st.markdown(f"""
                <div class="danger-card">
                    <strong>🚨 {flag}</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
        else:
            st.success("No red flags detected")
    
    # Growth recommendations
    st.markdown("### 🌱 Growth Recommendations")
    
    if evaluation.growth_recommendations:
        for i, rec in enumerate(evaluation.growth_recommendations, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.info("No specific growth recommendations at this time")


def display_competency_framework(evaluation: EvaluationReport):
    """Display competency framework analysis"""
    
    st.subheader("📋 Competency Framework Assessment")
    
    if evaluation.competency_assessments:
        # Create competency visualization
        competencies = []
        levels = []
        
        for assessment in evaluation.competency_assessments:
            competencies.append(assessment.competency_name)
            levels.append(assessment.level)
        
        fig = px.bar(
            x=competencies,
            y=levels,
            title="Competency Level Assessment",
            labels={"x": "Competency", "y": "Level (1-4)"},
            color=levels,
            color_continuous_scale="RdYlGn"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Competency details table
        comp_data = []
        for assessment in evaluation.competency_assessments:
            comp_data.append({
                "Competency": assessment.competency_name,
                "Current Level": f"L{assessment.level}",
                "Evidence Count": assessment.evidence_count,
                "Confidence": f"{assessment.confidence*100:.1f}%"
            })
        
        df = pd.DataFrame(comp_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Competency framework assessment not available for this evaluation")
    
    # Framework coverage
    st.metric(
        "Framework Coverage",
        f"{evaluation.framework_coverage*100:.1f}%",
        help="Percentage of competency framework covered by this assessment"
    )


def display_full_report(evaluation: EvaluationReport):
    """Display the full evaluation report"""
    
    st.subheader("📄 Complete Evaluation Report")
    
    # Report header
    st.markdown(f"""
    **Candidate:** {getattr(evaluation, 'candidate_name', 'N/A')}  
    **Repository:** {evaluation.candidate_repo_url}  
    **Evaluation Date:** {evaluation.evaluation_timestamp}  
    **Case Study:** {getattr(evaluation, 'case_study', 'N/A')}  
    **Position:** {getattr(evaluation, 'position', 'N/A')}
    """)
    
    st.markdown("---")
    
    # Executive Summary
    st.markdown("### Executive Summary")
    st.markdown(f"""
    The candidate achieved an overall weighted score of **{evaluation.weighted_total_score:.1f}%** 
    with a recommendation of **{evaluation.final_recommendation.value}**. 
    The evaluation confidence is **{evaluation.evaluation_confidence*100:.1f}%** based on 
    {sum(evaluation.evidence_summary.values())} evidence items analyzed.
    """)
    
    # Score breakdown
    st.markdown("### Score Breakdown")
    st.markdown(f"""
    - **Technical Compliance:** {evaluation.technical_compliance_score:.1f}% (Weight: 40%)
    - **Communication Quality:** {evaluation.communication_quality_score:.1f}% (Weight: 30%)
    - **Problem Solving Depth:** {evaluation.problem_solving_depth_score:.1f}% (Weight: 30%)
    """)
    
    # Technical breakdown details
    st.markdown("### Technical Analysis Details")
    for detail in evaluation.technical_breakdown.details:
        st.markdown(f"- {detail}")
    
    # Communication breakdown details
    st.markdown("### Communication Analysis Details")
    for detail in evaluation.communication_breakdown.details:
        st.markdown(f"- {detail}")
    
    # Problem solving breakdown details
    st.markdown("### Problem Solving Analysis Details")
    for detail in evaluation.problem_solving_breakdown.details:
        st.markdown(f"- {detail}")
    
    # Export option
    if st.button("📥 Export Report as JSON"):
        report_dict = asdict(evaluation)
        json_str = json.dumps(report_dict, indent=2, default=str)
        st.download_button(
            label="Download JSON Report",
            data=json_str,
            file_name=f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def display_history():
    """Display evaluation history"""
    
    st.header("📚 Evaluation History")
    
    if not st.session_state.evaluations:
        st.info("No evaluations completed yet. Run an assessment to see results here.")
        return
    
    # Summary statistics
    total_evaluations = len(st.session_state.evaluations)
    avg_score = sum(e.weighted_total_score for e in st.session_state.evaluations) / total_evaluations
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Evaluations", total_evaluations)
    col2.metric("Average Score", f"{avg_score:.1f}%")
    col3.metric("Strong Hires", sum(1 for e in st.session_state.evaluations if e.final_recommendation == RecommendationType.STRONG_HIRE))
    
    # Evaluation list
    st.subheader("Recent Evaluations")
    
    for i, evaluation in enumerate(reversed(st.session_state.evaluations)):
        with st.expander(f"Evaluation #{total_evaluations-i} - {getattr(evaluation, 'candidate_name', 'Unknown')} ({evaluation.weighted_total_score:.1f}%)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Repository:** {evaluation.candidate_repo_url}  
                **Score:** {evaluation.weighted_total_score:.1f}%  
                **Recommendation:** {evaluation.final_recommendation.value}  
                **Date:** {evaluation.evaluation_timestamp[:10]}
                """)
            
            with col2:
                if st.button(f"View Details", key=f"view_{i}"):
                    st.session_state.current_evaluation = evaluation
                    st.rerun()


def main():
    """Main application function"""
    
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🎯 SkillScribe")
    st.sidebar.markdown("*AI-Powered Technical Assessment Engine*")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Navigation",
        ["🏠 Home", "🎯 New Assessment", "📊 View Results", "📚 History", "⚙️ Configuration"]
    )
    
    # Add current evaluation info in sidebar if available
    if st.session_state.current_evaluation:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Current Evaluation")
        evaluation = st.session_state.current_evaluation
        st.sidebar.markdown(f"""
        **Candidate:** {getattr(evaluation, 'candidate_name', 'N/A')}  
        **Score:** {evaluation.weighted_total_score:.1f}%  
        **Recommendation:** {evaluation.final_recommendation.value}
        """)
        
        if st.sidebar.button("🗑️ Clear Current"):
            st.session_state.current_evaluation = None
            st.rerun()
    
    # Statistics in sidebar
    if st.session_state.evaluations:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Quick Stats")
        total_evals = len(st.session_state.evaluations)
        avg_score = sum(e.weighted_total_score for e in st.session_state.evaluations) / total_evals
        strong_hires = sum(1 for e in st.session_state.evaluations if e.final_recommendation == RecommendationType.STRONG_HIRE)
        
        st.sidebar.metric("Total Evaluations", total_evals)
        st.sidebar.metric("Average Score", f"{avg_score:.1f}%")
        st.sidebar.metric("Strong Hires", f"{strong_hires}/{total_evals}")
    
    # Main content area
    if page == "🏠 Home":
        display_home()
    elif page == "🎯 New Assessment":
        display_evaluation_form()
    elif page == "📊 View Results":
        display_evaluation_results()
    elif page == "📚 History":
        display_history()
    elif page == "⚙️ Configuration":
        display_configuration()


def display_home():
    """Display the home page"""
    
    st.title("🎯 SkillScribe")
    st.markdown("### AI-Powered Technical Assessment Engine")
    
    st.markdown("""
    Welcome to **SkillScribe**, GovTech's advanced technical assessment platform. 
    This system automates the evaluation of GitHub repositories against specific rubrics 
    and answer keys, reducing evaluation time from 45+ minutes to under 5 minutes per candidate.
    """)
    
    # Key features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Lightning Fast</h3>
            <p>Reduce evaluation time from 45+ minutes to under 5 minutes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Evidence-Based</h3>
            <p>3-layer verification: Existence → Correctness → Completeness</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🧠 Human-in-Loop</h3>
            <p>AI generates insights, humans make final decisions</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting started section
    st.markdown("### 🚀 Getting Started")
    
    with st.container():
        st.markdown("""
        1. **📋 Configure Assessment** - Set up your case study and evaluation criteria
        2. **🔗 Input Repository** - Provide the candidate's GitHub repository URL
        3. **🤖 AI Analysis** - Our engine analyzes the code, documentation, and approach
        4. **📊 Review Results** - Get detailed scoring with evidence trails
        5. **✅ Make Decision** - Use AI insights to make informed hiring decisions
        """)
    
    # Recent activity
    if st.session_state.evaluations:
        st.markdown("### 📈 Recent Activity")
        
        # Create timeline chart of recent evaluations
        recent_evals = st.session_state.evaluations[-10:]  # Last 10 evaluations
        
        eval_data = []
        for i, eval in enumerate(recent_evals):
            eval_data.append({
                "Evaluation": f"#{i+1}",
                "Score": eval.weighted_total_score,
                "Recommendation": eval.final_recommendation.value,
                "Date": eval.evaluation_timestamp[:10]
            })
        
        if eval_data:
            df = pd.DataFrame(eval_data)
            
            fig = px.bar(
                df, 
                x="Evaluation", 
                y="Score",
                color="Recommendation",
                title="Recent Evaluation Scores",
                color_discrete_map={
                    "Strong Hire": "#28a745",
                    "Tech Interview": "#ffc107", 
                    "Reject": "#dc3545"
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎯 Start New Assessment", type="primary"):
            st.session_state.page = "🎯 New Assessment"
            st.rerun()
    
    with col2:
        if st.button("📊 View Latest Results") and st.session_state.current_evaluation:
            st.session_state.page = "📊 View Results"
            st.rerun()
    
    with col3:
        if st.button("📚 Browse History"):
            st.session_state.page = "📚 History"
            st.rerun()
    
    with col4:
        if st.button("⚙️ Configuration"):
            st.session_state.page = "⚙️ Configuration"
            st.rerun()


def display_configuration():
    """Display configuration settings"""
    
    st.header("⚙️ System Configuration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Answer Keys", "🎯 Case Studies", "⚖️ Scoring Weights", "🔧 System Settings"])
    
    with tab1:
        st.subheader("📝 Answer Key Management")
        
        # Upload answer key
        uploaded_file = st.file_uploader(
            "Upload Answer Key (Excel format)",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with columns: problem_statement, look_out_for, pitfalls, bonus"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                st.success("Answer key uploaded successfully!")
                st.dataframe(df)
                
                # Store in session state
                case_study_name = st.text_input("Case Study Name", value="Custom Case Study")
                if st.button("Save Answer Key"):
                    st.session_state.answer_keys[case_study_name] = df.to_dict('records')
                    st.success(f"Answer key saved for '{case_study_name}'")
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # Display existing answer keys
        st.markdown("### Existing Answer Keys")
        if st.session_state.answer_keys:
            for name, data in st.session_state.answer_keys.items():
                with st.expander(f"📋 {name}"):
                    st.json(data)
        else:
            st.info("No custom answer keys configured. Upload one above to get started.")
    
    with tab2:
        st.subheader("🎯 Case Study Templates")
        
        # Predefined case studies
        case_studies = {
            "HDB Resale Portal Impact": {
                "description": "Analyze the business impact of HDB resale portal on property agents",
                "hidden_dimensions": ["Buyer reliance", "Seller reliance", "Geographic variation"],
                "stakeholder": "General Public",
                "complexity": "Intermediate"
            },
            "COE Bidding Analysis": {
                "description": "Time series analysis of Certificate of Entitlement bidding patterns",
                "hidden_dimensions": ["Category differences", "Economic cycles", "Policy impacts"],
                "stakeholder": "Policy Makers",
                "complexity": "Advanced"
            },
            "Traffic Pattern Analysis": {
                "description": "Urban traffic flow optimization using sensor data",
                "hidden_dimensions": ["Peak hour effects", "Weather impact", "Event correlation"],
                "stakeholder": "Technical Team",
                "complexity": "Intermediate"
            }
        }
        
        for name, details in case_studies.items():
            with st.expander(f"📋 {name}"):
                st.markdown(f"**Description:** {details['description']}")
                st.markdown(f"**Stakeholder:** {details['stakeholder']}")
                st.markdown(f"**Complexity:** {details['complexity']}")
                st.markdown("**Hidden Dimensions:**")
                for dim in details['hidden_dimensions']:
                    st.markdown(f"- {dim}")
    
    with tab3:
        st.subheader("⚖️ Scoring Configuration")
        
        st.markdown("### Component Weights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Default Weights:**")
            tech_weight = st.slider("Technical Compliance", 20, 60, 40)
            comm_weight = st.slider("Communication Quality", 20, 50, 30)
            prob_weight = st.slider("Problem Solving Depth", 20, 40, 30)
            
            # Ensure weights sum to 100
            total_weight = tech_weight + comm_weight + prob_weight
            if total_weight != 100:
                st.warning(f"Weights sum to {total_weight}%. Please adjust to equal 100%.")
        
        with col2:
            st.markdown("**Evidence Scoring Weights:**")
            existence_weight = st.slider("Existence Verification", 10, 30, 20)
            correctness_weight = st.slider("Correctness Verification", 40, 70, 50)
            completeness_weight = st.slider("Completeness Verification", 20, 40, 30)
            
            # Pitfall and bonus settings
            st.markdown("**Penalty/Bonus Settings:**")
            pitfall_deduction = st.slider("Pitfall Deduction (%)", 5, 25, 15)
            bonus_points = st.slider("Bonus Points (%)", 3, 10, 5)
    
    with tab4:
        st.subheader("🔧 System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### GitHub Integration")
            github_token = st.text_input("GitHub Personal Access Token", type="password", help="Optional: Increases API rate limits")
            timeout_seconds = st.number_input("Analysis Timeout (seconds)", min_value=30, max_value=300, value=120)
            
            st.markdown("### Evaluation Settings")
            confidence_threshold = st.slider("Minimum Confidence Threshold", 0.5, 1.0, 0.7)
            auto_save = st.checkbox("Auto-save evaluations", value=True)
        
        with col2:
            st.markdown("### Export Settings")
            default_format = st.selectbox("Default Export Format", ["JSON", "Excel", "PDF"])
            include_evidence = st.checkbox("Include evidence details in exports", value=True)
            
            st.markdown("### Display Preferences")
            show_confidence = st.checkbox("Show confidence scores", value=True)
            show_evidence_count = st.checkbox("Show evidence counts", value=True)
        
        if st.button("💾 Save Configuration"):
            # In a real app, this would save to a database or config file
            st.success("Configuration saved successfully!")


# Additional utility functions for the Streamlit app
def validate_github_url(url: str) -> bool:
    """Validate GitHub repository URL format"""
    github_pattern = r'^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/?
    return bool(re.match(github_pattern, url))


def format_recommendation_badge(recommendation: RecommendationType) -> str:
    """Format recommendation as colored badge"""
    colors = {
        RecommendationType.STRONG_HIRE: "🟢",
        RecommendationType.TECH_INTERVIEW: "🟡", 
        RecommendationType.REJECT: "🔴"
    }
    
    return f"{colors.get(recommendation, '⚪')} {recommendation.value}"


def create_summary_metrics():
    """Create summary metrics for dashboard"""
    if not st.session_state.evaluations:
        return
    
    evaluations = st.session_state.evaluations
    
    # Calculate metrics
    total_count = len(evaluations)
    avg_score = sum(e.weighted_total_score for e in evaluations) / total_count
    strong_hires = sum(1 for e in evaluations if e.final_recommendation == RecommendationType.STRONG_HIRE)
    tech_interviews = sum(1 for e in evaluations if e.final_recommendation == RecommendationType.TECH_INTERVIEW)
    rejects = sum(1 for e in evaluations if e.final_recommendation == RecommendationType.REJECT)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Evaluations", total_count)
    col2.metric("Average Score", f"{avg_score:.1f}%", f"{avg_score-70:.1f}%" if avg_score > 70 else None)
    col3.metric("Strong Hires", strong_hires, f"{(strong_hires/total_count)*100:.1f}%")
    col4.metric("Success Rate", f"{((strong_hires + tech_interviews)/total_count)*100:.1f}%")


if __name__ == "__main__":
    main()
