import type { Assessor } from './types';

export const ASSESSORS_POOL: Omit<Assessor, 'isLead'>[] = [
  { id: 'assessor-1', name: 'Alice Johnson' },
  { id: 'assessor-2', name: 'Bob Williams' },
  { id: 'assessor-3', name: 'Charlie Brown' },
  { id: 'assessor-4', name: 'Diana Miller' },
  { id: 'assessor-5', name: 'Ethan Davis' },
  { id: 'assessor-6', name: 'Fiona Garcia' },
];

export const VICTOR_ID = 'victor';
export const VICTOR_NAME = 'Victor Sterling';

export const JOB_TITLE_OPTIONS = [
    'Senior Frontend Engineer',
    'Cloud Infrastructure Specialist',
    'Lead Backend Engineer',
    'Data Scientist',
    'AI/ML Engineer',
    'Product Manager',
];

export const INTERVIEW_PROCESS_OPTIONS = [
    'Standard: Screening -> Case Study -> Technical Interviews',
    'Simplified: Screening -> Paired Programming Interview',
    'Comprehensive: Screening -> Case Study -> Panel Interview -> Cultural Fit',
    'Executive: Multiple Rounds -> Final Panel Presentation',
];

export const DIVISION_OPTIONS = [
    'AI Practice',
    'AI Program',
    'FDT',
    'NDI',
];