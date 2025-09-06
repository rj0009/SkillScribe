
import React, { useState } from 'react';
import type { JobPosting, Candidate } from '../types';
import { CandidateStatus } from '../types';
import { PlusIcon } from './icons/PlusIcon';
import Modal from './Modal';
import CreateCandidateForm from './CreateCandidateForm';
import AddGithubLinkForm from './AddGithubLinkForm';
import { generateAutomatedEvaluation, generateInterviewQuestions } from '../services/geminiService';
import { LoadingSpinner } from './icons/LoadingSpinner';
import { QuestionMarkIcon } from './icons/QuestionMarkIcon';

interface CandidateDashboardProps {
  job: JobPosting;
  candidates: Candidate[];
  onSelectCandidate: (candidate: Candidate) => void;
  addCandidate: (candidate: Omit<Candidate, 'id' | 'appliedAt' | 'status' | 'githubLink' | 'assessors' | 'assessments' | 'automatedEvaluation'>) => void;
  updateCandidateStatus: (candidateId: string, status: CandidateStatus) => void;
  addGithubLink: (candidateId: string, githubLink: string) => void;
  updateAutomatedEvaluation: (candidateId: string, evaluation: string) => void;
}

const CandidateCard: React.FC<{
  candidate: Candidate;
  onSelect: () => void;
  onUpdateStatus: (status: CandidateStatus) => void;
  onAddGithubLink: (githubLink: string) => void;
  onEvaluate: () => Promise<void>;
}> = ({ candidate, onSelect, onUpdateStatus, onAddGithubLink, onEvaluate }) => {
    const [isEvaluating, setIsEvaluating] = useState(false);

    const handleEvaluation = async () => {
        setIsEvaluating(true);
        await onEvaluate();
        setIsEvaluating(false);
    }
    
    const statusPill = (status: CandidateStatus) => {
        const colors: Record<CandidateStatus, string> = {
            [CandidateStatus.APPLIED]: 'bg-blue-100 text-blue-800',
            [CandidateStatus.CASE_STUDY_SENT]: 'bg-yellow-100 text-yellow-800',
            [CandidateStatus.CASE_STUDY_SUBMITTED]: 'bg-purple-100 text-purple-800',
            [CandidateStatus.ASSESSMENT]: 'bg-indigo-100 text-indigo-800',
            [CandidateStatus.FINAL_REVIEW]: 'bg-pink-100 text-pink-800',
            [CandidateStatus.ACCEPTED]: 'bg-green-100 text-green-800',
            [CandidateStatus.REJECTED]: 'bg-red-100 text-red-800',
        };
        return <span className={`px-3 py-1 text-xs font-semibold rounded-full ${colors[status]}`}>{status}</span>;
    };

    const renderActions = () => {
        switch (candidate.status) {
            case CandidateStatus.APPLIED:
                return <button onClick={() => onUpdateStatus(CandidateStatus.CASE_STUDY_SENT)} className="text-sm bg-primary text-white font-bold py-1 px-3 rounded-md hover:bg-secondary">Send Case Study</button>;
            case CandidateStatus.CASE_STUDY_SENT:
                return <AddGithubLinkForm onSubmit={onAddGithubLink} />;
            case CandidateStatus.CASE_STUDY_SUBMITTED:
                return <button disabled={isEvaluating} onClick={handleEvaluation} className="text-sm bg-primary text-white font-bold py-1 px-3 rounded-md hover:bg-secondary disabled:bg-gray-400 flex items-center">{isEvaluating && <LoadingSpinner className="h-4 w-4 mr-2"/>} {isEvaluating ? 'Evaluating...' : 'Start AI Evaluation'}</button>;
            case CandidateStatus.ASSESSMENT:
            case CandidateStatus.FINAL_REVIEW:
            case CandidateStatus.ACCEPTED:
            case CandidateStatus.REJECTED:
                 return <button onClick={onSelect} className="text-sm bg-gray-200 text-gray-800 font-bold py-1 px-3 rounded-md hover:bg-gray-300">View Assessment</button>;
            default:
                return null;
        }
    }

    return (
        <div className="bg-base-100 rounded-lg shadow-md p-4 transition-all duration-300 animate-slide-in-up">
            <div className="flex justify-between items-start">
                <div>
                    <h4 className="text-lg font-bold text-text-primary">{candidate.name}</h4>
                    <p className="text-sm text-text-secondary">{candidate.email}</p>
                    <p className="text-xs text-gray-400 mt-1">Applied on {candidate.appliedAt.toLocaleDateString()}</p>
                </div>
                {statusPill(candidate.status)}
            </div>
            <div className="mt-4 flex justify-end items-center">
               {renderActions()}
            </div>
        </div>
    );
};


