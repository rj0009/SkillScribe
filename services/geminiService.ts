
import { GoogleGenAI, Type } from "@google/genai";
import type { JobPosting, Candidate } from '../types';
import { Vote, CandidateStatus } from '../types';


// Ensure you have a .env file with your API_KEY
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

if (!API_KEY) {
  console.warn("Gemini API key not found. Using mocked responses. Please set process.env.API_KEY.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY! });

const MOCK_EVALUATION = `
**Overall Assessment:**
The candidate shows a foundational understanding of web development principles. The project is functional but lacks some of the polish and robustness expected for a senior role.

**Strengths:**
- **Component Structure:** The code is well-organized into reusable components.
- **API Integration:** Successfully fetches and displays data from an external API.
- **Basic State Management:** Utilizes React hooks effectively for managing local component state.

**Areas for Improvement:**
- **Code Quality:** Some parts of the code could be refactored for better readability and performance. There's a lack of comments and documentation.
- **Error Handling:** Missing comprehensive error handling for API calls and user inputs.
- **Testing:** No unit or integration tests were provided.
- **Styling:** The UI is basic and could be improved with more attention to responsive design and modern CSS practices.

**Recommendation:**
Potential for a mid-level role, but would require mentorship to reach senior-level expectations. Further discussion on architectural choices is recommended.
`;


export const generateAutomatedEvaluation = async (githubLink: string): Promise<string> => {
  if (!API_KEY) {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    return `**Mock Evaluation for ${githubLink}:**\n\n${MOCK_EVALUATION}`;
  }

  try {
    const prompt = `
      As a senior engineering manager, provide a brief, insightful code review for a project submitted via this GitHub link: ${githubLink}.
      
      Focus on the following aspects:
      1.  **Overall Assessment:** A short summary of your impressions.
      2.  **Strengths:** 2-3 bullet points on what the candidate did well (e.g., code structure, clarity, feature implementation).
      3.  **Areas for Improvement:** 2-3 bullet points on what could be improved (e.g., error handling, performance, testing, documentation).
      4.  **Recommendation:** A concluding sentence on their suitability for a senior role.

      Format the entire response in Markdown. Do not include any introductory or concluding phrases outside of this structure.
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
    });

    return response.text;
  } catch (error) {
    console.error("Error calling Gemini API:", error);
    return "Error generating AI evaluation. Please try again later.";
  }
};

export const generateInterviewQuestions = async (job: JobPosting): Promise<string[]> => {
  if (!API_KEY) {
    await new Promise(resolve => setTimeout(resolve, 1500));
    return [
      `Mock question: What is your experience with React for the ${job.title} role?`,
      "Mock question: Describe a challenging project you worked on in the cloud space.",
      "Mock question: How do you approach designing scalable systems?",
      "Mock question: Explain the importance of CI/CD in modern software development.",
      "Mock question: How would you troubleshoot a performance issue in a web application?"
    ];
  }

  try {
    const prompt = `
      Generate a list of 5 insightful interview questions for a '${job.title}' candidate in the '${job.division}' division.
      The interview process is described as: "${job.process}".
      The questions should assess both technical skills and problem-solving abilities relevant to the role.
      Focus on practical, open-ended questions.
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: 'application/json',
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            questions: {
              type: Type.ARRAY,
              items: {
                type: Type.STRING,
                description: "An interview question."
              }
            }
          }
        }
      }
    });
    
    const jsonResponse = JSON.parse(response.text.trim());
    return jsonResponse.questions || [];

  } catch (error) {
    console.error("Error calling Gemini API for interview questions:", error);
    return ["Error generating questions. Please try again."];
  }
};

export const generateAssessorReview = async (evaluation: string | null, vote: Vote, jobTitle: string): Promise<string> => {
   if (!API_KEY) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return `This is a mock review based on the vote '${vote}'. The candidate's AI evaluation was considered. They seem like a promising candidate for the ${jobTitle} position, though there are some areas for improvement as noted.`;
  }
  
  try {
     const prompt = `
      You are an engineering manager writing a concise review for a candidate applying for a '${jobTitle}' role.
      The candidate has been given a vote of '${vote}'.
      Here is the automated code evaluation for their submission:
      ---
      ${evaluation || 'No automated evaluation was provided.'}
      ---
      Based on the vote and the evaluation, write a 2-3 sentence review.
      - If the vote is 'Accept', the tone should be positive, highlighting strengths while briefly mentioning areas for growth.
      - If the vote is 'Reject', the tone should be constructive but clear about the reasons for not moving forward, referencing the weaknesses from the evaluation.
      - If the vote is 'Defer to Victor', the tone should be neutral, summarizing the pros and cons and stating why the decision is being deferred.
      Do not add any introductory or concluding phrases like "My review is:" or "Overall...". Just provide the review text itself.
    `;

    const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: prompt,
    });
    
    return response.text;

  } catch (error) {
    console.error("Error calling Gemini API for assessor review:", error);
    return "Error generating AI review. Please try again later.";
  }
};

