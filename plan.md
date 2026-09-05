# NeuroSprint Web App — MVP Specification & Project Plan

## 1. Executive Summary
NeuroSprint is a web application designed for personal execution of 3-week goal sprints followed by an integration week, structured on the Neurointegration methodology[cite: 1]. It balances cognitive load and goal execution using the 10/90 rule (allocating 10% of weekly waking hours, capped at 10 hours per project and 30 hours total per sprint across three core pillars: Foundation, Drive, and Joy)[cite: 1].

---

## 2. Core Modules & Feature Specifications

### Module 1: Sprint Planning & Canvas
* **Interface Architecture:** Split-screen layout (Left: Conversational AI Planning Coach; Right: Interactive Sprint Canvas).
* **Project Decomposition:** AI decomposes user goals into actionable backlog tasks capped at 10 hours per project (30 hours total per 3-week sprint)[cite: 1]:
  * **Foundation (Фундамент):** Physical/mental health, routines, recovery[cite: 1].
  * **Drive (Драйв):** Medium-term growth, ambitious career/skill challenges[cite: 1].
  * **Joy (Кайф):** Present-moment enjoyment, sensory pleasure, immediate recharge[cite: 1].
* **Backlog Approval:** Interactive Kanban-style canvas allowing manual task curation, time estimates, and one-click commitment.

### Module 2: Daily Standup Widget
* **UX Flow:** Lightweight 1–2 minute express widget accessible on dashboard load[cite: 1].
* **7-State NeuroBalance Tracker:** Interactive state scale[cite: 1]:
  * `Apathy` $\rightarrow$ `Passivity` $\rightarrow$ `Relaxation` $\rightarrow$ `Balance` $\rightarrow$ `Engagement` $\rightarrow$ `Overarousal` $\rightarrow$ `Panic`[cite: 1].
* **Top 3 Daily Priorities:** Selection of 3 focus tasks for the day filtered from the approved sprint backlog[cite: 1].
* **Resource Logging:** Single input field to log a "Remarkable moment of the last 24 hours" to train positive memory bias[cite: 1].

### Module 3: SOS Practices & Micro-regulations
* **Entry Point:** Global Floating Action Button (FAB) available on all screens.
* **Triage & Delivery:** Quick symptom selection (e.g., panic/overarousal vs. apathy/freeze) routing directly to a 2–5 minute guided somatic, sensory, or breathwork exercise with an interactive timer[cite: 1].
* **Neuro-Challenge Deck:** Weekly proactive micro-challenges (e.g., cold exposure, sensory anchoring) to build amygdala regulation and resilience[cite: 1].

### Module 4: Transformational Reflection & Archive
* **AI-Guided Sprint Retrospective:** End-of-sprint conversation analyzing state logs and completion velocity[cite: 1].
* **4-Step Transformational Framework:** Automatic structured persistence to the sprint archive[cite: 1]:
  1. *Key Change Observed (Какое главное изменение я замечаю?)*[cite: 1]
  2. *Action Taken (Что я для этого сделал?)*[cite: 1]
  3. *Self-Insight (Что я понял о себе?)*[cite: 1]
  4. *Emerging Opportunities (Что теперь возможно для меня?)*[cite: 1]
* **Integration Week / Joy-Passana Configurator:** Setup mode for Week 4 to manage sensory reset and quiet periods (configurable from 3 hours up to 3 days)[cite: 1].

### Module 5: Analytics Dashboard
* **NeuroBalance Heatmap:** 21-day color-coded visual tracking state trends and transitions between integration, distress, and burnout zones[cite: 1].
* **Sprint Time Meter:** Circular progress gauges displaying remaining/spent hours against the 30-hour cap (10 hours per project)[cite: 1].
* **Tri-Pillar Kanban View:** Status board categorized by Foundation, Drive, and Joy[cite: 1].

---

## 3. External Integrations

### Apple Reminders (iCloud CalDAV API)
* **Bidirectional Task Sync:** Approved sprint backlog tasks export directly to designated lists in Apple Reminders.
* **Status Reconciliation:** Completing a task on Apple devices (iPhone/Mac/Watch) automatically marks it complete in the web app and deducts estimated time from the sprint budget.

### Telegram Notification Service
* **Trigger Bot:** Automated cron notifications sending direct deep-links for:
  * Morning Daily Standup (1–2 min check-in).
  * End-of-week checkpoint.
  * End-of-sprint Transformational Reflection.

---

## 4. Suggested Tech Stack

| Layer | Recommended Technology |
| :--- | :--- |
| **Frontend** | Next.js (React), Tailwind CSS, Framer Motion, Lucide Icons |
| **Backend / API** | FastAPI (Python) or Node.js / Next.js Server Actions |
| **Database & Auth** | PostgreSQL (Supabase / Google Cloud SQL) |
| **AI Orchestration** | Google Cloud Vertex AI (Gemini 1.5 Pro / Flash) |
| **Integrations** | CalDAV client library (`tsdav` or `caldav-adapter`), `python-telegram-bot` |

---

## 5. Implementation Roadmap
Phase 1: Project Scaffolding, Data Modeling & Auth (Sprint, Task, StateLog schemas)
Phase 2: Sprint Canvas & Split-Screen AI Decomposition Engine
Phase 3: Daily Standup Widget & 7-State NeuroBalance Tracker
Phase 4: Global SOS Modal & Practice Audio/Timer Engine
Phase 5: Apple Reminders 2-Way CalDAV Sync & Telegram Trigger Service
Phase 6: Transformational Reflection AI Dialog, Archive & Dashboard Heatmap
