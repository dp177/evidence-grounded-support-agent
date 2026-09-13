"""Escalation Module — Phase 10.

Deterministic decision engine for Auto-Handle vs Human Escalation.
"""

from support_agent.escalation.decision import decide_escalation
from support_agent.escalation.escalation_policy import (
    EscalationConfig,
    check_state_consistency,
    detect_security_fraud_signals,
    is_clarification_response,
)

__all__ = [
    "decide_escalation",
    "EscalationConfig",
    "check_state_consistency",
    "detect_security_fraud_signals",
    "is_clarification_response",
]
