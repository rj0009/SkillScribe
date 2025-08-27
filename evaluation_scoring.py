"""
Evaluation Generation and Scoring System
Implements FR-SKILLS-010, FR-SKILLS-011, FR-SKILLS-012 from the PRD:
- Generate structured evaluation report with weighted scores
- Weight bonus elements by impact
- Integrate with competency framework to map skills demonstrated
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import math
from datetime import datetime


class RecommendationType(Enum):
    """Final recommendation types as per PRD"""
    STRONG_HIRE = "Strong Hire"
    TECH_INTERVIEW = "Tech Interview" 
    REJECT = "Reject"


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of scoring components"""
    component_name: str
    raw_score: float
    weighted_score: float
    weight: float
    evidence_count: int
    confidence: float
    details: List[str]


@dataclass
class EvaluationReport:
    """Complete evaluation report as specified in PRD"""
    candidate_repo_url: str
    evaluation_timestamp: str
    
    # Core scores (as per PRD: 40% + 30% + 30%)
    technical_compliance_score: float  # 40%
    communication_quality_score: float  # 30%
    problem_solving_depth_score: float  # 30%
    weighted_total_score: float
    
    # Score breakdowns
    technical_breakdown: ScoreBreakdown
    communication_breakdown: ScoreBreakdown
    problem_solving_breakdown: ScoreBreakdown
    
    # Competency assessments
    competency_assessments: List[Any]  # CompetencyAssessment objects
    
    # Critical insights
    critical_strengths: List[str]
    critical_gaps: List[str]
    red_flags: List[str]
    
    # Recommendations
    final_recommendation: RecommendationType
    growth_recommendations: List[str]
    
    # Evidence trail
    evidence_summary: Dict[str, int]
    pitfall_deductions: List[Dict[str, Any]]
    bonus_points: List[Dict[str, Any]]
    
    # Metadata
    evaluation_confidence: float
    framework_coverage: float


class EvidenceScorer:
    """Scores evidence items based on type and quality"""
    
    def __init__(self):
        self.scoring_weights = {
            "existence": 0.2,      # Basic existence of required artifacts
            "correctness": 0.5,    # Implementation matches requirements
            "completeness": 0.3    # All edge cases addressed
        }
    
    def score_evidence_items(self, evidence_items: List[Any]) -> Dict[str, Any]:
        """Score all evidence items and categorize by type"""
        
        scores = {
            "existence": {"passed": 0, "total": 0, "items": []},
            "correctness": {"passed": 0, "total": 0, "items": []},
            "completeness": {"passed": 0, "total": 0, "items": []}
        }
        
        pitfall_deductions = []
        bonus_points = []
        
        for item in evidence_items:
            evidence_type = getattr(item, 'evidence_type', 'correctness')
            
            if evidence_type in scores:
                scores[evidence_type]["total"] += 1
                scores[evidence_type]["items"].append(item)
                
                if item.passed:
                    scores[evidence_type]["passed"] += 1
                
                # Check for pitfalls and bonuses
                if hasattr(item, 'requirement_id'):
                    if item.requirement_id.startswith('pitfall_') and not item.passed:
                        # Pitfall triggered
                        pitfall_deductions.append({
                            "pitfall_id": item.requirement_id,
                            "description": item.description,
                            "deduction": 15.0,  # 15% deduction as per PRD
                            "file_path": item.file_path,
                            "line_number": item.line_number
                        })
                    
                    elif item.requirement_id.startswith('bonus_') and item.passed:
                        # Bonus achieved
                        bonus_points.append({
                            "bonus_id": item.requirement_id,
                            "description": item.description,
                            "points": 5.0,  # 5% bonus as per PRD
                            "file_path": item.file_path,
                            "line_number": item.line_number
                        })
        
        return {
            "scores": scores,
            "pitfall_deductions": pitfall_deductions,
            "bonus_points": bonus_points
        }


