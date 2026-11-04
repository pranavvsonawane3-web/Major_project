import os
import json
import uuid
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Initialize Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "devora_store.json"
WEB_DIR = BASE_DIR / "Repos" / "devora"
if not WEB_DIR.exists() or not (WEB_DIR / "index.html").exists():
    if (BASE_DIR / "web").exists():
        WEB_DIR = BASE_DIR / "web"
    elif (BASE_DIR / "index.html").exists():
        WEB_DIR = BASE_DIR

app = FastAPI(
    title="Devora AI DevOps Platform API",
    description="Backend API powering the Devora AI DevOps Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to read/write state
def get_store() -> dict:
    if not DATA_FILE.exists():
        raise HTTPException(status_code=500, detail="Data store not initialized.")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_store(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Models
class TicketCreate(BaseModel):
    summary: str
    priority: str = "Med"
    status: str = "To Do"
    repo: Optional[str] = "core-backend"
    assignee: Optional[str] = "Alex Chen"
    dueDate: Optional[str] = "In 3 days"
    description: Optional[str] = ""

class TicketUpdate(BaseModel):
    summary: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None
    dueDate: Optional[str] = None
    description: Optional[str] = None

class PRCreate(BaseModel):
    title: str
    repo: str
    branch: str
    targetBranch: Optional[str] = "main"
    description: Optional[str] = ""

class PRAction(BaseModel):
    action: str  # 'approve', 'request_changes', 'merge', 'rerun_ci'

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class IntegrationConfig(BaseModel):
    workspaceUrl: Optional[str] = None
    workspaceId: Optional[str] = None
    apiToken: Optional[str] = None
    appPassword: Optional[str] = None
    project: Optional[str] = None

# --- API Endpoints ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "services": {
            "api_gateway": "online",
            "auth_service": "online",
            "k8s_cluster": "connected",
            "redis_cache": "connected",
            "jira_connector": "synced",
            "bitbucket_webhook": "active"
        }
    }

@app.get("/api/state")
def get_full_state():
    return get_store()

@app.get("/api/stats")
def get_dashboard_stats():
    store = get_store()
    tickets = store.get("tickets", [])
    prs = store.get("pull_requests", [])
    
    open_tickets = [t for t in tickets if t.get("status") != "Done"]
    high_priority = [t for t in open_tickets if t.get("priority") == "High"]
    in_progress = [t for t in tickets if t.get("status") == "In Progress"]
    done_tickets = [t for t in tickets if t.get("status") == "Done"]
    
    total = len(tickets) if tickets else 1
    todo_count = len([t for t in tickets if t.get("status") == "To Do"])
    prog_count = len(in_progress)
    done_count = len(done_tickets)
    
    review_prs = [p for p in prs if p.get("status") in ["Needs Review", "Review"]]
    
    # Calculate sprint completion percentage
    sprint_percent = round((done_count / total) * 100) if total > 0 else 0

    return {
        "openTicketsCount": len(open_tickets),
        "highPriorityCount": len(high_priority),
        "inProgressCount": len(in_progress),
        "pullRequestsCount": len(prs),
        "pendingReviewsCount": len(review_prs),
        "doneCount": done_count,
        "distribution": {
            "todo": round((todo_count / total) * 100),
            "inProgress": round((prog_count / total) * 100),
            "done": round((done_count / total) * 100),
            "counts": {
                "todo": todo_count,
                "inProgress": prog_count,
                "done": done_count
            }
        },
        "sprintProgress": {
            "percent": sprint_percent,
            "daysRemaining": 3,
            "sprintName": "Sprint 42"
        }
    }

