import sys
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_endpoints():
    print("Testing /api/health...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print("  -> Health OK:", r.json()["status"])

    print("Testing /api/stats...")
    r = client.get("/api/stats")
    assert r.status_code == 200, f"Stats failed: {r.status_code}"
    stats = r.json()
    print("  -> Stats OK: Open Tickets:", stats["openTicketsCount"], "PRs:", stats["pullRequestsCount"])

    print("Testing /api/tickets...")
    r = client.get("/api/tickets")
    assert r.status_code == 200
    tickets = r.json()
    print(f"  -> Found {len(tickets)} tickets")

    print("Testing /api/tickets (POST create)...")
    r = client.post("/api/tickets", json={
        "summary": "Automated verification ticket",
        "priority": "High",
        "status": "In Progress",
        "repo": "test-repo",
        "dueDate": "Tomorrow"
    })
    assert r.status_code == 200
    new_ticket = r.json()
    print(f"  -> Created ticket: {new_ticket['id']}")

    print("Testing /api/pull-requests...")
    r = client.get("/api/pull-requests")
    assert r.status_code == 200
    prs = r.json()
    print(f"  -> Found {len(prs)} PRs")

    print("Testing /api/pull-requests (POST create)...")
    r = client.post("/api/pull-requests", json={
        "title": "feat(test): automated test PR",
        "repo": "core-backend",
        "branch": "feature/automated-test"
    })
    assert r.status_code == 200
    new_pr = r.json()
    print(f"  -> Created PR: #{new_pr['id']}")

    print("Testing /api/pull-requests/{id} (PUT approve)...")
    r = client.put(f"/api/pull-requests/{new_pr['id']}", json={"action": "approve"})
    assert r.status_code == 200
    assert r.json()["status"] == "Approved"
    print(f"  -> Approved PR #{new_pr['id']}")

    print("Testing /api/activity/standup (POST)...")
    r = client.post("/api/activity/standup")
    assert r.status_code == 200
    standup = r.json()
    print("  -> Standup generated with", len(standup["yesterday"]), "yesterday items")

    print("Testing /api/integrations...")
    r = client.get("/api/integrations")
    assert r.status_code == 200
    print(f"  -> Found {len(r.json())} integrations")

    print("Testing /api/chat (POST /jira)...")
    r = client.post("/api/chat", json={"message": "/jira"})
    assert r.status_code == 200
    chat_res = r.json()
    print("  -> AI response received:", chat_res["text"][:50], "...")

    print("Testing /api/search?q=auth...")
    r = client.get("/api/search?q=auth")
    assert r.status_code == 200
    results = r.json()
    print(f"  -> Search returned {len(results)} items")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    test_endpoints()
