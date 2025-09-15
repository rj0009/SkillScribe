import React, { useState } from 'react';
import type { JobPosting } from '../../types';
import { INTERVIEW_PROCESS_OPTIONS, DIVISION_OPTIONS, JOB_TITLE_OPTIONS } from '../../constants';

interface CreateJobPostingFormProps {
  onSubmit: (data: Omit<JobPosting, 'id' | 'createdAt' | 'status'>) => void;
}

const CreateJobPostingForm: React.FC<CreateJobPostingFormProps> = ({ onSubmit }) => {
  const [title, setTitle] = useState(JOB_TITLE_OPTIONS[0]);
  const [division, setDivision] = useState(DIVISION_OPTIONS[0]);
  const [process, setProcess] = useState(INTERVIEW_PROCESS_OPTIONS[0]);
  const [remarks, setRemarks] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !division || !process) {
      alert('Please fill out all fields.');
      return;
    }
    onSubmit({ title, division, process, remarks });
    // Reset form
    setTitle(JOB_TITLE_OPTIONS[0]);
    setDivision(DIVISION_OPTIONS[0]);
    setProcess(INTERVIEW_PROCESS_OPTIONS[0]);
    setRemarks('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-text-secondary">Job Title</label>
        <select
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="mt-1 block w-full px-3 py-2 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
          required
        >
          {JOB_TITLE_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="division" className="block text-sm font-medium text-text-secondary">Division</label>
        <select
          id="division"
          value={division}
          onChange={(e) => setDivision(e.target.value)}
          className="mt-1 block w-full px-3 py-2 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
          required
        >
          {DIVISION_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="process" className="block text-sm font-medium text-text-secondary">Interview Process</label>
        <select
          id="process"
          value={process}
          onChange={(e) => setProcess(e.target.value)}
          className="mt-1 block w-full px-3 py-2 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
          required
        >
          {INTERVIEW_PROCESS_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="remarks" className="block text-sm font-medium text-text-secondary">Additional Remarks (Optional)</label>
        <textarea
            id="remarks"
            value={remarks}
            onChange={(e) => setRemarks(e.target.value)}
            rows={3}
            className="mt-1 block w-full px-3 py-2 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
            placeholder="e.g., Urgent hiring, specific skill requirements..."
        />
      </div>
      <div className="flex justify-end pt-2">
        <button
          type="submit"
          className="bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm"
        >
          Create Job
        </button>
      </div>
    </form>
  );
};

export default CreateJobPostingForm;