class TechnicalComplianceScorer:
    """Scores technical compliance (40% of total score)"""
    
    def __init__(self):
        self.base_weight = 0.4
    
    def calculate_score(self, evidence_scores: Dict[str, Any], 
                       answer_key: Dict[str, Any]) -> ScoreBreakdown:
        """Calculate technical compliance score"""
        
        scores = evidence_scores["scores"]
        
        # Calculate component scores
        existence_score = self._calculate_component_score(scores["existence"])
        correctness_score = self._calculate_component_score(scores["correctness"])
        completeness_score = self._calculate_component_score(scores["completeness"])
        
        # Weight the components (existence: 20%, correctness: 50%, completeness: 30%)
        raw_score = (
            existence_score * 0.2 +
            correctness_score * 0.5 +
            completeness_score * 0.3
        )
        
        # Apply pitfall deductions
        pitfall_deduction = sum(p["deduction"] for p in evidence_scores["pitfall_deductions"])
        raw_score = max(0, raw_score - pitfall_deduction)
        
        # Apply bonus points (capped at 100)
        bonus_addition = sum(b["points"] for b in evidence_scores["bonus_points"])
        raw_score = min(100, raw_score + bonus_addition)
        
        # Calculate weighted score
        weighted_score = raw_score * self.base_weight
        
        # Generate details
        details = [
            f"Existence verification: {existence_score:.1f}% ({scores['existence']['passed']}/{scores['existence']['total']} passed)",
            f"Correctness verification: {correctness_score:.1f}% ({scores['correctness']['passed']}/{scores['correctness']['total']} passed)",
            f"Completeness verification: {completeness_score:.1f}% ({scores['completeness']['passed']}/{scores['completeness']['total']} passed)"
        ]
        
        if pitfall_deduction > 0:
            details.append(f"Pitfall deductions: -{pitfall_deduction:.1f}%")
        
        if bonus_addition > 0:
            details.append(f"Bonus points: +{bonus_addition:.1f}%")
        
        # Calculate confidence based on evidence quality
        total_evidence = sum(s["total"] for s in scores.values())
        confidence = min(total_evidence / 10.0, 1.0)  # Normalize to 0-1
        
        return ScoreBreakdown(
            component_name="Technical Compliance",
            raw_score=raw_score,
            weighted_score=weighted_score,
            weight=self.base_weight,
            evidence_count=total_evidence,
            confidence=confidence,
            details=details
        )
    
    def _calculate_component_score(self, component_data: Dict[str, Any]) -> float:
        """Calculate score for a component (existence/correctness/completeness)"""
        if component_data["total"] == 0:
            return 0.0
        
        return (component_data["passed"] / component_data["total"]) * 100


