
import React, { useState, useMemo } from 'react';
import type { JobPosting, Candidate, ViewState, CandidateStatus } from './types';
import { useMockData } from './hooks/useMockData';
import Header from './components/Header';
import JobPostingDashboard from './components/JobPostingDashboard';
import CandidateDashboard from './components/CandidateDashboard';
import AssessmentView from './components/AssessmentView';
import HiringOverviewDashboard from './components/HiringOverviewDashboard';
import FilteredCandidateView from './components/FilteredCandidateView';

const App: React.FC = () => {
  const mockData = useMockData();
  const [viewState, setViewState] = useState<ViewState>({ view: 'hiring_overview' });

  const handleSelectJob = (job: JobPosting) => {
    setViewState({ view: 'candidates', jobId: job.id });
  };

  const handleSelectCandidate = (candidate: Candidate) => {
    setViewState({ view: 'assessment', candidateId: candidate.id, jobId: candidate.jobId });
  };

  const handleSelectStatus = (status: CandidateStatus) => {
    setViewState({ view: 'filtered_candidates', status });
  };

  const navigateToOverview = () => {
    setViewState({ view: 'hiring_overview' });
  };

  const navigateToCandidates = () => {
    if (viewState.view !== 'job_postings' && viewState.view !== 'hiring_overview' && viewState.view !== 'filtered_candidates') {
       setViewState({ view: 'candidates', jobId: viewState.jobId });
    }
  };
  
  const selectedJob = useMemo(() => {
    if (viewState.view === 'job_postings' || viewState.view === 'hiring_overview' || viewState.view === 'filtered_candidates') return null;
    return mockData.jobPostings.find(j => j.id === viewState.jobId) || null;
  }, [viewState, mockData.jobPostings]);

  const selectedCandidate = useMemo(() => {
    if (viewState.view !== 'assessment') return null;
    return mockData.candidates.find(c => c.id === viewState.candidateId) || null;
  }, [viewState, mockData.candidates]);

  const renderContent = () => {
    switch (viewState.view) {
      case 'hiring_overview':
        return (
          <HiringOverviewDashboard
            jobPostings={mockData.jobPostings}
            candidates={mockData.candidates}
            onSelectJob={handleSelectJob}
            onSelectStatus={handleSelectStatus}
            addJobPosting={mockData.addJobPosting}
          />
        );
       case 'filtered_candidates':
        const filteredCandidates = mockData.candidates.filter(c => c.status === viewState.status);
        return (
          <FilteredCandidateView
            status={viewState.status}
            candidates={filteredCandidates}
            jobPostings={mockData.jobPostings}
            onSelectCandidate={handleSelectCandidate}
          />
        );
      case 'candidates':
        const candidatesForJob = mockData.candidates.filter(c => c.jobId === viewState.jobId);
        return selectedJob ? (
          <CandidateDashboard
            job={selectedJob}
            candidates={candidatesForJob}
            onSelectCandidate={handleSelectCandidate}
            addCandidate={mockData.addCandidate}
            updateCandidateStatus={mockData.updateCandidateStatus}
            addGithubLink={mockData.addGithubLink}
            updateAutomatedEvaluation={mockData.updateAutomatedEvaluation}
            sendCaseStudy={mockData.sendCaseStudy}
          />
        ) : <p>Job not found</p>;
      case 'assessment':
        return selectedCandidate && selectedJob ? (
          <AssessmentView
            candidate={selectedCandidate}
            job={selectedJob}
            updateAssessment={mockData.updateAssessment}
            updateCandidateStatus={mockData.updateCandidateStatus}
          />
        ) : <p>Candidate not found</p>;
       case 'job_postings': // Kept for completeness, though overview is primary
        return (
          <JobPostingDashboard
            jobPostings={mockData.jobPostings}
            onSelectJob={handleSelectJob}
            addJobPosting={mockData.addJobPosting}
          />
        );
      default:
        return <p>Something went wrong</p>;
    }
  };

  return (
    <div className="min-h-screen bg-base-200 text-text-primary">
      <Header
        viewState={viewState}
        selectedJob={selectedJob}
        selectedCandidate={selectedCandidate}
        onNavigateOverview={navigateToOverview}
        onNavigateCandidates={navigateToCandidates}
      />
      <main className="p-4 md:p-8">
        {renderContent()}
      </main>
    </div>
  );
};

export default App;