import React, { useState } from 'react';
import { StageInfo, StageName, AgentResponse } from '../../types/agent';
import { PipelineStage } from './PipelineStage';
import { StageDrawer } from './StageDrawer';
import { ChevronRight } from 'lucide-react';

interface PipelineStepperProps {
  stages: StageInfo[];
  response: AgentResponse | null;
}

export const PipelineStepper: React.FC<PipelineStepperProps> = ({
  stages,
  response,
}) => {
  const [activeStage, setActiveStage] = useState<StageName | null>(null);

  return (
    <>
      <nav
        aria-label="Agent Pipeline Progress"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 'var(--space-4)',
          padding: 'var(--space-8) var(--space-24)',
          backgroundColor: '#ffffff',
          borderBottom: '1px solid var(--border-light)',
          overflowX: 'auto',
        }}
      >
        {stages.map((stage, idx) => (
          <React.Fragment key={stage.name}>
            <PipelineStage
              stage={stage}
              isActive={activeStage === stage.name}
              onClick={() => setActiveStage(stage.name)}
            />
            {idx < stages.length - 1 && (
              <ChevronRight size={12} color="var(--hairline)" style={{ flexShrink: 0 }} />
            )}
          </React.Fragment>
        ))}
      </nav>

      <StageDrawer
        stageName={activeStage}
        response={response}
        onClose={() => setActiveStage(null)}
      />
    </>
  );
};