const CandidateDashboard: React.FC<CandidateDashboardProps> = ({ 
    job, 
    candidates, 
    onSelectCandidate, 
    addCandidate, 
    updateCandidateStatus, 
    addGithubLink,
    updateAutomatedEvaluation
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isQuestionsModalOpen, setIsQuestionsModalOpen] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState<string[]>([]);
  const [isGeneratingQuestions, setIsGeneratingQuestions] = useState(false);

  
  const handleEvaluate = async (candidate: Candidate) => {
    if(!candidate.githubLink) return;
    try {
        const evaluation = await generateAutomatedEvaluation(candidate.githubLink);
        updateAutomatedEvaluation(candidate.id, evaluation);
        updateCandidateStatus(candidate.id, CandidateStatus.ASSESSMENT);
    } catch (error) {
        console.error("Evaluation failed", error);
        alert("Failed to generate AI evaluation. Please check the console.");
    }
  };

  const handleGenerateQuestions = async () => {
    setIsQuestionsModalOpen(true);
    if (generatedQuestions.length > 0) return; // Don't re-generate if already have them

    setIsGeneratingQuestions(true);
    try {
        const questions = await generateInterviewQuestions(job);
        setGeneratedQuestions(questions);
    } catch (error) {
        console.error("Failed to generate questions", error);
        setGeneratedQuestions(["Sorry, we couldn't generate questions at this time."]);
    } finally {
        setIsGeneratingQuestions(false);
    }
  };

  return (
    <div className="animate-fade-in">
        <div className="flex justify-between items-center mb-6">
            <div>
                <h2 className="text-3xl font-bold text-text-primary">Candidates for {job.title}</h2>
                <p className="text-text-secondary mt-1">{job.division}</p>
            </div>
             <div className="flex items-center space-x-4">
                <button
                    onClick={handleGenerateQuestions}
                    className="flex items-center bg-secondary text-white font-bold py-2 px-4 rounded-lg hover:bg-primary transition-colors duration-300 shadow-sm"
                >
                    <QuestionMarkIcon className="h-5 w-5 mr-2" />
                    Generate Questions
                </button>
                <button 
                    onClick={() => setIsModalOpen(true)}
                    className="flex items-center bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm"
                >
                    <PlusIcon className="h-5 w-5 mr-2" />
                    New Candidate
                </button>
            </div>
        </div>
      <div className="space-y-4">
        {candidates.length > 0 ? candidates.map(c => (
          <CandidateCard 
            key={c.id} 
            candidate={c} 
            onSelect={() => onSelectCandidate(c)} 
            onUpdateStatus={(status) => updateCandidateStatus(c.id, status)}
            onAddGithubLink={(link) => addGithubLink(c.id, link)}
            onEvaluate={() => handleEvaluate(c)}
          />
        )) : (
            <div className="text-center py-10 bg-base-100 rounded-lg shadow-md">
                <p className="text-text-secondary">No candidates have applied for this position yet.</p>
            </div>
        )}
      </div>
       <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add New Candidate">
          <CreateCandidateForm onSubmit={(data) => {
              addCandidate({ ...data, jobId: job.id });
              setIsModalOpen(false);
          }} />
       </Modal>
        <Modal isOpen={isQuestionsModalOpen} onClose={() => setIsQuestionsModalOpen(false)} title={`Interview Questions for ${job.title}`}>
            {isGeneratingQuestions ? (
                <div className="flex justify-center items-center h-48">
                    <LoadingSpinner className="h-8 w-8 text-primary"/>
                    <p className="ml-4 text-text-secondary">Generating questions...</p>
                </div>
            ) : (
                <div>
                    <ul className="space-y-3 list-disc list-inside text-text-secondary">
                        {generatedQuestions.map((q, i) => <li key={i}>{q}</li>)}
                    </ul>
                    <div className="flex justify-end mt-6">
                        <button
                          onClick={() => navigator.clipboard.writeText(generatedQuestions.join('\n\n'))}
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

export default CandidateDashboard;