export const parseCv = async (base64Content: string, mimeType: string): Promise<{ name: string; email: string }> => {
  if (!API_KEY) {
    await new Promise(resolve => setTimeout(resolve, 1500));
    return { name: `Mock Candidate`, email: 'mock.cv.candidate@example.com' };
  }

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: {
        parts: [
          {
            inlineData: {
              data: base64Content,
              mimeType,
            },
          },
          { text: "Extract the full name and email address from this resume/CV document. Provide the output in JSON format." },
        ],
      },
      config: {
        responseMimeType: 'application/json',
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            name: {
              type: Type.STRING,
              description: "The candidate's full name.",
            },
            email: {
              type: Type.STRING,
              description: "The candidate's email address.",
            },
          },
          required: ['name', 'email'],
        },
      },
    });

    const parsedJson = JSON.parse(response.text.trim());
    if (!parsedJson.name || !parsedJson.email) {
        throw new Error("Parsed JSON is missing name or email.");
    }
    return parsedJson;

  } catch (error) {
    console.error("Error calling Gemini API for CV parsing:", error);
    throw new Error("Failed to parse CV with AI. The document might be unreadable or in an unsupported format.");
  }
};

export const generateFeedbackReport = async (
  candidate: Candidate, 
  job: JobPosting, 
  reportType: 'preliminary' | 'final'
): Promise<string> => {
  if (!API_KEY) {
    await new Promise(resolve => setTimeout(resolve, 1500));
    return `
# ${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Feedback Report for ${candidate.name}

**Role:** ${job.title}

---

### Summary
This is a mock-generated report. The candidate has shown strong potential. The final decision was **${candidate.status === CandidateStatus.ACCEPTED ? 'Accepted for Interview' : 'Rejected'}**.

### Strengths
- Good understanding of core concepts.
- Clean and well-structured code submission.

### Areas for Improvement
- More comprehensive testing could be beneficial.
- Lacks documentation in some areas.

### Next Steps
${reportType === 'final' 
  ? (candidate.status === CandidateStatus.ACCEPTED 
      ? 'We will be in touch shortly to schedule the next round of interviews.' 
      : 'While we are not moving forward at this time, we encourage you to apply for future roles.') 
  : 'The assessment is still in progress. Further review is required.'
}
    `;
  }

  try {
    const reviewsSummary = candidate.assessments
      .filter(a => a.review.trim() !== '')
      .map(a => `- Assessor (${a.vote}): "${a.review}"`)
      .join('\n');
      
    const finalDecision = `The final decision for this candidate is: **${candidate.status}**.`;

    const prompt = `
      As an impartial and professional HR manager, generate a candidate feedback report. The report should be encouraging and constructive, even if the feedback is negative.
      The report is for a candidate named '${candidate.name}' who applied for the '${job.title}' role.
      
      This is a '${reportType}' report.
      - A 'preliminary' report is for internal discussion while assessment is ongoing.
      - A 'final' report is generated after a decision has been made and can be shared with the candidate.

      Here is the available information:
      
      **Automated AI Code Evaluation:**
      ---
      ${candidate.automatedEvaluation || 'Not available.'}
      ---
      
      **Internal Assessor Reviews:**
      ---
      ${reviewsSummary || 'No manual reviews submitted yet.'}
      ---
      
      ${reportType === 'final' ? `**Final Decision:**\n${finalDecision}\n---` : ''}

      Based on ALL the information provided, structure the report in Markdown with the following sections:
      - A title: "# ${reportType === 'preliminary' ? 'Preliminary' : 'Final'} Feedback Report for ${candidate.name}"
      - The role they applied for.
      - A horizontal rule.
      - "### Summary": A brief, 2-3 sentence overview of the candidate's performance and the overall outcome.
      - "### Strengths": 2-3 bullet points highlighting what the candidate did well, based on positive aspects from the AI evaluation and assessor reviews.
      - "### Areas for Improvement": 2-3 bullet points on specific, actionable areas for growth, framed constructively.
      - "### Next Steps": 
        - If it's a 'preliminary' report, state that the review is ongoing.
        - If it's a 'final' report, clearly state the outcome based on the final decision. If 'Accepted for Interview', congratulate them and mention next steps. If 'Rejected', thank them for their time and effort and wish them luck, while being clear about the decision.
      
      Do not add any text before the title or after the "Next Steps" section.
    `;
    
    const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: prompt,
    });
    
    return response.text;

  } catch (error) {
    console.error("Error calling Gemini API for feedback report:", error);
    return "Error generating feedback report. Please try again later.";
  }
};