class CommunicationQualityScorer:
    """Scores communication quality (30% of total score)"""
    
    def __init__(self):
        self.base_weight = 0.3
    
    def calculate_score(self, evidence_scores: Dict[str, Any],
                       repo_analysis: Dict[str, Any],
                       stakeholder_profile: Dict[str, Any]) -> ScoreBreakdown:
        """Calculate communication quality score"""
        
        # Base score from evidence
        base_score = self._calculate_base_communication_score(evidence_scores, repo_analysis)
        
        # Adjust for stakeholder alignment
        stakeholder_adjustment = self._calculate_stakeholder_alignment(
            repo_analysis, stakeholder_profile
        )
        
        # Visualization quality assessment
        viz_score = self._assess_visualization_quality(repo_analysis)
        
        # Documentation quality assessment
        doc_score = self._assess_documentation_quality(repo_analysis)
        
        # Combine scores
        raw_score = (
            base_score * 0.4 +
            stakeholder_adjustment * 0.3 +
            viz_score * 0.2 +
            doc_score * 0.1
        )
        
        weighted_score = raw_score * self.base_weight
        
        details = [
            f"Evidence-based communication score: {base_score:.1f}%",
            f"Stakeholder alignment: {stakeholder_adjustment:.1f}%",
            f"Visualization quality: {viz_score:.1f}%",
            f"Documentation quality: {doc_score:.1f}%"
        ]
        
        # Calculate confidence
        viz_count = self._count_visualizations(repo_analysis)
        doc_count = len(repo_analysis.get("documentation", []))
        confidence = min((viz_count + doc_count) / 5.0, 1.0)
        
        return ScoreBreakdown(
            component_name="Communication Quality",
            raw_score=raw_score,
            weighted_score=weighted_score,
            weight=self.base_weight,
            evidence_count=viz_count + doc_count,
            confidence=confidence,
            details=details
        )
    
    def _calculate_base_communication_score(self, evidence_scores: Dict[str, Any],
                                          repo_analysis: Dict[str, Any]) -> float:
        """Calculate base communication score from evidence"""
        
        # Look for communication-related evidence
        comm_evidence = []
        
        for evidence_type in evidence_scores["scores"].values():
            for item in evidence_type["items"]:
                if any(keyword in item.description.lower() 
                      for keyword in ["visualization", "chart", "plot", "communication", "audience"]):
                    comm_evidence.append(item)
        
        if not comm_evidence:
            return 50.0  # Default score if no communication evidence
        
        passed_count = sum(1 for item in comm_evidence if item.passed)
        return (passed_count / len(comm_evidence)) * 100
    
    def _calculate_stakeholder_alignment(self, repo_analysis: Dict[str, Any],
                                       stakeholder_profile: Dict[str, Any]) -> float:
        """Calculate stakeholder alignment score"""
        
        audience = stakeholder_profile.get("audience", "general_public")
        technical_level = stakeholder_profile.get("technical_level", "basic")
        
        # Check for appropriate complexity level
        has_technical_jargon = self._detect_technical_jargon(repo_analysis)
        has_clear_explanations = self._detect_clear_explanations(repo_analysis)
        
        if audience == "general_public":
            if has_technical_jargon and not has_clear_explanations:
                return 30.0  # Poor alignment - too technical
            elif not has_technical_jargon and has_clear_explanations:
                return 90.0  # Good alignment - appropriate for public
            else:
                return 60.0  # Moderate alignment
        else:
            # Technical audience
            if has_technical_jargon:
                return 80.0  # Good for technical audience
            else:
                return 60.0  # May be too simplified
    
    def _assess_visualization_quality(self, repo_analysis: Dict[str, Any]) -> float:
        """Assess quality of visualizations"""
        
        viz_count = self._count_visualizations(repo_analysis)
        
        if viz_count == 0:
            return 20.0  # Low score for no visualizations
        elif viz_count >= 3:
            return 85.0  # Good variety of visualizations
        else:
            return 60.0  # Some visualizations present
    
    def _assess_documentation_quality(self, repo_analysis: Dict[str, Any]) -> float:
        """Assess quality of documentation"""
        
        docs = repo_analysis.get("documentation", [])
        
        if not docs:
            return 30.0  # Low score for no documentation
        
        # Check for README
        has_readme = any("readme" in doc["path"].lower() for doc in docs)
        
        if has_readme:
            return 80.0  # Good documentation
        else:
            return 60.0  # Some documentation
    
    def _count_visualizations(self, repo_analysis: Dict[str, Any]) -> int:
        """Count visualization calls in the repository"""
        
        viz_count = 0
        
        for code_analysis in repo_analysis.get("detailed_analysis", {}).get("code_analysis", []):
            viz_count += len(code_analysis.get("visualization_calls", []))
        
        for nb_analysis in repo_analysis.get("detailed_analysis", {}).get("notebook_analysis", []):
            if nb_analysis.get("has_visualizations"):
                viz_count += 1
        
        return viz_count
    
    def _detect_technical_jargon(self, repo_analysis: Dict[str, Any]) -> bool:
        """Detect presence of technical jargon"""
        
        jargon_keywords = [
            "p-value", "coefficient", "residual", "heteroskedasticity",
            "autocorrelation", "stationarity", "multicollinearity"
        ]
        
        # Check in documentation
        for doc in repo_analysis.get("documentation", []):
            # This is simplified - in practice we'd read the actual content
            if any(keyword in doc.get("path", "").lower() for keyword in jargon_keywords):
                return True
        
        return False
    
    def _detect_clear_explanations(self, repo_analysis: Dict[str, Any]) -> bool:
        """Detect presence of clear explanations"""
        
        explanation_indicators = [
            "explanation", "summary", "conclusion", "interpretation",
            "what this means", "in simple terms"
        ]
        
        # Check for markdown cells in notebooks
        for nb_analysis in repo_analysis.get("detailed_analysis", {}).get("notebook_analysis", []):
            if nb_analysis.get("markdown_cells", 0) > 2:
                return True
        
        return len(repo_analysis.get("documentation", [])) > 0


