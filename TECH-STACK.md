# NetCloak Technology Stack

**Last Updated:** 2025-12-18

This document outlines the recommended technology choices for NetCloak, prioritizing simplicity, proven technologies, and avoiding over-engineering.

---

## Core Principles

1. **Simple over clever** - Use boring, proven technology
2. **Monolith over microservices** - Single service initially
3. **Minimal dependencies** - Reduce complexity and maintenance burden
4. **Server-side first** - Avoid unnecessary frontend complexity
5. **Deploy fast** - No complex orchestration for MVP

---

## Backend Stack

### **VPN Infrastructure**

**netcloak-engine (VPN Server):**
```
Language: Go 1.21+
VPN Protocol: WireGuard (wireguard-go)
Network: encrypted WebSockets (fallback for restricted networks)
Memory target: <100MB RAM per instance
Concurrency: Native goroutines (handle 200 concurrent connections)
```

**Why Go:**
- ✅ WireGuard native support (wireguard-go official library)
- ✅ Excellent concurrency model (goroutines handle 200+ users easily)
- ✅ Low memory footprint (meets <100MB target)
- ✅ Single binary deployment (no dependencies)
- ✅ Fast network I/O (critical for VPN performance)
- ✅ Static typing (catch errors at compile time)

**Why NOT Python:**
- ❌ GIL limits concurrency (bad for simultaneous connections)
- ❌ Higher memory usage (won't meet <100MB target)
- ❌ Slower for network-intensive workloads
- ❌ Dependency management complexity

---

### **API Server**

**netcloak-api:**
```
Framework: Go stdlib net/http (no framework initially)
API Style: REST (simple HTTP/JSON, not gRPC)
Authentication: JWT tokens or session cookies
Rate Limiting: In-memory or Redis (if needed)
```

**Why stdlib HTTP:**
- ✅ No framework lock-in
- ✅ Minimal dependencies
- ✅ Easy debugging
- ✅ Scales to thousands of requests/sec

**Avoid:**
- ❌ GraphQL (overkill for simple CRUD)
- ❌ Heavy frameworks (Gin, Echo) - use if needed later
- ❌ gRPC (REST is simpler for web clients)

---

### **Database**

**Primary Database: PostgreSQL 15+**
```
Purpose: User data, points, usage logs, connections
Schema: Simple relational model
Access: database/sql + pgx driver (or sqlc for type-safety)
Backups: Daily automated backups
```

**Schema (MVP):**
```sql
shops (
  id, name, email, tin, points_balance,
  created_at, status
)

subscribers (
  id, shop_id, config_id, plan_type,
  data_cap_daily, expires_at, created_at
)

usage_logs (
  subscriber_id, date, data_used_mb,
  connection_count
)

connections (
  subscriber_id, ip_address,
  connected_at, disconnected_at
)

point_transactions (
  shop_id, amount, type, description,
  created_at
)
```

**Why PostgreSQL:**
- ✅ Reliable, battle-tested
- ✅ ACID compliance (important for points/billing)
- ✅ Good JSON support (if needed)
- ✅ Excellent tooling

**Avoid:**
- ❌ MongoDB (data is relational)
- ❌ ORMs (use sqlc or plain SQL for simplicity)

---

### **Caching (Optional)**

**Redis (only if needed):**
```
Use cases:
- Active connection tracking (config_id → IP mapping)
- Rate limiting
- Session storage
```

**Note:** Start without Redis. Add only when needed.

---

## Frontend Stack

### **Shop Admin Dashboard**

**Option 1: Server-Side Rendered (Recommended for MVP)**
```
Templates: Go html/template
CSS: Tailwind CSS (via CDN or build)
JS: Alpine.js (minimal interactivity)
Forms: Standard HTML forms + HTMX (optional)
```

**Why:**
- ✅ No build step required
- ✅ Fast development
- ✅ Works without JavaScript
- ✅ Simple deployment (single binary)

**Example stack:**
- Go serves HTML templates
- Tailwind for styling (use CDN initially)
- Alpine.js for dropdowns, modals, simple interactions
- HTMX for dynamic updates without full page reload

---

**Option 2: Single Page App (If preferred)**
```
Framework: SvelteKit
API: REST calls to netcloak-api
Build: Vite
Deployment: Static files served by nginx
```

**Why SvelteKit (if going SPA route):**
- ✅ Simpler than React/Vue
- ✅ Built-in SSR
- ✅ Smaller bundle sizes
- ✅ Less boilerplate

**Avoid:**
- ❌ React/Next.js (overkill, complex)
- ❌ Angular (too heavy)
- ❌ Vue 3 (SvelteKit is simpler)

---

### **Mobile Apps**

**Framework: Flutter**
```
Language: Dart
WireGuard: wireguard_flutter package
Platforms: Android + iOS (single codebase)
State Management: Riverpod or Provider
API Client: http package + JSON serialization
```

**Why Flutter:**
- ✅ Single codebase for Android + iOS
- ✅ Good WireGuard library support
- ✅ Native performance
- ✅ Fast development with hot reload
- ✅ Material Design built-in

**Avoid:**
- ❌ React Native (worse WireGuard integration)
- ❌ Native Swift/Kotlin (2× development work)

---

## Infrastructure & Deployment

### **Hosting**

**VPN Servers:**
```
Provider: Contabo Cloud VPS
Plan: VPS 20 ($4.77/mo for 200 users)
OS: Ubuntu 22.04 LTS
Management: systemd (no Docker initially)
```

**Web Server:**
```
Reverse Proxy: nginx
SSL: Let's Encrypt (certbot)
Static Files: Served by nginx
API: Proxied to Go backend
```

---

### **Deployment Strategy**

**Simple Deployment (MVP):**
```
1. Build Go binary on local machine
2. SCP binary to VPS
3. systemd restart service
4. nginx already configured
```

**Better Deployment (Month 2+):**
```
CI/CD: GitHub Actions
Steps:
  1. Run tests
  2. Build binary
  3. SCP to VPS
  4. systemd restart
  5. Health check
```

**Avoid (for now):**
- ❌ Docker/Docker Compose (adds complexity)
- ❌ Kubernetes (massive overkill)
- ❌ Complex CI/CD pipelines
- ❌ Multiple environments (dev/staging/prod)

---

### **Monitoring (MVP)**

**Logging:**
```
Application: Go stdlib log package
Format: JSON structured logs
Storage: Local files (rotate daily)
```

**Metrics:**
```
Basic: Server CPU/RAM/disk (htop, df)
Database: pg_stat_statements
Connection count: Simple counter in app
```

**Add later (Month 4+):**
- Prometheus + Grafana
- Alerting (PagerDuty, email)
- Error tracking (Sentry)

---

## Payment Integration

### **Wise Business API**

```
Library: Go net/http (direct API calls)
Endpoints:
  - Get account balance
  - List transactions
  - Webhooks for incoming payments
Auth: API token (environment variable)
```

**Why direct API calls:**
- ✅ Wise has simple REST API
- ✅ No official Go SDK needed
- ✅ Full control over implementation

---

## Development Tools

### **Code Quality**

```
Formatting: gofmt, goimports
Linting: golangci-lint
Testing: Go stdlib testing package
Coverage: go test -cover
```

### **Database Tools**

```
Migrations: golang-migrate or goose
Query Builder: sqlc (generates type-safe Go code)
Admin UI: pgAdmin or Postico (local development)
```

### **Version Control**

```
Git: GitHub
Branching: main (deploy from main)
Releases: Git tags (v1.0.0, v1.1.0)
```

---

## Complete Technology Matrix

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **VPN Core** | Go + WireGuard | Native support, low memory, fast |
| **API Server** | Go stdlib HTTP | Simple, no framework lock-in |
| **Database** | PostgreSQL 15+ | Reliable, ACID, proven |
| **Cache** | Redis (optional) | Only if needed for sessions |
| **Admin Dashboard** | Go templates + Tailwind + Alpine.js | Server-rendered, no build step |
| **Mobile Apps** | Flutter (Dart) | Single codebase, good WireGuard libs |
| **Reverse Proxy** | nginx | Industry standard |
| **SSL** | Let's Encrypt | Free, automated |
| **Deployment** | systemd on VPS | Simple, no containers |
| **CI/CD** | GitHub Actions | Free for public repos |
| **Monitoring** | Logs + basic metrics | Simple initially |
| **Payments** | Wise API (direct) | No SDK needed |

---

## What NOT to Use (Avoid Over-Engineering)

### **Architecture**
- ❌ **Microservices** - Single service is fine for 1,000-10,000 users
- ❌ **Message Queues** - No async jobs needed yet
- ❌ **Event Sourcing** - Overkill for simple CRUD
- ❌ **CQRS** - Not needed for this scale

### **Infrastructure**
- ❌ **Kubernetes** - Massive overkill for single VPS
- ❌ **Docker** (initially) - systemd is simpler
- ❌ **Service Mesh** - Not needed
- ❌ **Multiple regions** - Start with 1 region

### **Frontend**
- ❌ **React/Next.js** - Too complex for admin dashboard
- ❌ **GraphQL** - REST is simpler
- ❌ **Separate frontend repo** - Server-side render initially
- ❌ **Complex state management** - Keep it simple

### **Backend**
- ❌ **ORMs** - Use sqlc or plain SQL
- ❌ **Heavy frameworks** - Stdlib HTTP is enough
- ❌ **gRPC** - REST is easier to debug
- ❌ **Complex auth** - Simple JWT or sessions

---

## MVP Development Roadmap

### **Week 1-2: VPN Core**
- Go + WireGuard integration
- Basic connection establishment
- Speed limiting (15 Mbps)
- Daily data cap tracking (5 GB/day)
- Single concurrent connection enforcement

### **Week 3: Database & API**
- PostgreSQL schema setup
- API endpoints:
  - Create subscriber
  - Track usage
  - Check connection status
  - Deduct points
- Basic authentication

### **Week 4: Admin Dashboard**
- Shop login
- Points balance display
- Create subscriber (generate config link)
- View active subscribers
- Usage statistics (basic)

### **Week 5-6: Mobile App**
- Flutter project setup
- WireGuard integration
- Config import (via link)
- Connect/disconnect UI
- Usage display (data used today)

### **Week 7: Deployment & Testing**
- Deploy to Contabo VPS 20
- nginx + Let's Encrypt setup
- systemd service configuration
- Beta test with 1-2 shops
- Fix bugs, gather feedback

### **Week 8: Launch**
- Onboard first 10 shops
- Monitor performance
- Fix critical issues
- Document common problems

---

## Scaling Considerations (Future)

**When you reach 1,000 subscribers (5 VPS servers):**
- Add load balancer (nginx upstream)
- Redis for session sharing
- Database replication (read replicas)
- Prometheus + Grafana monitoring

**When you reach 10,000 subscribers (50 VPS servers):**
- Consider managed Postgres (RDS/DigitalOcean)
- Add caching layer (Redis cluster)
- Automated deployment (Ansible/Terraform)
- 24/7 monitoring and alerting

**When you reach 100,000 subscribers:**
- Re-evaluate architecture
- Consider regional deployments
- Dedicated ops team
- Advanced monitoring (Datadog, New Relic)

**But for MVP (200 subscribers on 1 VPS): Keep it simple.**

---

## Technology Decision Principles

When choosing new technology, ask:

1. **Do we actually need this?** (Default answer: No)
2. **Can we solve this with existing stack?** (Try first)
3. **Is this proven and boring?** (Prefer mature tech)
4. **Will this make debugging harder?** (Avoid if yes)
5. **Can one person maintain this?** (Important early on)

**Remember:** The best code is no code. The best dependency is no dependency. The best infrastructure is the simplest infrastructure that works.

---

*Tech stack will evolve based on real-world needs, but these choices provide a solid foundation for MVP and early growth.*
