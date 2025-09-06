
import React from 'react';

export const CompanyIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    {...props}
  >
    <path fillRule="evenodd" d="M5.625 1.5c-1.036 0-1.875.84-1.875 1.875v17.25c0 1.035.84 1.875 1.875 1.875h12.75c1.035 0 1.875-.84 1.875-1.875V12.75A3.75 3.75 0 0016.5 9h-1.875a1.875 1.875 0 01-1.875-1.875V5.25A3.75 3.75 0 009 1.5H5.625zM10.5 12a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" clipRule="evenodd" />
    <path d="M10.5 10.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
    <path fillRule="evenodd" d="M12.75 5.25a.75.75 0 01.75.75v3.375a3.75 3.75 0 01-1.056 2.555l-1.02 1.134a.75.75 0 11-1.12-1.004l1.02-1.134a2.25 2.25 0 00.627-1.55V6a.75.75 0 01.75-.75z" clipRule="evenodd" />
    <path fillRule="evenodd" d="M14.25 10.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" clipRule="evenodd" />
    <path d="M14.25 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
  </svg>
);