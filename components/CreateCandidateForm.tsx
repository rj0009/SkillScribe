
import React, { useState } from 'react';
import { parseCv } from '../services/geminiService';
import { LoadingSpinner } from './icons/LoadingSpinner';
import { DocumentArrowUpIcon } from './icons/DocumentArrowUpIcon';

interface CreateCandidateFormProps {
  onSubmit: (data: { name: string; email: string; }) => void;
}

const fileToBase64 = (file: File): Promise<string> => 
    new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            const result = reader.result as string;
            resolve(result.split(',')[1]); 
        };
        reader.onerror = error => reject(error);
    });


const CreateCandidateForm: React.FC<CreateCandidateFormProps> = ({ onSubmit }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [isParsing, setIsParsing] = useState(false);
  const [parseError, setParseError] = useState<string | null>(null);


  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsParsing(true);
    setParseError(null);

    try {
        const base64Content = await fileToBase64(file);
        const { name, email } = await parseCv(base64Content, file.type);
        setName(name);
        setEmail(email);
    } catch (error) {
        setParseError("Could not parse CV. Please fill fields manually.");
        console.error("CV parsing failed:", error);
    } finally {
        setIsParsing(false);
        // Reset file input value to allow re-uploading the same file
        event.target.value = '';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email) {
      alert('Please fill out all fields.');
      return;
    }
    onSubmit({ name, email });
    setName('');
    setEmail('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
       <div>
            <label className="block text-sm font-medium text-text-secondary">Autofill from CV (Optional)</label>
            <label
                htmlFor="cv-upload"
                className={`mt-1 flex justify-center items-center w-full px-6 py-3 border-2 border-base-300 border-dashed rounded-md transition-colors ${isParsing ? 'bg-base-200 cursor-not-allowed' : 'cursor-pointer hover:border-primary'}`}
            >
                {isParsing ? (
                    <LoadingSpinner className="h-5 w-5 text-primary mr-2" />
                ) : (
                    <DocumentArrowUpIcon className="h-5 w-5 text-text-secondary mr-2" />
                )}
                <span className="text-sm text-text-secondary">
                    {isParsing ? 'Parsing CV...' : 'Upload a CV'}
                </span>
            </label>
            <input
                id="cv-upload"
                name="cv-upload"
                type="file"
                className="hidden"
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx,.txt"
                disabled={isParsing}
            />
            {parseError && <p className="text-red-500 text-xs mt-1">{parseError}</p>}
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center" aria-hidden="true">
            <div className="w-full border-t border-base-300" />
          </div>
          <div className="relative flex justify-center">
            <span className="bg-base-100 px-2 text-sm text-text-secondary">Or fill manually</span>
          </div>
        </div>

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-text-secondary">Full Name</label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 block w-full px-3 py-2 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
          required
        />
      </div>
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-text-secondary">Email Address</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 block w-full px-3 py-2 bg-base-100 border border-base-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
          required
        />
      </div>
      <div className="flex justify-end pt-2">
        <button
          type="submit"
          disabled={isParsing}
          className="bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm disabled:bg-gray-400"
        >
          Add Candidate
        </button>
      </div>
    </form>
  );
};

export default CreateCandidateForm;
