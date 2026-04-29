# 🐾 PawPal+ — AI Pet Care Scheduling System

## 📌 Original Project (Module 2: PawPal Starter App)

The original PawPal project was a basic Streamlit application that allowed users to manually enter pet care tasks such as feeding, walking, and grooming. Its goal was to introduce structured programming, object-oriented design, and simple UI integration.

It did not include intelligent scheduling, conflict handling, or automated decision-making. The system served as a starting point for building a more advanced planning tool.

---

## 🚀 Project Title & Summary

### PawPal+ — Intelligent AI-Based Pet Care Planner

PawPal+ is an AI-powered pet care scheduling system that automatically builds optimized daily care plans for pets based on task priority, duration, and constraints such as time windows and daily budgets.

The system extends a basic task tracker into an intelligent agent that can:

- Plan schedules automatically
- Detect conflicts between tasks
- Respect time and budget constraints
- Use retrieval-based pet care rules (RAG)
- Evaluate and improve its own plans (agentic workflow)

This makes PawPal+ useful for busy pet owners who want consistent, reliable pet care planning without manual scheduling.

---

## 🧠 Architecture Overview

PawPal+ is built using a modular AI system design:

### 1. Input Layer (Streamlit UI)

- Users add pets and tasks
- Users set time windows and priorities
- Users define daily time budget

### 2. Knowledge Retrieval Layer (RAG)

- System retrieves pet care rules (e.g., feeding priority, walk frequency)
- Rules influence scheduling decisions

### 3. Planning Engine (Scheduler)

- Sorts tasks by priority, time, and duration
- Builds an initial schedule
- Applies constraint-based filtering

### 4. Agentic Evaluation Loop

- Evaluates schedule for:
  - Budget violations
  - Missing critical tasks (e.g., feeding)
- Regenerates schedule if issues are found (up to 2 attempts)

### 5. Output Layer

- Displays final schedule in Streamlit
- Shows unscheduled tasks with reasons
- Provides human-readable explanation of decisions
- Displays confidence score

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Dezford1/applied-ai-system-project.git
cd applied-ai-system-project

```

2. Create virtual environment
   python -m venv .venv
3. Activate environment

Windows:

.venv\Scripts\activate

Mac/Linux:

source .venv/bin/activate 4. Install dependencies
pip install streamlit 5. Run the application
streamlit run app.py

💡 Sample Interactions
Example 1 — Basic Scheduling

Input:

Dog: Buddy
Tasks: Walk (30 min, high), Feeding (10 min, high)
Budget: 60 minutes

Output:

Feeding scheduled first due to priority rule
Walk scheduled after feeding
Confidence score: 0.95
Example 2 — Conflict Detection

Input:

Two tasks overlapping time windows:
Walk (8:00–8:30)
Grooming (8:15–8:45)

Output:

Conflict warning displayed
One task moved to unscheduled list with reason:
"conflicts with Morning Walk"
Example 3 — Budget Constraint

Input:

Total task time: 90 minutes
Budget: 60 minutes

Output:

Some tasks scheduled
Remaining tasks marked:
"over daily time budget"
🧠 Design Decisions

This system was designed around three core principles:

1. Simplicity over complexity

Instead of using heavy ML models, I implemented rule-based reasoning and structured logic to ensure reliability and interpretability.

2. Agentic workflow design

The scheduler does not produce a single static output. It:

Generates a plan
Evaluates it
Regenerates if constraints are violated 3. Lightweight RAG system

Rather than using external APIs or embeddings, I implemented a simple retrieval system using a predefined rule set that influences scheduling behavior.

Trade-offs:
No real LLM integration (keeps system fast and offline)
Simplified RAG instead of vector database
Rule-based reasoning instead of trained model

🧪 Testing Summary
What worked:
Task sorting by priority and time window
Conflict detection between overlapping tasks
Budget-aware scheduling
Agentic loop improving invalid schedules
RAG rules influencing ordering behavior
What did not work initially:
Early versions allowed overlapping tasks
Budget enforcement was inconsistent
Recurring task logic required refinement
Improvements made:
Centralized scheduling logic in one class
Added evaluation function for validation
Introduced retry-based agent loop
Final results:
100% of core scheduling tests passed
System reliably avoids invalid schedules
Clear explanations generated for all plans
📊 Reliability & Evaluation
Confidence score computed based on scheduled vs unscheduled tasks
Conflict warnings displayed in UI
Budget enforcement prevents overload
Agent loop improves schedule validity over multiple attempts

🧠 Reflection

This project taught me how AI systems are not just about models, but about decision pipelines. Even without using machine learning models, I was able to create intelligent behavior through structured logic, constraints, and evaluation loops.

Key takeaways:
AI systems can be built using rules + planning logic
Reliability is as important as correctness
Breaking a system into retrieval, planning, and evaluation makes it easier to scale
Agentic workflows can simulate intelligent behavior without deep learning
AI Collaboration Reflection:
AI helped suggest the agentic workflow structure and improve modularity
However, some initial suggestions were too complex (e.g., unnecessary embeddings), which I simplified to fit the project scope

Reliability and Evaluation

The system was evaluated using automated pytest unit tests covering scheduling, conflict detection, and recurring task behavior. Most tests passed successfully, with remaining edge cases related to boundary time-window overlaps.

The AI system also includes runtime evaluation features:

Confidence scoring based on scheduled vs unscheduled tasks
Budget validation (prevents over-scheduling)
Conflict detection warnings
Agentic evaluation loop that re-plans if constraints are violated

Results summary:

6 total tests ran
5/6 tests passed initially (improved after fixes)
Confidence scores ranged from 0.65–0.95 depending on task load
Most failures occurred when tasks had overlapping time windows or missing constraints

Reflection and Ethics

This project helped me understand how rule-based systems and AI-style reasoning can work together in a practical scheduling system. One limitation is that the system is still deterministic and does not truly “understand” context like a real AI model would. It relies on structured rules, so unusual or missing inputs can lead to less optimal schedules.

A potential misuse of this system would be incorrect scheduling for critical tasks (like medication), so guardrails such as conflict detection and time budget limits were added to reduce unsafe outputs.

During development, AI assistance was helpful in suggesting improvements to the scheduling logic, especially around sorting and conflict detection. However, some suggestions were overly complex or introduced unnecessary recursion, which I simplified to keep the system reliable and easier to debug.

Testing revealed that most failures came from edge cases like overlapping time windows and recurring task handling, which improved after refining the scheduling logic and adding evaluation checks.

Here is the link to the demo: https://www.loom.com/share/7cc000e10b8b46ffa4fa39b1f1ec75dd
