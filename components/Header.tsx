
import React from 'react';
import type { ViewState, JobPosting, Candidate } from '../types';
import { CompanyIcon } from './icons/CompanyIcon';

interface HeaderProps {
  viewState: ViewState;
  selectedJob: JobPosting | null;
  selectedCandidate: Candidate | null;
  onNavigateOverview: () => void;
  onNavigateCandidates: () => void;
}

const BreadcrumbItem: React.FC<{ onClick?: () => void; children: React.ReactNode; isLast?: boolean }> = ({ onClick, children, isLast = false }) => {
    const commonClasses = "text-sm font-medium";
    if (isLast) {
        return <span className={`${commonClasses} text-text-primary`}>{children}</span>;
    }
    return (
        <>
            <button onClick={onClick} className={`${commonClasses} text-primary hover:underline`}>
                {children}
            </button>
            <span className="mx-2 text-text-secondary">/</span>
        </>
    );
};


const Header: React.FC<HeaderProps> = ({ viewState, selectedJob, selectedCandidate, onNavigateOverview, onNavigateCandidates }) => {
  return (
    <header className="bg-base-100 shadow-md p-4 flex justify-between items-center animate-fade-in">
       <button onClick={onNavigateOverview} className="flex items-center focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary rounded-lg p-1">
        <CompanyIcon className="h-8 w-8 text-primary" />
        <h1 className="text-2xl font-bold ml-3 text-text-primary tracking-tight">SkillScribe</h1>
      </button>
      <div className="flex items-center">
         {viewState.view !== 'hiring_overview' && (
          <>
            <BreadcrumbItem onClick={onNavigateOverview}>
              Hiring Overview
            </BreadcrumbItem>
             {viewState.view === 'filtered_candidates' && (
                <BreadcrumbItem isLast={true}>
                    {`Candidates: ${viewState.status}`}
                </BreadcrumbItem>
             )}
            {selectedJob && (
               <BreadcrumbItem 
                 onClick={onNavigateCandidates}
                 isLast={viewState.view === 'candidates'}
               >
                 {selectedJob.title}
               </BreadcrumbItem>
            )}
            {selectedCandidate && viewState.view === 'assessment' && (
              <BreadcrumbItem isLast={true}>
                {selectedCandidate.name}
              </BreadcrumbItem>
            )}
          </>
        )}
      </div>
    </header>
  );
};

export default Header;