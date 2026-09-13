import React, { useEffect, useState } from 'react';
import { useConversation } from '../hooks/useConversation';
import { useAgent } from '../hooks/useAgent';
import { useDemoCases } from '../hooks/useDemoCases';
import { AppShell } from '../components/layout/AppShell';
import { TopBar } from '../components/layout/TopBar';
import { StatusBar } from '../components/layout/StatusBar';
import { PipelineStepper } from '../components/pipeline/PipelineStepper';
import { ConversationPanel } from '../components/conversation/ConversationPanel';
import { ClassificationCard } from '../components/classification/ClassificationCard';
import { EvidencePanel } from '../components/retrieval/EvidencePanel';
import { RerankingPanel } from '../components/reranking/RerankingPanel';
import { ResponseComposer } from '../components/generation/ResponseComposer';
import { GroundingPanel } from '../components/grounding/GroundingPanel';
import { DecisionPanel } from '../components/escalation/DecisionPanel';
import { TracePanel } from '../components/observability/TracePanel';
import { DemoCaseSelector } from '../components/demo/DemoCaseSelector';
import { CustomLiveChat } from '../components/custom/CustomLiveChat';
import { DemoScenario } from '../types/agent';
import { AppMode } from '../types/customChat';
import { MessageSquare, LayoutGrid } from 'lucide-react';

export const App: React.FC = () => {
  const [appMode, setAppMode] = useState<AppMode>('DEMO_SCENARIOS');

  const {
    conversationId,
    messages,
    addMessage,
    appendAgentMessage,
    resetConversation,
    loadScenario,
    getCurrentMessage,
  } = useConversation();

  const {
    status,
    stages,
    response,
    runAgent,
    reset: resetAgent,
    loadDirectResponse,
  } = useAgent();

  const { scenarios, selectedScenario, selectScenario } = useDemoCases();
  const [, setMockToggle] = useState(0);

  // Initialize with the first scenario
  useEffect(() => {
    loadScenario(selectedScenario);
    loadDirectResponse(selectedScenario.responsePayload);
  }, []);

  const handleSelectScenario = (scenario: DemoScenario) => {
    selectScenario(scenario.id);
    loadScenario(scenario);
    loadDirectResponse(scenario.responsePayload);
  };

  const handleSendMessage = async (text: string, runImmediately: boolean) => {
    const newMsg = addMessage(text, 'CUSTOMER');

    if (runImmediately) {
      const allMessages = [...messages, newMsg];
      const result = await runAgent(conversationId, allMessages);
      if (result && result.escalation.decision === 'AUTO_HANDLE' && result.generated_reply.is_grounded) {
        appendAgentMessage(result.generated_reply.reply);
      }
    }
  };

  const handleSendResponse = (replyText: string) => {
    appendAgentMessage(replyText);
  };

  const handleRegenerate = async () => {
    const result = await runAgent(conversationId, messages);
    if (result && result.escalation.decision === 'AUTO_HANDLE') {
      appendAgentMessage(result.generated_reply.reply);
    }
  };

  const handleTakeOver = () => {
    alert(
      `Session ${conversationId} transferred to human tier. AI summary copied to operator buffer.`
    );
  };

  const handleToggleMock = () => {
    const current = localStorage.getItem('HIVIER_USE_MOCK_AGENT') !== 'false';
    localStorage.setItem('HIVIER_USE_MOCK_AGENT', current ? 'false' : 'true');
    setMockToggle((prev) => prev + 1);
  };

  const isRunning = status === 'running';

  // Mode Switcher Banner rendered at top
  const modeSwitcher = (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '6px var(--space-24)',
        backgroundColor: '#1f1f26',
        borderBottom: '1px solid #2e2e38',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
        <button
          type="button"
          onClick={() => setAppMode('DEMO_SCENARIOS')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 14px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: appMode === 'DEMO_SCENARIOS' ? 'var(--deep-enterprise-green)' : 'transparent',
            color: appMode === 'DEMO_SCENARIOS' ? '#ffffff' : 'var(--muted-slate)',
            border: appMode === 'DEMO_SCENARIOS' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid transparent',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            fontWeight: 600,
            cursor: 'pointer',
            letterSpacing: '0.2px',
          }}
        >
          <LayoutGrid size={12} />
          DEMO SCENARIOS
        </button>

        <button
          type="button"
          onClick={() => setAppMode('CUSTOM_LIVE')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 14px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: appMode === 'CUSTOM_LIVE' ? 'var(--action-blue)' : 'transparent',
            color: appMode === 'CUSTOM_LIVE' ? '#ffffff' : 'var(--muted-slate)',
            border: appMode === 'CUSTOM_LIVE' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid transparent',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            fontWeight: 600,
            cursor: 'pointer',
            letterSpacing: '0.2px',
          }}
        >
          <MessageSquare size={12} />
          CUSTOM LIVE DEMO (AI CHAT)
        </button>
      </div>

      <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--muted-slate)' }}>
        {appMode === 'CUSTOM_LIVE'
          ? 'MODE: Freeform Conversational Workspace'
          : 'MODE: 3-Column Operator Workspace'}
      </div>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--canvas-white)' }}>
      {/* 1. Global Navigation */}
      <TopBar onToggleMockMode={handleToggleMock} />

      {/* 2. Mode Switcher */}
      {modeSwitcher}

      {/* 3. Conditional Mode Rendering */}
      {appMode === 'CUSTOM_LIVE' ? (
        <CustomLiveChat />
      ) : (
        <AppShell
          topBar={<></>}
          demoSelector={
            <DemoCaseSelector
              scenarios={scenarios}
              selectedScenarioId={selectedScenario.id}
              onSelectScenario={handleSelectScenario}
              isRunning={isRunning}
            />
          }
          pipelineStepper={<PipelineStepper stages={stages} response={response} />}
          statusBar={
            <StatusBar
              conversationId={conversationId}
              turnCount={messages.length}
              primaryIntent={response?.classification.primary_intent}
              confidence={response?.classification.confidence}
              decision={response?.escalation.decision}
            />
          }
          tracePanel={<TracePanel trace={response?.trace} />}
          conversationCol={
            <ConversationPanel
              conversationId={conversationId}
              messages={messages}
              classification={response?.classification}
              isRunning={isRunning}
              onSendMessage={handleSendMessage}
              onReset={() => {
                resetConversation();
                resetAgent();
              }}
            />
          }
          intelligenceCol={
            <>
              <ClassificationCard classification={response?.classification} />
              <EvidencePanel
                evidenceList={response?.retrieved_evidence || []}
                retrievalQuery={response?.retrieval_query}
              />
              <RerankingPanel reranking={response?.reranking} />
            </>
          }
          responseCol={
            <>
              <ResponseComposer
                generatedReply={response?.generated_reply}
                decision={response?.escalation.decision}
                onSendResponse={handleSendResponse}
                onRegenerate={handleRegenerate}
                onTakeOver={handleTakeOver}
                isRunning={isRunning}
              />
              <GroundingPanel grounding={response?.grounding} />
              <DecisionPanel
                response={response}
                currentCustomerMessage={getCurrentMessage()}
                onTakeOver={handleTakeOver}
              />
            </>
          }
        />
      )}
    </div>
  );
};

export default App;
