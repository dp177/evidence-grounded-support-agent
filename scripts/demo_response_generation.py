"""Demo script for Phase 8: Grounded Response Generation.

Executes the full pipeline:
Customer Input -> Classifier V2 -> Qdrant Retrieval -> Reranking -> Response Generator
"""

import argparse
import json
import logging
import sys
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.retrieval.service import RetrievalService
from support_agent.generation.response_generator import ResponseGenerator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.WARNING)

def load_dev_samples(n=20):
    """Load n samples from the development corpus."""
    df = pd.read_parquet("data/processed/qdrant_development_sample.parquet")
    # Take a random sample
    sample = df.sample(n=n, random_state=42)
    return sample.to_dict("records")

def display_pipeline_output(idx, case, classification, evidence, generated):
    print(f"\n{'='*60}")
    print(f"CASE {idx+1}")
    print(f"{'='*60}")
    
    print("\n[CUSTOMER]")
    if case.get("relevant_context"):
        print(f"Context: {case['relevant_context']}")
    print(f"Message: {case['customer_message']}")
    
    print("\n[CLASSIFICATION]")
    print(f"Primary Intent: {classification.get('primary_intent')}")
    print(f"Intents: {classification.get('intents')}")
    print(f"States: {classification.get('states', [])}")
    
    print(f"\n[RETRIEVED EVIDENCE (Top {len(evidence)})]")
    for i, ev in enumerate(evidence, 1):
        print(f"  {i}. {ev['brand_response']} (Score: {ev.get('rerank_score', 0):.2f})")
    
    print("\n[GENERATED RESPONSE]")
    print(generated.get("reply", "ERROR NO REPLY"))
    
    print("\n[METADATA]")
    print(f"Evidence Used: {generated.get('evidence_ids', [])}")
    print(f"Needs Grounding Review: {generated.get('needs_grounding_review')}")
    print(f"Needs Human Review: {generated.get('needs_human_review')}")
    print("="*60)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-cases", type=int, default=20, help="Number of cases to demo")
    args = parser.parse_args()

    print("Initializing Pipeline Modules...")
    
    # 1. Classifier V2
    classifier = LLMIntentClassifier(prompt_path="prompts/classification_v2.md")
    
    # 2. Retrieval Service (Qdrant + Reranker)
    retrieval_service = RetrievalService(
        config_path="configs/retrieval.yaml", 
        rerank_config_path="configs/reranking.yaml"
    )
    
    # 3. Response Generator
    generator = ResponseGenerator(
        config_path="configs/response_generation.yaml", 
        prompt_path="prompts/response_generation_v1.md"
    )

    cases = load_dev_samples(args.num_cases)
    
    # Run classification in batch for speed
    print("Running classification...")
    classification_records = [{"customer_message": c["customer_message"], "context": c.get("relevant_context", "")} for c in cases]
    classifications = classifier.classify_batch(classification_records, max_workers=2, use_cache=False)
    
    for i, (case, clf) in enumerate(zip(cases, classifications)):
        c_msg = case["customer_message"]
        ctx = case.get("relevant_context", "")
        
        # 4. Retrieval
        evidence = retrieval_service.retrieve(
            customer_message=c_msg,
            context=ctx,
            predicted_intents=clf.get("intents", []),
            predicted_areas=clf.get("areas", []),
            predicted_states=clf.get("states", []),
            top_k_initial=30,
            top_k_final=5
        )
        
        # 5. Generation
        generated = generator.generate_response(
            customer_message=c_msg,
            context=ctx,
            classification=clf,
            historical_evidence=evidence
        )
        
        display_pipeline_output(i, case, clf, evidence, generated)

if __name__ == "__main__":
    main()
