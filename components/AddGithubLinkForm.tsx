
import React, { useState } from 'react';

interface AddGithubLinkFormProps {
  onSubmit: (link: string) => void;
}

const AddGithubLinkForm: React.FC<AddGithubLinkFormProps> = ({ onSubmit }) => {
    const [link, setLink] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if(!link) return;
        onSubmit(link);
        setLink('');
    };

    return (
        <form onSubmit={handleSubmit} className="flex items-center space-x-2 w-full max-w-sm">
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
    );
};

export default AddGithubLinkForm;