export const generateWorkflowsDocument = async (): Promise<string> => {
    // Simulate a delay as if fetching from a source
    await new Promise(resolve => setTimeout(resolve, 500));

    // Return a detailed, pre-formatted markdown string
    return `
# SkillScribe Application Workflow Guide

This document outlines the primary workflows for using the SkillScribe application to manage the hiring process efficiently.

---

### Workflow 1: Creating a New Job Posting
**Actor:** HR / Recruiter
**Goal:** To add a new, open position to the hiring pipeline.

1.  **Navigate to Dashboard:** From the main "Hiring Overview" dashboard, click the "New Job Posting" button. (Note: This button is currently on the legacy Job Postings view but the principle remains).
2.  **Enter Details:** A modal will appear. Fill in the required fields: "Job Title", "Division", and "Interview Process".
3.  **Create Job:** Click the "Create Job" button.
4.  **Outcome:** The new job posting is created and will now appear in the "Active Job Postings" table on the main dashboard.

---

### Workflow 2: Adding a Candidate to a Job
**Actor:** HR / Recruiter
**Goal:** To add a new candidate who has applied for a specific role.

1.  **Select Job Pipeline:** On the "Hiring Overview" dashboard, find the relevant job in the "Active Job Postings" table and click "View Pipeline".
2.  **Open New Candidate Form:** On the Candidate Dashboard, click the "New Candidate" button.
3.  **Enter Details:** A modal will appear. Fill in the candidate's "Full Name" and "Email Address".
4.  **Add Candidate:** Click the "Add Candidate" button.
5.  **Outcome:** The candidate is added to the job's pipeline with the initial status of "Applied".

---

### Workflow 3: Processing a Candidate's Application
**Actor:** HR / Recruiter
**Goal:** To move a candidate from application to the assessment stage.

1.  **Send Case Study:** For a candidate with "Applied" status, click the "Send Case Study" button. The status will update to "Case Study Sent".
2.  **Submit GitHub Link:** Once the candidate completes the case study and provides a GitHub link, paste the URL into the input field and click "Submit Link". The status updates to "Case Study Submitted".
3.  **Initiate AI Evaluation:** Click the "Start AI Evaluation" button. The system will:
    *   Call the Gemini API to perform a code review.
    *   Assign three random assessors, with the first being the lead.
    *   Update the candidate's status to "In Assessment".
4.  **Outcome:** The candidate is now ready to be reviewed by the assigned assessors.

---

### Workflow 4: Generating AI-Powered Interview Questions
**Actor:** Hiring Manager / Interviewer
**Goal:** To quickly create relevant, insightful interview questions for a specific role.

1.  **Navigate to Candidate Pipeline:** Go to the Candidate Dashboard for the desired job.
2.  **Generate Questions:** Click the "Generate Questions" button.
3.  **View and Copy:** A modal will appear, displaying 5 AI-generated interview questions tailored to the job description. Use the "Copy to Clipboard" button to easily save them.
4.  **Outcome:** The interviewer is equipped with a strong set of questions for the interview process.

---

### Workflow 5: Performing an Assessment
**Actor:** Assessor
**Goal:** To review a candidate's submission and provide a recommendation.

1.  **Access Assessment:** Navigate to the candidate's "Assessment View" by clicking on their card from the pipeline or a filtered list.
2.  **Review Materials:** Carefully review the candidate's information and, most importantly, the "Automated AI Evaluation" section.
3.  **Cast a Vote:** In your designated Assessor Card, select a vote: "Accept", "Reject", or "Defer to Victor".
4.  **Write a Review:** You can either write your own review in the text area or use the "Generate with AI" button. This AI helper uses your vote and the automated evaluation to draft a concise, context-aware review for you.
5.  **Outcome:** Your feedback is saved, contributing to the final hiring decision.

---

### Workflow 6: Making a Final Hiring Decision
**Actor:** Lead Assessor / Hiring Manager
**Goal:** To make the final call on whether to proceed with a candidate.

1.  **Wait for All Votes:** A final decision cannot be made until all assigned assessors have cast their vote.
2.  **Review Team Feedback:** Once all votes are in, the "Final Decision" panel will become active. Review the votes and written feedback from all assessors.
3.  **Make the Call:** Click either "Accept for Interview" or "Reject Candidate".
4.  **Outcome:** The candidate's status is officially updated, concluding the assessment phase. HR is notified to proceed with the next steps.

---

### Workflow 7: Monitoring the Overall Pipeline
**Actor:** HR / Hiring Manager
**Goal:** To get a high-level, actionable view of the entire recruitment process.

1.  **View Dashboard Stats:** The "Hiring Overview" dashboard shows key metrics like "Open Positions", "Total Candidates", "In Assessment", and "Ready for Interview".
2.  **Drill Down into Statuses:** The "In Assessment" and "Ready for Interview" cards are clickable. Clicking them will take you to a filtered view showing all candidates across all jobs who share that status.
3.  **Outcome:** This provides a quick way to identify bottlenecks and see which candidates require immediate attention.
`;
};
