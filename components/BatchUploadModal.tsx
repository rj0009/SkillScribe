
import React, { useState, useCallback } from 'react';
import type { Candidate } from '../types';
import Modal from './Modal';
import { parseCv } from '../services/geminiService';
import { DocumentArrowUpIcon } from './icons/DocumentArrowUpIcon';
import { LoadingSpinner } from './icons/LoadingSpinner';
import { CheckCircleIcon } from './CheckCircleIcon';
import { XCircleIcon } from './icons/XCircleIcon';

interface BatchUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobId: string;
  // Fix: Corrected the type for the `addCandidate` prop to align with its implementation,
  // omitting properties that are set by default upon candidate creation.
  addCandidate: (candidate: Omit<Candidate, 'id' | 'appliedAt' | 'status' | 'githubLink' | 'assessors' | 'assessments' | 'automatedEvaluation' | 'caseStudyDeadline'>) => void;
}

type Status = 'idle' | 'parsing' | 'success' | 'error';

interface FileStatus {
    file: File;
    status: Status;
    message?: string;
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

const BatchUploadModal: React.FC<BatchUploadModalProps> = ({ isOpen, onClose, jobId, addCandidate }) => {
    const [fileStatuses, setFileStatuses] = useState<FileStatus[]>([]);
    const [isParsing, setIsParsing] = useState(false);
    const [isDragging, setIsDragging] = useState(false);

    const resetState = () => {
        setFileStatuses([]);
        setIsParsing(false);
        setIsDragging(false);
    }

    const handleClose = () => {
        resetState();
        onClose();
    }

    const handleFiles = useCallback((files: FileList | null) => {
        if (!files) return;
        const newFileStatuses: FileStatus[] = Array.from(files)
            .filter(file => !fileStatuses.some(fs => fs.file.name === file.name))
            .map(file => ({ file, status: 'idle' }));
        setFileStatuses(prev => [...prev, ...newFileStatuses]);
    }, [fileStatuses]);

    const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        handleFiles(e.dataTransfer.files);
    };

    const handleParse = async () => {
        setIsParsing(true);
        const filesToParse = fileStatuses.filter(fs => fs.status === 'idle');

        for (const fileStatus of filesToParse) {
            setFileStatuses(prev => prev.map(fs => fs.file.name === fileStatus.file.name ? { ...fs, status: 'parsing' } : fs));
            try {
                const base64Content = await fileToBase64(fileStatus.file);
                const { name, email } = await parseCv(base64Content, fileStatus.file.type);
                if (!name || !email || name === 'N/A' || email === 'N/A') {
                    throw new Error("Could not extract name or email.");
                }
                addCandidate({ name, email, jobId });
                setFileStatuses(prev => prev.map(fs => fs.file.name === fileStatus.file.name ? { ...fs, status: 'success', message: `Added: ${name}` } : fs));
            } catch (error: any) {
                setFileStatuses(prev => prev.map(fs => fs.file.name === fileStatus.file.name ? { ...fs, status: 'error', message: error.message || 'Parsing failed.' } : fs));
            }
        }
        setIsParsing(false);
    };

    const StatusIcon = ({ status }: { status: Status }) => {
        switch(status) {
            case 'parsing': return <LoadingSpinner className="h-5 w-5 text-primary" />;
            case 'success': return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
            case 'error': return <XCircleIcon className="h-5 w-5 text-red-500" />;
            default: return null;
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title="Batch Upload CVs">
            <div className="space-y-4">
                {fileStatuses.length === 0 ? (
                    <div
                        onDragEnter={handleDragEnter}
                        onDragOver={handleDragEnter}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors ${isDragging ? 'border-primary bg-primary/10' : 'border-base-300 hover:border-primary'}`}
                        onClick={() => document.getElementById('file-upload-input')?.click()}
                    >
                        <DocumentArrowUpIcon className="h-12 w-12 mx-auto text-text-secondary" />
                        <p className="mt-2 text-sm text-text-secondary">
                            <span className="font-semibold text-primary">Click to upload</span> or drag and drop.
                        </p>
                        <p className="text-xs text-gray-400 mt-1">PDF, DOCX, TXT accepted</p>
                        <input
                            type="file"
                            id="file-upload-input"
                            multiple
                            accept=".pdf,.doc,.docx,.txt"
                            className="hidden"
                            onChange={(e) => handleFiles(e.target.files)}
                        />
                    </div>
                ) : (
                    <div className="space-y-2 max-h-60 overflow-y-auto p-1">
                        {fileStatuses.map(({ file, status, message }) => (
                            <div key={file.name} className="flex items-center p-2 bg-base-200 rounded-md">
                                <div className="flex-shrink-0 w-6 flex items-center justify-center">
                                    <StatusIcon status={status} />
                                </div>
                                <div className="flex-grow ml-3 min-w-0">
                                    <p className="text-sm font-medium text-text-primary truncate">{file.name}</p>
                                    {message && <p className="text-xs text-text-secondary">{message}</p>}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
                <div className="flex justify-end space-x-3 pt-2">
                    {fileStatuses.length > 0 && (
                         <button
                            type="button"
                            onClick={handleParse}
                            disabled={isParsing || fileStatuses.every(fs => fs.status !== 'idle')}
                            className="bg-primary text-white font-bold py-2 px-4 rounded-lg hover:bg-secondary transition-colors duration-300 shadow-sm disabled:bg-gray-400 disabled:cursor-not-allowed"
                        >
                             {isParsing && <LoadingSpinner className="h-5 w-5 mr-2 inline" />}
                            {isParsing ? 'Parsing...' : 'Parse & Add Candidates'}
                        </button>
                    )}
                    <button
                        type="button"
                        onClick={handleClose}
                        className="bg-base-200 text-text-secondary font-bold py-2 px-4 rounded-lg hover:bg-base-300 transition-colors duration-300"
                    >
                        {fileStatuses.some(fs => fs.status === 'success') ? 'Done' : 'Cancel'}
                    </button>
                </div>
            </div>
        </Modal>
    );
};

export default BatchUploadModal;