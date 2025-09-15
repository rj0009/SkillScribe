
import React, { useState } from 'react';
import Modal from './Modal';

interface SendCaseStudyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { deadline: Date }) => void;
}

const SendCaseStudyModal: React.FC<SendCaseStudyModalProps> = ({ isOpen, onClose, onSubmit }) => {
  
  const getInitialDateTime = (offsetDays: number = 0) => {
    const date = new Date();
    date.setDate(date.getDate() + offsetDays);
    // Adjust for timezone offset to correctly display in datetime-local input
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date.toISOString().slice(0, 16);
  };

  const [deadline, setDeadline] = useState(getInitialDateTime(7));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!deadline) {
      alert('Please fill out all fields.');
      return;
    }
    onSubmit({ deadline: new Date(deadline) });
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Send Case Study">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="deadline" className="block text-sm font-medium text-text-secondary">Submission Deadline</label>
          <input
            type="datetime-local"
            id="deadline"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            className="mt-1 block w-full px-3 py-2 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
            required
          />
        </div>
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm"
          >
            Set Deadline & Send
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default SendCaseStudyModal;