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
            evidence
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)


live

Jump to live
