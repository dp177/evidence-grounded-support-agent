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
import { DemoScenario } from '../types/agent';

export const App: React.FC = () => {
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

  return (
    <AppShell
      topBar={<TopBar onToggleMockMode={handleToggleMock} />}
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
  );
};
export default App;
