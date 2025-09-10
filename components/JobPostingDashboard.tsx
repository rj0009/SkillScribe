
import React, { useState } from 'react';
import type { JobPosting } from '../types';
import { JobStatus } from '../types';
import { PlusIcon } from './icons/PlusIcon';
import Modal from './Modal';
import CreateJobPostingForm from './icons/CreateJobPostingForm';

interface JobPostingDashboardProps {
  jobPostings: JobPosting[];
  onSelectJob: (job: JobPosting) => void;
  addJobPosting: (job: Omit<JobPosting, 'id' | 'createdAt' | 'status'>) => void;
}

const JobPostingCard: React.FC<{ job: JobPosting; onSelect: () => void }> = ({ job, onSelect }) => (
  <div
    onClick={onSelect}
    className="bg-base-100 rounded-lg shadow-md p-6 cursor-pointer hover:shadow-xl hover:-translate-y-1 transition-all duration-300 animate-slide-in-up"
  >
    <div className="flex justify-between items-start">
      <div>
        <h3 className="text-xl font-bold text-text-primary">{job.title}</h3>
        <p className="text-text-secondary mt-1">{job.division}</p>
      </div>
      <span className={`px-3 py-1 text-xs font-semibold rounded-full ${job.status === JobStatus.OPEN ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
        {job.status}
      </span>
    </div>
    <p className="text-sm text-text-secondary mt-4 line-clamp-2">{job.process}</p>
    <p className="text-xs text-gray-400 mt-4">Created on {job.createdAt.toLocaleDateString()}</p>
  </div>
);

const JobPostingDashboard: React.FC<JobPostingDashboardProps> = ({ jobPostings, onSelectJob, addJobPosting }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="animate-fade-in">
        <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl font-bold text-text-primary">Job Postings</h2>
            <button 
                onClick={() => setIsModalOpen(true)}
                className="flex items-center bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm"
            >
                <PlusIcon className="h-5 w-5 mr-2" />
                New Job Posting
            </button>
        </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {jobPostings.map(job => (
          <JobPostingCard key={job.id} job={job} onSelect={() => onSelectJob(job)} />
        ))}
      </div>
       <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Job Posting">
          <CreateJobPostingForm onSubmit={(data) => {
              addJobPosting(data);
              setIsModalOpen(false);
          }} />
       </Modal>
    </div>
  );
};

export default JobPostingDashboard;