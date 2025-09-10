
import React, { useState } from 'react';

interface AddGithubLinkFormProps {
  onSubmit: (link: string) => void;
  deadline: Date | null;
}

const AddGithubLinkForm: React.FC<AddGithubLinkFormProps> = ({ onSubmit, deadline }) => {
    const [link, setLink] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if(!link) return;
        onSubmit(link);
        setLink('');
    };
    
    const isOverdue = deadline ? new Date() > new Date(deadline) : false;

    return (
        <div className="w-full max-w-sm">
            <form onSubmit={handleSubmit} className="flex items-center space-x-2">
                <input 
                    type="url"
                    value={link}
                    onChange={e => setLink(e.target.value)}
                    placeholder="https://github.com/..."
                    className="flex-grow px-3 py-1 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm text-xs"
                    required
                />
                <button type="submit" className="text-sm bg-primary text-white font-bold py-1 px-3 rounded-md hover:bg-secondary">Submit Link</button>
            </form>
            {deadline && (
                <p className={`text-xs mt-1 text-right ${isOverdue ? 'text-red-500 font-semibold' : 'text-text-secondary'}`}>
                    Deadline: {new Date(deadline).toLocaleDateString()} {new Date(deadline).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} {isOverdue && '(Overdue)'}
                </p>
            )}
        </div>
    );
};

export default AddGithubLinkForm;