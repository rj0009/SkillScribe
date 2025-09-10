import React, { useState } from 'react';
import type { JobPosting, Candidate } from '../types';
import { JobStatus, CandidateStatus } from '../types';
import { BriefcaseIcon } from './BriefcaseIcon';
import { UsersIcon } from './icons/UsersIcon';
import { DocumentCheckIcon } from './icons/DocumentCheckIcon';
import { CheckCircleIcon } from './CheckCircleIcon';
import Modal from './Modal';
import { generateWorkflowsDocument } from '../services/geminiService';
import { LoadingSpinner } from './icons/LoadingSpinner';
import { DocumentTextIcon } from './icons/DocumentTextIcon';
import PipelineChart from './PipelineChart';
import { PlusIcon } from './icons/PlusIcon';
import CreateJobPostingForm from './icons/CreateJobPostingForm';


interface HiringOverviewDashboardProps {
  jobPostings: JobPosting[];
  candidates: Candidate[];
  onSelectJob: (job: JobPosting) => void;
  onSelectStatus: (status: CandidateStatus) => void;
  addJobPosting: (job: Omit<JobPosting, 'id' | 'createdAt' | 'status'>) => void;
}

const StatCard: React.FC<{ title: string; value: number; icon: React.ReactNode; onClick?: () => void; }> = ({ title, value, icon, onClick }) => {
  const isClickable = !!onClick;
  const cardClasses = `bg-base-100 p-6 rounded-lg shadow-md flex items-center animate-slide-in-up ${isClickable ? 'cursor-pointer hover:shadow-xl hover:-translate-y-1 transition-all duration-300' : ''}`;

  return (
    <div className={cardClasses} onClick={onClick}>
      <div className="p-3 bg-primary/10 rounded-full mr-4">
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-text-secondary">{title}</p>
        <p className="text-3xl font-bold text-text-primary">{value}</p>
      </div>
    </div>
  );
};

const HiringOverviewDashboard: React.FC<HiringOverviewDashboardProps> = ({ jobPostings, candidates, onSelectJob, onSelectStatus, addJobPosting }) => {
  const [isWorkflowModalOpen, setIsWorkflowModalOpen] = useState(false);
  const [isCreateJobModalOpen, setIsCreateJobModalOpen] = useState(false);
  const [workflowContent, setWorkflowContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const openPositions = jobPostings.filter(j => j.status === JobStatus.OPEN).length;
  const totalCandidates = candidates.length;
  const inAssessment = candidates.filter(c => c.status === CandidateStatus.ASSESSMENT).length;
  const readyForInterview = candidates.filter(c => c.status === CandidateStatus.ACCEPTED).length;
  
  const activeJobPostings = jobPostings.filter(j => j.status === JobStatus.OPEN);

  const handleGenerateWorkflows = async () => {
    setIsWorkflowModalOpen(true);
    setIsLoading(true);
    try {
        const doc = await generateWorkflowsDocument();
        setWorkflowContent(doc);
    } catch (error) {
        setWorkflowContent("Failed to generate workflow document.");
    } finally {
        setIsLoading(false);
    }
  };

  return (
    <div className="animate-fade-in space-y-8">
        <div className="flex justify-between items-start">
            <div>
                <h1 className="text-3xl font-bold text-text-primary">Hiring Overview</h1>
                <p className="text-text-secondary mt-1">A high-level view of your recruitment pipeline.</p>
            </div>
             <div className="flex items-center space-x-2">
                <button
                    onClick={handleGenerateWorkflows}
                    className="flex items-center bg-base-100 text-text-secondary font-bold py-2 px-4 rounded-lg hover:bg-base-300 transition-colors duration-300 shadow-sm border border-base-300"
                >
                    <DocumentTextIcon className="h-5 w-5 mr-2" />
                    Generate Workflow Guide
                </button>
                <button
                    onClick={() => setIsCreateJobModalOpen(true)}
                    className="flex items-center bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm"
                >
                    <PlusIcon className="h-5 w-5 mr-2" />
                    New Job Posting
                </button>
            </div>
        </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Open Positions" value={openPositions} icon={<BriefcaseIcon className="h-6 w-6 text-primary" />} />
        <StatCard title="Total Candidates" value={totalCandidates} icon={<UsersIcon className="h-6 w-6 text-primary" />} />
        <StatCard 
            title="In Assessment" 
            value={inAssessment} 
            icon={<DocumentCheckIcon className="h-6 w-6 text-primary" />} 
            onClick={() => onSelectStatus(CandidateStatus.ASSESSMENT)}
        />
        <StatCard 
            title="Ready for Interview" 
            value={readyForInterview} 
            icon={<CheckCircleIcon className="h-6 w-6 text-primary" />} 
            onClick={() => onSelectStatus(CandidateStatus.ACCEPTED)}
        />
      </div>
      
      <PipelineChart candidates={candidates} />

      <div className="bg-base-100 rounded-lg shadow-md overflow-hidden animate-slide-in-up" style={{ animationDelay: '200ms'}}>
        <div className="p-6">
            <h2 className="text-xl font-bold text-text-primary">Active Job Postings</h2>
        </div>
        <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-base-300">
                <thead className="bg-base-200">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Job Title</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Division</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Candidates</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Status</th>
                        <th scope="col" className="relative px-6 py-3"><span className="sr-only">View</span></th>
                    </tr>
                </thead>
                <tbody className="bg-base-100 divide-y divide-base-300">
                    {activeJobPostings.map(job => {
                        const candidateCount = candidates.filter(c => c.jobId === job.id).length;
                        return (
                            <tr key={job.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-text-primary">{job.title}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">{job.division}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">{candidateCount}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                     <span className="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                        {job.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button onClick={() => onSelectJob(job)} className="text-primary hover:text-secondary font-bold">View Pipeline</button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
            {activeJobPostings.length === 0 && (
                <p className="text-center text-text-secondary py-8">No active job postings found.</p>
            )}
        </div>
      </div>
        <Modal isOpen={isWorkflowModalOpen} onClose={() => setIsWorkflowModalOpen(false)} title="Application Workflow Guide">
            {isLoading ? (
                 <div className="flex justify-center items-center h-48">
                    <LoadingSpinner className="h-8 w-8 text-primary"/>
                    <p className="ml-4 text-text-secondary">Generating guide...</p>
                </div>
            ) : (
                <div>
                    <div className="prose max-w-none text-text-secondary bg-base-200 p-6 rounded-md max-h-[70vh] overflow-y-auto" dangerouslySetInnerHTML={{ __html: workflowContent.replace(/\n/g, '<br />') }}>
                    </div>
                     <div className="flex justify-end mt-6">
                        <button
                          onClick={() => navigator.clipboard.writeText(workflowContent.replace(/<br \/>/g, '\n').replace(/#+\s/g, ''))}
                          className="bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm"
                        >
                            Copy to Clipboard
                        </button>
                    </div>
                </div>
            )}
       </Modal>
       <Modal isOpen={isCreateJobModalOpen} onClose={() => setIsCreateJobModalOpen(false)} title="Create New Job Posting">
          <CreateJobPostingForm onSubmit={(data) => {
              addJobPosting(data);
              setIsCreateJobModalOpen(false);
          }} />
       </Modal>

    </div>
  );
};

export default HiringOverviewDashboard;