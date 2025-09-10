
import React from 'react';
import type { JobPosting, Candidate, Assessment } from '../types';
import { Vote, CandidateStatus } from '../types';
import { generateAssessorReview, generateFeedbackReport } from '../services/geminiService';
import { LoadingSpinner } from './icons/LoadingSpinner';
import Modal from './Modal';
import { DocumentTextIcon } from './icons/DocumentTextIcon';

interface AssessmentViewProps {
  candidate: Candidate;
  job: JobPosting;
  updateAssessment: (candidateId: string, assessment: Assessment) => void;
  updateCandidateStatus: (candidateId: string, status: CandidateStatus) => void;
}

const AssessorCard: React.FC<{
    assessment: Assessment;
    isLead: boolean;
    onUpdate: (assessment: Assessment) => void;
    jobTitle: string;
    automatedEvaluation: string | null;
}> = ({ assessment, isLead, onUpdate, jobTitle, automatedEvaluation }) => {
    const [review, setReview] = React.useState(assessment.review);
    const [isGenerating, setIsGenerating] = React.useState(false);
    
    const handleVote = (vote: Vote) => {
        onUpdate({ ...assessment, vote, review });
    };

    const handleReviewChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setReview(e.target.value);
    }
    
    const handleSaveReview = () => {
        // Only update if review has changed
        if (review !== assessment.review) {
            onUpdate({ ...assessment, review });
        }
    }
    
    const handleGenerateReview = async () => {
        if (assessment.vote === Vote.PENDING) {
            alert("Please select a vote before generating a review.");
            return;
        }
        setIsGenerating(true);
        try {
            const generatedReview = await generateAssessorReview(automatedEvaluation, assessment.vote, jobTitle);
            setReview(generatedReview);
            // also call onUpdate to save it immediately
            onUpdate({ ...assessment, vote: assessment.vote, review: generatedReview });
        } catch (error) {
            console.error("Failed to generate review", error);
        } finally {
            setIsGenerating(false);
        }
    };

    const voteColor = (vote: Vote) => {
        switch(vote) {
            case Vote.ACCEPT: return 'border-green-500 bg-green-50';
            case Vote.REJECT: return 'border-red-500 bg-red-50';
            case Vote.DEFER: return 'border-yellow-500 bg-yellow-50';
            default: return 'border-gray-300 bg-base-100';
        }
    };
    
    return (
        <div className={`p-4 rounded-lg border-2 ${voteColor(assessment.vote)}`}>
            <div className="flex items-center justify-between">
                <h4 className="font-bold text-text-primary">{assessment.assessorName} {isLead && <span className="text-xs font-semibold ml-2 bg-accent text-gray-800 px-2 py-0.5 rounded-full">Lead</span>}</h4>
                <div className="flex items-center space-x-2">
                    {Object.values(Vote).filter(v => v !== Vote.PENDING).map(vote => (
                        <button key={vote} onClick={() => handleVote(vote)} className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${assessment.vote === vote ? 'text-white' : 'text-gray-600'} ${vote === Vote.ACCEPT ? 'bg-green-500 hover:bg-green-600' : ''} ${vote === Vote.REJECT ? 'bg-red-500 hover:bg-red-600' : ''} ${vote === Vote.DEFER ? 'bg-yellow-500 hover:bg-yellow-600' : ''} ${assessment.vote !== vote ? 'bg-gray-200 hover:bg-gray-300' : ''}`}>{vote}</button>
                    ))}
                </div>
            </div>
            <div className="mt-4">
                <div className="flex justify-between items-center mb-2">
                     <label htmlFor={`review-${assessment.assessorId}`} className="block text-sm font-medium text-text-secondary">Assessor's Review</label>
                    <button
                        onClick={handleGenerateReview}
                        disabled={isGenerating || assessment.vote === Vote.PENDING}
                        className="flex items-center text-xs bg-secondary text-white font-bold py-1 px-2 rounded-md hover:bg-primary disabled:bg-gray-400 transition-colors"
                    >
                        {isGenerating ? <LoadingSpinner className="h-4 w-4 mr-1"/> : '✨'}
                        {isGenerating ? 'Generating...' : 'Generate with AI'}
                    </button>
                </div>
                <textarea 
                    id={`review-${assessment.assessorId}`}
                    value={review}
                    onChange={handleReviewChange}
                    onBlur={handleSaveReview}
                    rows={4}
                    placeholder="Write your review here or generate one with AI."
                    className="w-full p-2 border border-gray-300 rounded-md text-sm text-text-primary bg-base-100"
                />
            </div>
        </div>
    );
};

const AssessmentView: React.FC<AssessmentViewProps> = ({ candidate, job, updateAssessment, updateCandidateStatus }) => {
    const [isReportModalOpen, setIsReportModalOpen] = React.useState(false);
    const [reportContent, setReportContent] = React.useState('');
    const [isGeneratingReport, setIsGeneratingReport] = React.useState(false);
    const [reportType, setReportType] = React.useState<'preliminary' | 'final'>('preliminary');

    const handleUpdate = (assessment: Assessment) => {
        updateAssessment(candidate.id, assessment);
    }

    const handleGenerateReport = async (type: 'preliminary' | 'final') => {
        setReportType(type);
        setIsReportModalOpen(true);
        setIsGeneratingReport(true);
        setReportContent(''); // Clear previous content
        try {
            const report = await generateFeedbackReport(candidate, job, type);
            setReportContent(report);
        } catch (error) {
            console.error("Failed to generate report", error);
            setReportContent("Sorry, an error occurred while generating the report.");
        } finally {
            setIsGeneratingReport(false);
        }
    };

    const allVotesIn = candidate.assessments.every(a => a.vote !== Vote.PENDING);
    
    const renderFinalDecision = () => {
        if (!allVotesIn) {
            return (
                <div className="p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700 rounded-r-lg">
                    <p className="font-bold">Pending Final Decision</p>
                    <p>All assessors must submit their votes before a final decision can be made.</p>
                </div>
            );
        }
        
        if (candidate.status !== CandidateStatus.ACCEPTED && candidate.status !== CandidateStatus.REJECTED) {
             return (
                <div className="p-6 bg-base-100 rounded-lg shadow-md">
                    <h3 className="text-xl font-bold text-text-primary">Final Decision</h3>
                    <p className="text-text-secondary mt-2">All votes are in. The lead assessor or Victor can now make the final decision.</p>
                    <div className="mt-4 flex space-x-4">
                        <button onClick={() => updateCandidateStatus(candidate.id, CandidateStatus.ACCEPTED)} className="bg-green-500 text-white font-bold py-2 px-6 rounded-lg hover:bg-green-600 transition-colors">Accept for Interview</button>
                        <button onClick={() => updateCandidateStatus(candidate.id, CandidateStatus.REJECTED)} className="bg-red-500 text-white font-bold py-2 px-6 rounded-lg hover:bg-red-600 transition-colors">Reject Candidate</button>
                    </div>
                </div>
            );
        } else {
             return (
                <div className={`p-6 rounded-lg ${candidate.status === CandidateStatus.ACCEPTED ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                     <div className="flex justify-between items-start">
                        <div>
                            <p className="font-bold text-lg">Decision: {candidate.status === CandidateStatus.ACCEPTED ? "Accepted for Interview" : "Rejected"}</p>
                            <p>HR will be notified to schedule the next steps or inform the candidate.</p>
                        </div>
                        <button
                            onClick={() => handleGenerateReport('final')}
                            className="flex-shrink-0 flex items-center bg-white border border-current text-current text-sm font-semibold py-2 px-3 rounded-lg hover:bg-white/80 transition-colors duration-300 shadow-sm"
                        >
                            <DocumentTextIcon className="h-5 w-5 mr-2" />
                            Generate Final Report
                        </button>
                    </div>
                </div>
             );
        }
    }

    return (
        <div className="max-w-7xl mx-auto animate-fade-in grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column: Candidate Info & AI Eval */}
            <div className="lg:col-span-1 space-y-6">
                 <div className="bg-base-100 p-6 rounded-lg shadow-md">
                    <h3 className="text-2xl font-bold">{candidate.name}</h3>
                    <p className="text-text-secondary">{candidate.email}</p>
                    <p className="text-text-secondary">{job.title}</p>
                     {candidate.githubLink && <a href={candidate.githubLink} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline mt-2 block break-all">{candidate.githubLink}</a>}
                </div>
                <div className="bg-base-100 p-6 rounded-lg shadow-md">
                    <h3 className="text-xl font-bold mb-4 text-text-primary">Automated AI Evaluation</h3>
                    <div className="prose prose-sm max-w-none text-text-secondary whitespace-pre-wrap font-mono text-xs bg-base-200 p-4 rounded-md">
                        {candidate.automatedEvaluation ? <p>{candidate.automatedEvaluation}</p> : <p>No evaluation available.</p>}
                    </div>
                </div>
            </div>

            {/* Right Column: Assessments */}
            <div className="lg:col-span-2 space-y-6">
                <div className="bg-base-100 p-6 rounded-lg shadow-md">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-xl font-bold">Assessor Reviews</h3>
                        {(candidate.status === CandidateStatus.ASSESSMENT || candidate.status === CandidateStatus.FINAL_REVIEW) && (
                             <button
                                onClick={() => handleGenerateReport('preliminary')}
                                className="flex items-center bg-white border border-base-300 text-text-secondary text-sm font-semibold py-2 px-3 rounded-lg hover:bg-base-200 transition-colors duration-300 shadow-sm"
                            >
                                <DocumentTextIcon className="h-5 w-5 mr-2" />
                                Preliminary Report
                            </button>
                        )}
                    </div>
                     <div className="space-y-4">
                        {candidate.assessments.map(assessment => (
                            <AssessorCard 
                                key={assessment.assessorId}
                                assessment={assessment}
                                isLead={candidate.assessors.find(a => a.id === assessment.assessorId)?.isLead || false}
                                onUpdate={handleUpdate}
                                jobTitle={job.title}
                                automatedEvaluation={candidate.automatedEvaluation}
                            />
                        ))}
                    </div>
                </div>
                {renderFinalDecision()}
            </div>
            <Modal 
                isOpen={isReportModalOpen} 
                onClose={() => setIsReportModalOpen(false)} 
                title={`${reportType === 'preliminary' ? 'Preliminary' : 'Final'} Feedback Report`}
            >
                {isGeneratingReport ? (
                    <div className="flex justify-center items-center h-48">
                        <LoadingSpinner className="h-8 w-8 text-primary"/>
                        <p className="ml-4 text-text-secondary">Generating report...</p>
                    </div>
                ) : (
                    <div>
                        <div 
                          className="prose max-w-none text-text-secondary bg-base-200 p-4 rounded-md max-h-[60vh] overflow-y-auto"
                          dangerouslySetInnerHTML={{ __html: reportContent.replace(/\n/g, '<br />') }}
                        >
                        </div>
                        <div className="flex justify-end mt-6">
                            <button
                              onClick={() => navigator.clipboard.writeText(reportContent.replace(/<br \/>/g, '\n').replace(/#+\s/g, ''))}
                              className="bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm"
                            >
                                Copy to Clipboard
                            </button>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
};

export default AssessmentView;