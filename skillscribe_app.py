"""
Enhanced SkillScribe Streamlit Application
Integrates all MVP components for real candidate evaluations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime
import os
import sys

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
from evaluation_engine import SkillScribeEngine
from github_analyzer import EnhancedGitHubAnalyzer
from evidence_verification import AnswerKeyProcessor, EnhancedEvidenceVerifier
from competency_framework import CompetencyFrameworkLoader, CompetencyProfileGenerator
from evaluation_scoring import EvaluationGenerator


# Configure Streamlit page
st.set_page_config(
    page_title="SkillScribe MVP",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        margin: 0.5rem 0;
    }
    
    .success-card {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    
    .warning-card {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
    
    .danger-card {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    
    .evidence-item {
        background-color: #f1f3f4;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
        border-left: 3px solid #6c757d;
    }
    
    .evidence-pass {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    
    .evidence-fail {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
</style>
""", unsafe_allow_html=True)


class SkillScribeApp:
    """Main SkillScribe Streamlit application"""
    
    def __init__(self):
        self.initialize_session_state()
        self.load_components()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'evaluation_results' not in st.session_state:
            st.session_state.evaluation_results = None
        if 'evaluation_history' not in st.session_state:
            st.session_state.evaluation_history = []
        if 'current_repo_url' not in st.session_state:
            st.session_state.current_repo_url = ""
    
    def load_components(self):
        """Load SkillScribe components"""
        try:
            # Initialize core components
            self.engine = SkillScribeEngine()
            self.github_analyzer = EnhancedGitHubAnalyzer()
            self.answer_key_processor = AnswerKeyProcessor()
            self.evidence_verifier = EnhancedEvidenceVerifier()
            self.framework_loader = CompetencyFrameworkLoader()
            self.evaluation_generator = EvaluationGenerator()
            
            # Load competency framework
            self.competency_framework = self.framework_loader.create_sample_framework()
            self.profile_generator = CompetencyProfileGenerator(self.competency_framework)
            
        except Exception as e:
            st.error(f"Error loading SkillScribe components: {str(e)}")
    
    def render_header(self):
        """Render application header"""
        st.markdown('<div class="main-header">🎯 SkillScribe: AI-Powered Technical Assessment Engine</div>', 
                   unsafe_allow_html=True)
        
        st.markdown("""
        **Welcome to SkillScribe MVP** - Automated technical evaluation of GitHub repositories 
        against problem-specific rubrics and competency frameworks.
        
        *Based on GovTech AI Practice Product Requirements Document*
        """)
    
    def render_sidebar(self):
        """Render sidebar with configuration options"""
        st.sidebar.header("⚙️ Configuration")
        
        # Answer key configuration
        st.sidebar.subheader("Answer Key")
        use_custom_answer_key = st.sidebar.checkbox("Use custom answer key", value=False)
        
        if use_custom_answer_key:
            uploaded_file = st.sidebar.file_uploader(
                "Upload Excel answer key", 
                type=['xlsx', 'xls'],
                help="Upload Excel file with columns: problem_statement, look_out_for, pitfalls, bonus"
            )
            if uploaded_file:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Load answer key
                try:
                    answer_key = self.answer_key_processor.load_answer_key_from_excel(temp_path)
                    st.sidebar.success("✅ Custom answer key loaded")
                except Exception as e:
                    st.sidebar.error(f"❌ Error loading answer key: {str(e)}")
        else:
            # Use sample answer key
            answer_key = self.answer_key_processor.create_sample_answer_key()
            st.sidebar.info("📋 Using sample HDB case answer key")
        
        # Evaluation settings
        st.sidebar.subheader("Evaluation Settings")
        
        evaluation_mode = st.sidebar.selectbox(
            "Evaluation Mode",
            ["Standard", "Detailed", "Quick"],
            index=0,
            help="Standard: Full evaluation, Detailed: Extra analysis, Quick: Basic assessment"
        )
        
        show_evidence_details = st.sidebar.checkbox("Show detailed evidence", value=True)
        show_competency_breakdown = st.sidebar.checkbox("Show competency breakdown", value=True)
        
        # Evaluation history
        if st.session_state.evaluation_history:
            st.sidebar.subheader("📊 Evaluation History")
            for i, eval_data in enumerate(st.session_state.evaluation_history[-5:]):  # Show last 5
                repo_name = eval_data['repo_url'].split('/')[-1] if '/' in eval_data['repo_url'] else eval_data['repo_url']
                score = eval_data['weighted_score']
                recommendation = eval_data['recommendation']
                
                color = "🟢" if recommendation == "Strong Hire" else "🟡" if recommendation == "Tech Interview" else "🔴"
                st.sidebar.write(f"{color} {repo_name}: {score:.1f}%")
        
        return {
            'answer_key': answer_key,
            'evaluation_mode': evaluation_mode,
            'show_evidence_details': show_evidence_details,
            'show_competency_breakdown': show_competency_breakdown
        }
    
    def render_input_section(self):
        """Render candidate input section"""
        st.markdown('<div class="section-header">📝 Candidate Submission</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            repo_url = st.text_input(
                "GitHub Repository URL",
                value=st.session_state.current_repo_url,
                placeholder="https://github.com/username/repository",
                help="Enter the GitHub repository URL for evaluation"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            evaluate_button = st.button("🚀 Run Evaluation", type="primary", use_container_width=True)
        
        # Sample repositories for testing
        st.markdown("**Sample repositories for testing:**")
        sample_repos = [
            "https://github.com/chuawjk/hdb_resale_portal",
            "https://github.com/microsoft/vscode",
            "https://github.com/pandas-dev/pandas"
        ]
        
        cols = st.columns(len(sample_repos))
        for i, sample_repo in enumerate(sample_repos):
            with cols[i]:
                if st.button(f"📂 {sample_repo.split('/')[-1]}", key=f"sample_{i}"):
                    st.session_state.current_repo_url = sample_repo
                    st.rerun()
        
        return repo_url, evaluate_button
    
    def run_evaluation(self, repo_url: str, config: dict):
        """Run the complete evaluation process"""
        
        # Validation
        if not repo_url or not repo_url.startswith('http'):
            st.error("❌ Please enter a valid GitHub repository URL")
            return None
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Download and analyze repository
            status_text.text("📥 Downloading repository...")
            progress_bar.progress(10)
            
            repo_path = self.github_analyzer.download_repository(repo_url)
            if not repo_path:
                st.error("❌ Failed to download repository. Please check the URL and try again.")
                return None
            
            # Step 2: Analyze repository structure
            status_text.text("🔍 Analyzing repository structure...")
            progress_bar.progress(25)
            
            repo_analysis = self.github_analyzer.analyze_repository_comprehensive(repo_path)
            
            # Step 3: Problem deconstruction
            status_text.text("🧩 Deconstructing problem requirements...")
            progress_bar.progress(40)
            
            problem_elements = self.engine.problem_deconstruction.extract_core_elements(
                config['answer_key']['problem_statement']
            )
            
            # Step 4: Evidence verification
            status_text.text("🔬 Verifying evidence...")
            progress_bar.progress(55)
            
            evidence_items = self.evidence_verifier.verify_repository(
                repo_analysis, 
                self.answer_key_processor.verification_rules
            )
            
            # Step 5: Competency assessment
            status_text.text("📊 Assessing competencies...")
            progress_bar.progress(70)
            
            competency_profile = self.profile_generator.generate_profile(
                repo_url, repo_analysis, evidence_items
            )
            
            # Step 6: Generate evaluation
            status_text.text("📋 Generating evaluation report...")
            progress_bar.progress(85)
            
            evaluation_report = self.evaluation_generator.generate_evaluation(
                repo_url, repo_analysis, evidence_items, 
                config['answer_key'], problem_elements, competency_profile
            )
            
            # Step 7: Finalize
            status_text.text("✅ Evaluation complete!")
            progress_bar.progress(100)
            
            # Store results
            st.session_state.evaluation_results = {
                'report': evaluation_report,
                'repo_analysis': repo_analysis,
                'evidence_items': evidence_items,
                'competency_profile': competency_profile,
                'problem_elements': problem_elements
            }
            
            # Add to history
            st.session_state.evaluation_history.append({
                'repo_url': repo_url,
                'timestamp': datetime.now().isoformat(),
                'weighted_score': evaluation_report.weighted_total_score,
                'recommendation': evaluation_report.final_recommendation.value
            })
            
            # Cleanup
            self.github_analyzer.cleanup()
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            return evaluation_report
            
        except Exception as e:
            st.error(f"❌ Evaluation failed: {str(e)}")
            progress_bar.empty()
            status_text.empty()
            return None
    
    def render_evaluation_results(self, config: dict):
        """Render evaluation results"""
        
        if not st.session_state.evaluation_results:
            st.info("👆 Enter a GitHub repository URL above and click 'Run Evaluation' to get started.")
            return
        
        results = st.session_state.evaluation_results
        report = results['report']
        
        # Main results header
        st.markdown('<div class="section-header">📊 Evaluation Results</div>', unsafe_allow_html=True)
        
        # Key metrics
        self.render_key_metrics(report)
        
        # Detailed breakdowns
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_score_breakdown(report)
            if config['show_competency_breakdown']:
                self.render_competency_assessment(results['competency_profile'])
        
        with col2:
            self.render_insights_and_recommendations(report)
            if config['show_evidence_details']:
                self.render_evidence_details(results['evidence_items'])
        
        # Additional sections
        self.render_repository_analysis(results['repo_analysis'])
        
        # Export options
        self.render_export_options(report)
    
    def render_key_metrics(self, report):
        """Render key evaluation metrics"""
        
        # Recommendation badge
        rec_color = {
            "Strong Hire": "success",
            "Tech Interview": "warning", 
            "Reject": "error"
        }
        
        rec_emoji = {
            "Strong Hire": "🟢",
            "Tech Interview": "🟡",
            "Reject": "🔴"
        }
        
        recommendation = report.final_recommendation.value
        
        # Main metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Overall Score",
                f"{report.weighted_total_score:.1f}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "Technical Compliance",
                f"{report.technical_compliance_score:.1f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                "Communication Quality", 
                f"{report.communication_quality_score:.1f}%",
                delta=None
            )
        
        with col4:
            st.metric(
                "Problem Solving Depth",
                f"{report.problem_solving_depth_score:.1f}%",
                delta=None
            )
        
        with col5:
            st.markdown(f"""
            <div class="metric-card {rec_color.get(recommendation, 'warning')}-card">
                <h3>{rec_emoji.get(recommendation, '🟡')} {recommendation}</h3>
                <p>Confidence: {report.evaluation_confidence:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_score_breakdown(self, report):
        """Render detailed score breakdown with visualizations"""
        
        st.subheader("📈 Score Breakdown")
        
        # Create score breakdown chart
        categories = ['Technical\nCompliance', 'Communication\nQuality', 'Problem Solving\nDepth']
        scores = [
            report.technical_compliance_score,
            report.communication_quality_score, 
            report.problem_solving_depth_score
        ]
        weights = [40, 30, 30]  # As per PRD
        
        fig = go.Figure()
        
        # Add bars for scores
        fig.add_trace(go.Bar(
            x=categories,
            y=scores,
            name='Score',
            marker_color=['#3498db', '#2ecc71', '#e74c3c'],
            text=[f'{score:.1f}%' for score in scores],
            textposition='auto'
        ))
        
        # Add weight annotations
        for i, (cat, weight) in enumerate(zip(categories, weights)):
            fig.ad
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)


live
