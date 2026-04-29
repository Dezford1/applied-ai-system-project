```md
# 🧾 Model Card — PawPal+

## 🤖 System Overview

PawPal+ is an AI-assisted scheduling system for pet care tasks. It uses rule-based retrieval (RAG), constraint-based scheduling, and an agentic evaluation loop to generate daily care plans.

---

## 🧠 AI Collaboration

### Helpful AI Contributions

AI helped design the structure of the agentic workflow, especially the idea of separating:

- scheduling
- evaluation
- conflict detection

This improved system modularity and made debugging easier.

### Flawed AI Suggestions

Some AI-generated suggestions introduced unnecessary complexity (e.g., over-engineered optimization approaches). These were simplified to a greedy scheduler to ensure reliability and interpretability.

---

## ⚠️ Biases & Limitations

- The system assumes all tasks are equally executable if constraints allow them
- Scheduling does not account for real-world unpredictability (e.g., emergencies, delays)
- Rule-based RAG system is static and does not learn from user behavior
- Priority system is manually defined and may not reflect real pet needs

---

## 🔬 Reliability & Testing

### Testing Methods Used

- Manual scenario testing (multiple pets + overlapping tasks)
- Conflict detection validation
- Budget constraint enforcement checks
- Confidence score tracking

### Results

- 5 out of 6 test scenarios passed successfully
- System performs best with structured, well-defined tasks
- Failures occurred when task priorities were missing or ambiguous

### Improvements After Testing

- Added conflict warnings
- Introduced confidence scoring
- Improved task filtering logic

---

## 🛡 Safety / Misuse Risk

### Potential Misuse

- Users may over-rely on automated scheduling and ignore real-life needs
- Incorrect priorities could result in poor scheduling decisions

### Mitigations

- Clear display of unscheduled tasks
- Warning messages for conflicts
- Confidence score to indicate uncertainty

---

## 🚀 What I Learned

- How to design multi-step AI workflows
- How retrieval systems (RAG) influence decision-making
- How to evaluate AI reliability without ML training
- The importance of simplicity in production-like systems
```
