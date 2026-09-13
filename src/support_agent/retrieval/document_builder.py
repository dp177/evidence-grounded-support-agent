"""Retrieval Document Builder and Golden Leakage Guard for AmazonHelp.

Constructs one historical retrieval document per meaningful customer->brand interaction turn:
- Excludes 100% of Golden V1 conversations
- Selects relevant preceding context using deterministic scoring
- Formats single embedding_text vector payload:
    CUSTOMER: <message>
    RELEVANT CONTEXT: <context>
    AMAZON RESPONSE: <response>
- Exports data/processed/retrieval_documents.parquet
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from support_agent.retrieval.context_selector import select_relevant_context
from support_agent.retrieval.conversation_builder import ConversationGraph, build_conversation_graph

logger = logging.getLogger(__name__)


def load_golden_conversation_ids(golden_path: Path | str = "data/golden/golden_set.jsonl") -> Set[int]:
    """Load the frozen set of Golden V1 conversation IDs."""
    path = Path(golden_path)
    if not path.exists():
        raise FileNotFoundError(f"Golden set file not found: {path}")

    cids: Set[int] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                cid = data.get("conversation_id")
                if cid is not None:
                    cids.add(int(cid))
    return cids


def validate_retrieval_isolation(
    conversation_ids: Iterable[int],
    golden_path: Path | str = "data/golden/golden_set.jsonl",
) -> bool:
    """Assert zero overlap between candidate conversation IDs and Golden V1.
    
    Raises ValueError immediately if leakage is detected.
    """
    golden_cids = load_golden_conversation_ids(golden_path)
    overlap = set(int(c) for c in conversation_ids).intersection(golden_cids)
    if overlap:
        raise ValueError(
            f"CRITICAL LEAKAGE DETECTED: Found {len(overlap)} Golden V1 conversations in retrieval candidate pool: {overlap}"
        )
    return True


@dataclass
class RetrievalDocument:
    """One historical decision-point document for retrieval & future embedding."""
    document_id: str
    case_id: str
    conversation_id: int
    turn_index: int
    customer_tweet_id: int
    brand_response_tweet_id: int
    customer_message: str
    relevant_context: str
    brand_response: str
    selected_context_tweet_ids: List[Optional[int]]
    selected_context_scores: List[float]
    created_at: Optional[str]
    thread_length: int
    language: str
    quality_status: str
    embedding_text: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "case_id": self.case_id,
            "conversation_id": self.conversation_id,
            "turn_index": self.turn_index,
            "customer_tweet_id": self.customer_tweet_id,
            "brand_response_tweet_id": self.brand_response_tweet_id,
            "customer_message": self.customer_message,
            "relevant_context": self.relevant_context,
            "brand_response": self.brand_response,
            "selected_context_tweet_ids": self.selected_context_tweet_ids,
            "selected_context_scores": self.selected_context_scores,
            "created_at": self.created_at,
            "thread_length": self.thread_length,
            "language": self.language,
            "quality_status": self.quality_status,
            "embedding_text": self.embedding_text,
        }


TURN_PATTERN = re.compile(r"^(CUSTOMER|BRAND):\s*(.*)$")


def parse_context_clean(context_clean_str: str) -> List[Dict[str, str]]:
    """Parse role-prefixed clean context string into structured turns.
    
    Format in canonical dataset:
    CUSTOMER: <text>
    BRAND: <text>
    """
    if not context_clean_str or not context_clean_str.strip():
        return []
    turns: List[Dict[str, str]] = []
    current_role: Optional[str] = None
    current_text_parts: List[str] = []

    for line in context_clean_str.split("\n"):
        m = TURN_PATTERN.match(line)
        if m:
            if current_role is not None:
                txt = "\n".join(current_text_parts).strip()
                if txt:
                    turns.append({"role": current_role, "text": txt})
            current_role = m.group(1)
            current_text_parts = [m.group(2)]
        else:
            if current_role is not None:
                current_text_parts.append(line)

    if current_role is not None:
        txt = "\n".join(current_text_parts).strip()
        if txt:
            turns.append({"role": current_role, "text": txt})

    return turns


def get_clean_preceding_turns(
    row: Any,
    graph: ConversationGraph,
    conv_text_to_tid: Optional[Dict[Tuple[int, str, str], int]] = None,
) -> List[Dict[str, Any]]:
    """Reconstruct clean preceding conversation turns using the conversation graph and clean fields.
    
    Guarantees:
    - 0% raw tweet text / Twitter noise leaked into context
    - Strictly uses canonical clean text (customer_message_clean, brand_response_clean, context_clean)
    - Never falls back silently to raw context
    - Preserves provenance tweet IDs for auditability
    """
    cust_tid = int(row.customer_tweet_id)
    cid = int(row.conversation_id)
    cust_clean_val = getattr(row, "customer_message_clean", None)
    cust_clean = str(cust_clean_val).strip() if cust_clean_val is not None else ""

    # 1. Recover preceding nodes from conversation graph
    graph_records = graph.get_preceding_context(cust_tid)
    graph_turns: List[Dict[str, Any]] = [
        {
            "role": rec.role,
            "author": rec.author_id,
            "text": rec.text,
            "tweet_id": rec.tweet_id,
            "turn_index": rec.turn_index,
        }
        for rec in graph_records
        if rec.text and rec.text.strip()
    ]

    # 2. Parse canonical context_clean as complementary clean turns
    cc_str = str(getattr(row, "context_clean", "") or "").strip()
    parsed_cc = parse_context_clean(cc_str)

    cc_preceding: List[Dict[str, Any]] = []
    if parsed_cc:
        last = parsed_cc[-1]
        if last["role"] == "CUSTOMER" and last["text"] == cust_clean:
            cc_preceding = parsed_cc[:-1]
        elif len(parsed_cc) > 1 and last["role"] == "CUSTOMER" and cust_clean.startswith(last["text"][:30]):
            cc_preceding = parsed_cc[:-1]
        else:
            # Check if customer message is located at an intermediate turn
            found_idx = -1
            for i, t in enumerate(parsed_cc):
                if t["role"] == "CUSTOMER" and t["text"] == cust_clean:
                    found_idx = i
                    break
            if found_idx >= 0:
                cc_preceding = parsed_cc[:found_idx]
            else:
                cc_preceding = parsed_cc

    # Attach provenance tweet IDs to cc_preceding if missing
    if conv_text_to_tid is not None:
        for t in cc_preceding:
            if "tweet_id" not in t or t["tweet_id"] is None:
                tid = conv_text_to_tid.get((cid, t["role"], t["text"]))
                t["tweet_id"] = tid
                t["author"] = "AmazonHelp" if t["role"] == "BRAND" else str(getattr(row, "customer_author_id", "CUSTOMER"))

    # Reconcile graph turns and context_clean turns
    if len(graph_turns) >= len(cc_preceding) and len(graph_turns) > 0:
        return graph_turns
    elif len(cc_preceding) > 0:
        # Align graph tweet IDs into cc_preceding if available
        if len(graph_turns) > 0 and len(graph_turns) <= len(cc_preceding):
            g_idx = 0
            for ct in cc_preceding:
                if (
                    g_idx < len(graph_turns)
                    and ct["role"] == graph_turns[g_idx]["role"]
                    and (
                        ct["text"] == graph_turns[g_idx]["text"]
                        or (len(ct["text"]) >= 20 and ct["text"][:20] in graph_turns[g_idx]["text"])
                    )
                ):
                    ct["tweet_id"] = graph_turns[g_idx]["tweet_id"]
                    g_idx += 1
        return cc_preceding
    else:
        return graph_turns


def format_embedding_text(customer_message: str, relevant_context: str, brand_response: str) -> str:
    """Format the canonical tripartite text chunk for future single-vector embedding."""
    ctx_str = relevant_context.strip() if relevant_context.strip() else "None"
    return (
        f"CUSTOMER:\n{customer_message.strip()}\n\n"
        f"RELEVANT CONTEXT:\n{ctx_str}\n\n"
        f"AMAZON RESPONSE:\n{brand_response.strip()}"
    )


def build_retrieval_documents(
    input_parquet_path: Path | str = "data/processed/amazon_support_cases.parquet",
    output_parquet_path: Path | str = "data/processed/retrieval_documents.parquet",
    golden_path: Path | str = "data/golden/golden_set.jsonl",
    max_context_turns: int = 6,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Build retrieval documents from AmazonHelp support cases.
    
    - Filters out Golden V1 conversations (zero leakage)
    - Reconstructs preceding context strictly from canonical clean fields
    - Performs quality checks & deduplication
    - Selects relevant context per interaction using deterministic scoring
    - Generates embedding_text in tripartite format
    - Returns DataFrame and detailed audit report
    """
    in_file = Path(input_parquet_path)
    out_file = Path(output_parquet_path)
    golden_file = Path(golden_path)

    if not in_file.exists():
        raise FileNotFoundError(f"Input cases parquet not found: {in_file}")

    logger.info(f"Loading cases from {in_file}...")
    df = pd.read_parquet(in_file)
    raw_count = len(df)

    audit: Dict[str, Any] = {
        "raw_candidates": raw_count,
        "golden_v1_exclusions": 0,
        "missing_customer_message_exclusions": 0,
        "missing_brand_response_exclusions": 0,
        "duplicate_interaction_exclusions": 0,
        "malformed_relationship_exclusions": 0,
        "valid_documents": 0,
        "flagged_non_english": 0,
        "flagged_non_ok_quality": 0,
        "avg_context_turns": 0.0,
        "median_context_turns": 0.0,
        "max_context_turns": 0,
        "zero_context_documents": 0,
    }

    # 1. Strict Golden V1 Exclusion
    golden_cids = load_golden_conversation_ids(golden_file)
    logger.info(f"Loaded {len(golden_cids)} Golden V1 conversation IDs.")

    is_golden = df["conversation_id"].isin(golden_cids)
    audit["golden_v1_exclusions"] = int(is_golden.sum())
    dev_df = df[~is_golden].copy()
    logger.info(f"Excluded {audit['golden_v1_exclusions']} golden cases. Remaining dev pool: {len(dev_df)}")

    # Verify zero leakage
    validate_retrieval_isolation(dev_df["conversation_id"].unique(), golden_file)

    # 2. Build conversation graph and clean tweet ID lookup map
    logger.info("Reconstructing conversation graph for clean turn traversal...")
    graph, _ = build_conversation_graph(df)

    logger.info("Indexing canonical clean tweet texts for provenance recovery...")
    conv_text_to_tid: Dict[Tuple[int, str, str], int] = {}
    for r in df.itertuples(index=False):
        c_id = int(r.conversation_id)
        c_tid = int(r.customer_tweet_id)
        r_tid = int(r.response_tweet_id)
        c_clean = str(getattr(r, "customer_message_clean", "") or "").strip()
        r_clean = str(getattr(r, "brand_response_clean", "") or "").strip()
        if c_clean:
            conv_text_to_tid[(c_id, "CUSTOMER", c_clean)] = c_tid
        if r_clean:
            conv_text_to_tid[(c_id, "BRAND", r_clean)] = r_tid

    # 3. Extract and sanitize interaction documents
    documents: List[RetrievalDocument] = []
    seen_interactions: Set[Tuple[int, int]] = set()
    context_turn_counts: List[int] = []
    doc_counter = 0

    # Sort once upfront for streaming performance
    sorted_dev = dev_df.sort_values(["conversation_id", "turn_index"])

    for row in sorted_dev.itertuples(index=False):
        cid = int(row.conversation_id)
        cust_tid = int(row.customer_tweet_id)
        resp_tid = int(row.response_tweet_id)
        turn_idx = int(row.turn_index)
        case_id = str(row.case_id)

        # STRICT CANONICAL CLEAN: never fall back to raw customer_message or brand_response
        cust_clean_val = getattr(row, "customer_message_clean", None)
        cust_msg = str(cust_clean_val).strip() if cust_clean_val is not None else ""

        brand_clean_val = getattr(row, "brand_response_clean", None)
        brand_resp = str(brand_clean_val).strip() if brand_clean_val is not None else ""

        # Quality exclusions
        if not cust_msg:
            audit["missing_customer_message_exclusions"] += 1
            continue
        if not brand_resp:
            audit["missing_brand_response_exclusions"] += 1
            continue

        pair_key = (cust_tid, resp_tid)
        if pair_key in seen_interactions:
            audit["duplicate_interaction_exclusions"] += 1
            continue
        seen_interactions.add(pair_key)

        # Reconstruct clean preceding turns from graph and canonical clean fields
        preceding_turns = get_clean_preceding_turns(row, graph, conv_text_to_tid)

        # Apply deterministic context selection
        rel_context_str, sel_tids, sel_scores, _ = select_relevant_context(
            preceding_turns=preceding_turns,
            current_customer_message=cust_msg,
            max_context_turns=max_context_turns,
        )

        turns_preserved = len(sel_scores)
        context_turn_counts.append(turns_preserved)
        if turns_preserved == 0:
            audit["zero_context_documents"] += 1

        lang = str(getattr(row, "language", "unknown"))
        quality = str(getattr(row, "quality_status", "OK"))

        if lang != "en":
            audit["flagged_non_english"] += 1
        if quality != "OK":
            audit["flagged_non_ok_quality"] += 1

        embedding_txt = format_embedding_text(cust_msg, rel_context_str, brand_resp)

        doc_id = f"retrieval_doc_{doc_counter:07d}"
        doc_counter += 1

        doc = RetrievalDocument(
            document_id=doc_id,
            case_id=case_id,
            conversation_id=int(cid),
            turn_index=turn_idx,
            customer_tweet_id=cust_tid,
            brand_response_tweet_id=resp_tid,
            customer_message=cust_msg,
            relevant_context=rel_context_str,
            brand_response=brand_resp,
            selected_context_tweet_ids=sel_tids,
            selected_context_scores=sel_scores,
            created_at=getattr(row, "created_at", None) if pd.notna(getattr(row, "created_at", None)) else None,
            thread_length=int(getattr(row, "thread_length", 2)),
            language=lang,
            quality_status=quality,
            embedding_text=embedding_txt,
        )
        documents.append(doc)

    audit["valid_documents"] = len(documents)

    if context_turn_counts:
        s_turns = pd.Series(context_turn_counts)
        audit["avg_context_turns"] = round(float(s_turns.mean()), 3)
        audit["median_context_turns"] = round(float(s_turns.median()), 1)
        audit["max_context_turns"] = int(s_turns.max())

    logger.info(
        f"Constructed {len(documents)} retrieval documents. "
        f"Avg context turns: {audit['avg_context_turns']} (median: {audit['median_context_turns']}, max: {audit['max_context_turns']})"
    )

    # 3. Export Parquet
    doc_dicts = [d.to_dict() for d in documents]
    docs_df = pd.DataFrame(doc_dicts)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    docs_df.to_parquet(out_file, index=False, engine="pyarrow", compression="snappy")
    logger.info(f"Saved retrieval documents parquet to {out_file} ({out_file.stat().st_size / (1024*1024):.2f} MB).")

    return docs_df, audit
