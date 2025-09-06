import React, { useMemo } from 'react';
import type { Candidate } from '../types';
import { CandidateStatus } from '../types';

interface PipelineChartProps {
  candidates: Candidate[];
}

interface FunnelStage {
  name: string;
  count: number;
  color: string;
}

const PipelineChart: React.FC<PipelineChartProps> = ({ candidates }) => {
  const funnelData = useMemo(() => {
    const stages: Record<string, number> = {
      'Applied': 0,
      'Screening': 0,
      'In Assessment': 0,
      'Ready for Interview': 0,
    };

    candidates.forEach(c => {
      switch (c.status) {
        case CandidateStatus.APPLIED:
          stages['Applied']++;
          break;
        case CandidateStatus.CASE_STUDY_SENT:
        case CandidateStatus.CASE_STUDY_SUBMITTED:
          stages['Screening']++;
          break;
        case CandidateStatus.ASSESSMENT:
        case CandidateStatus.FINAL_REVIEW:
          stages['In Assessment']++;
          break;
        case CandidateStatus.ACCEPTED:
          stages['Ready for Interview']++;
          break;
        // Rejected candidates are not part of the positive funnel
      }
    });

    const data: FunnelStage[] = [
      { name: 'Applied', count: stages['Applied'], color: 'bg-blue-400' },
      { name: 'Screening', count: stages['Screening'], color: 'bg-yellow-400' },
      { name: 'In Assessment', count: stages['In Assessment'], color: 'bg-indigo-400' },
      { name: 'Ready for Interview', count: stages['Ready for Interview'], color: 'bg-green-400' },
    ];
    
    return data;
  }, [candidates]);

  const maxValue = useMemo(() => {
    const max = Math.max(...funnelData.map(d => d.count));
    return max > 0 ? max : 1; // Avoid division by zero
  }, [funnelData]);

  return (
    <div className="bg-base-100 p-6 rounded-lg shadow-md animate-slide-in-up" style={{ animationDelay: '300ms' }}>
      <h2 className="text-xl font-bold text-text-primary mb-4">Candidate Pipeline Funnel</h2>
      <div className="space-y-4">
        {funnelData.map((stage) => (
          <div key={stage.name} className="flex items-center">
            <div className="w-40 text-sm font-medium text-text-secondary pr-4">{stage.name}</div>
            <div className="flex-grow bg-base-300 rounded-full h-6">
              <div
                className={`${stage.color} h-6 rounded-full flex items-center justify-end pr-2 text-white font-bold text-sm`}
                style={{ width: `${(stage.count / maxValue) * 100}%` }}
              >
                {stage.count > 0 && <span>{stage.count}</span>}
              </div>
            </div>
          </div>
        ))}
         {funnelData.every(stage => stage.count === 0) && (
            <p className="text-center text-text-secondary py-4">No candidate data to display in the funnel yet.</p>
        )}
      </div>
    </div>
  );
};

export default PipelineChart;
