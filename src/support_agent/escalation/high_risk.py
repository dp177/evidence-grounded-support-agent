"""Deterministic high-risk escalation overrides.

Implements strict policy overrides with clear precedence:
1. Account security compromise (hacked, unauthorized changes, broke into, hijacked, takeover)
2. Repeated unsuccessful support attempts (multiple contacts, transferred repeatedly, unfulfilled callback)
3. Carrier misconduct and delivery refusal (driver refusal, hostile driver, demanding customer meet at vehicle, package thrown)
4. Account lockout with inability to access after failed recovery attempts

These overrides mandate escalation (decision: HUMAN_REVIEW) and override
both SAFE_TO_AUTO_HANDLE and SAFE_CLARIFICATION.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

# A. Account Security Compromise Indicators
SECURITY_COMPROMISE_PATTERNS = [
    r"\b(?:account\s+)?hacked\b",
    r"\bhacker\b",
    r"\bcompromised\b",
    r"\bunauthori[zs]ed\b",
    r"\bwithout\s+(?:my\s+)?authori[zs]ation\b",
    r"\bwithout\s+(?:my\s+)?permission\b",
    r"\bnot\s+me\b",
    r"\bwasn'?t\s+me\b",
    r"\bdidn'?t\s+authori[zs]e\b",
    r"\bsomeone\s+(?:else\s+)?(?:accessed|logged\s+into|hacked|used|broke\s+into|infiltrated)\s+(?:my\s+)?account\b",
    r"\b(?:someone|somebody|intruder)\s+broke\s+into\b",
    r"\baccount\s+(?:was\s+|got\s+|is\s+|has\s+been\s+)?(?:hijacked|hacked|compromised|taken\s+over|infiltrated)\b",
    r"\baccount\s+hijacked\b",
    r"\bsuspicious\s+(?:account\s+)?activity\b",
    r"\b(?:email|password|phone(?:\s+number)?)\s+(?:was\s+)?changed\s+without\s+authori[zs]ation\b",
    r"\b(?:email|password|phone(?:\s+number)?)\s+and\s+(?:email|password|phone(?:\s+number)?)\s+changed\b",
    r"\bsomeone\s+changed\s+(?:both\s+)?(?:my\s+)?(?:primary\s+)?(?:email|password|phone|recovery)\b",
    r"\b(?:never|didn'?t|did\s+not|haven'?t|have\s+not)\s+(?:request(?:ed)?|authori[zs]e|made\s+(?:any\s+)?request\s+(?:to\s+change|for))\s+.*?\b(?:password|email|phone|credentials?)\b",
    r"\bnever\s+requested\s+(?:a\s+|that\s+)?(?:password|email)\s+change\b",
    r"\b(?:password|email)\s+changed\s+without\s+(?:my\s+)?(?:knowledge|consent|request)\b",
    r"\bidentity\s+theft\b",
    r"\baccount\s+takeover\b",
    r"\badded\s+(?:their|unknown|unauthorized)\s+.*?\bas\s+2fa\b",
    r"\b(?:broke\s+into|hacked|hijacked|compromised)\b.*?\b(?:ordered|purchased|bought|charged)\b",
]

# B. Repeated Failed Support Attempts Indicators
REPEATED_SUPPORT_PATTERNS = [
    r"\b(?:contacted|called|messaged|spoke\s+to|talked\s+to|reached\s+out\s+to|chatted\s+with|emailed)\s+(?:customer\s+(?:care|service)|support|help|rep|agent|amazon)\b.*?\b(?:multiple|several|\d+|more\s+than|many|repeatedly|separate)\s+(?:times|attempts|occasions)\b",
    r"\b(?:called|contacted|emailed|messaged)\s+(?:\d+|several|multiple|repeatedly)\s+(?:separate\s+)?times\b",
    r"\b(?:more\s+than|over)\s+(?:\d+|one|two|three|four|five)\s+times\b",
    r"\b(?:contacted\s+customer\s+care|contacted\s+support)\s+more\s+than\b",
    r"\balready\s+contacted\s+(?:support|customer\s+care|service|help|amazon)\b.*?\b(?:no\s+help|unresolved|no\s+luck|again|still)\b",
    r"\bstill\s+no\s+luck\b",
    r"\bno\s+one\s+(?:has\s+)?helped\b",
    r"\bno\s+one\s+has\s+been\s+able\s+to\s+resolve\b",
    r"\brepeated\s+(?:attempts|calls|emails|messages)\b",
    r"\b(?:getting|kept\s+getting)\s+the\s+(?:same\s+)?run\s*around\b",
    r"\bno\s+resolution\s+(?:was\s+)?offered\b",
    r"\b(?:rep|agent)\s+(?:just\s+)?hung\s+up\s+on\s+me\b",
    r"\bfollowing\s+(?:up\s+)?(?:from|for)\s+\d+\s+(?:days|weeks|months)\b",
    r"\bsent\s+(?:four|\d+)\s+faxes.*called\s+\d+\s+times\b",
    r"\bassigned\s+\d+\s+different\s+case\s+numbers\b",
    r"\b(?:transferred|redirected|bounced|transfers\s+me)\b.*?\b(?:someone\s+else|another|department)\b",
    r"\beach\s+representative\s+transfers\s+me\b",
    r"\b(?:promised|scheduled)\s+(?:a\s+)?(?:callback|call\s*back|call|response)\s+.*?\b(?:never\s+(?:came|happened|called)|didn'?t\s+call)\b",
    r"\bcallback\s+(?:that\s+)?never\s+came\b",
    r"\bcalled\s+support\s+repeatedly\b",
    r"\brescheduled\s+(?:this\s+)?(?:return\s+)?pickup\s+\d+\s+times\b",
    r"\bcontacted\s+support\s+.*?\bacross\s+\d+\s+attempts\b",
]

# C. Carrier Misconduct / Delivery Refusal Indicators
CARRIER_MISCONDUCT_PATTERNS = [
    r"\b(?:driver|courier|delivery\s+(?:agent|person|driver))\s+refused\s+to\s+(?:deliver|bring|drop|walk|climb|hand\s+over)\b",
    r"\brefused\s+to\s+(?:deliver|bring|drop|hand\s+over|bring\s+parcel)\b",
    r"\brefusing\s+to\s+(?:deliver|bring|drop)\b",
    r"\bdelivery\s+refusal\b",
    r"\bchronic\s+delivery\s+refusal\b",
    r"\brefused\s+to\s+enter\s+(?:my\s+)?(?:gated\s+community|gate|building)\b",
    r"\b(?:driver|courier)\s+(?:demanded|demanding|insisted|told\s+me)\s+.*?\b(?:walk|come\s+down|meet|pick\s*up)\b",
    r"\bdemanded\s+i\s+(?:walk|come\s+down|meet|pick\s*up)\b",
    r"\btold\s+me\s+to\s+(?:come\s+down|pickup\s+from\s+depot)\b",
    r"\b(?:driver|courier|delivery\s+person)\s+(?:was\s+)?(?:extremely\s+)?(?:aggressive|hostile|belligerent|violent|threatening)\b",
    r"\b(?:driver|courier|delivery\s+person)\s+(?:shouted|screamed|cursed|swore|used\s+profanity)\b",
    r"\brudely\s+shouted\b",
    r"\bdemanded\s+a\s+(?:cash\s+)?tip\b",
    r"\b(?:driver|courier)\s+(?:threw|tossed|flung|chucked)\s+(?:the\s+)?(?:box|package|parcel)\b",
    r"\bthrew\s+(?:the\s+)?(?:heavy\s+)?(?:box|package|parcel)\b",
    r"\bforged\s+(?:my\s+)?signature\b",
]

# D. Account Lockout with Inability to Access After Failed Recovery
ACCOUNT_LOCK_PATTERNS = [
    r"\b(?:account\s+)?(?:is\s+|was\s+|been\s+)?(?:locked|blocked|put\s+on\s+hold|suspended|on\s+hold)\b",
    r"\bdecided\s+an\s+order.*was\s+suspicious\s+and\s+locked\s+my\s+account\b",
    r"\baccount\s+locked\b",
    r"\baccount\s+has\s+been\s+locked\b",
    r"\baccount\s+is\s+put\s+on\s+hold\b",
]

FAILED_RECOVERY_SIGNALS = [
    r"\bpassword\s+reset\s+appears\s+to\s+work\s+but\s+still\s+can'?t\s+log\s+in\b",
    r"\bpassword\s+reset\s+(?:failed|not\s+working|loop|does\s+not\s+work)\b",
    r"\bcan'?t\s+(?:sign\s+in|log\s+in)\s+because\s+(?:my\s+)?account\s+(?:has\s+been|is|was)\s+locked\b",
    r"\bresponded\s+to\s+(?:the\s+)?(?:address\s+verification|email|fax)\b",
    r"\bsent\s+(?:fax|faxes|email|emails|documents)\b",
    r"\bfollowing\s+(?:up\s+)?(?:from|for)\s+\d+\s+weeks\s+to\s+unhold\b",
    r"\btrying\s+to\s+solve\b.*\blocked\b",
    r"\bverification\s+failed\b",
]


def evaluate_high_risk_escalation(
    customer_conversation: Dict[str, Any],
    classification: Optional[Dict[str, Any]] = None,
    conversation_state: Optional[List[str]] = None,
) -> Optional[Dict[str, str]]:
    """Evaluate deterministic high-risk escalation overrides with explicit precedence.

    Precedence:
    1. Account Security Compromise
    2. Repeated Failed Support Attempts
    3. Carrier Misconduct and Delivery Refusal
    4. Account Lockout After Failed Recovery Attempts

    Returns dict with reason_code and message if an override applies, else None.
    """
    msg = str(customer_conversation.get("customer_message") or "").strip().lower()
    ctx = str(customer_conversation.get("context") or "").strip().lower()
    full_text = f"{ctx} {msg}".strip()

    if not full_text:
        return None

    # Precedence 1: Account Security Compromise
    for pat in SECURITY_COMPROMISE_PATTERNS:
        if re.search(pat, full_text, re.IGNORECASE):
            return {
                "override_type": "SECURITY_COMPROMISE",
                "reason_code": "ACCOUNT_SECURITY_COMPROMISE",
                "message": "Account security compromise indicators detected requiring mandatory specialist review.",
            }

    # Precedence 2: Repeated Failed Support Attempts
    # Direct pattern match
    for pat in REPEATED_SUPPORT_PATTERNS:
        if re.search(pat, full_text, re.IGNORECASE):
            return {
                "override_type": "REPEATED_FAILED_SUPPORT",
                "reason_code": "REPEATED_FAILED_SUPPORT_ATTEMPTS",
                "message": "Customer reports repeated unsuccessful support attempts requiring human specialist escalation.",
            }

    # Structured state integration: WAITING_WINDOW_EXCEEDED with prior support contact
    states = conversation_state or (classification.get("states", []) if classification else [])
    state_set = set(states) if isinstance(states, list) else {str(states)}
    if "WAITING_WINDOW_EXCEEDED" in state_set:
        prior_support_indicators = [
            r"\b(?:contacted|called|messaged|spoke\s+to|talked\s+to|chatted\s+with|reached\s+out\s+to)\s+(?:customer\s+(?:care|service)|support|help|agent|rep|amazon)\b",
            r"\b(?:support|agent|rep|customer\s+care)\s+(?:told\s+me|promised|said|advised|transfers?)\b",
            r"\bcallback\b",
            r"\bticket\s*#?\s*\d+\b",
            r"\brescheduled\b",
            r"\brepeatedly\b",
            r"\bfailed\s+return\s+pickup\b",
        ]
        if any(re.search(pat, full_text, re.IGNORECASE) for pat in prior_support_indicators):
            return {
                "override_type": "REPEATED_FAILED_SUPPORT",
                "reason_code": "REPEATED_FAILED_SUPPORT_ATTEMPTS",
                "message": "Customer reports repeated unsuccessful support attempts or broken service commitments requiring escalation.",
            }

    # Precedence 3: Carrier Misconduct and Delivery Refusal
    for pat in CARRIER_MISCONDUCT_PATTERNS:
        if re.search(pat, full_text, re.IGNORECASE):
            return {
                "override_type": "CARRIER_MISCONDUCT_AND_REFUSAL",
                "reason_code": "CARRIER_MISCONDUCT_AND_REFUSAL",
                "message": "Carrier misconduct or delivery refusal reported requiring human specialist intervention.",
            }

    # Precedence 4: Account Lockout with Inability to Access & Failed Recovery
    has_lock = any(re.search(pat, full_text, re.IGNORECASE) for pat in ACCOUNT_LOCK_PATTERNS)
    has_failed_recovery = any(re.search(pat, full_text, re.IGNORECASE) for pat in FAILED_RECOVERY_SIGNALS)
    prior_attempts_state = bool(state_set & {"WAITING_WINDOW_EXCEEDED", "DETAILS_ALREADY_PROVIDED"})

    if has_lock and (has_failed_recovery or prior_attempts_state or "suspicious" in full_text):
        return {
            "override_type": "ACCOUNT_LOCK_FAILED_RECOVERY",
            "reason_code": "ACCOUNT_SECURITY_COMPROMISE",
            "message": "Account lockout with failed recovery attempts requiring account specialist assistance.",
        }

    return None
