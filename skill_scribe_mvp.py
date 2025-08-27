# skills_scribe_mvp.py

import streamlit as st
import pandas as pd
import random
import time
import requests
import io

# ==============================================================================
# 1. Core Functions (Simulated Backend)
# ==============================================================================

def fetch_github_content(github_url):
    """
    Simulates fetching content from a GitHub repository.
    In a real-world scenario, this would use the GitHub API to list and fetch
    files, but for this MVP, we'll just check if the URL is valid.
    """
    if "github.com" not in github_url:
        return False
    try:
        # Construct a raw URL for a sample file. This is a simple check, not a full clone.
        test_url = github_url.replace("github.com", "raw.githubusercontent.com") + "/master/README.md"
        response = requests.get(test_url)
        # Check if the file exists and the request was successful
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def simulate_evaluation(github_url: str, answer_key_df: pd.DataFrame):
    """
    This function simulates the SkillScribe AI backend.
    
    It takes a GitHub URL and the answer key dataframe, and returns a
    plausible-looking evaluation report. The real implementation would involve
    complex LLM calls, code analysis, and evidence verification as per the PRD.
    """
    # Simulate processing time
    time.sleep(3)

    # Validate that the answer key DataFrame has the expected columns
    required_cols = ['problem_statement', 'look_out_for', 'pitfalls', 'bonus']
    if not all(col in answer_key_df.columns for col in required_cols):
        raise ValueError("Answer Key is missing one or more required columns.")

    # Get sample data from the answer key for the report
    look_out_for_items = answer_key_df['look_out_for'].dropna().tolist()
    pitfall_items = answer_key_df['pitfalls'].dropna().tolist()
    bonus_items = answer_key_df['bonus'].dropna().tolist()

    # Generate plausible, semi-random scores based on PRD ranges
    technical_score = random.randint(50, 95)
    communication_score = random.randint(60, 90)
    problem_solving_score = random.randint(55, 95)

    # Determine recommendation based on a simple score threshold
    avg_score = (technical_score + communication_score + problem_solving_score) / 3
    if avg_score >= 80:
        recommendation = "Strong Hire"
    elif avg_score >= 65:
        recommendation = "Tech Interview"
    else:
        recommendation = "Reject"
    
    # Generate a mock evidence trail and report text
    report_text = f"""
    Based on a preliminary analysis of the repository at `{github_url}`, the candidate's submission has been assessed against the provided rubric.

    **Core Strengths:**
    - The candidate successfully implemented the primary objective as defined in the problem statement.
    - Demonstrated strong problem-solving skills by addressing the hidden dimension: "{random.choice(look_out_for_items)}".
    - The code structure is clean and well-commented, indicating strong communication skills.

    **Areas for Improvement / Gaps:**
    - The code triggered a major pitfall: "{random.choice(pitfall_items)}". This resulted in a point deduction.
    - The candidate did not implement the bonus item: "{random.choice(bonus_items)}", missing an opportunity for additional credit.

    **Evidence Trail:**
    - **Passed:** Implemented core logic as expected - `analysis.py:L142`
    - **Passed:** Differentiates between core concepts - `data_processing.ipynb:L35`
    - **Pitfall Triggered:** Used absolute values without ratio normalization - `analysis.py:L187`
    - **Bonus Not Implemented:** Slicing analysis was not found.

    **Competency Profile:**
    - **Time Series Analysis:** L2 Proficiency (Demonstrates solid understanding, but not advanced techniques)
    - **Experimental Design:** L1 Foundational (Shows some knowledge, but lacks implementation)

    This is an automated evaluation. A human-in-the-loop review is required to make the final hiring decision.
    """

    return {
        "technical_score": technical_score,
        "communication_score": communication_score,
        "problem_solving_score": problem_solving_score,
        "recommendation": recommendation,
        "report_text": report_text,
    }


# ==============================================================================
# 2. Streamlit UI (Frontend)
# ==============================================================================

st.set_page_config(
    page_title="SkillScribe MVP",
    page_icon="🤖",
    layout="wide"
)

# App Title and Description
st.markdown("<h1 style='text-align: center;'>SkillScribe: AI-Powered Assessment Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Automated evaluation of candidate GitHub submissions against custom rubrics.</p>", unsafe_allow_html=True)
st.markdown("---")

# User Input Section
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1. Upload Answer Key")
    uploaded_file = st.file_uploader(
        "Upload a `.xlsx` or `.csv` file",
        type=['xlsx', 'csv'],
        help="Please use the provided template with 'problem_statement', 'look_out_for', 'pitfalls', and 'bonus' columns."
    )

with col2:
    st.markdown("### 2. Enter Candidate Submission URL")
    github_url = st.text_input(
        "GitHub Repository URL",
        placeholder="e.g., https://github.com/govtech/my-project"
    )

st.markdown("---")

# Evaluation Button
if st.button("Run Evaluation", use_container_width=True, type="primary"):
    if not uploaded_file:
        st.error("Please upload an answer key file.")
    elif not github_url:
        st.error("Please enter a GitHub repository URL.")
    elif not fetch_github_content(github_url):
        st.error("Invalid GitHub URL or repository not found. Please check the URL.")
    else:
        # Read the uploaded Excel or CSV file
        try:
            if uploaded_file.name.endswith('.xlsx'):
                answer_key_df = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                answer_key_df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()

        with st.spinner("Analyzing candidate submission... This may take a moment."):
            try:
                # Call the simulated backend function
                evaluation_report = simulate_evaluation(github_url, answer_key_df)

                # Display the results
                st.success("Evaluation Complete!")
                
                st.markdown("### Evaluation Summary")

                # Metrics
                col_scores = st.columns(3)
                with col_scores[0]:
                    st.metric("Technical Score", f"{evaluation_report['technical_score']}%")
                with col_scores[1]:
                    st.metric("Communication Score", f"{evaluation_report['communication_score']}%")
                with col_scores[2]:
                    st.metric("Problem-Solving Score", f"{evaluation_report['problem_solving_score']}%")

                # Recommendation
                if evaluation_report['recommendation'] == "Strong Hire":
                    st.balloons()
                    st.success(f"**Recommendation:** {evaluation_report['recommendation']} 🎉", icon="✅")
                elif evaluation_report['recommendation'] == "Tech Interview":
                    st.info(f"**Recommendation:** {evaluation_report['recommendation']}", icon="➡️")
                else:
                    st.error(f"**Recommendation:** {evaluation_report['recommendation']}", icon="❌")

                # Full Report in an expander
                with st.expander("View Full Evaluation Report", expanded=True):
                    st.markdown(evaluation_report['report_text'])

            except ValueError as ve:
                st.error(f"Evaluation failed: {ve}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
