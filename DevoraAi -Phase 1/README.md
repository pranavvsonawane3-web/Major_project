# Devora AI — DevOps Intelligence Platform

An intelligent DevOps and developer productivity platform that unifies Jira issue tracking, Git pull requests (Bitbucket, GitHub), CI/CD build observability, automated daily stand-up generation, and conversational AI assistance into a fast, unified command center.

---

## 🌟 Key Features

### 1. 📊 Centralized Command Dashboard (`dashboard.html`)
- **Real-Time KPI Metrics:** Live tracking of My Open Tickets, High Priority (P1) issues, In Progress tasks, Active Pull Requests, Pending Reviews, and Tasks Completed This Week.
- **Ticket Status Distribution:** Dynamic visual breakdown of sprint tickets across To Do, In Progress, and Done with live percentage calculations.
- **Sprint 42 Progress Ring:** Interactive SVG ring tracking real-time sprint completion percentage and remaining countdown.
- **Critical Action Items & Due Soon:** Direct links to pressing deadlines and P1 priority tasks.
- **Live Bitbucket & Git Commits Feed:** Real-time commit stream with author tags, repository labels, and relative timestamps.

### 2. 🎫 Jira Ticket Management (`tickets.html`)
- **Instant Search:** Real-time filtering across issue keys (`PROJ-xxx`, `SYS-xxx`), summaries, repositories, and assignees.
- **Status Tabs & Live Badges:** Filter between *All Active*, *To Do*, *In Progress*, *Review*, and *Done* with dynamic badge counters.
- **Priority Filter:** Filter tickets by High (P1), Medium (P2), or Low (P3).
- **Create Issue Modal:** Create new Jira tickets on the fly with custom summary, priority, repository, due date, and acceptance criteria.
- **Interactive Ticket Details Editor:** Click any ticket to open a modal to update status, change priority, modify notes, or delete the issue.

### 3. 🔀 Pull Requests & Code Reviews (`pull-requests.html`)
- **Review Workflow:** Categorized views for *Waiting for my review*, *Approved*, *Draft*, and *Recently Merged*.
- **Direct PR Actions:**
  - **Approve:** One-click approval badge.
  - **Merge:** Merge pull request into target branch and automatically record the activity event.
  - **Rerun CI:** Retry failed CI test suites with one click.
- **New Pull Request Modal:** Open new pull requests with custom branches, target branch, and diff summary.
- **PR Details Modal:** Inspect repository, branch paths, author, CI pipeline state, and code review comments.

### 4. 🤖 Devora AI DevOps Assistant (`chat.html`)
- **Interactive Conversational AI:** Natural language assistant tailored for DevOps, Kubernetes, Docker, Helm, CI/CD pipelines, and Git workflows.
- **Command Shortcuts:**
  - `/jira`: Instantly queries assigned sprint tickets and renders interactive preview cards.
  - `/pr`: Lists active pull requests with reviewer status and CI health.
  - `/standup`: Auto-generates structured daily stand-up updates (Yesterday, Today, Blockers).
  - `/status`: Checks microservice and infrastructure uptime.
- **Rich Media Output:** Renders formatted Markdown, interactive clickable ticket cards, status tables, and syntax-highlighted code.
- **Dual Engine Architecture:**
  - **Cloud:** Seamlessly connects to **Google Gemini API** (`gemini-3.8-flash`) when a `GEMINI_API_KEY` is provided.
  - **Edge/Offline:** Built-in intelligent rule & NLP engine that understands workspace state even without internet or API keys.

### 5. 🚀 Daily Stand-up & Activity Stream (`activity.html`)
- **AI Standup Generator:** One-click generation synthesizing yesterday's closed tickets and commits, today's priority items, and potential pipeline blockers.
- **Copy to Clipboard:** Copy markdown-ready updates directly into Slack, Microsoft Teams, or Jira with a single click.
- **Productivity Trend Chart:** Interactive weekly velocity visualization comparing code commits and review volume.
- **Live Activity Feed:** Chronological timeline of merged PRs, status transitions, review comments, and build events.

### 6. 🔌 Integrations Hub (`integrations.html` & `api-settings.html`)
- **Supported Platforms:** Jira, Bitbucket, GitHub, Jenkins, Slack, MS Teams, Datadog.
- **Connection Management:** Toggle connection states, configure workspace URLs, and securely store API tokens.
- **Sync All:** Synchronize webhooks and pipeline states across all active tools with live spinning progress.
- **Connection Test:** Live latency ping and health test for external credentials.

### 7. ⚙️ Account & Workspace Settings (`settings.html`)
- **Profile:** Manage user display name, avatar, role, and department.
- **Notifications:** Granular alert toggles for failed builds, PR review assignments, and Jira tickets.
- **API Key Manager:** Programmatically generate, copy, and revoke `devora_live_...` personal access tokens.
- **Appearance:** Theme toggle with high-contrast Dark Mode and clean Light Mode.

### 8. 🔍 Global Spotlight / Command Palette (⌘K / Ctrl+K)
- Available on every screen by pressing `⌘K` or `Ctrl+K` or clicking the Search bar in the top navigation header.
- Instantly searches tickets, pull requests, commits, and system pages.

---

## 🏗️ Architecture & Tech Stack

- **Backend:** Python 3.14 + FastAPI + Uvicorn (ASGI)
- **Data Persistence:** Persistent JSON Data Store (`data/devora_store.json`) with automated client-side `localStorage` caching fallback.
- **Frontend:** Semantic HTML5, Tailwind CSS, Google Material Symbols, Inter & JetBrains Mono typography.
- **Client Engine (`devora-core.js`):** Unified reactive client library handling API synchronization, modals, toasts, global keyboard shortcuts, and state events.
- **AI SDK:** `google-genai` SDK with support for `gemini-3.8-flash`.

---

## 🚀 Getting Started

### Quick Start (One-Click)
Double-click `start.bat` in the root project folder:
```cmd
..\start.bat
```
This automatically launches the FastAPI backend and opens the dashboard in your default browser at `http://127.0.0.1:8000`.