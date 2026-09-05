# NeuroSprint — Task Backlog

Tasks are ordered roughly by dependency (earlier tasks unblock later ones) but each is written to be handed to someone who has not read the others — the Description gives enough context to start without cross-referencing this file. Stack reference: [plan.md](plan.md#L60) (Next.js frontend + FastAPI backend + PostgreSQL + Gemini API).

---

**Phase 1 — Scaffolding, Data Modeling & Auth**

## 1. Empty project scaffold with a passing test
Goal: Stand up the repo skeleton for both services with one green test in each.
Description: Create the Next.js app (TypeScript, Tailwind configured) and the FastAPI app (Python, project layout with a `tests/` folder) as separate services in the monorepo. Each should run locally with a single command and have exactly one trivial passing test (e.g. a health-check route test) wired into whatever test runner is chosen, so CI has something real to execute from day one.

## 2. PostgreSQL schema: Sprint, Task, StateLog
Goal: Define and migrate the three core relational tables the rest of the app builds on.
Description: Using SQLAlchemy/SQLModel (or the chosen ORM) in the FastAPI service, model `Sprint` (start/end dates, integration-week config), `Task` (title, pillar enum: Foundation/Drive/Joy, hour estimate, status, sprint FK), and `StateLog` (timestamp, one of the 7 NeuroBalance states, optional note). Include a migration tool (e.g. Alembic) with an initial migration that creates all three tables against a local Postgres instance.

## 3. User authentication (signup/login)
Goal: Let a user create an account and log in, with the session usable by both frontend and backend.
Description: Wire up an auth provider (e.g. Supabase Auth or a FastAPI JWT flow) so a user can sign up, log in, and log out. The FastAPI backend must be able to verify the identity of an incoming request; the Next.js frontend must be able to redirect unauthenticated users to a login page and persist the session across reloads.

## 4. Frontend-to-backend API client
Goal: Give the Next.js app a single, typed way to call the FastAPI backend.
Description: Build a thin API client module in the frontend (base URL, auth header injection, error handling) that all future features call through instead of raw `fetch`. Add one real round-trip (e.g. calling a `/health` or `/me` endpoint) to prove the wiring works end-to-end, including auth token forwarding from Task 3.

## 5. CI pipeline for lint + test
Goal: Every push/PR automatically runs lint and tests for both services.
Description: Add a CI workflow (e.g. GitHub Actions) with two jobs — one for the Next.js app (lint + test) and one for FastAPI (lint + test) — that must pass before merge. Use the passing tests from Task 1 as the initial baseline so the pipeline is provably working before any real feature lands.

---

**Phase 2 — Sprint Canvas & AI Decomposition**

## 6. Gemini API client wrapper
Goal: Give the backend one safe, reusable way to call the Gemini API.
Description: Add a small service module in FastAPI that reads the Google AI Studio API key from environment config and exposes a function to send a prompt and get a structured (JSON) response back. Include basic error handling for rate limits/timeouts and one integration test that can be skipped when no key is configured.

## 7. AI goal-decomposition endpoint
Goal: Turn a free-text user goal into a list of candidate backlog tasks.
Description: Add a FastAPI endpoint that takes a user's goal description, calls the Gemini wrapper (Task 6) with a prompt instructing it to output tasks tagged by pillar (Foundation/Drive/Joy) and hour estimate, and returns them as structured JSON. Enforce the 10-hour-per-project cap in the prompt and validate it in the response.

## 8. Split-screen Sprint Planning layout
Goal: Give Module 1 its page shell with the two-pane layout.
Description: Build the Next.js route for Sprint Planning with a left pane (placeholder for the chat coach) and a right pane (placeholder for the canvas), responsive down to a stacked layout on narrow screens. No real data yet — this is the structural shell later tasks fill in.

## 9. Conversational AI Planning Coach UI
Goal: Let the user chat with the AI to decompose a goal, inside the left pane from Task 8.
Description: Build a chat interface (message list + input box) that sends the user's messages to the decomposition endpoint (Task 7) and renders the AI's replies, including the returned candidate tasks in a readable format the user can react to before they're added to the canvas.

## 10. Interactive Kanban canvas
Goal: Let the user see and rearrange candidate/approved tasks visually.
Description: Build the right-pane canvas from Task 8 as a drag-and-drop Kanban board with columns per pillar (Foundation/Drive/Joy), where each card shows title and hour estimate and can be dragged between columns or reordered within one.

## 11. Backlog approval & sprint commitment
Goal: Let the user finalize which tasks become the active sprint's backlog.
Description: Add an endpoint and UI action that takes the currently arranged canvas tasks, lets the user adjust time estimates inline, and on confirmation persists them as committed `Task` rows (Task 2) attached to a new or current `Sprint`, locking them out of further free-form editing.

## 12. 10/90 rule budget guardrails
Goal: Prevent a sprint from exceeding its hour caps.
Description: Add validation (backend) and inline UI feedback (frontend) enforcing the 10-hour-per-project and 30-hour-total-per-sprint caps at the moment of backlog approval (Task 11), rejecting or flagging over-budget submissions with a clear message showing remaining hours per pillar.

---

**Phase 3 — Daily Standup Widget**

## 13. Daily Standup widget shell
Goal: Give Module 2 a lightweight entry point that appears on dashboard load.
Description: Build a compact modal or panel component that opens automatically once per day when the user loads the dashboard (track "already shown today" client- or server-side), with placeholder sections for the state tracker, priorities, and resource log that later tasks fill in.

## 14. 7-state NeuroBalance tracker
Goal: Let the user log their current state on the 7-point scale.
Description: Build an interactive horizontal scale UI (Apathy → Passivity → Relaxation → Balance → Engagement → Overarousal → Panic) that on selection posts a new `StateLog` row (Task 2) with a timestamp, inside the widget shell from Task 13.

## 15. Top 3 Daily Priorities selector
Goal: Let the user pick today's focus tasks from the approved backlog.
Description: Add a picker inside the standup widget that lists the current sprint's approved, incomplete tasks (from Task 11) and lets the user mark up to 3 as today's priorities, persisting the selection with today's date.

## 16. Remarkable-moment resource log
Goal: Capture one positive moment per day to train memory bias.
Description: Add a single free-text input inside the standup widget ("Remarkable moment of the last 24 hours") that saves the entry with a timestamp, and a simple read-only list elsewhere (even just an API endpoint) to confirm past entries persist correctly.

---

**Phase 4 — SOS Practices & Micro-regulations**

## 17. Global SOS floating action button
Goal: Make the SOS entry point reachable from anywhere in the app.
Description: Add a floating action button rendered in the app's root layout (so it appears on every screen) that opens an empty SOS modal placeholder on click, with no practice logic yet — just the always-available entry point.

## 18. Practice content data model + seed data
Goal: Have real practice content to route users to.
Description: Define a data model (or static content file) for a "practice": name, target state category (e.g. panic/overarousal vs. apathy/freeze), duration in minutes, and step-by-step instructions. Seed it with at least 3–4 real practices covering both trigger categories.

## 19. SOS triage flow
Goal: Route the user from "what I'm feeling" to the right practice.
Description: Inside the SOS modal (Task 17), add a quick symptom-selection step (e.g. "panic/overarousal" vs. "apathy/freeze") that, based on the answer, selects a matching practice from the content seeded in Task 18 and hands off to the practice player.

## 20. Guided practice player with timer
Goal: Walk the user through a single practice in real time.
Description: Build the player view that displays a chosen practice's instructions step by step alongside a running countdown timer (2–5 minutes), with start/pause/finish controls, launched from the triage flow in Task 19.

## 21. Neuro-Challenge Deck
Goal: Surface a proactive weekly micro-challenge outside of crisis moments.
Description: Add a small "deck" UI (e.g. on the dashboard) that shows one rotating weekly challenge (e.g. cold exposure, sensory anchoring) from a seeded challenge list, with a way to mark it done for the week.

---

**Phase 5 — Apple Reminders & Telegram Integrations**

## 22. CalDAV export of approved tasks
Goal: Push committed sprint tasks into Apple Reminders.
Description: Using a Python CalDAV client, add a backend job/endpoint that takes a user's committed `Task` rows (Task 11) and creates corresponding reminders in a designated iCloud Reminders list, storing the returned external ID on each `Task` row for later reconciliation.

## 23. CalDAV completion reconciliation
Goal: Reflect Apple Reminders completions back into the app.
Description: Add a scheduled job that polls (or syncs via CalDAV) the designated Reminders list, and for any reminder marked complete whose external ID matches a `Task` (Task 22), marks that task complete in the database and deducts its estimated hours from the sprint's spent-hours total.

## 24. Telegram bot scaffolding
Goal: Stand up a working Telegram bot the app can send messages through.
Description: Register a bot with BotFather, wire up `python-telegram-bot` in the FastAPI service with a webhook or polling loop, and implement a basic `/start` command that confirms the bot can reach a specific chat ID — no scheduled logic yet.

## 25. Scheduled Telegram notifications
Goal: Send the three recurring check-in prompts on schedule.
Description: Using the bot from Task 24, add scheduled jobs (e.g. via APScheduler/cron) that send a deep link message for the Morning Daily Standup, the End-of-week checkpoint, and the End-of-sprint Transformational Reflection, each linking back into the relevant app screen.

---

**Phase 6 — Reflection, Archive & Analytics Dashboard**

## 26. AI-guided sprint retrospective conversation
Goal: Let the AI walk the user through a review of their sprint at its close.
Description: Add an endpoint that gathers a sprint's `StateLog` history and task completion velocity, feeds a summary of it to the Gemini wrapper (Task 6) with a prompt to generate reflective, open-ended retrospective questions, and a chat UI (reusing patterns from Task 9) for the resulting conversation.

## 27. 4-Step Transformational Framework capture
Goal: Persist the structured end-of-sprint reflection.
Description: Add a form (or the natural end of the Task 26 conversation) with the four fixed prompts (Key Change Observed, Action Taken, Self-Insight, Emerging Opportunities), and an endpoint that saves the four answers to a sprint archive table linked to the completed `Sprint`.

## 28. Integration Week / Joy-Passana configurator
Goal: Let the user set up their Week 4 reset period.
Description: Build a settings screen for the integration week that lets the user pick a quiet-period duration (from 3 hours up to 3 days) and any reset preferences, persisting the configuration against the current `Sprint` record.

## 29. NeuroBalance heatmap
Goal: Visualize 21 days of state history at a glance.
Description: Build a color-coded grid/heatmap component that reads a sprint's `StateLog` entries (Task 2) across its 21 days and colors each day by dominant state, distinguishing integration, distress, and burnout zones per the design spec.

## 30. Sprint Time Meter gauges
Goal: Show remaining vs. spent hours at a glance.
Description: Build circular progress gauge components showing hours spent vs. the 10-hour cap for each of the three pillars and the 30-hour total cap, driven by completed/committed task hours (Tasks 11 and 23) for the current sprint.

## 31. Tri-Pillar Kanban dashboard view
Goal: Give the analytics dashboard a status-board view of the whole sprint.
Description: Build a read-only Kanban-style board (distinct from the planning canvas in Task 10) grouped by Foundation/Drive/Joy showing each task's current status, for use on the Module 5 analytics dashboard.