class ProblemSolvingDepthScorer:
    """Scores problem solving depth (30% of total score)"""
    
    def __init__(self):
        self.base_weight = 0.3
    
    def calculate_score(self, evidence_scores: Dict[str, Any],
                       repo_analysis: Dict[str, Any],
                       problem_elements: Dict[str, Any]) -> ScoreBreakdown:
        """Calculate problem solving depth score"""
        
        # Hidden dimension coverage
        hidden_dim_score = self._assess_hidden_dimension_coverage(
            repo_analysis, problem_elements
        )
        
        # Innovation and creativity
        innovation_score = self._assess_innovation_level(repo_analysis, evidence_scores)
        
        # Methodological sophistication
        method_score = self._assess_methodological_sophistication(repo_analysis)
        
        # Edge case handling
        edge_case_score = self._assess_edge_case_handling(evidence_scores)
        
        # Combine scores
        raw_score = (
            hidden_dim_score * 0.3 +
            innovation_score * 0.3 +
            method_score * 0.25 +
            edge_case_score * 0.15
        )
        
        weighted_score = raw_score * self.base_weight
        
        details = [
            f"Hidden dimension coverage: {hidden_dim_score:.1f}%",
            f"Innovation and creativity: {innovation_score:.1f}%",
            f"Methodological sophistication: {method_score:.1f}%",
            f"Edge case handling: {edge_case_score:.1f}%"
        ]
        
        # Calculate confidence
        method_count = self._count_statistical_methods(repo_analysis)
        confidence = min(method_count / 5.0, 1.0)
        
        return ScoreBreakdown(
            component_name="Problem Solving Depth",
            raw_score=raw_score,
            weighted_score=weighted_score,
            weight=self.base_weight,
            evidence_count=method_count,
            confidence=confidence,
            details=details
        )
    
    def _assess_hidden_dimension_coverage(self, repo_analysis: Dict[str, Any],
                                        problem_elements: Dict[str, Any]) -> float:
        """Assess coverage of hidden problem dimensions"""
        
        hidden_dimensions = problem_elements.get("hidden_dimensions", [])
        
        if not hidden_dimensions:
            return 70.0  # Neutral score if no hidden dimensions specified
        
        covered_dimensions = 0
        
        # Check for evidence of addressing each hidden dimension
        for dimension in hidden_dimensions:
            if self._dimension_addressed_in_repo(dimension, repo_analysis):
                covered_dimensions += 1
        
        if len(hidden_dimensions) == 0:
            return 70.0
        
        coverage_ratio = covered_dimensions / len(hidden_dimensions)
        return coverage_ratio * 100
    
    def _assess_innovation_level(self, repo_analysis: Dict[str, Any],
                               evidence_scores: Dict[str, Any]) -> float:
        """Assess innovation and creativity in approach"""
        
        # Check for bonus points achieved (indicates innovation)
        bonus_count = len(evidence_scores.get("bonus_points", []))
        
        if bonus_count >= 2:
            return 90.0  # High innovation
        elif bonus_count == 1:
            return 70.0  # Some innovation
        
        # Check for advanced statistical methods
        advanced_methods = self._count_advanced_methods(repo_analysis)
        
        if advanced_methods >= 3:
            return 80.0
        elif advanced_methods >= 1:
            return 60.0
        else:
            return 40.0
    
    def _assess_methodological_sophistication(self, repo_analysis: Dict[str, Any]) -> float:
        """Assess sophistication of statistical/analytical methods"""
        
        method_count = self._count_statistical_methods(repo_analysis)
        advanced_count = self._count_advanced_methods(repo_analysis)
        
        base_score = min(method_count * 15, 60)  # Up to 60% for basic methods
        advanced_bonus = min(advanced_count * 20, 40)  # Up to 40% bonus for advanced
        
        return min(base_score + advanced_bonus, 100)
    
    def _assess_edge_case_handling(self, evidence_scores: Dict[str, Any]) -> float:
        """Assess handling of edge cases and robustness"""
        
        completeness_items = evidence_scores["scores"]["completeness"]["items"]
        
        if not completeness_items:
            return 50.0  # Default if no completeness evidence
        
        edge_case_items = [
            item for item in completeness_items 
            if any(keyword in item.description.lower() 
                  for keyword in ["edge case", "robustness", "validation", "error handling"])
        ]
        
        if not edge_case_items:
            return 40.0  # Low score if no edge case handling
        
        passed_count = sum(1 for item in edge_case_items if item.passed)
        return (passed_count / len(edge_case_items)) * 100
    
    def _dimension_addressed_in_repo(self, dimension: str, repo_analysis: Dict[str, Any]) -> bool:
        """Check if a hidden dimension is addressed in the repository"""
        
        dimension_lower = dimension.lower()
        
        # Check in code analysis
        for code_analysis in repo_analysis.get("detailed_analysis", {}).get("code_analysis", []):
            if any(dimension_lower in var.lower() 
                  for var in code_analysis.get("variables", [])):
                return True
            
            if any(dimension_lower in func.lower() 
                  for func in code_analysis.get("functions", [])):
                return True
        
        # Check in notebook analysis
        for nb_analysis in repo_analysis.get("detailed_analysis", {}).get("notebook_analysis", []):
            # This is simplified - in practice we'd analyze notebook content
            if dimension_lower in str(nb_analysis).lower():
                return True
        
        return False
    
    def _count_statistical_methods(self, repo_analysis: Dict[str, Any]) -> int:
        """Count statistical methods used"""
        
        method_keywords = [
            "regression", "correlation", "ttest", "anova", "chi2",
            "mean", "median", "std", "var", "describe"
        ]
        
        method_count = 0
        
        for code_analysis in repo_analysis.get("detailed_analysis", {}).get("code_analysis", []):
            for keyword in method_keywords:
                if keyword in str(code_analysis.get("imports", [])).lower():
                    method_count += 1
                if keyword in str(code_analysis.get("function_calls", [])).lower():
                    method_count += 1
        
        return method_count
    
    def _count_advanced_methods(self, repo_analysis: Dict[str, Any]) -> int:
        """Count advanced statistical methods used"""
        
        advanced_keywords = [
            "arima", "sarima", "prophet", "lstm", "machine learning",
            "random forest", "gradient boost", "neural network",
            "clustering", "dimensionality reduction", "pca"
        ]
        
        advanced_count = 0
        
        for code_analysis in repo_analysis.get("detailed_analysis", {}).get("code_analysis", []):
            for keyword in advanced_keywords:
                if keyword in str(code_analysis.get("imports", [])).lower():
                    advanced_count += 1
                if keyword in str(code_analysis.get("function_calls", [])).lower():
                    advanced_count += 1
        
        return advanced_count


