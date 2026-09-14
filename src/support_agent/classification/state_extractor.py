"""Evidence-based conversation state extractor.

Implements strict precedence:
1. repeated failed support / exceeded waiting window -> WAITING_WINDOW_EXCEEDED
2. carrier already contacted                          -> CARRIER_ALREADY_CONTACTED
3. tracking/status already checked                   -> TRACKING_ALREADY_CHECKED
4. required details already provided                 -> DETAILS_ALREADY_PROVIDED
5. otherwise                                         -> INITIAL_INQUIRY
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

# Precedence 1: WAITING_WINDOW_EXCEEDED
REPEATED_FAILED_PATTERNS = [
    r"\b(?:contacted|called|messaged|spoke\s+to|talked\s+to|reached\s+out\s+to|chatted\s+with|emailed)\s+(?:customer\s+(?:care|service)|support|help|rep|agent|amazon)\b.*?\b(?:multiple|several|\d+|more\s+than\s+one|many|repeatedly|separate)\s+(?:times|attempts|occasions)\b",
    r"\b(?:called|contacted|emailed|messaged)\s+(?:\d+|several|multiple|repeatedly)\s+(?:separate\s+)?times\b",
    r"\b(?:more\s+than|over)\s+(?:\d+|one|two|three|four|five)\s+times\b",
    r"\b(?:contacted\s+customer\s+care|contacted\s+support)\s+more\s+than\b",
    r"\balready\s+contacted\s+(?:support|customer\s+care|service|help|amazon)\b",
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
    r"\b(?:transferred|redirected|transfers\s+me)\b.*?\b(?:someone\s+else|another|department)\b",
    r"\beach\s+representative\s+transfers\s+me\b",
    r"\b(?:promised|scheduled|advised)\s+.*?\b(?:callback|call\s*back|call|response)\s+.*?\b(?:never\s+(?:came|happened|called)|didn'?t\s+call)\b",
    r"\bcallback\s+(?:that\s+)?never\s+came\b",
    r"\bcalled\s+support\s+repeatedly\b",
    r"\brescheduled\s+(?:this\s+)?(?:return\s+)?pickup\s+\d+\s+times\b",
    r"\bcontacted\s+support\s+.*?\bacross\s+\d+\s+attempts\b",
    r"\btold\s+to\s+wait\b.*\b(?:days?|hours?|window)\b.*\b(?:passed|exceeded|elapsed|still)\b",
    r"\bwaiting\s+window\s+(?:has\s+)?(?:passed|exceeded|elapsed)\b",
]

# Precedence 2: CARRIER_ALREADY_CONTACTED
CARRIER_CONTACTED_PATTERNS = [
    r"\b(?:contacted|called|spoke\s+to|talked\s+to|reached\s+out\s+to)\s+(?:the\s+)?(?:carrier|courier|delivery\s+(?:agent|person|company|service)|driver|ups|fedex|usps|dhl|hermes|royal\s+mail)\b",
    r"\b(?:carrier|courier|delivery\s+(?:agent|person|company)|driver|ups|fedex|usps|dhl)\s+(?:said|told\s+me|refused|stated|claimed)\b",
    r"\b(?:delivery\s+(?:agent|person)|driver|courier)\s+(?:refused\s+to\s+deliver|demanded|asked\s+me\s+to\s+pickup)\b",
]

# Precedence 3: TRACKING_ALREADY_CHECKED
TRACKING_CHECKED_PATTERNS = [
    r"\b(?:checked|viewed|monitored|saw|looked\s+at)\s+(?:the\s+)?(?:tracking|order\s+status|tracking\s+status|shipment\s+status)\b",
    r"\btracking\s+(?:says|shows|states|indicates|marked\s+as|updates)\b",
    r"\baccording\s+to\s+(?:the\s+)?tracking\b",
    r"\b(?:marked|shows|says)\s+delivered\s+(?:on|in)\s+(?:tracking|the\s+app|website)\b",
    r"\btracking\s+states\b",
]

# Exclusions for tracking checked: e.g. "where can I find my tracking number?"
TRACKING_NUMBER_INQUIRY_PATTERNS = [
    r"\bwhere\s+(?:can\s+i|to)\s+find\s+(?:my\s+)?tracking\s+number\b",
    r"\bhow\s+(?:do\s+i|can\s+i)\s+find\s+(?:my\s+)?tracking\s+number\b",
    r"\bwhat\s+is\s+my\s+tracking\s+number\b",
]

# Precedence 4: DETAILS_ALREADY_PROVIDED
DETAILS_PROVIDED_PATTERNS = [
    r"\b(?:already|previously)\s+(?:provided|sent|given|shared)\s+(?:my\s+)?(?:details|order\s+number|info|information|email|fax|address|documents)\b",
    r"\bsent\s+(?:the\s+)?(?:fax|email|details|order\s+number|documents)\b",
    r"\bprovided\s+(?:my|the)\s+(?:order\s+number|details|info)\b",
    r"\bshared\s+(?:in\s+)?(?:dm|direct\s+message)\b",
]


def extract_conversation_state(
    customer_message: str,
    context: Optional[str] = None,
    model_states: Optional[List[str]] = None,
) -> List[str]:
    """Extract evidence-based conversation state following the defined hierarchy.

    Precedence:
    1. WAITING_WINDOW_EXCEEDED
    2. CARRIER_ALREADY_CONTACTED
    3. TRACKING_ALREADY_CHECKED
    4. DETAILS_ALREADY_PROVIDED
    5. Fallback to model_state (if valid and non-INITIAL_INQUIRY) or INITIAL_INQUIRY
    """
    msg = str(customer_message or "").strip().lower()
    ctx = str(context or "").strip().lower()
    full_text = f"{ctx} {msg}".strip()

    if not full_text:
        return ["INITIAL_INQUIRY"]

    # 1. Check WAITING_WINDOW_EXCEEDED / REPEATED_FAILED_SUPPORT
    for pat in REPEATED_FAILED_PATTERNS:
        if re.search(pat, full_text, re.IGNORECASE):
            return ["WAITING_WINDOW_EXCEEDED"]

    # 2. Check CARRIER_ALREADY_CONTACTED
    for pat in CARRIER_CONTACTED_PATTERNS:
        if re.search(pat, full_text, re.IGNORECASE):
            return ["CARRIER_ALREADY_CONTACTED"]

    # 3. Check TRACKING_ALREADY_CHECKED
    is_tracking_inquiry = any(re.search(pat, msg, re.IGNORECASE) for pat in TRACKING_NUMBER_INQUIRY_PATTERNS)
    if not is_tracking_inquiry:
        for pat in TRACKING_CHECKED_PATTERNS:
            if re.search(pat, full_text, re.IGNORECASE):
                return ["TRACKING_ALREADY_CHECKED"]

    # 4. Check DETAILS_ALREADY_PROVIDED
    for pat in DETAILS_PROVIDED_PATTERNS:
        if re.search(pat, full_text, re.IGNORECASE):
            return ["DETAILS_ALREADY_PROVIDED"]

    # Context turns inspection: if context contains customer providing order ID (e.g. 123-4567890-1234567)
    if ctx and re.search(r"\b\d{3}-\d{7}-\d{7}\b", ctx):
        return ["DETAILS_ALREADY_PROVIDED"]

    # 5. Respect model state if model detected a valid non-default state
    if model_states:
        valid_states = {
            "WAITING_WINDOW_EXCEEDED",
            "CARRIER_ALREADY_CONTACTED",
            "TRACKING_ALREADY_CHECKED",
            "DETAILS_ALREADY_PROVIDED",
        }
        for st in model_states:
            if st in valid_states:
                # If model predicted TRACKING_ALREADY_CHECKED but user just asked where tracking number is, ignore
                if st == "TRACKING_ALREADY_CHECKED" and is_tracking_inquiry:
                    continue
                return [st]

    return ["INITIAL_INQUIRY"]
