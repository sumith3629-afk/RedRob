# Redrob AI Founding Team Candidate Discovery & Ranking System

An intelligent, production-ready hybrid ranking system built for the **Redrob India Runs Data & AI Challenge**. 

This repository implements a high-performance candidate retrieval and ranking pipeline designed to discover the ideal **Senior AI Engineer — Founding Team** profile while filtering out keyword-stuffed synthetic traps (honeypots).

---

## 🚀 Quick Start & Reproduction

To reproduce the submission CSV from the raw candidate pool under the **5-minute compute budget**, execute the following command:

```bash
# 1. Setup virtual environment and dependencies
pip install -r requirements.txt

# 2. Run the ranking pipeline
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

> [!IMPORTANT]
> The ranking pipeline relies on the precomputed embeddings cache file `candidate_embeddings.npy` included in the repository. This enables the script to run in **~10 seconds on CPU**, avoiding live embedding generation which exceeds the 5-minute sandbox limit.

---

## 🧠 System Architecture

The pipeline consists of a sequential, multi-stage retrieval and re-ranking architecture:

```
[candidates.jsonl] 
       │
       ▼
 [Honeypot Filter]  ──► Filters out synthetic profiles (impossible experience/skills)
       │
       ▼
[Semantic Retrieval] ──► Computes MiniLM-L6-v2 cosine similarity with Job Description
       │
       ▼ (Top 1,000)
[Heuristic Re-Ranker] ──► Adjusts scores for location, stability, notice period, and product-vs-service
       │
       ▼
 [Score Calibration] ──► Enforces monotonic non-increasing scores & deterministic tie-breaks
       │
       ▼
[Reasoning Generator] ──► Dynamically drafts 1-2 sentence rationales referencing profile facts
       │
       ▼
  [submission.csv]
```

### 1. Robust Honeypot Detection
The system automatically identifies and discards synthetic "honeypot" profiles using three deterministic inconsistency rules:
* **Zero-Duration Skills:** Flags profiles claiming `expert` or `advanced` proficiency on $\ge 3$ skills with $0$ months of usage.
* **Timeline Discrepancy:** Cross-references the start and end dates of career roles with stated durations (flags deviations $> 6$ months).
* **Experience Inflation:** Verifies that overall profile experience years do not exceed the sum of actual job history durations by more than $3$ years.

### 2. Semantic Matching
Candidate profiles (combining Title, Headline, Summary, Skills, and Recent Roles) are compared against the Job Description using **SentenceTransformers (`all-MiniLM-L6-v2`)** to capture semantic intent beyond simple keyword matching.

### 3. Founding Team Heuristic Re-ranking
The top 1,000 candidates are re-scored based on Series A Founding Team criteria:
* **Location/Relocation:** Noida/Pune local candidates get $+0.1$, profiles open to relocation get $+0.05$, and foreign candidates needing visas get $-0.3$.
* **Notice Period:** Candidates with $\le 30$-day notice periods get $+0.05$, while notice periods $> 90$ days get $-0.08$.
* **Stability:** Job hoppers with an average tenure $< 18$ months get $-0.08$, while stable candidates ($\ge 36$ months) get $+0.05$.
* **Product vs. Service Background:** Candidates with product company backgrounds (e.g. Google, Microsoft, Swiggy, Paytm, freshworks) get $+0.05$, while service-only backgrounds (TCS, Wipro, Infosys, Accenture, Cognizant, etc.) get a $-0.15$ penalty.
* **Skill Assessments:** Adds up to $+0.05$ bonus scaled from scores in relevant platform assessments (NLP, Pinecone, Milvus, Vector Search, MLOps).

### 4. Monotonic Calibration & Tie Resolution
Ranks are strictly ordered. The model's score is calibrated to be strictly non-increasing by rank. Sorting ties are resolved deterministically using `candidate_id` in ascending order, adhering strictly to the hackathon validator spec.

---

## 📊 Evaluation & Compute Performance

* **Time Complexity:** $O(N)$ retrieval via precomputed NumPy matrix multiplication + $O(K \log K)$ sorting for $K=1000$ candidates.
* **Latency:** **~10 seconds** wall-clock time on standard 8-core CPU.
* **Memory footprint:** **< 1.5 GB RAM** (highly optimized vector caching).
* **Honeypots Detected:** **65** synthetic profiles successfully identified and filtered out.

---

## 🛠️ Repository File Structure

* `rank.py`: Core ranking python script.
* `candidate_embeddings.npy`: Precomputed candidate embeddings cache (384-dim, float32).
* `requirements.txt`: Package dependencies for virtual environment setup.
* `submission_metadata.yaml`: Team portal metadata configuration.
* `challenge_files/`: Challenge documentation, schema, and validator scripts.
