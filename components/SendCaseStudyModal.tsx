
import React, { useState } from 'react';
import Modal from './Modal';

interface SendCaseStudyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { deadline: Date; sendAt: Date }) => void;
}

const SendCaseStudyModal: React.FC<SendCaseStudyModalProps> = ({ isOpen, onClose, onSubmit }) => {
  
  const getInitialDateTime = (offsetDays: number = 0) => {
    const date = new Date();
    date.setDate(date.getDate() + offsetDays);
    // Adjust for timezone offset to correctly display in datetime-local input
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date.toISOString().slice(0, 16);
  };

  const [sendAt, setSendAt] = useState(getInitialDateTime(0));
  const [deadline, setDeadline] = useState(getInitialDateTime(7));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!deadline || !sendAt) {
      alert('Please fill out all fields.');
      return;
    }
    onSubmit({ deadline: new Date(deadline), sendAt: new Date(sendAt) });
    onClose();
  };
  
  // Check if sendAt is more than a minute in the future
  const isScheduling = new Date(sendAt).getTime() > new Date().getTime() + 60000;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Send Case Study">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="sendAt" className="block text-sm font-medium text-text-secondary">Email Send Time</label>
          <input
            type="datetime-local"
            id="sendAt"
            value={sendAt}
            onChange={(e) => setSendAt(e.target.value)}
            className="mt-1 block w-full px-3 py-2 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
            required
          />
           <p className="text-xs text-gray-500 mt-1">Select a future time to schedule the email, or leave as is to send now.</p>
        </div>
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
            {isScheduling ? 'Schedule Email' : 'Send Now'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default SendCaseStudyModal;
