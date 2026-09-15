# EMP-12: 1-Minute Spoken Elevator Pitch

**Problem ID:** EMP-12  
**Title:** Job & Skill Terminology Simplifier  
**Target Duration:** ~60 seconds (130–150 spoken words)  
**Target Audience:** Evaluation committee, faculty examiners, project reviewers  

---

## 🎙️ Spoken Script (Word Count: ~145 words | ~60 seconds)

> *"Good morning, respected professors and committee members.*
>
> *Beginners, fresh graduates, and career changers often struggle to decode employment terminology—acronyms like CI/CD, roles like Site Reliability Engineer, or legal terms like At-Will Employment.*
>
> *To solve this, we engineered **EMP-12: Job & Skill Terminology Simplifier**, a domain-specific Retrieval-Augmented Generation (RAG) assistant designed to simplify complex employment and technical terms.*
>
> *Unlike general conversational bots that hallucinate or provide generic answers, EMP-12 grounds every explanation in a curated, verified knowledge base of 60 standardized employment concepts across 5 categories.*
>
> *Our pipeline embeds user queries using `all-MiniLM-L6-v2`, retrieves exact matching contexts with FAISS vector search, applies strict guardrails to reject out-of-scope queries or prompt injections, and prompts Gemini Flash to generate beginner-friendly, structured explanations with real-world examples.*
>
> *The system achieves 100% Recall@1 across a 92-case benchmark and is verified by 229 unit tests. Thank you."*

---

## ⏱️ Timing & Delivery Breakdown

| Section | Content | Target Time | Key Emphasis |
|---|---|---|---|
| **The Hook & Problem** | Unfamiliar jargon, barrier for students & job seekers | 0:00 – 0:12 | Clarity of the beginner's challenge |
| **Project Identity** | EMP-12: Job & Skill Terminology Simplifier | 0:12 – 0:20 | Confident, clear project name & purpose |
| **Key Differentiator** | Grounded domain RAG vs. unconstrained general LLM | 0:20 – 0:32 | "Domain-specific", "Curated 60 concepts" |
| **Technical Architecture** | MiniLM (384-d), FAISS FlatIP, Guardrails (0.55), Gemini Flash | 0:32 – 0:48 | Exact stack, guardrail thresholds |
| **Validation & Climax** | 100% Recall@1, 92 eval cases, 229 automated tests | 0:48 – 1:00 | Concrete empirical evidence |

---

## 💡 Speaker Tips

1. **Pacing:** Speak at a calm, conversational pace (~130 words/minute). Avoid rushing through acronyms.
2. **Pronunciation:** Say *"F-A-I-S-S"* as *"FAISS"* (rhymes with *face* or *phase*), and *"MiniLM"* as *"Mini-L-M"*.
3. **Posture:** Stand tall, make direct eye contact with the examiners, and pause for one second after stating the 100% recall metric.
4. **Transition:** Follow immediately with: *"I would now be delighted to demonstrate the live application or walk through our architecture."*
