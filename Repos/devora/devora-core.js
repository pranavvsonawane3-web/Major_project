/**
 * Devora AI - Core Application Engine & Data Layer
 * Handles dynamic rendering, state persistence (API + LocalStorage fallback),
 * modals, global search, notifications, chat, and all page interactions.
 */

(function () {
  'use strict';

  // Default Initial Dataset (used if backend is offline or localStorage is empty)
  const DEFAULT_DATA = {
    user: {
      name: "Alex Chen",
      email: "alex.chen@systemcore.dev",
      role: "Senior DevOps Engineer",
      avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuAfGl7Ti_ddQRcdadRwh6S-WjOJ7pVim5eugp1PMBLCpFAWRtMItbSA5AmYXOZdFLmr4hqr0XEiAkXE4tpOX79lzvnurZBiT8tQsPycBANDwYptifDEMS322Fb0vY6DE_lYOXlU9hoSseAQrseERt5oVvKlS2qv2Q1gYhwhsNj28_6k5WwxX8qMj20vgbeG_8nh72KzAfCwexo-YuGxEmxUJvMzh1u6TdWALqw39Z31mOJdrRTw-g062A",
      department: "Platform Infrastructure",
      status: "online"
    },
    tickets: [
      {
        id: "PROJ-452",
        summary: "Implement OAuth flow for third-party integrations",
        priority: "High",
        status: "In Progress",
        assignee: "Alex Chen",
        dueDate: "Oct 24",
        repo: "core-auth-service",
        description: "Allow single sign-on with Google, GitHub, and Bitbucket using OAuth2 PKCE flow."
      },
      {
        id: "PROJ-489",
        summary: "Fix race condition in worker pool shutdown",
        priority: "High",
        status: "In Progress",
        assignee: "Alex Chen",
        dueDate: "Oct 22",
        repo: "data-pipeline-go",
        description: "Gracefully drain task channel on SIGTERM signal without dropping active batch transactions."
      },
      {
        id: "SYS-4092",
        summary: "Investigate high latency on core auth service",
        priority: "High",
        status: "To Do",
        assignee: "Alex Chen",
        dueDate: "Oct 20",
        repo: "core-auth-service",
        description: "p99 latency spikes during JWT signature verification under peak traffic hours."
      },
      {
        id: "UI-883",
        summary: "Refactor notification dropdown component",
        priority: "Med",
        status: "In Progress",
        assignee: "Alex Chen",
        dueDate: "Oct 25",
        repo: "frontend-webapp",
        description: "Improve keyboard navigation, ARIA attributes, and smooth CSS transitions on open/close."
      },
      {
        id: "DB-102",
        summary: "Add index to user_sessions table",
        priority: "Low",
        status: "To Do",
        assignee: "Alex Chen",
        dueDate: "Oct 28",
        repo: "database-migrations",
        description: "Create composite B-tree index on (user_id, expires_at) for efficient session garbage collection."
      },
      {
        id: "SYS-4100",
        summary: "Finalize API Contract for Microservices",
        priority: "High",
        status: "In Progress",
        assignee: "Alex Chen",
        dueDate: "Oct 26",
        repo: "api-gateway",
        description: "Align OpenAPI 3.1 specifications across billing, auth, and analytics services."
      },
      {
        id: "DEVOPS-99",
        summary: "Deploy RC to Staging",
        priority: "Med",
        status: "Review",
        assignee: "Alex Chen",
        dueDate: "Oct 27",
        repo: "infra-k8s",
        description: "Deploy Helm chart release 2.4.0-rc3 to the European staging cluster for QA validation."
      },
      {
        id: "AUTH-442",
        summary: "Implement OAuth2 refresh token rotation mechanism",
        priority: "High",
        status: "Done",
        assignee: "Alex Chen",
        dueDate: "Oct 18",
        repo: "core-auth-service",
        description: "Revoke previous refresh tokens upon reuse detection to prevent replay attacks."
      },
      {
        id: "CORE-891",
        summary: "Refactor user session caching strategy in Redis cluster",
        priority: "Med",
        status: "Done",
        assignee: "Alex Chen",
        dueDate: "Oct 19",
        repo: "cache-service",
        description: "Use Redis hash structures instead of raw JSON strings to minimize memory footprint by 35%."
      },
      {
        id: "PROJ-124",
        summary: "Implement rate limiting middleware",
        priority: "Med",
        status: "In Progress",
        assignee: "Alex Chen",
        dueDate: "Oct 24",
        repo: "api-gateway",
        description: "Token bucket algorithm with Redis backend supporting per-tenant tier limits."
      },
      {
        id: "PROJ-189",
        summary: "Update dependencies for core runner",
        priority: "Low",
        status: "To Do",
        assignee: "Alex Chen",
        dueDate: "Oct 29",
        repo: "runner-core",
        description: "Bump Go dependencies to latest security patches and run vulnerability scan."
      },
      {
        id: "PROJ-201",
        summary: "Fix UI inconsistency on mobile nav",
        priority: "Med",
        status: "Review",
        assignee: "Alex Chen",
        dueDate: "Oct 26",
        repo: "frontend-webapp",
        description: "Ensure drawer closes smoothly when clicking outside or selecting any navigation link."
      }
    ],
    pull_requests: [
      {
        id: "4892",
        title: "Implement new virtual scrolling strategy for datagrid",
        repo: "frontend-core",
        branch: "feature/virtual-scroll",
        author: "alex.chen",
        status: "Needs Review",
        ciStatus: "Failed",
        updated: "2h ago",
        reviewers: ["sarah.j", "ME"]
      },
      {
        id: "112",
        title: "WIP: Migrate to generic OAuth2 provider interface",
        repo: "auth-service",
        branch: "refactor/oauth2-provider",
        author: "sarah.j",
        status: "Draft",
        ciStatus: "Passing",
        updated: "4h ago",
        reviewers: ["ME"]
      },
      {
        id: "492",
        title: "feat: impl oauth2 flow",
        repo: "core-auth-service",
        branch: "feature/oauth-login",
        author: "jsmith",
        status: "Review",
        ciStatus: "Passing",
        updated: "1d ago",
        reviewers: ["ME", "alex.chen"]
      },
      {
        id: "811",
        title: "fix: race condition in worker pool",
        repo: "data-pipeline-go",
        branch: "bugfix/worker-race",
        author: "alee",
        status: "Approved",
        ciStatus: "Passing",
        updated: "2d ago",
        reviewers: ["alex.chen"]
      },
      {
        id: "1102",
        title: "chore: update react to 18",
        repo: "frontend-webapp",
        branch: "chore/react-18",
        author: "mchen",
        status: "Draft",
        ciStatus: "Passing",
        updated: "3d ago",
        reviewers: ["alex.chen"]
      },
      {
        id: "1024",
        title: "feat(auth): implement oauth2 token rotation",
        repo: "core-auth-service",
        branch: "feat/token-rotation",
        author: "alex.chen",
        status: "Merged",
        ciStatus: "Passing",
        updated: "4d ago",
        reviewers: ["jsmith"]
      }
    ],
    commits: [
      {
        hash: "7a8f9c1",
        message: "Merge branch 'hotfix/db-conn' into main",
        repo: "core-backend",
        author: "alex.chen",
        time: "12m ago"
      },
      {
        hash: "b2c3d4e",
        message: "fix: connection pool exhaustion under load",
        repo: "core-backend",
        author: "alex.chen",
        time: "45m ago"
      },
      {
        hash: "f4e5a6b",
        message: "docs: update readme with new setup instructions",
        repo: "frontend-webapp",
        author: "mchen",
        time: "2h ago"
      },
      {
        hash: "c6c7f73",
        message: "added integration file and connection endpoints",
        repo: "devora",
        author: "alex.chen",
        time: "4h ago"
      },
      {
        hash: "8dad9b1",
        message: "A step towards my developer journey",
        repo: "devora",
        author: "alex.chen",
        time: "1d ago"
      }
    ],
    integrations: [
      { id: "jira", name: "Jira", connected: true, status: "Connected", project: "Alpha", openIssues: 12 },
      { id: "bitbucket", name: "Bitbucket", connected: true, status: "Connected", repositories: 12, activePrs: 5 },
      { id: "github", name: "GitHub", connected: false, status: "Disconnected", repositories: "--", activePrs: "--" },
      { id: "jenkins", name: "Jenkins", connected: true, status: "Connected", activePipelines: 3, lastBuild: "5m ago" },
      { id: "slack", name: "Slack", connected: true, status: "Needs Config", workspace: "DevOps-Internal", alertChannels: "Pending" },
      { id: "teams", name: "MS Teams", connected: false, status: "Disconnected", workspace: "--", alertChannels: "--" }
    ],
    notifications: [
      { id: 1, title: "Build Failed", text: "Staging pipeline e2e test timeout on branch main", time: "10m ago", unread: true, icon: "error", color: "error" },
      { id: 2, title: "PR Review Requested", text: "sarah.j requested your review on PR #112", time: "42m ago", unread: true, icon: "rate_review", color: "primary" },
      { id: 3, title: "Ticket Assigned", text: "SYS-4100 was assigned to you by Tech Lead", time: "2h ago", unread: false, icon: "assignment_ind", color: "secondary" }
    ],
    settings: {
      notifications: { failedBuilds: true, prReviews: true, ticketAssignments: true, slackAlerts: false },
      appearance: { theme: "dark" }
    }
  };

  // State Management: sync with localStorage and backend
  class DevoraState {
    constructor() {
      this.isOnline = true;
      this.initLocal();
    }

    initLocal() {
      const stored = localStorage.getItem('devora_state');
      if (!stored) {
        localStorage.setItem('devora_state', JSON.stringify(DEFAULT_DATA));
      }
    }

    getLocal() {
      try {
        return JSON.parse(localStorage.getItem('devora_state')) || DEFAULT_DATA;
      } catch (e) {
        return DEFAULT_DATA;
      }
    }

    setLocal(data) {
      localStorage.setItem('devora_state', JSON.stringify(data));
    }

    async api(endpoint, options = {}) {
      try {
        const res = await fetch('/api' + endpoint, {
          headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
          ...options
        });
        if (res.ok) {
          const json = await res.json();
          return json;
        }
      } catch (err) {
        // Fallback gracefully to client-side localStorage handling
      }
      return this.handleLocalApi(endpoint, options);
    }

    handleLocalApi(endpoint, options = {}) {
      const method = (options.method || 'GET').toUpperCase();
      const body = options.body ? JSON.parse(options.body) : {};
      const state = this.getLocal();

      if (endpoint === '/stats') {
        const tickets = state.tickets || [];
        const open = tickets.filter(t => t.status !== 'Done');
        const high = open.filter(t => t.priority === 'High');
        const inProg = tickets.filter(t => t.status === 'In Progress');
        const done = tickets.filter(t => t.status === 'Done');
        const total = tickets.length || 1;
        const todo = tickets.filter(t => t.status === 'To Do');

        return {
          openTicketsCount: open.length,
          highPriorityCount: high.length,
          inProgressCount: inProg.length,
          pullRequestsCount: state.pull_requests.length,
          pendingReviewsCount: state.pull_requests.filter(p => p.status === 'Needs Review' || p.status === 'Review').length,
          doneCount: done.length,
          distribution: {
            todo: Math.round((todo.length / total) * 100),
            inProgress: Math.round((inProg.length / total) * 100),
            done: Math.round((done.length / total) * 100),
            counts: { todo: todo.length, inProgress: inProg.length, done: done.length }
          },
          sprintProgress: {
            percent: Math.round((done.length / total) * 100),
            daysRemaining: 3
          }
        };
      }

      if (endpoint.startsWith('/tickets')) {
        if (method === 'GET') {
          return state.tickets || [];
        }
        if (method === 'POST') {
          const tickets = state.tickets || [];
          const nextId = "PROJ-" + (Math.floor(Math.random() * 800) + 500);
          const newTicket = {
            id: nextId,
            summary: body.summary,
            priority: body.priority || 'Med',
            status: body.status || 'To Do',
            assignee: body.assignee || state.user.name,
            dueDate: body.dueDate || 'Next week',
            repo: body.repo || 'core-backend',
            description: body.description || ''
          };
          tickets.unshift(newTicket);
          state.tickets = tickets;
          this.setLocal(state);
          return newTicket;
        }
      }

      if (endpoint.startsWith('/pull-requests')) {
        if (method === 'GET') return state.pull_requests || [];
        if (method === 'POST') {
          const prs = state.pull_requests || [];
          const nextPr = {
            id: String(Math.floor(Math.random() * 8000) + 1200),
            title: body.title,
            repo: body.repo,
            branch: body.branch,
            author: state.user.name.toLowerCase().replace(' ', '.'),
            status: 'Needs Review',
            ciStatus: 'Passing',
            updated: 'Just now',
            reviewers: ['ME']
          };
          prs.unshift(nextPr);
          state.pull_requests = prs;
          this.setLocal(state);
          return nextPr;
        }
      }

      if (endpoint === '/activity/standup') {
        const done = (state.tickets || []).filter(t => t.status === 'Done');
        const prog = (state.tickets || []).filter(t => t.status === 'In Progress');
        return {
          timestamp: new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }),
          yesterday: done.map(t => `Completed ${t.id}: ${t.summary}`),
          today: prog.map(t => `Working on ${t.id}: ${t.summary}`),
          blockers: ["None reported at present."]
        };
      }

      if (endpoint === '/chat') {
        const msg = (body.message || '').toLowerCase();
        if (msg.includes('/jira') || msg.includes('ticket')) {
          const open = (state.tickets || []).filter(t => t.status !== 'Done');
          return {
            sender: 'ai',
            text: `You have **${open.length} active tickets** in Sprint 42:`,
            cards: open.slice(0, 3).map(t => ({ key: t.id, priority: t.priority, title: t.summary, status: t.status })),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
        }
        if (msg.includes('/pr') || msg.includes('pull request')) {
          const prs = state.pull_requests || [];
          return {
            sender: 'ai',
            text: `You have **${prs.length} pull requests** currently tracked across repositories:`,
            table: prs.slice(0, 4).map(p => ({ key: '#' + p.id, summary: p.title, priority: p.repo, status: p.status, due: p.ciStatus })),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
        }
        if (msg.includes('/standup')) {
          return {
            sender: 'ai',
            text: "### 📋 Daily Standup Summary\n\n**Yesterday:** Completed OAuth token refresh & session caching.\n**Today:** Focus on worker pool race condition.\n**Blockers:** None currently.",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
        }
        return {
          sender: 'ai',
          text: `Devora AI analyzed your query: *"${body.message}"*.\n\nUse quick commands like \`/jira\`, \`/pr\`, or \`/standup\` to view real-time pipeline and sprint data!`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
      }

      return state;
    }
  }

  const Devora = {
    state: new DevoraState(),

    // Toast notification manager
    toast(message, type = 'info') {
      let container = document.getElementById('devora-toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'devora-toast-container';
        container.className = 'fixed bottom-6 right-6 z-[9999] flex flex-col gap-2 pointer-events-none';
        document.body.appendChild(container);
      }

      const toast = document.createElement('div');
      const bgColors = {
        success: 'bg-[#171f33] border-primary text-on-surface',
        error: 'bg-[#171f33] border-error text-error',
        info: 'bg-[#171f33] border-outline-variant text-on-surface',
        warning: 'bg-[#171f33] border-tertiary-container text-tertiary'
      };

      const iconNames = {
        success: 'check_circle',
        error: 'error',
        info: 'info',
        warning: 'warning'
      };

      toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl border shadow-2xl backdrop-blur-xl pointer-events-auto transform translate-y-4 opacity-0 transition-all duration-300 ${bgColors[type] || bgColors.info}`;
      toast.innerHTML = `
        <span class="material-symbols-outlined text-[20px]">${iconNames[type] || 'info'}</span>
        <span class="text-sm font-medium font-body-md">${message}</span>
        <button class="ml-2 text-outline hover:text-on-surface text-lg leading-none" onclick="this.parentElement.remove()">&times;</button>
      `;

      container.appendChild(toast);

      requestAnimationFrame(() => {
        toast.classList.remove('translate-y-4', 'opacity-0');
      });

      setTimeout(() => {
        toast.classList.add('translate-y-4', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    },

    // Global Modal Controller
    openModal(htmlContent, onOpen) {
      this.closeModal();
      const overlay = document.createElement('div');
      overlay.id = 'devora-modal-overlay';
      overlay.className = 'fixed inset-0 bg-background/80 backdrop-blur-md z-[999] flex items-center justify-center p-4 transition-opacity duration-200';
      overlay.innerHTML = `
        <div class="relative w-full max-w-lg bg-surface-container rounded-2xl border border-outline-variant shadow-2xl overflow-hidden p-6 scale-95 transform transition-transform duration-200" id="devora-modal-box">
          <button class="absolute top-4 right-4 text-outline hover:text-on-surface" onclick="Devora.closeModal()">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
          ${htmlContent}
        </div>
      `;
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) Devora.closeModal();
      });
      document.body.appendChild(overlay);

      requestAnimationFrame(() => {
        const box = document.getElementById('devora-modal-box');
        if (box) box.classList.remove('scale-95');
      });

      if (onOpen) onOpen(overlay);
    },

    closeModal() {
      const existing = document.getElementById('devora-modal-overlay');
      if (existing) {
        const box = document.getElementById('devora-modal-box');
        if (box) box.classList.add('scale-95');
        existing.style.opacity = '0';
        setTimeout(() => existing.remove(), 150);
      }
    },

    // Global Search Palette (⌘K)
    openSearchPalette() {
      this.openModal(`
        <div class="flex flex-col gap-4">
          <div class="flex items-center gap-3 border-b border-outline-variant pb-3">
            <span class="material-symbols-outlined text-outline text-[22px]">search</span>
            <input id="palette-search-input" type="text" placeholder="Search tickets, PRs, commits, pages... (e.g. PROJ, auth, review)" class="w-full bg-transparent text-on-surface placeholder:text-outline outline-none font-body-md text-base" autofocus />
            <span class="text-xs font-label-mono bg-surface-container-high px-2 py-1 rounded text-outline">ESC</span>
          </div>
          <div id="palette-results" class="max-h-72 overflow-y-auto flex flex-col gap-1 pr-1">
            <div class="text-xs font-label-mono text-outline uppercase px-2 py-1">Quick Navigation</div>
            <a href="dashboard.html" class="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-container-high text-on-surface transition-colors">
              <span class="material-symbols-outlined text-[18px] text-primary">dashboard</span>
              <div class="flex flex-col">
                <span class="text-sm font-medium">Dashboard</span>
                <span class="text-xs text-on-surface-variant">Live metrics and overview</span>
              </div>
            </a>
            <a href="tickets.html" class="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-container-high text-on-surface transition-colors">
              <span class="material-symbols-outlined text-[18px] text-primary">confirmation_number</span>
              <div class="flex flex-col">
                <span class="text-sm font-medium">My Tickets</span>
                <span class="text-xs text-on-surface-variant">Jira issues & active sprint</span>
              </div>
            </a>
            <a href="pull-requests.html" class="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-container-high text-on-surface transition-colors">
              <span class="material-symbols-outlined text-[18px] text-primary">merge</span>
              <div class="flex flex-col">
                <span class="text-sm font-medium">Pull Requests</span>
                <span class="text-xs text-on-surface-variant">Reviews and merging</span>
              </div>
            </a>
            <a href="chat.html" class="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-container-high text-on-surface transition-colors">
              <span class="material-symbols-outlined text-[18px] text-primary">smart_toy</span>
              <div class="flex flex-col">
                <span class="text-sm font-medium">Devora AI Assistant</span>
                <span class="text-xs text-on-surface-variant">Interactive DevOps queries</span>
              </div>
            </a>
          </div>
        </div>
      `, (overlay) => {
        const input = overlay.querySelector('#palette-search-input');
        const results = overlay.querySelector('#palette-results');
        if (!input) return;
        input.focus();

        input.addEventListener('input', async () => {
          const val = input.value.trim().toLowerCase();
          if (!val) return;
          const searchRes = await Devora.state.api('/search?q=' + encodeURIComponent(val));
          if (Array.isArray(searchRes) && searchRes.length > 0) {
            results.innerHTML = `
              <div class="text-xs font-label-mono text-outline uppercase px-2 py-1">Search Results (${searchRes.length})</div>
              ${searchRes.map(item => `
                <a href="${item.url}" class="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-container-high text-on-surface transition-colors">
                  <span class="material-symbols-outlined text-[18px] text-primary">${item.icon || 'arrow_forward'}</span>
                  <div class="flex flex-col flex-1 min-w-0">
                    <span class="text-sm font-medium truncate">${item.title}</span>
                    <span class="text-xs text-on-surface-variant truncate">${item.subtitle || ''}</span>
                  </div>
                </a>
              `).join('')}
            `;
          } else {
            results.innerHTML = `<div class="p-4 text-center text-outline text-sm">No results found for "${val}"</div>`;
          }
        });
      });
    },

    // Global Notifications Menu
    toggleNotifications(anchorEl) {
      let popover = document.getElementById('devora-notifications-popover');
      if (popover) {
        popover.remove();
        return;
      }

      const rect = anchorEl.getBoundingClientRect();
      popover = document.createElement('div');
      popover.id = 'devora-notifications-popover';
      popover.className = 'fixed bg-surface-container border border-outline-variant rounded-2xl shadow-2xl w-80 z-[100] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150';
      popover.style.top = (rect.bottom + 8) + 'px';
      popover.style.right = (window.innerWidth - rect.right) + 'px';

      const notifs = Devora.state.getLocal().notifications || [];

      popover.innerHTML = `
        <div class="p-3 border-b border-outline-variant flex items-center justify-between bg-surface-container-high">
          <span class="font-headline-sm text-sm font-semibold text-on-surface">Notifications</span>
          <button class="text-xs text-primary hover:underline" id="notif-clear-btn">Mark all read</button>
        </div>
        <div class="max-h-72 overflow-y-auto divide-y divide-outline-variant/30">
          ${notifs.length === 0 ? '<div class="p-6 text-center text-outline text-sm">No notifications</div>' : notifs.map(n => `
            <div class="p-3 flex items-start gap-3 hover:bg-surface-container-high transition-colors cursor-pointer">
              <span class="material-symbols-outlined text-[20px] text-${n.color || 'primary'} mt-0.5">${n.icon || 'notifications'}</span>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-medium text-on-surface truncate">${n.title}</span>
                  <span class="text-[10px] font-label-mono text-outline">${n.time}</span>
                </div>
                <p class="text-xs text-on-surface-variant line-clamp-2 mt-0.5">${n.text}</p>
              </div>
            </div>
          `).join('')}
        </div>
      `;

      document.body.appendChild(popover);

      popover.querySelector('#notif-clear-btn')?.addEventListener('click', () => {
        const state = Devora.state.getLocal();
        state.notifications = [];
        Devora.state.setLocal(state);
        Devora.toast('Notifications cleared', 'success');
        popover.remove();
      });

      const closeHandler = (e) => {
        if (!popover.contains(e.target) && e.target !== anchorEl && !anchorEl.contains(e.target)) {
          popover.remove();
          document.removeEventListener('click', closeHandler);
        }
      };
      setTimeout(() => document.addEventListener('click', closeHandler), 10);
    },

    // Global User Profile Dropdown
    toggleProfileMenu(anchorEl) {
      let popover = document.getElementById('devora-profile-popover');
      if (popover) {
        popover.remove();
        return;
      }

      const rect = anchorEl.getBoundingClientRect();
      popover = document.createElement('div');
      popover.id = 'devora-profile-popover';
      popover.className = 'fixed bg-surface-container border border-outline-variant rounded-2xl shadow-2xl w-64 z-[100] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150';
      popover.style.top = (rect.bottom + 8) + 'px';
      popover.style.right = (window.innerWidth - rect.right) + 'px';

      const user = Devora.state.getLocal().user || { name: "Alex Chen", email: "alex.chen@systemcore.dev", role: "DevOps Engineer" };

      popover.innerHTML = `
        <div class="p-4 border-b border-outline-variant bg-surface-container-high flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center font-bold text-on-primary">
            AC
          </div>
          <div class="flex flex-col min-w-0">
            <span class="text-sm font-semibold text-on-surface truncate">${user.name}</span>
            <span class="text-xs text-on-surface-variant truncate">${user.role}</span>
          </div>
        </div>
        <div class="p-2 flex flex-col gap-1">
          <a href="settings.html" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-on-surface hover:bg-surface-container-high transition-colors">
            <span class="material-symbols-outlined text-[18px] text-outline">settings</span>
            Settings
          </a>
          <a href="api-settings.html" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-on-surface hover:bg-surface-container-high transition-colors">
            <span class="material-symbols-outlined text-[18px] text-outline">key</span>
            API Keys & Tokens
          </a>
          <div class="h-px bg-outline-variant/40 my-1"></div>
          <button id="devora-signout-btn" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-error hover:bg-error/10 transition-colors w-full text-left">
            <span class="material-symbols-outlined text-[18px]">logout</span>
            Sign Out
          </button>
        </div>
      `;

      document.body.appendChild(popover);

      popover.querySelector('#devora-signout-btn')?.addEventListener('click', () => {
        localStorage.removeItem('devora_auth_user');
        Devora.toast('Signed out successfully', 'info');
        setTimeout(() => window.location.href = 'index.html', 500);
      });

      const closeHandler = (e) => {
        if (!popover.contains(e.target) && e.target !== anchorEl && !anchorEl.contains(e.target)) {
          popover.remove();
          document.removeEventListener('click', closeHandler);
        }
      };
      setTimeout(() => document.addEventListener('click', closeHandler), 10);
    },

    // Modal to create Jira Ticket
    openCreateTicketModal(onCreated) {
      this.openModal(`
        <div class="flex flex-col gap-4">
          <div class="flex items-center justify-between border-b border-outline-variant pb-3">
            <h3 class="font-headline-sm text-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">add_task</span>
              Create Jira Ticket
            </h3>
          </div>
          <form id="create-ticket-form" class="flex flex-col gap-3">
            <div>
              <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Summary *</label>
              <input id="ticket-summary" required type="text" placeholder="e.g. Implement rate limiting on API gateway" class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary transition-colors" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Priority</label>
                <select id="ticket-priority" class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary">
                  <option value="High">High (P1)</option>
                  <option value="Med" selected>Medium (P2)</option>
                  <option value="Low">Low (P3)</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Status</label>
                <select id="ticket-status" class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary">
                  <option value="To Do">To Do</option>
                  <option value="In Progress" selected>In Progress</option>
                  <option value="Review">Review</option>
                  <option value="Done">Done</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Repository</label>
                <input id="ticket-repo" type="text" value="core-backend" class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary" />
              </div>
              <div>
                <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Due Date</label>
                <input id="ticket-due" type="text" value="In 3 days" class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Description</label>
              <textarea id="ticket-desc" rows="3" placeholder="Provide background, steps, or acceptance criteria..." class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary resize-none"></textarea>
            </div>
            <div class="flex justify-end gap-2 pt-2 border-t border-outline-variant mt-2">
              <button type="button" onclick="Devora.closeModal()" class="px-4 py-2 rounded-lg bg-surface-container-high text-on-surface text-sm hover:bg-surface-bright transition-colors">Cancel</button>
              <button type="submit" class="px-4 py-2 rounded-lg bg-primary text-on-primary font-medium text-sm hover:opacity-90 transition-opacity">Create Ticket</button>
            </div>
          </form>
        </div>
      `, (overlay) => {
        const form = overlay.querySelector('#create-ticket-form');
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const summary = overlay.querySelector('#ticket-summary').value;
          const priority = overlay.querySelector('#ticket-priority').value;
          const status = overlay.querySelector('#ticket-status').value;
          const repo = overlay.querySelector('#ticket-repo').value;
          const dueDate = overlay.querySelector('#ticket-due').value;
          const description = overlay.querySelector('#ticket-desc').value;

          const created = await Devora.state.api('/tickets', {
            method: 'POST',
            body: JSON.stringify({ summary, priority, status, repo, dueDate, description })
          });

          Devora.toast(`Created ticket ${created.id || 'successfully'}`, 'success');
          Devora.closeModal();
          if (onCreated) onCreated(created);
        });
      });
    },

    // Modal to create Pull Request
    openCreatePRModal(onCreated) {
      this.openModal(`
        <div class="flex flex-col gap-4">
          <div class="flex items-center justify-between border-b border-outline-variant pb-3">
            <h3 class="font-headline-sm text-lg font-bold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">call_merge</span>
              New Pull Request
            </h3>
          </div>
          <form id="create-pr-form" class="flex flex-col gap-3">
            <div>
              <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">PR Title *</label>
              <input id="pr-title" required type="text" placeholder="e.g. feat(auth): add OAuth2 PKCE callback validator" class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Repository</label>
                <select id="pr-repo" class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary">
                  <option value="core-auth-service">core-auth-service</option>
                  <option value="data-pipeline-go">data-pipeline-go</option>
                  <option value="frontend-webapp">frontend-webapp</option>
                  <option value="infra-k8s">infra-k8s</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Branch Name</label>
                <input id="pr-branch" type="text" value="feature/new-enhancement" class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-label-mono uppercase text-on-surface-variant mb-1">Description / Notes</label>
              <textarea id="pr-desc" rows="3" placeholder="Explain the changes made in this branch..." class="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface outline-none focus:border-primary resize-none"></textarea>
            </div>
            <div class="flex justify-end gap-2 pt-2 border-t border-outline-variant mt-2">
              <button type="button" onclick="Devora.closeModal()" class="px-4 py-2 rounded-lg bg-surface-container-high text-on-surface text-sm hover:bg-surface-bright transition-colors">Cancel</button>
              <button type="submit" class="px-4 py-2 rounded-lg bg-primary text-on-primary font-medium text-sm hover:opacity-90 transition-opacity">Submit Pull Request</button>
            </div>
          </form>
        </div>
      `, (overlay) => {
        const form = overlay.querySelector('#create-pr-form');
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const title = overlay.querySelector('#pr-title').value;
          const repo = overlay.querySelector('#pr-repo').value;
          const branch = overlay.querySelector('#pr-branch').value;
          const description = overlay.querySelector('#pr-desc').value;

          const created = await Devora.state.api('/pull-requests', {
            method: 'POST',
            body: JSON.stringify({ title, repo, branch, description })
          });

          Devora.toast(`Opened PR #${created.id || 'new'} successfully!`, 'success');
          Devora.closeModal();
          if (onCreated) onCreated(created);
        });
      });
    },

    // Initialize global UI hooks across pages
    initGlobal() {
      // 1. Keyboard shortcut: Cmd/Ctrl + K or '/'
      document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault();
          this.openSearchPalette();
        }
        if (e.key === 'Escape') {
          this.closeModal();
        }
      });

      // 2. Search Bar button in header
      const searchBtns = document.querySelectorAll('header div.cursor-pointer, header .search-box');
      searchBtns.forEach(btn => {
        if (btn.textContent.includes('Search') || btn.querySelector('span')?.textContent === 'search') {
          btn.addEventListener('click', () => this.openSearchPalette());
        }
      });

      // 3. Notifications icon in header
      const notifIcons = document.querySelectorAll('header span.material-symbols-outlined');
      notifIcons.forEach(icon => {
        if (icon.textContent === 'notifications') {
          icon.parentElement.style.cursor = 'pointer';
          icon.parentElement.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleNotifications(icon.parentElement);
          });
        }
      });

      // 4. User profile avatar in header
      const profileAvatars = document.querySelectorAll('header .w-8.h-8.rounded-full.bg-primary');
      profileAvatars.forEach(avatar => {
        avatar.style.cursor = 'pointer';
        avatar.addEventListener('click', (e) => {
          e.stopPropagation();
          this.toggleProfileMenu(avatar);
        });
      });

      // 5. Standardize Sidebar Active States
      const currentPath = window.location.pathname.split('/').pop() || 'index.html';
      const sideLinks = document.querySelectorAll('aside nav a');
      sideLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href === currentPath) {
          link.classList.add('bg-secondary-container', 'text-on-secondary-container', 'font-medium');
          link.classList.remove('text-on-surface-variant');
        }
      });
    }
  };

  // Expose globally
  window.Devora = Devora;

  // Auto-run on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    Devora.initGlobal();
  });
})();
