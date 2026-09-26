# Literature Review for Offline Evidence Grounding

Revised 25 September 2026. This review preserves the project's research families and paper catalogue while replacing unsupported gap-closure, uniqueness and performance claims. The offline condition applies to the implemented system and experiments. Research papers describing internet search remain background material; their external services are not permitted runtime dependencies.

## Research question

Can a locally deployed verifier make evidential support and disagreement understandable at claim level while maintaining useful accuracy, coverage and latency? The relevant engineering contribution is a complete offline workflow with traceable evidence and honest uncertainty. Novelty or superiority over all existing tools is not established by this review.

## Research families and their relevance

| Family | Papers in the project catalogue | Relevance to VeritasRAG | Offline boundary |
|---|---|---|---|
| Retrieval-augmented generation | Lewis et al.; Gao et al. survey | Separate generation from an evidence source | Use a local corpus and local generator |
| RAG failure analysis | Barnett et al. | Distinguish retrieval, extraction and answer-quality failures | Missing local knowledge remains explicit |
| Hallucination surveys | Ji et al.; Huang et al. | Define types of unsupported or conflicting output | Taxonomy does not establish detector accuracy |
| Sentence representations | Reimers and Gurevych | Efficient semantic comparison | Bundle weights; similarity is not proof of entailment |
| Language understanding models | He et al. DeBERTa | Background for the chosen NLI family | Model architecture paper is not a grounding benchmark |
| Atomic factual evaluation | Min et al. FActScore | Motivate checking smaller claims | Local implementation must preserve meaning and evidence scope |
| Search-assisted factual evaluation | Wei et al. SAFE | Contrast evidence acquisition with checking | External web search is excluded |
| Sampling-based consistency | Manakul et al. SelfCheckGPT | Contrast consistency signals with source support | Any generator sampling must be local; consistency is not truth |
| Retrieval/generation correction | Asai et al. Self-RAG; Yan et al. CRAG | Compare intervention points | External retrieval fallbacks are excluded |
| RAG evaluation | Es et al. RAGAs | Inform metric separation | Only locally configured, executable variants could be run |
| Labelled evaluation resources | Niu et al. RAGTruth; Li et al. HaluEval; FaithBench | Guide dataset and annotation design | Provision datasets locally and preserve provenance |

The broad summaries identify how the research informs the project; they do not establish that every implementation of a named tool has the same dependencies, granularity or latency. Exact experimental claims require original-paper and implementation checks.

## Design implications

Semantic similarity is a useful baseline but does not by itself determine support. NLI provides a premise/claim comparison, but performance on general inference tasks does not establish correctness on every local domain. Atomic decomposition can improve inspection granularity while introducing new errors through lost negation, conditions or subject relationships.

Evidence acquisition and evidence verification are different. A local corpus can supply additional evidence, but the result must distinguish original generator context from passages found later. An absent local fact cannot be repaired through internet search under this project's requirement.

Source-relative support also differs from source quality, currentness, relevance and completeness. Preserve these distinctions instead of combining them into a single grounding percentage. Model-score thresholds require local development data and separate final testing.

## Claims this review does not establish

The project has not established that no other system offers claim-level explanations, that all competing tools are response-level, or that all LLM-based judges require a fixed number of seconds. No claim of being the first system, closing every research gap, or guaranteeing subsecond operation is justified here.

The current implementation does not demonstrate Redis caching, parallel execution, adaptive latency budgets, automatic calibration or broad framework compatibility. Those statements from earlier drafts were design aspirations or unsupported descriptions and are not retained as completed capabilities.

The saved 40-example results favour sentence NLI over the hybrid in aggregate F1 and latency. Research motivation for guards and decomposition does not substitute for evidence that they improve this implementation.

## Evaluation implications

Use identified records from locally available datasets or explicitly labelled custom cases. Preserve original labels, transformations and grouped splits. Benchmark on held-out examples, retain failed cases, and compare locally runnable methods on identical inputs. Evaluate explanation fidelity and coverage separately from binary detection.

Paper-reported figures can supply historical context, but must not be merged with local measurements as a leaderboard. No cloud judge is required by the revised evaluation plan.

## Paper catalogue

The following existing research identifiers are retained for reference and local-paper lookup. They are not runtime fetch instructions. Bibliographic details should be checked against the retained PDFs before formal submission; this revision did not perform a new internet literature search.

1. Lewis et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020. arXiv:2005.11401.
2. Min et al. FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation. EMNLP 2023. arXiv:2305.14251.
3. Niu et al. RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models. ACL 2024. arXiv:2401.00396.
4. Asai et al. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. ICLR 2024. arXiv:2310.11511.
5. Es et al. RAGAs: Automated Evaluation of Retrieval Augmented Generation. EACL 2024. arXiv:2309.15217.
6. Manakul, Liusie and Gales. SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models. EMNLP 2023. arXiv:2303.08896.
7. Gao et al. Retrieval-Augmented Generation for Large Language Models: A Survey. arXiv:2312.10997.
8. Wei et al. Long-form Factuality in Large Language Models, associated with SAFE. arXiv:2403.18802.
9. Huang et al. A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions. arXiv:2311.05232.
10. He et al. DeBERTa: Decoding-enhanced BERT with Disentangled Attention. ICLR 2021. arXiv:2006.03654.
11. Yan et al. Corrective Retrieval Augmented Generation. arXiv:2401.15884.
12. Barnett et al. Seven Failure Points When Engineering a Retrieval Augmented Generation System. arXiv:2401.05856.
13. Li et al. HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models. EMNLP 2023. arXiv:2305.11747.
14. FaithBench: A Diverse Hallucination Benchmark for Summarization by Modern LLMs. arXiv:2410.13210; conference publication NAACL 2025.
15. Reimers and Gurevych. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP 2019. arXiv:1908.10084.

Ji et al.'s Survey of Hallucination in Natural Language Generation is additional background referenced in the earlier architecture. The exact local catalogue and bibliography should be reconciled before claiming a fixed number of papers comprehensively reviewed.

## Relationship to the implementation plan

Use [the architecture](../architecture.md) for actual and target components, [the issue register](../DESIGN_ISSUES_AND_RESOLUTIONS.md) for unresolved assumptions, and [the evaluation plan](Experimental_Evaluation_Results.md) for experiments. The literature supplies motivations and alternatives; the offline acceptance record will establish what this project actually delivers.
