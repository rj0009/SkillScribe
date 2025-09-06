
import React from 'react';

export const QuestionMarkIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    {...props}
  >
    <path d="M9.75 18.75H14.25a.75.75 0 010 1.5H9.75a.75.75 0 010-1.5z" />
    <path fillRule="evenodd" d="M12 1.5a8.25 8.25 0 018.25 8.25c0 2.855-1.42 5.435-3.6 6.963a.75.75 0 01-.84-1.203 6.75 6.75 0 00-7.62 0 .75.75 0 01-.84 1.203C5.67 15.185 4.25 12.605 4.25 9.75A8.25 8.25 0 0112 1.5zM12 21a.75.75 0 01-.75-.75v-.063c0-.88.718-1.597 1.598-1.597h.004c.88 0 1.597.717 1.597 1.597V20.25a.75.75 0 01-.75.75h-.697z" clipRule="evenodd" />
  </svg>
);