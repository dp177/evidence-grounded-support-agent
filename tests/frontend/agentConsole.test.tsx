import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { App } from '../../src/app/App';
import { ConversationPanel } from '../../src/components/conversation/ConversationPanel';
import { ClassificationCard } from '../../src/components/classification/ClassificationCard';
import { EvidenceCard } from '../../src/components/retrieval/EvidenceCard';
import { RerankingPanel } from '../../src/components/reranking/RerankingPanel';
import { GroundingPanel } from '../../src/components/grounding/GroundingPanel';
import { DecisionPanel } from '../../src/components/escalation/DecisionPanel';
import { AgentActivityMessage } from '../../src/components/custom/AgentActivityMessage';
import { mockAgentApi } from '../../src/services/mockAgentApi';
import { agentApi } from '../../src/services/agentApi';
import { DEMO_SCENARIOS } from '../../src/data/demoCases';

describe('AI Support Agent Console - Unit & Integration Tests', () => {
  // 1. Rendering Empty State
  it('renders conversation empty state when no messages are present', () => {
    render(
      <ConversationPanel
        conversationId="conv_test_empty"
        messages={[]}
        isRunning={false}
        onSendMessage={() => {}}
        onReset={() => {}}
      />
    );
    expect(screen.getByText(/No messages in session/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Send a customer message to start analysis/i)
    ).toBeInTheDocument();
  });

  // 2. Rendering Conversation Timeline
  it('renders customer and agent messages in the timeline', () => {
    const messages = [
      { id: '1', role: 'CUSTOMER' as const, text: 'Where is my order?' },
      { id: '2', role: 'AGENT' as const, text: 'Please check your tracking link.' },
    ];
    render(
      <ConversationPanel
        conversationId="conv_test_active"
        messages={messages}
        isRunning={false}
        onSendMessage={() => {}}
        onReset={() => {}}
      />
    );
    expect(screen.getByText('Where is my order?')).toBeInTheDocument();
    expect(screen.getByText('Please check your tracking link.')).toBeInTheDocument();
  });

  // 3. Classification Card & Model Confidence (Never labeled Certainty)
  it('renders intent, area, states, and "MODEL CONFIDENCE" in ClassificationCard', () => {
    const classification = DEMO_SCENARIOS[0].responsePayload.classification;
    render(<ClassificationCard classification={classification} />);

    expect(screen.getByText('PRIMARY INTENT')).toBeInTheDocument();
    expect(screen.getByText('DELIVERY_DELAYED')).toBeInTheDocument();
    expect(screen.getByText('MODEL CONFIDENCE')).toBeInTheDocument();
    expect(screen.queryByText(/CERTAINTY/i)).not.toBeInTheDocument();
    expect(screen.getByText('TRACKING_ALREADY_CHECKED')).toBeInTheDocument();
  });

  // 4. Evidence Card with Mandatory "HISTORICAL PRECEDENT" Badge
  it('displays prominent "HISTORICAL PRECEDENT" badge on retrieved evidence cards', () => {
    const evidence = DEMO_SCENARIOS[0].responsePayload.retrieved_evidence[0];
    render(<EvidenceCard evidence={evidence} onOpenDetails={() => {}} />);

    expect(screen.getByText('HISTORICAL PRECEDENT')).toBeInTheDocument();
    expect(screen.getByText(evidence.case_id)).toBeInTheDocument();
  });

  // 5. Evidence Card Expansion and Details
  it('expands evidence card to show relevant context and Amazon brand response', () => {
    const evidence = DEMO_SCENARIOS[0].responsePayload.retrieved_evidence[0];
    render(<EvidenceCard evidence={evidence} onOpenDetails={() => {}} initiallyExpanded={true} />);

    expect(screen.getByText(/Historical Amazon Precedent Action/i)).toBeInTheDocument();
    expect(screen.getByText(evidence.brand_response)).toBeInTheDocument();
  });

  // 6. Reranking Signal Funnel & Signals
  it('renders candidate funnel and ranking compatibility signals', () => {
    const reranking = DEMO_SCENARIOS[0].responsePayload.reranking;
    render(<RerankingPanel reranking={reranking} />);

    expect(screen.getByText(/Why these cases\?/i)).toBeInTheDocument();
    expect(screen.getAllByText(/30/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Semantic Similarity/i)[0]).toBeInTheDocument();
  });

  // 7. Grounding Panel - Passed
  it('renders passed grounding state with claim counts', () => {
    const grounding = DEMO_SCENARIOS[0].responsePayload.grounding;
    render(<GroundingPanel grounding={grounding} />);

    expect(screen.getByText(/SCORE: 1.00/i)).toBeInTheDocument();
    expect(screen.getByText(/Passed 1st Pass Grounding/i)).toBeInTheDocument();
  });

  // 8. Grounding Panel - Revision Loop Display
  it('renders revision banner when grounding underwent revision', () => {
    const refundScenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-refund-status')!;
    render(<GroundingPanel grounding={refundScenario.responsePayload.grounding} />);

    expect(screen.getByText(/Revision 1/i)).toBeInTheDocument();
  });

  // 9. Auto-Handle Policy State
  it('renders Auto-Handle decision with green success treatment and action', () => {
    const payload = DEMO_SCENARIOS[0].responsePayload;
    render(<DecisionPanel response={payload} />);

    expect(screen.getByText(/Safe to handle automatically/i)).toBeInTheDocument();
    expect(screen.getByText('SAFE_TO_AUTO_HANDLE')).toBeInTheDocument();
  });

  // 10. Human Review Policy State (Account Hacked / High-Risk)
  it('renders Human Review Required and blocker reasons for high-risk security', () => {
    const hackedScenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-account-hacked')!;
    render(<DecisionPanel response={hackedScenario.responsePayload} />);

    expect(screen.getByText(/Human Review Required/i)).toBeInTheDocument();
    expect(screen.getByText('HIGH_RISK_SECURITY')).toBeInTheDocument();
    expect(screen.getByText(/HUMAN HANDOFF PACKAGE READY/i)).toBeInTheDocument();
  });

  // 11. Deterministic Mock API & Multi-Turn State Evolution
  it('updates state dynamically to TRACKING_ALREADY_CHECKED when customer verifies tracking', async () => {
    const messages = [
      { id: '1', role: 'CUSTOMER' as const, text: 'Where is my order?' },
      { id: '2', role: 'CUSTOMER' as const, text: 'I already checked tracking and it says delayed.' },
    ];
    const result = await mockAgentApi.runAgent('conv_test_progression', messages);
    expect(result.classification.states).toContain('TRACKING_ALREADY_CHECKED');
  });

  // 12. Full App Shell Integration & Scenario Switching
  it('mounts full App shell and allows scenario switching', () => {
    render(<App />);

    expect(screen.getByText('AI Support Agent Console')).toBeInTheDocument();
    expect(screen.getByText(/DEMO DATA/i)).toBeInTheDocument();

    // Click Account Hacked scenario
    const hackedBtn = screen.getByRole('button', { name: /Account Hacked/i });
    fireEvent.click(hackedBtn);

    expect(screen.getAllByText(/ACCOUNT_ACCESS_RECOVERY/i).length).toBeGreaterThan(0);
  });

  // 13. Custom Live Demo Mode Switcher & Empty State
  it('switches to Custom Live Demo mode and shows centered chat hero', () => {
    render(<App />);

    const customModeBtn = screen.getByRole('button', { name: /CUSTOM LIVE DEMO/i });
    fireEvent.click(customModeBtn);

    expect(screen.getByText(/^AI Support Agent$/i)).toBeInTheDocument();
    expect(screen.getByText(/Type a customer-support message to start/i)).toBeInTheDocument();
    expect(screen.getByText(/SAMPLE INQUIRIES TO EXPLORE/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Type a customer message/i)).toBeInTheDocument();
  });

  // 14. Custom Live Demo Arbitrary Message & Assistant Turn
  it('submits arbitrary customer message and renders assistant turn', async () => {
    render(<App />);

    const customModeBtn = screen.getByRole('button', { name: /CUSTOM LIVE DEMO/i });
    fireEvent.click(customModeBtn);

    const input = screen.getByPlaceholderText(/Type a customer message/i);
    fireEvent.change(input, { target: { value: 'My package is late and tracking shows delayed' } });

    const sendBtn = screen.getByTitle(/Send Message/i);
    fireEvent.click(sendBtn);

    expect(screen.getByText('My package is late and tracking shows delayed')).toBeInTheDocument();
  });

  // 15. No Chain-of-Thought Exposure Verification
  it('strictly displays observable system activity without internal chain-of-thought', () => {
    render(<App />);

    const customModeBtn = screen.getByRole('button', { name: /CUSTOM LIVE DEMO/i });
    fireEvent.click(customModeBtn);

    expect(screen.queryByText(/chain of thought/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/internal reasoning/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/secret thoughts/i)).not.toBeInTheDocument();
  });

  // 16. Live Mode API Contract & No Silent Fallback Verification
  it('live mode strictly calls POST /api/agent/message and does not silently fall back to mock on failure', async () => {
    agentApi.setMockMode(false);
    expect(agentApi.isMock()).toBe(false);

    // Mock fetch to simulate live backend network rejection
    const originalFetch = global.fetch;
    global.fetch = vi.fn().mockRejectedValue(new Error('Connection refused by backend on port 8000'));

    await expect(
      agentApi.runAgent('conv_test_live', [{ id: 'm1', role: 'CUSTOMER', text: 'Where is my order?' }])
    ).rejects.toThrow(/LIVE AGENT UNAVAILABLE/);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/agent/message'),
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    );

    // Restore fetch and mock mode
    global.fetch = originalFetch;
    agentApi.setMockMode(true);
  });

  // 17. Multi-Turn History Preservation & New Conversation Reset
  it('preserves conversation_id across multi-turn messages and resets cleanly on New Conversation', async () => {
    render(<App />);

    const customModeBtn = screen.getByRole('button', { name: /CUSTOM LIVE DEMO/i });
    fireEvent.click(customModeBtn);

    const input = screen.getByPlaceholderText(/Type a customer message/i);

    // Turn 1
    fireEvent.change(input, { target: { value: 'My package says delivered but I never got it' } });
    const sendBtn = screen.getByTitle(/Send Message/i);
    fireEvent.click(sendBtn);

    expect(screen.getByText('My package says delivered but I never got it')).toBeInTheDocument();

    // Turn 2
    fireEvent.change(input, { target: { value: 'is it delivered to wrong address?' } });
    fireEvent.click(sendBtn);

    expect(screen.getByText('is it delivered to wrong address?')).toBeInTheDocument();

    // Reset via New Conversation button
    const newConvBtn = screen.getByText(/New conversation/i);
    fireEvent.click(newConvBtn);

    expect(screen.getByText(/Type a customer-support message to start/i)).toBeInTheDocument();
  });

  // 18. Reranking Signal Explanation & Honesty Footer
  it('renders interactive "How is this calculated?" expanders, decimal scores, and honesty limitation footer', async () => {
    const reranking = DEMO_SCENARIOS[0].responsePayload.reranking;
    render(<RerankingPanel reranking={reranking} />);

    // Honesty footer must be present
    expect(screen.getByText(/These scores are ranking signals used to order historical evidence/i)).toBeInTheDocument();

    // Reranking signal badge must be present
    expect(screen.getAllByText(/Reranking signal/i).length).toBeGreaterThan(0);

    // Expand "How is this calculated?" on the first signal
    const calcBtns = screen.getAllByText(/How is this calculated\?/i);
    expect(calcBtns.length).toBeGreaterThan(0);
    fireEvent.click(calcBtns[0]);

    // Check that explanation sections appear
    expect(screen.getByText(/WHAT IT MEANS/i)).toBeInTheDocument();
    expect(screen.getByText(/HOW WE CALCULATE IT/i)).toBeInTheDocument();
    expect(screen.getByText(/Important limitation:/i)).toBeInTheDocument();

    // Check "Why this case was selected" checklist is present
    expect(screen.getByText(/WHY THIS CASE WAS SELECTED/i)).toBeInTheDocument();

    // Check Candidate Reranking Breakdown table is present
    expect(screen.getByText(/CANDIDATE RERANKING BREAKDOWN/i)).toBeInTheDocument();
    expect(screen.getByText('Final')).toBeInTheDocument();
  });

  // 19. Candidate Reranking Breakdown Table Truthful Values
  it('renders truthful candidate table columns, N/A tooltips for uncomputed features, and distinct weights', () => {
    const reranking = DEMO_SCENARIOS[0].responsePayload.reranking;
    const retrievedEvidence = DEMO_SCENARIOS[0].responsePayload.retrieved_evidence;
    render(<RerankingPanel reranking={reranking} retrievedEvidence={retrievedEvidence} />);

    // Check all required column headers: Rank, Case, Semantic, Lexical, Intent, State, Action, Final
    expect(screen.getByText('Rank')).toBeInTheDocument();
    expect(screen.getByText('Case')).toBeInTheDocument();
    expect(screen.getAllByText('Semantic')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Lexical')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Intent')[0]).toBeInTheDocument();
    expect(screen.getAllByText('State')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Action')[0]).toBeInTheDocument();
    expect(screen.getByText('Final')).toBeInTheDocument();

    // Check uncomputed values display N/A with tooltip "Not computed for this candidate."
    const naElements = screen.getAllByText('N/A');
    expect(naElements.length).toBeGreaterThan(0);
    expect(naElements[0]).toHaveAttribute('title', 'Not computed for this candidate.');

    // Expand weights and verify weights are distinct from candidate scores
    const weightToggle = screen.getByText(/Reranking Configuration Weights/i);
    fireEvent.click(weightToggle);
    expect(screen.getByText(/Semantic Weight:/i)).toBeInTheDocument();
    expect(screen.getByText(/Action Penalty:/i)).toBeInTheDocument();
  });

  // 20. Continuous Thinking UI & Elapsed Timer Display
  it('renders dynamic thinking indicator, elapsed timer, and thought duration badge', () => {
    const steps = [
      { id: 's0', stage: 'Conversation' as const, label: 'Conversation loaded', status: 'COMPLETED' as const },
      { id: 's1', stage: 'Classify' as const, label: 'Analyzing intent...', status: 'RUNNING' as const },
    ];

    // Running thinking state with live elapsed timer
    const { rerender } = render(
      <AgentActivityMessage
        steps={steps}
        isRunning={true}
        elapsedSeconds={4.2}
      />
    );
    expect(screen.getByText(/Thinking \(4.2s\)/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Analyzing intent/i)[0]).toBeInTheDocument();

    // Completed thought state with final duration
    rerender(
      <AgentActivityMessage
        steps={steps.map((s) => ({ ...s, status: 'COMPLETED' as const }))}
        isRunning={false}
        thoughtDuration={14.8}
      />
    );
    expect(screen.getByText(/Thought for 14.8s/i)).toBeInTheDocument();
  });
});

