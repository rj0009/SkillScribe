import React from 'react';

// A stylized icon representing the SkillScribe logo, designed to be a more accurate representation of the brand image.
export const CompanyIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    aria-label="SkillScribe Logo"
    role="img"
    {...props}
  >
    <g stroke="currentColor" strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round">
      {/* Main circles */}
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="5" />

      {/* Spokes (from inner circle to outer dots) */}
      <path d="M12 7 V2" /> {/* Top */}
      <path d="M17 12 H22" /> {/* Right */}
      <path d="M12 17 V22" /> {/* Bottom */}
      <path d="M7 12 H2" /> {/* Left */}
      <path d="M15.53 8.46 L19.29 4.71" /> {/* Top-Right */}
      <path d="M15.53 15.53 L19.29 19.29" /> {/* Bottom-Right */}
      <path d="M8.46 15.53 L4.71 19.29" /> {/* Bottom-Left */}
      <path d="M8.46 8.46 L4.71 4.71" /> {/* Top-Left */}
      
      {/* Webbing (connecting outer dots to adjacent inner points) */}
      <path d="M12 2 L15.53 8.46" />
      <path d="M12 2 L8.46 8.46" />
      
      <path d="M22 12 L15.53 8.46" />
      <path d="M22 12 L15.53 15.53" />
      
      <path d="M12 22 L15.53 15.53" />
      <path d="M12 22 L8.46 15.53" />
      
      <path d="M2 12 L8.46 15.53" />
      <path d="M2 12 L8.46 8.46" />
    </g>

    {/* The 8 outer dots (filled) */}
    <g fill="currentColor" stroke="none">
      <circle cx="12" cy="2" r="1.2" />
      <circle cx="19.29" cy="4.71" r="1.2" />
      <circle cx="22" cy="12" r="1.2" />
      <circle cx="19.29" cy="19.29" r="1.2" />
      <circle cx="12" cy="22" r="1.2" />
      <circle cx="4.71" cy="19.29" r="1.2" />
      <circle cx="2" cy="12" r="1.2" />
      <circle cx="4.71" cy="4.71" r="1.2" />
    </g>
  </svg>
);
