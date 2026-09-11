# Golden Evaluation Set v1 — Annotation Progress Tracker

**GOLDEN V1 STATUS:** `HUMAN SIGN-OFF APPROVED (AWAITING LOCK)`  
**Target Benchmark:** Golden Evaluation Set (`golden_v1`)  
**Workspace File:** `data/golden/golden_v1_human_signoff.csv` (200 cases)  
**Priority Review File:** `data/golden/priority_human_signoff.csv` (24 cases)  
**Instructions Reference:** `data/golden/HUMAN_SIGNOFF_INSTRUCTIONS.md`  
**Last Updated:** 2026-09-12  

> [!NOTE]
> **Human Sign-Off Complete:** All 24 priority cases and 176 remaining cases have been reviewed and accepted (`human_decision = ACCEPT`).
> All validation checks pass. `golden_v1` is ready for final lock.

---

## 1. Current Progress Status

| Metric | Count | Percentage |
|---|:---:|:---:|
| **Total Cases Requiring Sign-Off** | 200 | 100.0% |
| **Priority Cases Reviewed** | **24 / 24** | **100.0% (ACCEPTED)** |
| **Remaining Cases Reviewed** | **176 / 176** | **100.0% (ACCEPTED)** |
| **Human Decisions Completed** | **200 / 200** | **100.0%** |
| **Remaining Human Decisions** | **0** | **0.0%** |
| **Current Status** | **APPROVED — READY FOR LOCK** | — |

---

## 2. Milestone Tracking

- [x] **Setup Review CSV (`golden_annotation_review.csv`)**: 200 cases prepared with blank `human_*` columns.
- [x] **Publish Annotation Guidelines (`ANNOTATION_INSTRUCTIONS.md`)**: Complete with boundary rules and taxonomy schema.
- [ ] **Batch 1 (Cases 1–50)**: High-Risk, Ambiguous, and Out-of-Scope cases review.
- [ ] **Batch 2 (Cases 51–100)**: Multi-Intent and Boundary cases review.
- [ ] **Batch 3 (Cases 101–150)**: Rare and Underrepresented leaf intent cases review.
- [ ] **Batch 4 (Cases 151–200)**: Common normal single-intent cases review.
- [ ] **Final Adjudication & Ground Truth Lock**: Overwrite / finalize ground-truth in `data/golden/golden_set.jsonl`.

---

## 3. How to Update Progress

As human annotators review rows in `data/golden/golden_annotation_review.csv`:
1. Record verified values in the `human_*` columns.
2. Update the `Reviewed by Human` and `Remaining to Review` counts above.
3. Check off completed batch milestones.
4. When all 200 rows are reviewed, proceed to lock the finalized golden set.
