
export enum JobStatus {
  OPEN = 'Open',
  CLOSED = 'Closed',
}

export interface JobPosting {
  id: string;
  title: string;
  division: string;
  process: string;
  status: JobStatus;
  createdAt: Date;
}

export enum CandidateStatus {
  APPLIED = 'Applied',
  CASE_STUDY_SENT = 'Case Study Sent',
  CASE_STUDY_SUBMITTED = 'Case Study Submitted',
  ASSESSMENT = 'In Assessment',
  FINAL_REVIEW = 'Final Review',
  ACCEPTED = 'Accepted for Interview',
  REJECTED = 'Rejected',
}

export enum Vote {
  ACCEPT = 'Accept',
  REJECT = 'Reject',
  DEFER = 'Defer to Victor',
  PENDING = 'Pending',
}

export interface Assessor {
  id: string;
  name: string;
  isLead: boolean;
}

export interface Assessment {
  assessorId: string;
  assessorName: string;
  review: string;
  vote: Vote;
}

export interface Candidate {
  id: string;
  jobId: string;
  name: string;
  email: string;
  githubLink: string | null;
  status: CandidateStatus;
  appliedAt: Date;
  assessors: Assessor[];
  assessments: Assessment[];
  automatedEvaluation: string | null;
}

export type ViewState = 
  | { view: 'hiring_overview' }
  | { view: 'job_postings' }
  | { view: 'candidates', jobId: string }
  | { view: 'assessment', jobId: string, candidateId: string }
  | { view: 'filtered_candidates', status: CandidateStatus };