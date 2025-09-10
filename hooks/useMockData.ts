
import { useState } from 'react';
import type { JobPosting, Candidate, Assessment, Assessor } from '../types';
import { JobStatus, CandidateStatus, Vote } from '../types';
import { ASSESSORS_POOL, INTERVIEW_PROCESS_OPTIONS, DIVISION_OPTIONS, JOB_TITLE_OPTIONS } from '../constants';

const initialJobPostings: JobPosting[] = [
  {
    id: 'job-1',
    title: JOB_TITLE_OPTIONS[0], // Senior Frontend Engineer
    division: DIVISION_OPTIONS[0], // AI Practice
    process: INTERVIEW_PROCESS_OPTIONS[0],
    status: JobStatus.OPEN,
    createdAt: new Date('2025-06-20T10:00:00Z'),
  },
  {
    id: 'job-2',
    title: JOB_TITLE_OPTIONS[1], // Cloud Infrastructure Specialist
    division: DIVISION_OPTIONS[2], // FDT
    process: INTERVIEW_PROCESS_OPTIONS[2],
    status: JobStatus.OPEN,
    createdAt: new Date('2025-06-18T14:30:00Z'),
  },
];

const initialCandidates: Candidate[] = [
    {
        id: 'cand-1',
        jobId: 'job-1',
        name: 'John Doe',
        email: 'john.doe@example.com',
        githubLink: null,
        status: CandidateStatus.APPLIED,
        appliedAt: new Date('2025-06-21T09:00:00Z'),
        assessors: [],
        assessments: [],
        automatedEvaluation: null,
        caseStudyDeadline: null,
        caseStudyEmailScheduledAt: null,
    },
    {
        id: 'cand-2',
        jobId: 'job-1',
        name: 'Jane Smith',
        email: 'jane.smith@example.com',
        githubLink: 'https://github.com/example/project-1',
        status: CandidateStatus.ASSESSMENT,
        appliedAt: new Date('2025-06-22T11:00:00Z'),
        assessors: [
            { id: 'assessor-1', name: 'Alice Johnson', isLead: true },
            { id: 'assessor-2', name: 'Bob Williams', isLead: false },
            { id: 'assessor-3', name: 'Charlie Brown', isLead: false },
        ],
        assessments: [
            { assessorId: 'assessor-1', assessorName: 'Alice Johnson', review: 'Solid fundamentals, but could use more work on state management.', vote: Vote.PENDING },
            { assessorId: 'assessor-2', assessorName: 'Bob Williams', review: '', vote: Vote.PENDING },
            { assessorId: 'assessor-3', assessorName: 'Charlie Brown', review: '', vote: Vote.PENDING },
        ],
        automatedEvaluation: "The project demonstrates a good understanding of React components and props. However, the code lacks proper error handling and could be structured more efficiently. The CSS is not responsive, which is a key requirement. Overall, a decent attempt but needs refinement.",
        caseStudyDeadline: new Date('2025-07-01T23:59:00Z'),
        caseStudyEmailScheduledAt: null,
    },
    {
        id: 'cand-3',
        jobId: 'job-2',
        name: 'Peter Jones',
        email: 'peter.jones@example.com',
        githubLink: null,
        status: CandidateStatus.CASE_STUDY_SENT,
        appliedAt: new Date('2025-06-20T16:00:00Z'),
        assessors: [],
        assessments: [],
        automatedEvaluation: null,
        caseStudyDeadline: new Date('2025-06-28T23:59:00Z'),
        caseStudyEmailScheduledAt: null,
    },
];

export const useMockData = () => {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>(initialJobPostings);
  const [candidates, setCandidates] = useState<Candidate[]>(initialCandidates);

  const addJobPosting = (job: Omit<JobPosting, 'id' | 'createdAt' | 'status'>) => {
    const newJob: JobPosting = {
      ...job,
      id: `job-${Date.now()}`,
      createdAt: new Date(),
      status: JobStatus.OPEN,
    };
    setJobPostings(prev => [newJob, ...prev]);
  };

  const addCandidate = (candidate: Omit<Candidate, 'id' | 'appliedAt' | 'status' | 'githubLink' | 'assessors' | 'assessments' | 'automatedEvaluation' | 'caseStudyDeadline' | 'caseStudyEmailScheduledAt'>) => {
    const newCandidate: Candidate = {
      ...candidate,
      id: `cand-${Date.now()}`,
      appliedAt: new Date(),
      status: CandidateStatus.APPLIED,
      githubLink: null,
      assessors: [],
      assessments: [],
      automatedEvaluation: null,
      caseStudyDeadline: null,
      caseStudyEmailScheduledAt: null,
    };
    setCandidates(prev => [...prev, newCandidate]);
  };

  const updateCandidateStatus = (candidateId: string, status: CandidateStatus) => {
    setCandidates(prev => prev.map(c => {
      if (c.id === candidateId) {
        const updatedCandidate = { ...c, status };
        // Assign assessors when case study is submitted
        if (status === CandidateStatus.ASSESSMENT && c.assessors.length === 0) {
          const shuffled = [...ASSESSORS_POOL].sort(() => 0.5 - Math.random());
          const assignedAssessors: Assessor[] = shuffled.slice(0, 3).map((assessor, index) => ({
            ...assessor,
            isLead: index === 0, // First one is the lead
          }));
          updatedCandidate.assessors = assignedAssessors;
          updatedCandidate.assessments = assignedAssessors.map(a => ({
              assessorId: a.id,
              assessorName: a.name,
              review: '',
              vote: Vote.PENDING,
          }));
        }
        return updatedCandidate;
      }
      return c;
    }));
  };

  const scheduleOrSendCaseStudy = (candidateId: string, deadline: Date, sendAt: Date) => {
    const now = new Date();
    // Treat schedules within the next minute as "now" to avoid weird UI states
    const isScheduledForFuture = sendAt.getTime() > now.getTime() + 60000;

    setCandidates(prev => prev.map(c => {
        if (c.id === candidateId) {
            return {
                ...c,
                caseStudyDeadline: deadline,
                caseStudyEmailScheduledAt: isScheduledForFuture ? sendAt : null,
                status: isScheduledForFuture ? CandidateStatus.APPLIED : CandidateStatus.CASE_STUDY_SENT,
            };
        }
        return c;
    }));
  };
  
  const addGithubLink = (candidateId: string, githubLink: string) => {
    setCandidates(prev => prev.map(c => 
      c.id === candidateId ? { ...c, githubLink, status: CandidateStatus.CASE_STUDY_SUBMITTED } : c
    ));
  };
  
  const updateAutomatedEvaluation = (candidateId: string, evaluation: string) => {
       setCandidates(prev => prev.map(c =>
        c.id === candidateId ? { ...c, automatedEvaluation: evaluation } : c
    ));
  }

  const updateAssessment = (candidateId: string, assessment: Assessment) => {
    setCandidates(prev => prev.map(c => {
      if (c.id === candidateId) {
        const newAssessments = c.assessments.map(a => 
          a.assessorId === assessment.assessorId ? assessment : a
        );
        return { ...c, assessments: newAssessments };
      }
      return c;
    }));
  };

  return { 
    jobPostings, 
    candidates, 
    addJobPosting, 
    addCandidate, 
    updateCandidateStatus,
    scheduleOrSendCaseStudy,
    addGithubLink,
    updateAutomatedEvaluation,
    updateAssessment,
  };
};