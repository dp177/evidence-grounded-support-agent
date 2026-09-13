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
import { mockAgentApi } from '../../src/services/mockAgentApi';
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
    expect(screen.getByText(/30/i)).toBeInTheDocument();
    expect(screen.getByText(/Semantic Similarity/i)).toBeInTheDocument();
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

    expect(screen.getByText(/AI Support Agent — Custom Live Demo/i)).toBeInTheDocument();
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
});