# Tickets Endpoints
@app.get("/api/tickets")
def list_tickets(status: Optional[str] = None, priority: Optional[str] = None, search: Optional[str] = None):
    store = get_store()
    tickets = store.get("tickets", [])
    
    if status and status.lower() != "all" and status.lower() != "all active":
        tickets = [t for t in tickets if t.get("status", "").lower() == status.lower()]
    elif status and status.lower() == "all active":
        tickets = [t for t in tickets if t.get("status") != "Done"]

    if priority and priority.lower() != "all":
        tickets = [t for t in tickets if t.get("priority", "").lower() == priority.lower()]

    if search:
        s = search.lower()
        tickets = [
            t for t in tickets
            if s in t.get("id", "").lower() 
            or s in t.get("summary", "").lower() 
            or s in t.get("description", "").lower()
            or s in t.get("repo", "").lower()
        ]
        
    return tickets

@app.post("/api/tickets")
def create_ticket(item: TicketCreate):
    store = get_store()
    tickets = store.get("tickets", [])
    
    # Generate sequential or unique key
    existing_nums = []
    for t in tickets:
        parts = t.get("id", "").split("-")
        if len(parts) == 2 and parts[1].isdigit():
            existing_nums.append(int(parts[1]))
    next_num = max(existing_nums, default=500) + 1
    new_id = f"PROJ-{next_num}"
    
    user = store.get("user", {})
    new_ticket = {
        "id": new_id,
        "summary": item.summary,
        "priority": item.priority,
        "status": item.status,
        "assignee": item.assignee or user.get("name", "Alex Chen"),
        "assigneeAvatar": user.get("avatar", ""),
        "dueDate": item.dueDate or "Next Week",
        "repo": item.repo or "core-backend",
        "description": item.description or item.summary,
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    tickets.insert(0, new_ticket)
    
    # Add activity log
    activities = store.get("activities", [])
    activities.insert(0, {
        "id": f"act-{uuid.uuid4().hex[:6]}",
        "type": "ticket_created",
        "title": f"Created {new_id}",
        "subtitle": item.summary,
        "time": "Just now",
        "icon": "confirmation_number",
        "color": "primary"
    })
    
    save_store(store)
    return new_ticket

@app.put("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, patch: TicketUpdate):
    store = get_store()
    tickets = store.get("tickets", [])
    
    target = None
    for t in tickets:
        if t.get("id") == ticket_id:
            target = t
            break
            
    if not target:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    old_status = target.get("status")
    for k, v in patch.model_dump(exclude_unset=True).items():
        if v is not None:
            target[k] = v
            
    if patch.status and patch.status != old_status:
        activities = store.get("activities", [])
        activities.insert(0, {
            "id": f"act-{uuid.uuid4().hex[:6]}",
            "type": "ticket_status",
            "title": f"Moved {ticket_id} to {patch.status}",
            "subtitle": target.get("summary"),
            "time": "Just now",
            "icon": "check_circle" if patch.status == "Done" else "sync",
            "color": "primary" if patch.status == "Done" else "tertiary"
        })
        
    save_store(store)
    return target

@app.delete("/api/tickets/{ticket_id}")
def delete_ticket(ticket_id: str):
    store = get_store()
    tickets = store.get("tickets", [])
    new_tickets = [t for t in tickets if t.get("id") != ticket_id]
    if len(new_tickets) == len(tickets):
        raise HTTPException(status_code=404, detail="Ticket not found")
    store["tickets"] = new_tickets
    save_store(store)
    return {"success": True, "deleted": ticket_id}

# Pull Requests Endpoints
@app.get("/api/pull-requests")
def list_prs(search: Optional[str] = None, status: Optional[str] = None):
    store = get_store()
    prs = store.get("pull_requests", [])
    if status and status.lower() != "all":
        prs = [p for p in prs if p.get("status", "").lower() == status.lower()]
    if search:
        s = search.lower()
        prs = [p for p in prs if s in p.get("title", "").lower() or s in p.get("repo", "").lower() or s in p.get("branch", "").lower()]
    return prs

@app.post("/api/pull-requests")
def create_pr(item: PRCreate):
    store = get_store()
    prs = store.get("pull_requests", [])
    
    # Generate sequential PR number
    existing_nums = [int(p.get("id")) for p in prs if p.get("id", "").isdigit()]
    next_num = max(existing_nums, default=1200) + 1
    
    user = store.get("user", {})
    new_pr = {
        "id": str(next_num),
        "title": item.title,
        "repo": item.repo,
        "branch": item.branch,
        "targetBranch": item.targetBranch or "main",
        "author": user.get("name", "alex.chen").lower().replace(" ", "."),
        "authorAvatar": user.get("avatar", ""),
        "status": "Needs Review",
        "ciStatus": "Passing",
        "updated": "Just now",
        "reviewers": ["sarah.j", "ME"],
        "commentsCount": 0,
        "diff": "+64 -12 lines across 2 files"
    }
    
    prs.insert(0, new_pr)
    
    activities = store.get("activities", [])
    activities.insert(0, {
        "id": f"act-{uuid.uuid4().hex[:6]}",
        "type": "pr_opened",
        "title": f"Opened PR #{next_num} on {item.repo}",
        "subtitle": item.title,
        "time": "Just now",
        "icon": "call_split",
        "color": "primary"
    })
    
    save_store(store)
    return new_pr

@app.put("/api/pull-requests/{pr_id}")
def update_pr(pr_id: str, action_data: PRAction):
    store = get_store()
    prs = store.get("pull_requests", [])
    target = None
    for p in prs:
        if p.get("id") == pr_id:
            target = p
            break
            
    if not target:
        raise HTTPException(status_code=404, detail="Pull request not found")
        
    act = action_data.action.lower()
    if act == "approve":
        target["status"] = "Approved"
        target["updated"] = "Just now"
    elif act == "request_changes":
        target["status"] = "Changes Requested"
        target["updated"] = "Just now"
    elif act == "merge":
        target["status"] = "Merged"
        target["updated"] = "Just now"
        # Log activity
        activities = store.get("activities", [])
        activities.insert(0, {
            "id": f"act-{uuid.uuid4().hex[:6]}",
            "type": "pr_merge",
            "title": f"Merged PR #{pr_id} into {target.get('targetBranch', 'main')}",
            "subtitle": target.get("title"),
            "time": "Just now",
            "icon": "merge",
            "color": "primary"
        })
    elif act == "rerun_ci":
        target["ciStatus"] = "Passing"
        target["updated"] = "Just now"
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {act}")
        
    save_store(store)
    return target

# Activity & Stand-up Endpoints
@app.get("/api/activity")
def get_activity():
    store = get_store()
    return {
        "activities": store.get("activities", []),
        "commits": store.get("commits", [])
    }

@app.post("/api/activity/standup")
def generate_standup():
    store = get_store()
    tickets = store.get("tickets", [])
    commits = store.get("commits", [])
    prs = store.get("pull_requests", [])
    
    yesterday_done = [t for t in tickets if t.get("status") == "Done"]
    today_active = [t for t in tickets if t.get("status") == "In Progress"]
    high_priority = [t for t in tickets if t.get("priority") == "High" and t.get("status") != "Done"]
    
    # Generate stand-up text
    standup = {
        "timestamp": datetime.datetime.now().strftime("%A, %B %d, %Y"),
        "yesterday": [
            f"Completed ticket {t['id']}: {t['summary']}" for t in yesterday_done[:3]
        ] + [
            f"Pushed commit {c['hash']}: {c['message']} ({c['repo']})" for c in commits[:2]
        ],
        "today": [
            f"Focusing on {t['id']}: {t['summary']} (Priority: {t['priority']})" for t in today_active[:3]
        ] + [
            f"Reviewing PR #{p['id']}: {p['title']} ({p['repo']})" for p in prs if p.get("status") in ["Needs Review", "Review"]
        ][:2],
        "blockers": [
            f"High Priority Issue: {t['id']} - {t['summary']} requires immediate attention" for t in high_priority[:2]
        ] if high_priority else ["No blocking impediments currently."]
    }
    
    # Formatted markdown output
    md_text = f"### 🚀 Daily Standup - {standup['timestamp']}\n\n"
    md_text += "**Yesterday:**\n" + "\n".join(f"- {item}" for item in standup["yesterday"]) + "\n\n"
    md_text += "**Today:**\n" + "\n".join(f"- {item}" for item in standup["today"]) + "\n\n"
    md_text += "**Blockers:**\n" + "\n".join(f"- {item}" for item in standup["blockers"])
    
    standup["markdown"] = md_text
    return standup

# Integrations Endpoints
@app.get("/api/integrations")
def get_integrations():
    store = get_store()
    return store.get("integrations", [])

@app.post("/api/integrations/{name}/toggle")
def toggle_integration(name: str):
    store = get_store()
    integrations = store.get("integrations", [])
    target = None
    for item in integrations:
        if item.get("id").lower() == name.lower() or item.get("name").lower() == name.lower():
            target = item
            break
            
    if not target:
        raise HTTPException(status_code=404, detail="Integration not found")
        
    target["connected"] = not target["connected"]
    target["status"] = "Connected" if target["connected"] else "Disconnected"
    if target["connected"]:
        target["lastSync"] = "Just now"
        
    save_store(store)
    return target

@app.post("/api/integrations/{name}/configure")
def configure_integration(name: str, config: IntegrationConfig):
    store = get_store()
    integrations = store.get("integrations", [])
    target = None
    for item in integrations:
        if item.get("id").lower() == name.lower() or item.get("name").lower() == name.lower():
            target = item
            break
            
    if not target:
        raise HTTPException(status_code=404, detail="Integration not found")
        
    for k, v in config.model_dump(exclude_unset=True).items():
        if v:
            target[k] = v
            
    target["connected"] = True
    target["status"] = "Connected"
    target["lastSync"] = "Just now"
    save_store(store)
    return target

@app.post("/api/integrations/sync-all")
def sync_all_integrations():
    store = get_store()
    integrations = store.get("integrations", [])
    synced_count = 0
    for item in integrations:
        if item.get("connected"):
            item["lastSync"] = "Just now"
            synced_count += 1
    save_store(store)
    return {
        "success": True,
        "syncedCount": synced_count,
        "message": f"Successfully synced {synced_count} active integrations"
    }

@app.post("/api/integrations/test-connection")
def test_connection(payload: dict = Body(...)):
    # Simulate pinging API
    service = payload.get("service", "Integration")
    return {
        "success": True,
        "latencyMs": 142,
        "status": 200,
        "message": f"Connection to {service} verified successfully!"
    }

# Settings Endpoints
@app.get("/api/settings")
def get_settings():
    store = get_store()
    return store.get("settings", {})

@app.put("/api/settings")
def update_settings(payload: dict = Body(...)):
    store = get_store()
    current_settings = store.get("settings", {})
    current_settings.update(payload)
    store["settings"] = current_settings
    save_store(store)
    return current_settings

@app.get("/api/user")
def get_user_profile():
    store = get_store()
    return store.get("user", {})

@app.put("/api/user")
def update_user_profile(payload: dict = Body(...)):
    store = get_store()
    user = store.get("user", {})
    user.update(payload)
    store["user"] = user
    save_store(store)
    return user

# Global Search
@app.get("/api/search")
def global_search(q: str = Query(..., min_length=1)):
    store = get_store()
    query = q.lower()
    results = []
    
    # Search Tickets
    for t in store.get("tickets", []):
        if query in t.get("id", "").lower() or query in t.get("summary", "").lower():
            results.append({
                "type": "ticket",
                "title": f"{t['id']}: {t['summary']}",
                "subtitle": f"{t['status']} · {t['priority']} Priority",
                "url": f"tickets.html?id={t['id']}",
                "icon": "confirmation_number"
            })
            
    # Search PRs
    for p in store.get("pull_requests", []):
        if query in p.get("id", "").lower() or query in p.get("title", "").lower() or query in p.get("repo", "").lower():
            results.append({
                "type": "pull_request",
                "title": f"#{p['id']}: {p['title']}",
                "subtitle": f"{p['repo']} · {p['status']}",
                "url": f"pull-requests.html?id={p['id']}",
                "icon": "merge"
            })
            
    # Search Commits
    for c in store.get("commits", []):
        if query in c.get("message", "").lower() or query in c.get("hash", "").lower() or query in c.get("repo", "").lower():
            results.append({
                "type": "commit",
                "title": f"{c['hash']}: {c['message']}",
                "subtitle": f"{c['repo']} · {c['time']}",
                "url": f"dashboard.html",
                "icon": "commit"
            })
            
    # Search Integrations
    for i in store.get("integrations", []):
        if query in i.get("name", "").lower():
            results.append({
                "type": "integration",
                "title": f"{i['name']} Integration",
                "subtitle": f"Status: {i['status']}",
                "url": "integrations.html",
                "icon": "extension"
            })

    # Search Pages
    pages = [
        {"title": "Dashboard", "subtitle": "System overview & metrics", "url": "dashboard.html", "icon": "dashboard"},
        {"title": "Tickets Management", "subtitle": "Jira issues & active sprint", "url": "tickets.html", "icon": "confirmation_number"},
        {"title": "Pull Requests", "subtitle": "Code reviews & PR tracking", "url": "pull-requests.html", "icon": "merge"},
        {"title": "Devora AI Chat", "subtitle": "Query tickets, PRs, and DevOps assistance", "url": "chat.html", "icon": "smart_toy"},
        {"title": "Daily Stand-up & Activity", "subtitle": "Standup generator & timeline", "url": "activity.html", "icon": "switch_account"},
        {"title": "Integrations", "subtitle": "Jira, Bitbucket, GitHub, Jenkins", "url": "integrations.html", "icon": "extension"},
        {"title": "Settings", "subtitle": "Profile, notifications & API keys", "url": "settings.html", "icon": "settings"},
        {"title": "API & Token Settings", "subtitle": "Workspace credentials", "url": "api-settings.html", "icon": "key"}
    ]
    for page in pages:
        if query in page["title"].lower() or query in page["subtitle"].lower():
            results.append({
                "type": "page",
                "title": page["title"],
                "subtitle": page["subtitle"],
                "url": page["url"],
                "icon": page["icon"]
            })

    return results

# AI Chat Assistant Endpoint
@app.post("/api/chat")
async def chat_interaction(req: ChatRequest):
    store = get_store()
    user_msg = req.message.strip()
    low_msg = user_msg.lower()
    
    # Check for real Gemini API Key
    gemini_key = os.environ.get("GEMINI_API_KEY") or store.get("settings", {}).get("gemini", {}).get("apiKey")
    
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=gemini_key)
            system_prompt = f"""You are Devora AI, an intelligent DevOps assistant.
Current User: {store.get('user', {}).get('name', 'Alex Chen')} ({store.get('user', {}).get('role')})
Current Tickets in Sprint: {len(store.get('tickets', []))}
Open PRs: {len(store.get('pull_requests', []))}
Active Integrations: {', '.join([i['name'] for i in store.get('integrations', []) if i.get('connected')])}

You help engineers query Jira tickets, pull requests, CI/CD pipelines, Docker, Kubernetes, and generate standups.
Format responses in clear, readable Markdown with code blocks and bullet points. Be concise, technical, and helpful."""

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_msg,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7
                )
            )
            return {
                "sender": "ai",
                "text": response.text,
                "timestamp": datetime.datetime.now().strftime("%I:%M %p")
            }
        except Exception as e:
            # Fall through to built-in smart assistant engine if error or quota reached
            pass

    # Built-in Intelligent DevOps Engine
    tickets = store.get("tickets", [])
    prs = store.get("pull_requests", [])
    commits = store.get("commits", [])
    
    # 1. /jira or ticket query
    if "/jira" in low_msg or "ticket" in low_msg or "issue" in low_msg:
        open_t = [t for t in tickets if t.get("status") != "Done"]
        high_t = [t for t in open_t if t.get("priority") == "High"]
        
        cards = [
            {
                "key": t["id"],
                "priority": t["priority"],
                "title": t["summary"],
                "status": t["status"]
            }
            for t in open_t[:4]
        ]
        
        table = [
            {
                "key": t["id"],
                "summary": t["summary"],
                "priority": t["priority"],
                "status": t["status"],
                "due": t["dueDate"]
            }
            for t in open_t[:5]
        ]
        
        return {
            "sender": "ai",
            "text": f"You currently have **{len(open_t)} active tickets** assigned in Sprint 42 ({len(high_t)} are High Priority):",
            "cards": cards,
            "table": table,
            "timestamp": datetime.datetime.now().strftime("%I:%M %p")
        }
        
    # 2. /pr or pull request query
    if "/pr" in low_msg or "pull request" in low_msg or "review" in low_msg:
        active_prs = [p for p in prs if p.get("status") != "Merged"]
        table = [
            {
                "key": f"#{p['id']}",
                "summary": p["title"],
                "priority": p["repo"],
                "status": p["status"],
                "due": p["ciStatus"]
            }
            for p in active_prs[:5]
        ]
        return {
            "sender": "ai",
            "text": f"You have **{len(active_prs)} open Pull Requests** across your repositories. 1 has a failed CI check:",
            "table": table,
            "actions": [
                {"label": "View All PRs", "url": "pull-requests.html"},
                {"label": "New PR", "action": "open_pr_modal"}
            ],
            "timestamp": datetime.datetime.now().strftime("%I:%M %p")
        }
        
    # 3. /standup or standup query
    if "/standup" in low_msg or "standup" in low_msg or "yesterday" in low_msg:
        yesterday_items = [t for t in tickets if t.get("status") == "Done"][:2]
        today_items = [t for t in tickets if t.get("status") == "In Progress"][:2]
        text = "### 📋 AI Stand-up Generated for Today\n\n"
        text += "**Yesterday:**\n"
        for t in yesterday_items:
            text += f"- Completed `{t['id']}`: {t['summary']}\n"
        text += f"- Merged PR #1024 into main (`core-auth-service`)\n\n"
        text += "**Today:**\n"
        for t in today_items:
            text += f"- Working on `{t['id']}`: {t['summary']}\n"
        text += "- Reviewing pending PRs for staging deployment\n\n"
        text += "**Blockers:**\n"
        text += "- None at present. Staging pipeline health is green."
        return {
            "sender": "ai",
            "text": text,
            "timestamp": datetime.datetime.now().strftime("%I:%M %p")
        }

    # 4. /status or health query
    if "/status" in low_msg or "health" in low_msg or "system" in low_msg:
        return {
            "sender": "ai",
            "text": "### 🟢 System Status: All Systems Operational\n\n- **API Gateway:** 99.98% uptime, 24ms avg latency\n- **Auth Service:** Healthy (Redis session cache hit rate 94%)\n- **Kubernetes:** 12/12 worker nodes Ready\n- **CI/CD Pipeline:** Jenkins 3 active jobs, Bitbucket webhooks operational",
            "timestamp": datetime.datetime.now().strftime("%I:%M %p")
        }
        
    # 5. Default DevOps Assistance
    return {
        "sender": "ai",
        "text": f"I analyzed your request: *\"{user_msg}\"*\n\nHere are some quick actions you can run:\n- Type `/jira` to inspect your assigned tickets\n- Type `/pr` to view open pull requests and CI status\n- Type `/standup` to auto-generate your daily update\n- Type `/status` to check infrastructure health\n\nOr ask any question about Kubernetes, Docker, Helm, Git, or CI/CD pipelines!",
        "timestamp": datetime.datetime.now().strftime("%I:%M %p")
    }

# Static file mount for web frontend
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    reload_mode = True if os.environ.get("PORT") is None else False
    print("\n" + "="*60)
    print(" >>> DEVORA AI - DEVOPS INTELLIGENCE PLATFORM")
    print(f" Access Web App: http://{host}:{port}")
    print(f" API Documentation: http://{host}:{port}/docs")
    print("="*60 + "\n")
    uvicorn.run("server:app", host=host, port=port, reload=reload_mode)