class EvaluationGenerator:
    """Main class for generating complete evaluation reports"""
    
    def __init__(self):
        self.evidence_scorer = EvidenceScorer()
        self.technical_scorer = TechnicalComplianceScorer()
        self.communication_scorer = CommunicationQualityScorer()
        self.problem_solving_scorer = ProblemSolvingDepthScorer()
    
    def generate_evaluation(self, 
                          candidate_repo_url: str,
                          evidence_items: List[Any],
                          repo_analysis: Dict[str, Any],
                          answer_key: Dict[str, Any],
                          problem_elements: Dict[str, Any],
                          stakeholder_profile: Dict[str, Any],
                          competency_assessments: List[Any] = None) -> EvaluationReport:
        """Generate complete evaluation report"""
        
        # Score all evidence items
        evidence_scores = self.evidence_scorer.score_evidence_items(evidence_items)
        
        # Calculate component scores
        technical_breakdown = self.technical_scorer.calculate_score(
            evidence_scores, answer_key
        )
        
        communication_breakdown = self.communication_scorer.calculate_score(
            evidence_scores, repo_analysis, stakeholder_profile
        )
        
        problem_solving_breakdown = self.problem_solving_scorer.calculate_score(
            evidence_scores, repo_analysis, problem_elements
        )
        
        # Calculate overall weighted score
        weighted_total_score = (
            technical_breakdown.weighted_score +
            communication_breakdown.weighted_score +
            problem_solving_breakdown.weighted_score
        )
        
        # Generate insights and recommendations
        critical_strengths, critical_gaps, red_flags = self._generate_insights(
            technical_breakdown, communication_breakdown, problem_solving_breakdown,
            evidence_scores
        )
        
        final_recommendation = self._determine_final_recommendation(
            weighted_total_score, red_flags, evidence_scores
        )
        
        growth_recommendations = self._generate_growth_recommendations(
            critical_gaps, competency_assessments or []
        )
        
        # Calculate metadata
        evaluation_confidence = self._calculate_evaluation_confidence(
            technical_breakdown, communication_breakdown, problem_solving_breakdown
        )
        
        framework_coverage = self._calculate_framework_coverage(
            competency_assessments or []
        )
        
        # Generate evidence summary
        evidence_summary = {
            "existence_checks": evidence_scores["scores"]["existence"]["total"],
            "correctness_checks": evidence_scores["scores"]["correctness"]["total"],
            "completeness_checks": evidence_scores["scores"]["completeness"]["total"],
            "pitfalls_triggered": len(evidence_scores["pitfall_deductions"]),
            "bonuses_achieved": len(evidence_scores["bonus_points"])
        }
        
        return EvaluationReport(
            candidate_repo_url=candidate_repo_url,
            evaluation_timestamp=datetime.now().isoformat(),
            technical_compliance_score=technical_breakdown.raw_score,
            communication_quality_score=communication_breakdown.raw_score,
            problem_solving_depth_score=problem_solving_breakdown.raw_score,
            weighted_total_score=weighted_total_score,
            technical_breakdown=technical_breakdown,
            communication_breakdown=communication_breakdown,
            problem_solving_breakdown=problem_solving_breakdown,
            competency_assessments=competency_assessments or [],
            critical_strengths=critical_strengths,
            critical_gaps=critical_gaps,
            red_flags=red_flags,
            final_recommendation=final_recommendation,
            growth_recommendations=growth_recommendations,
            evidence_summary=evidence_summary,
            pitfall_deductions=evidence_scores["pitfall_deductions"],
            bonus_points=evidence_scores["bonus_points"],
            evaluation_confidence=evaluation_confidence,
            framework_coverage=framework_coverage
        )
    
    def _generate_insights(self, technical: ScoreBreakdown, 
                          communication: ScoreBreakdown,
                          problem_solving: ScoreBreakdown,
                          evidence_scores: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
        """Generate critical strengths, gaps, and red flags"""
        
        strengths = []
        gaps = []
        red_flags = []
        
        # Analyze technical strengths/gaps
        if technical.raw_score >= 80:
            strengths.append("Strong technical implementation with high compliance")
        elif technical.raw_score < 50:
            gaps.append("Technical implementation needs significant improvement")
        
        # Analyze communication strengths/gaps
        if communication.raw_score >= 80:
            strengths.append("Excellent communication and presentation skills")
        elif communication.raw_score < 50:
            gaps.append("Communication and documentation need improvement")
        
        # Analyze problem solving strengths/gaps
        if problem_solving.raw_score >= 80:
            strengths.append("Demonstrates deep analytical thinking and innovation")
        elif problem_solving.raw_score < 50:
            gaps.append("Limited depth in problem-solving approach")
        
        # Check for red flags
        pitfall_count = len(evidence_scores["pitfall_deductions"])
        if pitfall_count >= 3:
            red_flags.append(f"Multiple critical errors detected ({pitfall_count} pitfalls)")
        
        if technical.raw_score < 30:
            red_flags.append("Extremely low technical compliance score")
        
        return strengths, gaps, red_flags
    
    def _determine_final_recommendation(self, total_score: float,
                                      red_flags: List[str],
                                      evidence_scores: Dict[str, Any]) -> RecommendationType:
        """Determine final hiring recommendation"""
        
        # Automatic reject if critical red flags
        if len(red_flags) >= 2:
            return RecommendationType.REJECT
        
        # Score-based recommendations
        if total_score >= 70:
            return RecommendationType.STRONG_HIRE
        elif total_score >= 50:
            return RecommendationType.TECH_INTERVIEW
        else:
            return RecommendationType.REJECT
    
    def _generate_growth_recommendations(self, gaps: List[str],
                                       competency_assessments: List[Any]) -> List[str]:
        """Generate growth and development recommendations"""
        
        recommendations = []
        
        for gap in gaps:
            if "technical" in gap.lower():
                recommendations.append("Focus on strengthening core technical skills and implementation practices")
            elif "communication" in gap.lower():
                recommendations.append("Develop documentation and visualization skills for better stakeholder communication")
            elif "problem" in gap.lower():
                recommendations.append("Practice advanced analytical techniques and creative problem-solving approaches")
        
        # Add competency-specific recommendations
        for assessment in competency_assessments:
            if hasattr(assessment, 'level') and assessment.level < 2:
                recommendations.append(f"Strengthen {assessment.competency_name} skills to reach intermediate level")
        
        return recommendations
    
    def _calculate_evaluation_confidence(self, technical: ScoreBreakdown,
                                       communication: ScoreBreakdown,
                                       problem_solving: ScoreBreakdown) -> float:
        """Calculate overall confidence in the evaluation"""
        
        confidence_scores = [
            technical.confidence,
            communication.confidence,
            problem_solving.confidence
        ]
        
        return sum(confidence_scores) / len(confidence_scores)
    
    def _calculate_framework_coverage(self, competency_assessments: List[Any]) -> float:
        """Calculate coverage of competency framework"""
        
        if not competency_assessments:
            return 0.0
        
        # This is simplified - in practice would check against full framework
        return min(len(competency_assessments) / 10.0, 1.0)
