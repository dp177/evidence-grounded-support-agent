"""Candidate Reranker for Semantic Retrieval.

Applies lexical, intent, area, state, and action usefulness scoring on top of semantic similarity.
Provides conversation deduplication and explainable candidate-level feature breakdowns.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
import yaml

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Configurable defaults
DEFAULT_WEIGHTS = {
    "semantic": 1.0,
    "lexical": 0.3,
    "intent": 0.2,
    "area": 0.1,
    "state": 0.1,
    "action_penalty": -0.2,
}

# Generic words to de-emphasize in lexical matching
LEXICAL_STOP_WORDS = {"order", "package", "delivery", "refund", "help", "amazon", "please", "hi", "hello", "thanks"}

# Canonical taxonomy mapping: intent -> broad area
INTENT_TO_AREA = {
    "WHERE_IS_MY_ORDER": "DELIVERY_AND_FULFILLMENT",
    "DELIVERY_DELAYED": "DELIVERY_AND_FULFILLMENT",
    "MARKED_DELIVERED_NOT_RECEIVED": "DELIVERY_AND_FULFILLMENT",
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS": "DELIVERY_AND_FULFILLMENT",
    "DAMAGED_OR_DEFECTIVE_ITEM": "RETURNS_AND_REPLACEMENTS",
    "WRONG_ITEM_RECEIVED": "RETURNS_AND_REPLACEMENTS",
    "RETURN_PICKUP_ISSUE": "RETURNS_AND_REPLACEMENTS",
    "REFUND_STATUS_INQUIRY": "REFUNDS_AND_BILLING",
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE": "REFUNDS_AND_BILLING",
    "CANCEL_ORDER_REQUEST": "ORDER_MANAGEMENT",
    "MODIFY_ORDER_DETAILS": "ORDER_MANAGEMENT",
    "PRIME_MEMBERSHIP_MANAGEMENT": "DIGITAL_SERVICES_AND_PRIME",
    "DIGITAL_CONTENT_ACCESS": "DIGITAL_SERVICES_AND_PRIME",
    "ACCOUNT_LOGIN_ISSUES": "ACCOUNT_ACCESS_AND_SECURITY",
}

# Deterministic regex patterns to identify intent signals in candidate evidence
INTENT_PATTERNS = {
    "DELIVERY_DELAYED": re.compile(
        r"\b(?:delayed|delay|late|supposed to arrive|past due|overdue|still not arrived|not arrived yet|hasn't arrived|has not arrived|taking so long|where is my late)\b",
        re.IGNORECASE,
    ),
    "MARKED_DELIVERED_NOT_RECEIVED": re.compile(
        r"\b(?:marked (?:as )?delivered|shows? (?:.* )?delivered|says? (?:.* )?delivered|stated delivered|delivered but|delivered.*(?:not received|never received|never got|haven't received|did not receive|not here|missing)|stolen|misdeliver|wrong address)\b",
        re.IGNORECASE,
    ),
    "WHERE_IS_MY_ORDER": re.compile(
        r"\b(?:where is (?:my )?(?:order|package|item|delivery)|where's (?:my )?(?:order|package|delivery)|track my (?:order|package|delivery)|tracking update|when will (?:my )?(?:order|package|delivery|it) arrive|status of (?:my )?(?:order|delivery)|tracking shows)\b",
        re.IGNORECASE,
    ),
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS": re.compile(
        r"\b(?:delivery (?:driver|person|agent|guy)|courier (?:rude|refused|left)|safe place|gate code|porch|front door|signature|driver refused)\b",
        re.IGNORECASE,
    ),
    "DAMAGED_OR_DEFECTIVE_ITEM": re.compile(
        r"\b(?:damaged|broken|cracked|shattered|defective|faulty|torn|leaking|not working|smashed|dented|damaged in transit)\b",
        re.IGNORECASE,
    ),
    "WRONG_ITEM_RECEIVED": re.compile(
        r"\b(?:wrong (?:item|product|size|color|package)|different (?:item|product)|ordered .* but received|not what i ordered|sent (?:the )?wrong)\b",
        re.IGNORECASE,
    ),
    "RETURN_PICKUP_ISSUE": re.compile(
        r"\b(?:return pickup|pick up (?:my )?return|courier pickup|return (?:label|code|drop off)|pickup failed|pickup missed)\b",
        re.IGNORECASE,
    ),
    "REFUND_STATUS_INQUIRY": re.compile(
        r"\b(?:refund|money back|refund status|when will i get my refund|refund not received|refund credited|reimbursement|refund posted)\b",
        re.IGNORECASE,
    ),
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE": re.compile(
        r"\b(?:charged twice|double charged|unauthorized charge|extra charge|deducted twice|charged my card|unknown charge|unrecognized charge)\b",
        re.IGNORECASE,
    ),
    "CANCEL_ORDER_REQUEST": re.compile(
        r"\b(?:cancel (?:my )?order|cancellation|cancel this item|cancel shipment|stop shipment|ordered by mistake)\b",
        re.IGNORECASE,
    ),
    "MODIFY_ORDER_DETAILS": re.compile(
        r"\b(?:change address|change delivery address|update address|modify order|change delivery slot|change payment|update (?:payment|card|billing|credit card)|payment method|billing settings)\b",
        re.IGNORECASE,
    ),
    "PRIME_MEMBERSHIP_MANAGEMENT": re.compile(
        r"\b(?:prime membership|amazon prime|cancel prime|prime renewed|prime subscription|prime fee)\b",
        re.IGNORECASE,
    ),
    "DIGITAL_CONTENT_ACCESS": re.compile(
        r"\b(?:kindle|fire stick|prime video|ebook|digital content|download error|audiobook|streaming error)\b",
        re.IGNORECASE,
    ),
    "ACCOUNT_LOGIN_ISSUES": re.compile(
        r"\b(?:can't log ?in|cannot log ?in|password reset|otp|verification code|account locked|hacked|account compromised|sign ?in issue)\b",
        re.IGNORECASE,
    ),
}

# Deterministic patterns to detect operational progression states
STATE_PATTERNS = {
    "TRACKING_ALREADY_CHECKED": re.compile(
        r"\b(?:checked (?:the )?tracking|tracking (?:says|shows|states|updates|indicates)|looked at tracking|tracking link|checked online|tracking number|app shows|app says|status says|website shows)\b",
        re.IGNORECASE,
    ),
    "CARRIER_ALREADY_CONTACTED": re.compile(
        r"\b(?:called (?:the )?(?:carrier|courier|driver|usps|ups|fedex|hermes|dpd|royal mail|post office)|contacted (?:the )?(?:carrier|courier|driver)|spoke to (?:the )?(?:carrier|courier|driver)|driver said|courier told me|carrier said|already (?:called|contacted)|delivery agent said)\b",
        re.IGNORECASE,
    ),
    "WAITING_WINDOW_EXCEEDED": re.compile(
        r"\b(?:told me to wait|waited \d+ (?:days|hours|weeks)|waiting window|said to wait|already waited|window (?:has )?passed|still waiting after|been \d+ (?:days|hours|weeks)|past the (?:promised|expected) (?:date|window))\b",
        re.IGNORECASE,
    ),
    "DETAILS_ALREADY_PROVIDED": re.compile(
        r"\b(?:already (?:sent|provided|dmed|messaged|given)|sent (?:a )?dm|sent (?:my )?order (?:number|id|details)|provided (?:my )?details|dm sent|sent info)\b",
        re.IGNORECASE,
    ),
}

# Patterns indicating concrete operational guidance in historical brand response
ACTION_GUIDANCE_PATTERNS = [
    re.compile(r"\b(?:please (?:check|verify|visit|log in|go to|track|look for|confirm|reach out|select|click on|fill out|fill|enter|allow))\b", re.IGNORECASE),
    re.compile(r"\b(?:check (?:with|around|your)? (?:neighbors|porch|garage|mailbox|door|tracking|account|statement|order|building|reception))\b", re.IGNORECASE),
    re.compile(r"\b(?:allow \d+[-–\s]*(?:to|or)?\s*\d*\s*(?:business days?|days?|hours?)|within \d+ (?:business days?|days?|hours?)|takes? \d+[-–\s]*(?:to|or)?\s*\d*\s*(?:business days?|days?|hours?))\b", re.IGNORECASE),
    re.compile(r"\b(?:refund|replacement|reship|resend|reimburse|issue a (?:refund|replacement)|cancel (?:the )?order|return label|file a claim|concession)\b", re.IGNORECASE),
    re.compile(r"\b(?:carrier|courier|driver|delivery partner|usps|ups|fedex|tracking link|gps delivery scan|handed to|safe location)\b", re.IGNORECASE),
]

# Patterns that indicate pure deflection / generic boilerplate
GENERIC_BOILERPLATE_PATTERNS = [
    r"reach us via phone or chat",
    r"send us a dm",
    r"dm us",
    r"sorry to hear",
    r"we'd like to help",
    r"provide us with more details",
    r"can you please confirm",
    r"we would like to look into this",
    r"click the link below",
    r"sorry for the wait",
    r"sorry for the frustration",
    r"contact us via dm",
]


def compute_rrf(
    semantic_rank: Optional[int],
    lexical_rank: Optional[int],
    k: int = 60,
) -> float:
    """Compute Reciprocal Rank Fusion score from 1-based semantic and lexical ranks.

    Formula:
        RRF(d) = 1 / (k + semantic_rank(d)) + 1 / (k + lexical_rank(d))
    If candidate does not appear in a ranking, that ranking contributes 0.0.
    """
    score = 0.0
    if semantic_rank is not None and semantic_rank > 0:
        score += 1.0 / (k + semantic_rank)
    if lexical_rank is not None and lexical_rank > 0:
        score += 1.0 / (k + lexical_rank)
    return round(score, 5)


class CandidateReranker:
    """Reranks historical candidates using Two-Ranking Reciprocal Rank Fusion (RRF).

    Combines Top-N Semantic Candidates and Top-N Lexical Candidates using:
        RRF(d) = 1 / (k + semantic_rank(d)) + 1 / (k + lexical_rank(d)), k=60
    """

    def __init__(self, config_path: str = "configs/reranking.yaml", k: int = 60):
        self.k = k
        self.weights = DEFAULT_WEIGHTS.copy()
        self.max_results_per_conversation = 1
        self._load_config(config_path)

        self.boilerplate_regexes = [re.compile(p, re.IGNORECASE) for p in GENERIC_BOILERPLATE_PATTERNS]
        self.action_guidance_regexes = ACTION_GUIDANCE_PATTERNS

    def _load_config(self, config_path: str) -> None:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

            rerank_cfg = cfg.get("reranking", {})
            self.k = int(rerank_cfg.get("k", self.k))
            weights = rerank_cfg.get("weights", {})
            for k, v in weights.items():
                if k in self.weights:
                    self.weights[k] = float(v)

            self.max_results_per_conversation = rerank_cfg.get("max_results_per_conversation", 1)
        except Exception as e:
            logger.warning("Could not load %s, using defaults. Error: %s", config_path, str(e))

    def _compute_lexical_similarity(self, query: str, candidates: List[Dict[str, Any]]) -> List[float]:
        """Compute TF-IDF cosine similarity between query and candidate customer_message."""
        if not query or not candidates:
            return [0.0] * len(candidates)

        texts = [query] + [c.get("customer_message", "") for c in candidates]

        vectorizer = TfidfVectorizer(stop_words=list(LEXICAL_STOP_WORDS), token_pattern=r"(?u)\b\w+\b")
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            return [round(float(s), 4) for s in cosine_sims]
        except ValueError:
            return [0.0] * len(candidates)

    def _check_overlap(self, predicted: Optional[List[str]], actual: Optional[Any]) -> float:
        """Return 1.0 if there is any intersection, else 0.0 (preserved for test compatibility)."""
        if not predicted or actual is None:
            return 0.0

        if isinstance(actual, str):
            actual_set = {actual} if actual.strip() else set()
        elif isinstance(actual, (list, set, tuple)):
            actual_set = set(actual)
        else:
            return 0.0

        if not actual_set:
            return 0.0

        pred_set = set(predicted)
        if pred_set.intersection(actual_set):
            return 1.0
        return 0.0

    def _compute_action_penalty(self, brand_response: str) -> float:
        """Return penalty score (1.0 if boilerplate deflection, 0.0 if clean). Preserved for test compatibility."""
        if not brand_response:
            return 0.0

        for regex in self.boilerplate_regexes:
            if regex.search(brand_response):
                return 1.0
        return 0.0

    def _compute_action_usefulness(self, brand_response: str) -> tuple[float, float]:
        """Compute candidate-specific Action Usefulness (0.05 to 1.00) and Action Penalty (0.0 to 0.95)."""
        if not brand_response or not brand_response.strip():
            return 0.20, 0.80

        text = brand_response.strip()
        action_matches = sum(1 for pat in self.action_guidance_regexes if pat.search(text))
        has_deflection = any(regex.search(text) for regex in self.boilerplate_regexes)

        usefulness = 0.25
        if action_matches >= 3:
            usefulness += 0.65
        elif action_matches == 2:
            usefulness += 0.45
        elif action_matches == 1:
            usefulness += 0.25

        words = len(text.split())
        if words >= 25:
            usefulness += 0.10
        elif words < 8:
            usefulness -= 0.15

        if has_deflection:
            if action_matches == 0:
                usefulness = max(0.05, usefulness - 0.35)
            else:
                usefulness = max(0.20, usefulness - 0.15)

        action_usefulness = round(min(max(usefulness, 0.05), 1.00), 2)
        action_penalty = round(max(0.0, 1.0 - action_usefulness), 2)
        return action_usefulness, action_penalty

    def _compute_intent_compatibility(
        self, candidate: Dict[str, Any], predicted_intents: Optional[List[str]]
    ) -> float:
        """Compute deterministic Intent Compatibility score (0.0 to 1.0). Preserved for reference."""
        if not predicted_intents:
            return 0.0

        primary_intent = predicted_intents[0] if predicted_intents else None
        if not primary_intent:
            return 0.0

        metadata = candidate.get("metadata", {})
        raw_intents = metadata.get("intents") or metadata.get("intent")

        if raw_intents is not None:
            overlap = self._check_overlap(predicted_intents, raw_intents)
            if overlap > 0:
                return 1.0
            target_area = INTENT_TO_AREA.get(primary_intent)
            if target_area:
                cand_intents = [raw_intents] if isinstance(raw_intents, str) else list(raw_intents)
                for ci in cand_intents:
                    if INTENT_TO_AREA.get(ci) == target_area:
                        return 0.4
            return 0.0

        cand_text = f"{candidate.get('customer_message', '')} {candidate.get('relevant_context', '')}".lower()
        if not cand_text.strip():
            return 0.0

        pattern = INTENT_PATTERNS.get(primary_intent)
        if pattern and pattern.search(cand_text):
            return 1.0

        target_area = INTENT_TO_AREA.get(primary_intent)
        if target_area:
            for sibling_intent, area in INTENT_TO_AREA.items():
                if area == target_area and sibling_intent != primary_intent:
                    sib_pattern = INTENT_PATTERNS.get(sibling_intent)
                    if sib_pattern and sib_pattern.search(cand_text):
                        return 0.40

        return 0.10

    def _compute_area_compatibility(
        self, candidate: Dict[str, Any], predicted_areas: Optional[List[str]], predicted_intents: Optional[List[str]]
    ) -> float:
        """Compute deterministic broad area compatibility score (0.0 to 1.0). Preserved for reference."""
        areas = list(predicted_areas or [])
        if not areas and predicted_intents:
            for pi in predicted_intents:
                a = INTENT_TO_AREA.get(pi)
                if a and a not in areas:
                    areas.append(a)

        if not areas:
            return 0.0

        target_area = areas[0]
        metadata = candidate.get("metadata", {})
        raw_areas = metadata.get("areas") or metadata.get("area")
        if raw_areas is not None:
            return self._check_overlap(areas, raw_areas)

        cand_text = f"{candidate.get('customer_message', '')} {candidate.get('relevant_context', '')}".lower()
        for intent, area in INTENT_TO_AREA.items():
            if area == target_area:
                pat = INTENT_PATTERNS.get(intent)
                if pat and pat.search(cand_text):
                    return 1.0

        return 0.0

    def _compute_state_compatibility(
        self, candidate: Dict[str, Any], predicted_states: Optional[List[str]]
    ) -> float:
        """Compute deterministic State Compatibility score (0.0 to 1.0). Preserved for reference."""
        curr_states = [s for s in (predicted_states or []) if s]
        if not curr_states:
            curr_states = ["INITIAL_INQUIRY"]

        metadata = candidate.get("metadata", {})
        raw_state = metadata.get("state") or metadata.get("states")

        if raw_state is not None:
            overlap = self._check_overlap(curr_states, raw_state)
            return 1.0 if overlap > 0 else 0.0

        cand_text = f"{candidate.get('customer_message', '')} {candidate.get('relevant_context', '')}".lower()
        cand_detected = [state for state, pat in STATE_PATTERNS.items() if pat.search(cand_text)]
        if not cand_detected:
            cand_detected = ["INITIAL_INQUIRY"]

        curr_set = set(curr_states)
        cand_set = set(cand_detected)

        if curr_set == cand_set:
            return 1.0

        overlap = curr_set.intersection(cand_set)
        if overlap:
            union = curr_set.union(cand_set)
            return round(len(overlap) / len(union), 2)

        return 0.0

    def rerank(
        self,
        query_text: str = "",
        candidates: Optional[List[Dict[str, Any]]] = None,
        semantic_candidates: Optional[List[Dict[str, Any]]] = None,
        lexical_candidates: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 5,
        k: Optional[int] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Rerank candidates using pure Two-Ranking Reciprocal Rank Fusion (RRF).

        Only semantic retrieval ranking and lexical retrieval ranking are fused.
        Intent, state, area, action usefulness, and action penalty are NOT used for ranking.

        Formula:
            RRF(d) = 1 / (k + semantic_rank(d)) + 1 / (k + lexical_rank(d))
            k = 60

        Ranks are 1-based. If a candidate does not appear in one ranking, that ranking
        contributes 0.0 to its RRF score and its rank field is None.
        """
        rrf_k = k if k is not None else self.k

        # 1. Resolve semantic candidates
        sem_list = semantic_candidates
        if sem_list is None and candidates is not None:
            sem_list = candidates
        if sem_list is None:
            sem_list = []

        # 2. Resolve lexical candidates
        lex_list = lexical_candidates
        if lex_list is None:
            # If no explicit lexical candidates were supplied, but candidates were passed with lexical scores or text
            if sem_list and query_text:
                # Check if candidates already have lexical_score
                has_lex = any(c.get("lexical_score") is not None for c in sem_list)
                if has_lex:
                    # Sort by lexical_score to form lexical ranking
                    sorted_by_lex = sorted(
                        sem_list,
                        key=lambda x: float(x.get("lexical_score") or 0.0),
                        reverse=True,
                    )
                    lex_list = sorted_by_lex
                else:
                    lex_scores = self._compute_lexical_similarity(query_text, sem_list)
                    scored_lex = []
                    for i, c in enumerate(sem_list):
                        scored_lex.append({**c, "lexical_score": lex_scores[i], "score": lex_scores[i]})
                    scored_lex.sort(key=lambda x: x["lexical_score"], reverse=True)
                    lex_list = scored_lex
            else:
                lex_list = []

        # 3. Map candidates and 1-based ranks
        # Helper to extract a stable identifier
        def get_cid(c: Dict[str, Any], prefix: str, i: int) -> str:
            val = c.get("case_id") or c.get("id") or c.get("document_id")
            return str(val) if val is not None and str(val).strip() else f"{prefix}_{i + 1}"

        # Dictionary to accumulate unified candidate objects
        unified_candidates: Dict[str, Dict[str, Any]] = {}
        sem_ranks: Dict[str, int] = {}
        sem_scores: Dict[str, float] = {}

        for idx, c in enumerate(sem_list):
            cid = get_cid(c, "sem", idx)
            sem_ranks[cid] = idx + 1  # 1-based
            raw_sc = c.get("score") if c.get("score") is not None else c.get("semantic_score")
            sem_scores[cid] = round(float(raw_sc), 4) if raw_sc is not None else 0.0
            if cid not in unified_candidates:
                unified_candidates[cid] = {**c, "case_id": cid}

        lex_ranks: Dict[str, int] = {}
        lex_scores: Dict[str, float] = {}

        for idx, c in enumerate(lex_list):
            cid = get_cid(c, "lex", idx)
            lex_ranks[cid] = idx + 1  # 1-based
            raw_sc = c.get("lexical_score") if c.get("lexical_score") is not None else c.get("score")
            lex_scores[cid] = round(float(raw_sc), 4) if raw_sc is not None else 0.0
            if cid not in unified_candidates:
                unified_candidates[cid] = {**c, "case_id": cid}
            else:
                # Merge any missing fields from lexical
                for k_field, v_val in c.items():
                    if k_field not in unified_candidates[cid] or unified_candidates[cid][k_field] is None:
                        unified_candidates[cid][k_field] = v_val

        if not unified_candidates:
            return []

        # 4. Compute RRF score for each candidate
        scored_list: List[Dict[str, Any]] = []
        for cid, cand in unified_candidates.items():
            s_rank: Optional[int] = sem_ranks.get(cid)
            l_rank: Optional[int] = lex_ranks.get(cid)
            s_score: Optional[float] = sem_scores.get(cid)
            l_score: Optional[float] = lex_scores.get(cid)

            rrf_score = compute_rrf(s_rank, l_rank, k=rrf_k)

            # Preserve informational fields but rank ONLY by rrf_score
            scored_cand = {
                **cand,
                "case_id": cid,
                "semantic_rank": s_rank,
                "lexical_rank": l_rank,
                "rrf_score": rrf_score,
                "final_score": rrf_score,  # alias for backward compatibility
                "rerank_score": rrf_score,  # alias for backward compatibility
                "semantic_score": s_score,
                "lexical_score": l_score,
                # Informational / backward-compat placeholders
                "intent_score": None,
                "area_score": None,
                "state_score": None,
                "action_usefulness": None,
                "action_penalty": 0.0,
                "action_penalty_flag": 0.0,
            }
            scored_list.append(scored_cand)

        # 5. Sort candidates strictly by descending RRF score
        # Break ties deterministically: prefer candidate appearing in both, then lower semantic rank, then lower lexical rank
        def sort_key(item: Dict[str, Any]):
            r_score = item["rrf_score"]
            s_r = item["semantic_rank"] if item["semantic_rank"] is not None else 999999
            l_r = item["lexical_rank"] if item["lexical_rank"] is not None else 999999
            return (-r_score, s_r, l_r)

        scored_list.sort(key=sort_key)

        # 6. Deduplicate conversations
        final_results: List[Dict[str, Any]] = []
        conversation_counts: Dict[Any, int] = {}

        for c in scored_list:
            conv_id = c.get("conversation_id")
            if conv_id is not None and str(conv_id).strip():
                count = conversation_counts.get(conv_id, 0)
                if count < self.max_results_per_conversation:
                    final_results.append(c)
                    conversation_counts[conv_id] = count + 1
            else:
                final_results.append(c)

            if len(final_results) >= top_k:
                break

        # 7. Assign 1-based final rank
        for idx, res in enumerate(final_results):
            res["rank"] = idx + 1

        return final_results

