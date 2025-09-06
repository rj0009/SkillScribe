
import React from 'react';
import type { Candidate, JobPosting, CandidateStatus } from '../types';

interface FilteredCandidateViewProps {
  status: CandidateStatus;
  candidates: Candidate[];
  jobPostings: JobPosting[];
  onSelectCandidate: (candidate: Candidate) => void;
}

const FilteredCandidateView: React.FC<FilteredCandidateViewProps> = ({ status, candidates, jobPostings, onSelectCandidate }) => {
  
  const getJobTitle = (jobId: string) => {
    return jobPostings.find(j => j.id === jobId)?.title || 'Unknown Job';
  }

  return (
    <div className="animate-fade-in bg-base-100 rounded-lg shadow-md">
      <div className="p-6 border-b border-base-300">
        <h2 className="text-2xl font-bold text-text-primary">Candidates: {status}</h2>
        <p className="text-text-secondary mt-1">
          Showing all candidates across all job postings with the status "{status}".
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-base-300">
          <thead className="bg-base-200">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Candidate Name</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Job Posting</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Applied On</th>
              <th scope="col" className="relative px-6 py-3"><span className="sr-only">View Assessment</span></th>
            </tr>
          </thead>
          <tbody className="bg-base-100 divide-y divide-base-300">
            {candidates.map(candidate => (
              <tr key={candidate.id} className="hover:bg-base-200">
                <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-text-primary">{candidate.name}</div>
                    <div className="text-sm text-text-secondary">{candidate.email}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">{getJobTitle(candidate.jobId)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">{candidate.appliedAt.toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button onClick={() => onSelectCandidate(candidate)} className="text-primary hover:text-secondary font-bold">
                    View Assessment
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {candidates.length === 0 && (
          <p className="text-center text-text-secondary py-8">
            No candidates found with this status.
          </p>
        )}
      </div>
    </div>
  );
};

export default FilteredCandidateView;