# NetCloak Platform Architecture

**Last Updated:** 2025-12-18

This document defines the complete technical architecture for the NetCloak B2B VPN platform, integrating business requirements, existing PoC components, and multi-server design considerations.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [System Actors](#system-actors)
4. [Component Architecture](#component-architecture)
5. [Database Schema](#database-schema)
6. [API Specifications](#api-specifications)
7. [Multi-Server Architecture](#multi-server-architecture)
8. [Critical Workflows](#critical-workflows)
9. [Security Model](#security-model)
10. [Migration from PoC](#migration-from-poc)
11. [Deployment Architecture](#deployment-architecture)

---

## System Overview

### Business Model

NetCloak is a **B2B wholesale VPN platform** targeting mobile phone retail shops in the Philippines. The platform provides VPN infrastructure that shops resell to their customers.

**Value Chain:**
```
Platform (NetCloak) → Phone Shops → Subscribers (End Users)
       $0.75/month      ₱99-149/month
```

**Core Operations:**
1. Shops purchase points ($0.75 per point = 1 subscriber for 1 month)
2. Shops create subscriber accounts (generates WireGuard config)
3. Subscribers download mobile app and import config
4. Platform enforces service limits (15 Mbps, 5 GB/day, 1 active connection)
5. Points auto-deduct daily from shop balance

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      NetCloak Platform                          │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Shop       │      │  Subscriber  │      │   VPN        │ │
│  │   Dashboard  │──────│  Management  │──────│   Server     │ │
│  │   (Web UI)   │      │   (API)      │      │   Cluster    │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│         │                      │                      │        │
│         │                      │                      │        │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Payment    │      │  PostgreSQL  │      │   Redis      │ │
│  │  Processing  │      │   Database   │      │   (State)    │ │
│  │   (Wise)     │      │              │      │              │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
    ┌────┴────┐            ┌────┴────┐           ┌─────┴──────┐
    │  Phone  │            │ Mobile  │           │  WireGuard │
    │  Shop   │            │   App   │           │   Client   │
    │  Owner  │            │ (Subsc) │           │            │
    └─────────┘            └─────────┘           └────────────┘
```

---

## Architecture Principles

### Core Design Philosophy

1. **Simple over clever** - Boring, proven technology
2. **Monolith first** - Single service, scale horizontally by adding servers
3. **Stateless servers** - VPN servers are independent, state in central database
4. **Security by design** - Privilege separation, minimal attack surface
5. **B2B-first** - Phone shops are customers, subscribers are products

### Key Constraints

- **Single active connection per subscriber** - Same config on multiple devices OK, only 1 connected at a time
- **Daily data caps** - 5 GB/day (Fast) or 15 GB/day (Premium), reset at midnight UTC
- **Flat rate limits** - 15 Mbps or 40 Mbps, no bursting
- **Mobile-only** - Android/iOS apps, no desktop clients initially
- **Independent servers** - Each VPN server is autonomous, coordinated via central state

---

## System Actors

### 1. Platform (NetCloak Operations)

**Responsibilities:**
- Provision VPN infrastructure (Contabo VPS servers)
- Maintain central database (PostgreSQL)
- Process payments from shops (Wise Business)
- Monitor system health and performance
- Handle technical support escalations

**Access Level:** Full administrative control

---

### 2. Phone Shops (Business Customers)

**Profile:**
- Mobile phone retailers in Philippines
- 20-100+ devices sold per month
- Existing customer base for reselling
- Business registration (TIN required)

**Capabilities:**
- Purchase points ($0.75 per subscriber per month)
- Create/delete subscriber accounts
- View subscriber usage and status
- Monitor points balance
- Download subscriber config links
- View usage statistics

**Access Level:** Shop-scoped data only (own subscribers, points, transactions)

**Authentication:** Email/password → JWT token

---

### 3. Subscribers (End Users)

**Profile:**
- Filipino mobile phone users
- Purchased VPN service from phone shop (₱99-149/month)
- Non-technical users (simple mobile app UX)

**Capabilities:**
- Import WireGuard config via link
- Connect/disconnect VPN
- View data usage (today's consumption vs. daily cap)
- View plan details (speed, daily limit)

**Access Level:** No platform authentication (WireGuard keypair is credential)

**Authentication:** WireGuard public/private key pair

---

### 4. VPN Servers (Infrastructure)

**Profile:**
- Contabo VPS 20 instances ($4.77/month each)
- 200 subscribers per server (max capacity)
- Independent operation (no direct inter-server communication)
- Coordinated via central Redis state

**Responsibilities:**
- Accept WireGuard connections
- Enforce speed limits (TC bandwidth shaping)
- Track data usage per subscriber
- Enforce daily data caps
- Report connection events to central database
- Block multi-server abuse (same config on 2 servers)

**Access Level:** Server-scoped operations, write to central state

---

## Component Architecture

### High-Level Component View

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Tier                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  netcloak-admin (Go HTTP Server)                         │  │
│  │  - Shop authentication (JWT)                             │  │
│  │  - Admin dashboard (Go templates + Tailwind + Alpine)    │  │
│  │  - Shop API (create subscribers, view usage, manage $)   │  │
│  │  - Wise webhooks (payment notifications)                 │  │
│  │  Port: 8080 (behind nginx)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ PostgreSQL queries
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Tier                                  │
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │   PostgreSQL 15+     │         │   Redis 7+           │    │
│  │   - shops            │         │   - active_conns     │    │
│  │   - subscribers      │         │   - server_health    │    │
│  │   - point_txns       │         │   - rate_limits      │    │
│  │   - usage_logs       │         │   TTL: 24-48 hours   │    │
│  │   - connections      │         │                      │    │
│  └──────────────────────┘         └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ IPC + DB writes
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      VPN Tier (Per Server)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  netcloak-edge (Go HTTP - Unprivileged)                  │  │
│  │  - VPN server health API                                 │  │
│  │  - Connection event reporting                            │  │
│  │  - Rate limiting (per-IP)                                │  │
│  │  - IPC client (Unix socket → engine)                     │  │
│  │  Port: 8081                                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              │ Unix socket IPC                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  netcloak-engine (Go - Root Privileged)                  │  │
│  │  - WireGuard peer management (add/remove)                │  │
│  │  - Traffic control (TC bandwidth limits: 15/40 Mbps)     │  │
│  │  - IP allocation (IPv4 + IPv6)                           │  │
│  │  - Data usage tracking (eBPF or iptables counters)       │  │
│  │  - Daily cap enforcement (5 GB/15 GB per day)            │  │
│  │  - Orphan cleanup (stale connections)                    │  │
│  │  - IPC server (Unix socket)                              │  │
│  │  Interface: wg0                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### netcloak-admin (New Component - Web/API Tier)

**Purpose:** Shop-facing web dashboard and API server

**Technology:**
- Language: Go 1.21+
- HTTP: stdlib net/http
- Templates: html/template
- CSS: Tailwind CSS (CDN)
- JS: Alpine.js (minimal interactivity)

**Responsibilities:**
1. **Shop Authentication:**
   - Email/password login → JWT token
   - Session management
   - Password reset flows

2. **Shop Dashboard (Server-Side Rendered):**
   - Points balance display
   - Create subscriber form
   - View active/expired subscribers
   - Usage statistics (daily/monthly)
   - Transaction history

3. **Shop API (REST JSON):**
   - `POST /api/subscribers` - Create new subscriber
   - `GET /api/subscribers` - List shop's subscribers
   - `DELETE /api/subscribers/:id` - Deactivate subscriber
   - `GET /api/usage/:subscriber_id` - View subscriber usage
   - `GET /api/points/balance` - Current points balance
   - `GET /api/points/transactions` - Transaction history

4. **Wise Integration:**
   - Webhook endpoint: `POST /webhooks/wise`
   - Verify signature, credit shop points
   - Record transaction in database

5. **Subscriber Provisioning:**
   - Generate WireGuard keypair
   - Assign to least-loaded VPN server
   - Create database record
   - Return config download link

**Database Access:** Direct PostgreSQL queries (pgx driver)

**Deployment:** Single binary, systemd service, nginx reverse proxy

---

### netcloak-edge (Refactored from PoC - VPN Server API)

**Purpose:** Unprivileged HTTP API for VPN server operations

**Technology:**
- Language: Go 1.21+
- HTTP Framework: Gin (from PoC)
- IPC: Unix domain socket client

**Responsibilities (Changed from PoC):**

**Remove:**
- ❌ Anonymous session creation
- ❌ Decoy pages (traffic obfuscation)
- ❌ Public-facing authentication

**Keep:**
- ✅ Health check endpoint (`GET /health`)
- ✅ Rate limiting (per-IP)
- ✅ IPC client (communicate with engine)

**Add:**
- ✅ Connection event webhook (report to netcloak-admin)
- ✅ Server capacity endpoint (`GET /capacity`) - return active connections count
- ✅ Daily data reset trigger (called by cron at midnight UTC)

**API Endpoints:**
```
GET  /health              → Server health status
GET  /capacity            → Current active connections count
POST /internal/reset-daily → Trigger daily data counter reset (cron only)
```

**IPC Commands to Engine:**
```
GetActiveConnections  → List currently connected subscribers
ResetDailyCounters    → Reset all daily data usage to 0
GetSubscriberUsage    → Get specific subscriber's data usage today
```

**Database Access:** Write-only connection events to PostgreSQL

**Deployment:** Runs on each VPN server alongside netcloak-engine

---

### netcloak-engine (Refactored from PoC - VPN Core)

**Purpose:** Root-privileged VPN management service

**Technology:**
- Language: Go 1.21+
- VPN: WireGuard (wgctrl library)
- Traffic Control: TC (exec tc commands)
- Data Tracking: iptables counters or eBPF

**Responsibilities (Changed from PoC):**

**Keep:**
- ✅ WireGuard interface management (wg0)
- ✅ Peer add/remove operations
- ✅ IP allocation (IPv4 10.8.0.0/24, IPv6 fd42:42:42::/112)
- ✅ Traffic control (TC HTB qdisc + IFB for bidirectional shaping)
- ✅ Orphan cleanup (disconnect stale peers)
- ✅ Health monitoring
- ✅ IPC server (Unix socket)

**Change:**
- ⚠️ Bandwidth limits: 2 fixed tiers (15 Mbps / 40 Mbps) instead of dynamic tiers
- ⚠️ Data tracking: Daily caps (5 GB/day or 15 GB/day) instead of session-based
- ⚠️ State storage: Query PostgreSQL + Redis for subscriber info, not SQLite
- ⚠️ Connection validation: Check Redis for active connections before allowing new peer

**Add:**
- ✅ Daily data cap enforcement (throttle to near-zero when cap reached)
- ✅ Single active connection enforcement (check Redis, block if already connected)
- ✅ Multi-server abuse prevention (write active connection to Redis with server ID)
- ✅ Daily counter reset (triggered by edge at midnight UTC)

**IPC Protocol (Keep from PoC):**
- Transport: Unix domain socket (`/var/run/netcloak/engine.sock`)
- Format: Length-prefixed JSON messages
- Permissions: 0660, group `netcloak`

**IPC Commands:**

**From PoC (Keep):**
```json
{"action": "add_peer", "public_key": "...", "bandwidth_tier": 1}
{"action": "remove_peer", "public_key": "..."}
{"action": "get_peer_stats", "public_key": "..."}
{"action": "health_check"}
```

**New Commands:**
```json
{"action": "check_active_connection", "config_id": "uuid"}
  → Response: {"active": true, "server_id": "vpn-01", "ip": "10.8.0.5"}

{"action": "validate_subscriber", "config_id": "uuid"}
  → Response: {"valid": true, "plan": "fast", "data_used_today": 2.5, "cap": 5.0}

{"action": "reset_daily_counters"}
  → Response: {"reset_count": 150, "success": true}
```

**State Management:**

**PostgreSQL (Source of Truth):**
- Subscriber configuration (plan, daily cap, status)
- Historical usage logs (written every hour)
- Connection history

**Redis (Ephemeral State - TTL 48h):**
- Active connections: `active_conn:{config_id}` → `{server_id, ip, connected_at}`
- Today's usage: `usage:{config_id}:{date}` → `{bytes_used}`
- Server health: `server:{server_id}:health` → `{active_conns, cpu, mem}`

**Connection Flow (Changed from PoC):**

1. WireGuard handshake initiated with public key
2. Engine receives connection attempt
3. **NEW:** Query PostgreSQL: `SELECT config_id, plan, status FROM subscribers WHERE public_key = ?`
4. **NEW:** Check Redis: `EXISTS active_conn:{config_id}`
   - If exists: Reject connection (error: "Already connected on another device")
5. **NEW:** Check Redis: `GET usage:{config_id}:{today}`
   - If >= daily cap: Reject or throttle to near-zero
6. If valid: Add WireGuard peer, set TC limits, write to Redis
7. Write connection event to PostgreSQL: `INSERT INTO connections (...)`

**Deployment:** Runs as root (systemd service), listens on Unix socket

---

## Database Schema

### PostgreSQL Schema (Central Database)

**Design Principles:**
- ACID compliance (critical for points/billing)
- Normalized relational model
- Use UUIDs for distributed ID generation
- Index on foreign keys and query patterns
- Store timestamps as UTC

---

### Table: `shops`

**Purpose:** Phone shop business accounts

**Minimalistic approach** - Only collect what's essential for operations

```sql
CREATE TABLE shops (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Business Info (Minimal)
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,

  -- Points Balance
  points_balance INTEGER NOT NULL DEFAULT 0,  -- 1 point = 1 subscriber for 1 month

  -- Status
  status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, suspended, closed

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Indexes
  CONSTRAINT points_balance_non_negative CHECK (points_balance >= 0)
);

CREATE INDEX idx_shops_email ON shops(email);
CREATE INDEX idx_shops_status ON shops(status);
```

**Removed fields:**
- `tin` - Not needed for MVP (no tax reporting initially)
- `phone` - Can contact via email
- `address` - Not needed (digital service)
- `verified` - Implicit (status = 'active' means verified)
- `updated_at` - Not used in MVP

---

### Table: `subscribers`

**Purpose:** End-user VPN accounts created by shops

**Minimalistic approach** - No PII, only technical VPN configuration

```sql
CREATE TABLE subscribers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Ownership
  shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,

  -- VPN Configuration
  config_id UUID NOT NULL UNIQUE,  -- Used for config download link
  public_key VARCHAR(44) NOT NULL UNIQUE,  -- WireGuard public key (base64)
  private_key_encrypted TEXT NOT NULL,  -- Encrypted with shop-specific key

  -- Server Assignment
  assigned_server_id VARCHAR(50) NOT NULL,  -- e.g., "vpn-01", "vpn-02"
  ipv4_address INET NOT NULL UNIQUE,  -- 10.8.0.x
  ipv6_address INET NOT NULL UNIQUE,  -- fd42:42:42::x

  -- Plan Details
  plan_type VARCHAR(20) NOT NULL DEFAULT 'fast',  -- fast, premium
  bandwidth_mbps INTEGER NOT NULL DEFAULT 15,  -- 15 or 40
  data_cap_daily_gb DECIMAL(5,2) NOT NULL DEFAULT 5.00,  -- 5.00 or 15.00

  -- Billing
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ,  -- NULL = active (daily billing), NOT NULL = expired
  last_billed_date DATE,  -- Last date points were deducted

  -- Status
  status VARCHAR(20) NOT NULL DEFAULT 'active'  -- active, expired, suspended
);

CREATE INDEX idx_subscribers_shop_id ON subscribers(shop_id);
CREATE INDEX idx_subscribers_config_id ON subscribers(config_id);
CREATE INDEX idx_subscribers_public_key ON subscribers(public_key);
CREATE INDEX idx_subscribers_status ON subscribers(status);
CREATE INDEX idx_subscribers_expires_at ON subscribers(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_subscribers_assigned_server ON subscribers(assigned_server_id);
```

**Removed fields:**
- `device_name` - Not needed (no customer tracking)
- `notes` - Not needed (shop can track externally if needed)
- `activated_at` - Redundant (use created_at)
- `updated_at` - Not used

---

### Table: `point_transactions`

**Purpose:** Audit trail for all points changes

```sql
CREATE TABLE point_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Reference
  shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
  subscriber_id UUID REFERENCES subscribers(id) ON DELETE SET NULL,  -- NULL for purchases

  -- Transaction Details
  amount INTEGER NOT NULL,  -- Positive = credit, Negative = debit
  type VARCHAR(30) NOT NULL,  -- purchase, daily_deduction, refund, admin_adjustment
  description TEXT NOT NULL,

  -- Balance After Transaction
  balance_after INTEGER NOT NULL,

  -- Payment Reference (for purchases)
  payment_reference VARCHAR(255),  -- Wise transaction ID
  payment_method VARCHAR(50),  -- wise, gcash, admin

  -- Metadata
  created_by VARCHAR(50),  -- 'system', 'admin', 'wise_webhook'
  metadata JSONB,  -- Flexible field for additional data

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_point_txns_shop_id ON point_transactions(shop_id);
CREATE INDEX idx_point_txns_subscriber_id ON point_transactions(subscriber_id);
CREATE INDEX idx_point_txns_type ON point_transactions(type);
CREATE INDEX idx_point_txns_created_at ON point_transactions(created_at DESC);
```

---

### Table: `usage_logs`

**Purpose:** Daily data usage tracking per subscriber

```sql
CREATE TABLE usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Reference
  subscriber_id UUID NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,

  -- Date
  date DATE NOT NULL,  -- UTC date

  -- Usage Metrics
  data_used_mb DECIMAL(10,2) NOT NULL DEFAULT 0,  -- Megabytes used today
  data_cap_mb DECIMAL(10,2) NOT NULL,  -- Daily cap (5120 or 15360 MB)

  -- Connection Stats
  connection_count INTEGER NOT NULL DEFAULT 0,  -- Number of times connected today
  total_duration_seconds INTEGER NOT NULL DEFAULT 0,

  -- Peak Usage
  peak_bandwidth_mbps DECIMAL(5,2),

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Constraints
  UNIQUE(subscriber_id, date)
);

CREATE INDEX idx_usage_logs_subscriber_date ON usage_logs(subscriber_id, date DESC);
CREATE INDEX idx_usage_logs_date ON usage_logs(date DESC);
```

---

### Table: `connections`

**Purpose:** Real-time and historical connection tracking

**Minimalistic approach** - Track only what's needed for operations, no PII

```sql
CREATE TABLE connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Reference
  subscriber_id UUID NOT NULL REFERENCES subscribers(id) ON DELETE CASCADE,

  -- Server Info
  server_id VARCHAR(50) NOT NULL,  -- vpn-01, vpn-02, etc.

  -- Connection Details
  connected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  disconnected_at TIMESTAMPTZ,  -- NULL = currently active

  -- Session Metrics (bytes only, for billing/usage tracking)
  bytes_sent BIGINT DEFAULT 0,
  bytes_received BIGINT DEFAULT 0,

  -- Disconnect Reason
  disconnect_reason VARCHAR(50)  -- normal, daily_cap_reached, expired, error
);

CREATE INDEX idx_connections_subscriber_id ON connections(subscriber_id);
CREATE INDEX idx_connections_active ON connections(disconnected_at) WHERE disconnected_at IS NULL;
CREATE INDEX idx_connections_server_id ON connections(server_id);
CREATE INDEX idx_connections_connected_at ON connections(connected_at DESC);
```

**Removed fields:**
- `client_ip` - PII, not needed for operations
- `assigned_vpn_ip` - Redundant (already in subscribers table)
- `created_at` - Redundant (use connected_at)

---

### Table: `servers`

**Purpose:** VPN server registry and health tracking

```sql
CREATE TABLE servers (
  id VARCHAR(50) PRIMARY KEY,  -- vpn-01, vpn-02, etc.

  -- Network Config
  public_ip INET NOT NULL,
  public_port INTEGER NOT NULL DEFAULT 51820,
  region VARCHAR(50),  -- ph-manila, ph-cebu (future multi-region)

  -- Capacity
  max_subscribers INTEGER NOT NULL DEFAULT 200,
  current_subscribers INTEGER NOT NULL DEFAULT 0,

  -- Status
  status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, maintenance, offline
  health_status VARCHAR(20) NOT NULL DEFAULT 'healthy',  -- healthy, degraded, unhealthy

  -- Health Metrics (updated every 5 minutes)
  cpu_usage_percent DECIMAL(5,2),
  memory_usage_percent DECIMAL(5,2),
  bandwidth_usage_mbps DECIMAL(8,2),
  active_connections INTEGER DEFAULT 0,

  -- Timestamps
  last_health_check TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_servers_status ON servers(status);
CREATE INDEX idx_servers_health_status ON servers(health_status);
```

---

### Redis Schema (Ephemeral State)

**Purpose:** Fast lookups for active connections and rate limiting

**Key Patterns:**

```
# Active Connection Tracking (prevent multi-server abuse)
Key:   active_conn:{config_id}
Value: {"server_id": "vpn-01", "ip": "10.8.0.5", "connected_at": "2025-12-18T10:30:00Z"}
TTL:   48 hours (auto-cleanup if disconnect event missed)

# Today's Data Usage (fast counter)
Key:   usage:{config_id}:{YYYY-MM-DD}
Value: 2147483648  (bytes used today)
TTL:   48 hours (expires day after tomorrow)

# Server Health Heartbeat
Key:   server:{server_id}:health
Value: {"active_conns": 150, "cpu": 45.2, "mem": 62.1, "updated_at": "2025-12-18T10:35:00Z"}
TTL:   10 minutes (considered offline if expired)

# Rate Limiting (per-IP connection attempts)
Key:   ratelimit:conn:{client_ip}
Value: 5  (connection attempts in last minute)
TTL:   60 seconds

# Subscriber Info Cache (reduce PostgreSQL load)
Key:   subscriber:{config_id}
Value: {"plan": "fast", "bandwidth": 15, "daily_cap": 5368709120, "status": "active"}
TTL:   5 minutes
```

**Why Redis + PostgreSQL:**
- Redis: Fast lookups for connection validation (sub-millisecond)
- PostgreSQL: Source of truth for billing, persistent state
- Redis TTLs handle cleanup automatically (no orphan state)

---

## API Specifications

### Shop API (netcloak-admin)

**Base URL:** `https://api.netcloak.app`

**Authentication:** Bearer token (JWT) in `Authorization` header

---

#### 1. Authentication

**POST /auth/login**

Login to shop account

**Request:**
```json
{
  "email": "shop@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "shop": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Manila Mobile Shop",
    "email": "shop@example.com",
    "points_balance": 150
  }
}
```

---

#### 2. Points Management

**GET /api/points/balance**

Get current points balance

**Response (200 OK):**
```json
{
  "balance": 150,
  "reserved": 25,  // Points reserved for active subscribers
  "available": 125  // Available to create new subscribers
}
```

---

**GET /api/points/transactions**

Get transaction history

**Query Parameters:**
- `limit` (default: 50, max: 200)
- `offset` (default: 0)
- `type` (filter: purchase, daily_deduction, refund)

**Response (200 OK):**
```json
{
  "transactions": [
    {
      "id": "tx-uuid-1",
      "amount": -1,
      "type": "daily_deduction",
      "description": "Daily billing for subscriber Juan's iPhone",
      "balance_after": 150,
      "created_at": "2025-12-18T00:00:05Z"
    },
    {
      "id": "tx-uuid-2",
      "amount": 100,
      "type": "purchase",
      "description": "Wise payment received",
      "payment_reference": "wise-12345",
      "balance_after": 151,
      "created_at": "2025-12-17T14:30:00Z"
    }
  ],
  "total": 245,
  "limit": 50,
  "offset": 0
}
```

---

#### 3. Subscriber Management

**POST /api/subscribers**

Create new subscriber account

**Request:**
```json
{
  "plan_type": "fast"  // fast or premium (default: fast)
}
```

**Response (201 Created):**
```json
{
  "subscriber": {
    "id": "sub-uuid-1",
    "config_id": "conf-uuid-1",
    "plan_type": "fast",
    "bandwidth_mbps": 15,
    "data_cap_daily_gb": 5.0,
    "status": "active",
    "assigned_server": "vpn-01",
    "created_at": "2025-12-18T10:45:00Z",
    "expires_at": null
  },
  "config_link": "https://netcloak.app/config/conf-uuid-1",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS..."
}
```

**Points Deducted:** 1 point reserved (first daily deduction happens at midnight UTC)

---

**GET /api/subscribers**

List all subscribers for this shop

**Query Parameters:**
- `status` (filter: active, expired, suspended, all)
- `limit` (default: 50)
- `offset` (default: 0)

**Response (200 OK):**
```json
{
  "subscribers": [
    {
      "id": "sub-uuid-1",
      "config_id": "conf-uuid-1",
      "plan_type": "fast",
      "status": "active",
      "created_at": "2025-12-18T10:45:00Z",
      "last_connected": "2025-12-18T11:00:00Z",
      "data_used_today_mb": 1024.5,
      "data_cap_mb": 5120
    }
  ],
  "total": 25,
  "active": 23,
  "expired": 2
}
```

---

**DELETE /api/subscribers/:id**

Deactivate subscriber (stop daily billing)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Subscriber deactivated. WireGuard peer removed."
}
```

**Effect:**
- Sets `expires_at` to NOW(), `status` = 'expired'
- Removes WireGuard peer from assigned server (IPC call)
- Stops daily points deduction
- Frees up 1 point from reserved balance

---

**GET /api/subscribers/:id/usage**

Get detailed usage for specific subscriber

**Query Parameters:**
- `days` (default: 7, max: 90) - Number of days of history

**Response (200 OK):**
```json
{
  "subscriber_id": "sub-uuid-1",
  "current_period": {
    "date": "2025-12-18",
    "data_used_mb": 1024.5,
    "data_cap_mb": 5120,
    "connection_count": 3,
    "currently_connected": true,
    "connected_since": "2025-12-18T11:00:00Z"
  },
  "history": [
    {
      "date": "2025-12-17",
      "data_used_mb": 4850.2,
      "data_cap_mb": 5120,
      "connection_count": 5,
      "total_duration_seconds": 28800
    }
  ]
}
```

---

**GET /api/config/:config_id**

Download WireGuard config file (public endpoint, no auth)

**Response (200 OK):**
```
Content-Type: application/x-wireguard-profile
Content-Disposition: attachment; filename="netcloak.conf"

[Interface]
PrivateKey = <encrypted_private_key>
Address = 10.8.0.5/32, fd42:42:42::5/128
DNS = 1.1.1.1, 1.0.0.1

[Peer]
PublicKey = <server_public_key>
Endpoint = vpn-01.netcloak.app:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

**Security:** Config ID is UUID (unguessable), but contains full WireGuard private key

---

### VPN Server API (netcloak-edge)

**Base URL:** Internal only (not exposed to internet)

**Purpose:** Health checks, capacity reporting, internal coordination

---

**GET /health**

Server health check

**Response (200 OK):**
```json
{
  "status": "healthy",
  "server_id": "vpn-01",
  "active_connections": 150,
  "capacity": 200,
  "utilization_percent": 75.0,
  "cpu_percent": 45.2,
  "memory_percent": 62.1,
  "uptime_seconds": 864000
}
```

---

**GET /capacity**

Current capacity for load balancing

**Response (200 OK):**
```json
{
  "server_id": "vpn-01",
  "max_subscribers": 200,
  "current_subscribers": 150,
  "available_slots": 50
}
```

---

**POST /internal/reset-daily**

Trigger daily data counter reset (called by cron at midnight UTC)

**Request:**
```json
{
  "date": "2025-12-18",
  "auth_token": "internal-secret-token"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "counters_reset": 150,
  "redis_keys_deleted": 150
}
```

---

## Multi-Server Architecture

### Design Philosophy

**Independent Servers, Coordinated State**

- Each VPN server is an autonomous unit (can operate even if others fail)
- No direct server-to-server communication
- Coordination happens through central Redis + PostgreSQL
- Load balancing at subscriber creation time (not dynamic)

---

### Server Coordination Mechanisms

#### 1. Subscriber Assignment (at Creation)

**Algorithm:** Assign to least-loaded server

**Process:**
1. Shop creates subscriber via `POST /api/subscribers`
2. netcloak-admin queries: `SELECT id, current_subscribers, max_subscribers FROM servers WHERE status = 'active' ORDER BY (current_subscribers::float / max_subscribers) ASC LIMIT 1`
3. Assign subscriber to selected server
4. Increment `servers.current_subscribers` counter
5. Return config with server endpoint (e.g., `vpn-01.netcloak.app:51820`)

**Result:** Subscriber is permanently bound to this server (no migration)

---

#### 2. Multi-Server Abuse Prevention

**Problem:** Subscriber shares config with friend, both connect to different servers simultaneously

**Solution:** Global active connection registry in Redis

**Flow:**

1. User attempts to connect to `vpn-01`
2. netcloak-engine on `vpn-01` receives WireGuard handshake
3. Engine queries Redis: `GET active_conn:{config_id}`
4. **If key exists:**
   ```json
   {"server_id": "vpn-02", "ip": "10.8.0.25", "connected_at": "2025-12-18T10:30:00Z"}
   ```
   - Connection is ACTIVE on different server
   - Reject connection with error: "Already connected on another device"
   - Log abuse attempt to PostgreSQL
5. **If key does NOT exist:**
   - Connection is allowed
   - Write to Redis: `SET active_conn:{config_id} '{"server_id":"vpn-01","ip":"10.8.0.5","connected_at":"2025-12-18T11:00:00Z"}' EX 172800` (48h TTL)
   - Add WireGuard peer, set TC limits
   - Write to PostgreSQL: `INSERT INTO connections (...)`

6. On disconnect (WireGuard peer removed):
   - Delete Redis key: `DEL active_conn:{config_id}`
   - Update PostgreSQL: `UPDATE connections SET disconnected_at = NOW() WHERE id = ?`

**Result:** Same config cannot connect to 2 servers at the same time

**Edge Case:** What if Redis is down?

- Fallback: Allow connection (fail open)
- Log warning: "Redis unavailable, skipping multi-server check"
- Risk: Temporary abuse possible during Redis outage
- Mitigation: Monitor Redis uptime (should be 99.9%+)

---

#### 3. Daily Data Usage Tracking

**Challenge:** Data counters are per-server (iptables/eBPF on each VPN server)

**Solution:** Each server independently tracks its own usage, writes to shared Redis key

**Flow:**

1. User connects to `vpn-01`
2. Engine tracks bytes sent/received (iptables counters or eBPF)
3. Every 5 minutes, engine updates Redis:
   ```
   INCRBY usage:{config_id}:{2025-12-18} 524288000  # Add 500 MB
   EXPIRE usage:{config_id}:{2025-12-18} 172800     # Renew 48h TTL
   ```
4. Before allowing connection, engine checks:
   ```
   GET usage:{config_id}:{2025-12-18}
   ```
   - If >= daily cap (5 GB = 5,368,709,120 bytes): Reject or throttle
5. At midnight UTC, cron job calls `POST /internal/reset-daily` on all servers
6. Each server deletes yesterday's keys from Redis

**Result:** Daily data caps enforced even if user switches servers during the day

**Edge Case:** User consumes 3 GB on `vpn-01`, disconnects, connects to `vpn-02` (different server)

- `vpn-02` checks Redis: `GET usage:{config_id}:{today}` → Returns 3 GB
- User has 2 GB remaining (shared across all servers)

---

#### 4. Server Health Monitoring

**Purpose:** Detect unhealthy servers, stop assigning new subscribers

**Process:**

1. Each server runs health check every 5 minutes
2. netcloak-edge collects metrics (CPU, memory, active connections, bandwidth)
3. Edge writes to Redis:
   ```
   SETEX server:{server_id}:health 600 '{"active_conns":150,"cpu":45.2,"mem":62.1,"updated_at":"2025-12-18T10:35:00Z"}'
   ```
   (TTL: 10 minutes)
4. netcloak-admin checks Redis when assigning new subscribers:
   ```
   GET server:{server_id}:health
   ```
   - If key missing (TTL expired): Server considered offline, skip it
   - If CPU > 90% or memory > 90%: Mark as `degraded`, skip it
5. Admin dashboard shows server status grid

**Result:** Automatic failover - unhealthy servers don't receive new subscribers

---

### Server Lifecycle

#### Adding a New Server

**Process:**

1. Provision Contabo VPS 20 ($4.77/month)
2. Install Ubuntu 22.04, configure WireGuard, deploy netcloak-engine + edge
3. Add to PostgreSQL:
   ```sql
   INSERT INTO servers (id, public_ip, public_port, max_subscribers, status)
   VALUES ('vpn-03', '192.0.2.30', 51820, 200, 'active');
   ```
4. Configure DNS: `vpn-03.netcloak.app` → `192.0.2.30`
5. Server starts reporting health to Redis
6. netcloak-admin automatically includes it in load balancing

**No code changes required** - system auto-discovers via database

---

#### Removing a Server

**Process:**

1. Set status to `maintenance` in PostgreSQL:
   ```sql
   UPDATE servers SET status = 'maintenance' WHERE id = 'vpn-02';
   ```
2. netcloak-admin stops assigning new subscribers to this server
3. Existing subscribers continue working (no migration)
4. Wait until `current_subscribers` drops to 0 (natural churn)
5. Decommission server

**Forced migration (if needed):**
- Not implemented in MVP
- Future: Script to reassign subscribers, regenerate configs with new endpoint

---

### Scaling Strategy

**Current (MVP): 1 server**
- Server: vpn-01.netcloak.app
- Capacity: 200 subscribers
- Cost: $4.77/month

**Milestone 1: 200 subscribers**
- Add vpn-02.netcloak.app
- Capacity: 400 subscribers
- Cost: $9.54/month

**Milestone 2: 1,000 subscribers**
- 5 servers (vpn-01 through vpn-05)
- Cost: $23.85/month
- Revenue: $750/month
- Margin: 96.8%

**Milestone 3: 10,000 subscribers**
- 50 servers
- Cost: $238.50/month
- Revenue: $7,500/month
- Margin: 96.8%
- **Consideration:** Managed PostgreSQL (AWS RDS or DigitalOcean Managed DB)

---

## Critical Workflows

### Workflow 1: Shop Registration & First Purchase

**Actors:** Shop owner, netcloak-admin, Wise

**Steps:**

1. Shop owner visits `https://netcloak.app/register`
2. Fills form: name, email, password (minimalistic - 3 fields only)
3. netcloak-admin creates shop record:
   ```sql
   INSERT INTO shops (name, email, password_hash, points_balance, status)
   VALUES ('Manila Mobile', 'shop@example.com', '$2a$10$...', 0, 'active');
   ```
4. Email sent: "Verify your email" (click link to activate)
5. Shop clicks verification link → `status = 'active'`
6. Shop logs in, sees dashboard with `points_balance: 0`
7. Dashboard shows payment instructions:
   ```
   Send payment to:
   Wise Account: NetCloak Philippines
   Account Number: 1234567890
   Reference: SHOP-<shop_id>

   Points Pricing:
   100 points = $75.00 USD (₱4,300 PHP)
   200 points = $150.00 USD (₱8,600 PHP)
   ```
8. Shop sends ₱8,600 via Wise with reference `SHOP-550e8400`
9. Wise posts webhook to `POST /webhooks/wise`:
   ```json
   {
     "event": "transfer.complete",
     "transfer_id": "wise-12345",
     "amount": 150.00,
     "currency": "USD",
     "reference": "SHOP-550e8400"
   }
   ```
10. netcloak-admin verifies signature, parses reference → shop_id
11. Credits points:
    ```sql
    BEGIN;
    UPDATE shops SET points_balance = points_balance + 200 WHERE id = '550e8400';
    INSERT INTO point_transactions (shop_id, amount, type, description, payment_reference, balance_after)
    VALUES ('550e8400', 200, 'purchase', 'Wise payment received', 'wise-12345', 200);
    COMMIT;
    ```
12. Shop refreshes dashboard → `points_balance: 200`

---

### Workflow 2: Creating a Subscriber

**Actors:** Shop owner, netcloak-admin, netcloak-engine (vpn-01)

**Steps:**

1. Shop clicks "Create Subscriber" in dashboard
2. Selects plan: Fast or Premium (single dropdown)
3. netcloak-admin validates:
   - Shop has available points? (balance >= 1)
   - Check server capacity
4. Select least-loaded server:
   ```sql
   SELECT id, current_subscribers, max_subscribers
   FROM servers
   WHERE status = 'active'
   ORDER BY (current_subscribers::float / max_subscribers) ASC
   LIMIT 1;
   ```
   → Returns `vpn-01` (current: 50/200)
5. Generate WireGuard keypair:
   ```go
   privateKey, _ := wgtypes.GeneratePrivateKey()
   publicKey := privateKey.PublicKey()
   ```
6. Assign IP addresses:
   - IPv4: Next available in 10.8.0.0/24 (query for gaps)
   - IPv6: fd42:42:42::5
7. Create subscriber record:
   ```sql
   INSERT INTO subscribers (
     shop_id, config_id, public_key, private_key_encrypted,
     assigned_server_id, ipv4_address, ipv6_address,
     plan_type, bandwidth_mbps, data_cap_daily_gb, status
   ) VALUES (
     '550e8400', gen_random_uuid(), '<public_key>', '<encrypted_private>',
     'vpn-01', '10.8.0.5', 'fd42:42:42::5',
     'fast', 15, 5.00, 'active'
   );
   ```
8. Send IPC command to vpn-01 engine:
   ```json
   {
     "action": "add_peer",
     "public_key": "<public_key>",
     "ipv4": "10.8.0.5",
     "ipv6": "fd42:42:42::5",
     "bandwidth_mbps": 15
   }
   ```
9. Engine adds WireGuard peer:
   ```bash
   wg set wg0 peer <public_key> allowed-ips 10.8.0.5/32,fd42:42:42::5/128
   ```
10. Engine sets TC traffic shaping (15 Mbps bidirectional)
11. Increment server counter:
    ```sql
    UPDATE servers SET current_subscribers = current_subscribers + 1 WHERE id = 'vpn-01';
    ```
12. Generate config file content (WireGuard .conf format)
13. Return to shop:
    ```json
    {
      "config_link": "https://netcloak.app/config/<config_id>",
      "qr_code": "data:image/png;base64,..."
    }
    ```
14. Shop gives link/QR to customer

**Points:** Not deducted yet (first deduction at midnight UTC)

---

### Workflow 3: Subscriber Connects to VPN

**Actors:** Mobile app, netcloak-engine (vpn-01), Redis, PostgreSQL

**Steps:**

1. Subscriber opens mobile app, imports config via link or QR
2. App stores WireGuard config locally, shows "Disconnected" status
3. Subscriber taps "Connect"
4. Mobile app initiates WireGuard handshake to `vpn-01.netcloak.app:51820`
5. netcloak-engine receives handshake with public key
6. Engine validates subscriber:
   ```sql
   SELECT id, config_id, plan_type, bandwidth_mbps, data_cap_daily_gb, status
   FROM subscribers
   WHERE public_key = '<public_key>';
   ```
7. Check status:
   - If `status != 'active'`: Reject (subscriber expired)
8. Check multi-server abuse:
   ```redis
   GET active_conn:<config_id>
   ```
   - If exists: Reject with error "Already connected on another device"
9. Check daily data usage:
   ```redis
   GET usage:<config_id>:2025-12-18
   ```
   - If >= 5,368,709,120 bytes (5 GB): Reject or throttle
10. All checks passed → Accept connection:
    ```redis
    SET active_conn:<config_id> '{"server_id":"vpn-01","ip":"10.8.0.5","connected_at":"2025-12-18T11:00:00Z"}' EX 172800
    ```
11. Add WireGuard peer (if not already added at creation)
12. Set TC bandwidth limit (15 Mbps)
13. Write connection event to PostgreSQL:
    ```sql
    INSERT INTO connections (subscriber_id, server_id, client_ip, assigned_vpn_ip, connected_at)
    VALUES ('<subscriber_id>', 'vpn-01', '203.0.113.50', '10.8.0.5', NOW());
    ```
14. Mobile app shows "Connected" with green indicator
15. Subscriber browses internet through VPN

**Data tracking:**
- Engine tracks bytes via iptables: `iptables -L -n -v -x`
- Every 5 minutes, increment Redis counter:
  ```redis
  INCRBY usage:<config_id>:2025-12-18 524288000  # Add 500 MB
  ```

---

### Workflow 4: Daily Data Cap Reached

**Actors:** netcloak-engine, mobile app

**Steps:**

1. Subscriber has used 4.8 GB today, still connected
2. Engine checks usage every 1 minute (background goroutine)
3. Query Redis: `GET usage:<config_id>:2025-12-18` → Returns 5,150,000,000 bytes (4.8 GB)
4. Downloads 300 MB more data → Total: 5.1 GB
5. Engine updates Redis: `INCRBY usage:<config_id>:2025-12-18 314572800`
6. Next check (1 minute later):
   ```redis
   GET usage:<config_id>:2025-12-18  → 5,400,000,000 bytes (5.04 GB)
   ```
   - Exceeds cap (5.0 GB)
7. Engine throttles connection:
   ```bash
   tc class change dev ifb0 classid 1:5 htb rate 128kbit  # Near-zero bandwidth
   ```
8. Engine sends push notification (future feature): "Daily limit reached. Resets at midnight UTC."
9. After 5 minutes of throttled state:
   - Remove WireGuard peer
   - Delete Redis key: `DEL active_conn:<config_id>`
   - Update PostgreSQL:
     ```sql
     UPDATE connections SET disconnected_at = NOW(), disconnect_reason = 'daily_cap_reached' WHERE id = ?;
     ```
10. Mobile app shows "Disconnected - Daily limit reached (5 GB). Resets at midnight UTC."

---

### Workflow 5: Daily Billing (Midnight UTC)

**Actors:** Cron job, netcloak-admin, PostgreSQL

**Steps:**

1. Cron job runs at 00:00 UTC: `/usr/local/bin/netcloak-daily-billing`
2. Query active subscribers:
   ```sql
   SELECT id, shop_id, config_id FROM subscribers WHERE status = 'active';
   ```
   → Returns 500 active subscribers
3. For each subscriber:
   a. Check shop points balance:
      ```sql
      SELECT points_balance FROM shops WHERE id = '<shop_id>' FOR UPDATE;
      ```
   b. If balance >= 1:
      - Deduct 1 point:
        ```sql
        UPDATE shops SET points_balance = points_balance - 1 WHERE id = '<shop_id>';
        ```
      - Record transaction:
        ```sql
        INSERT INTO point_transactions (shop_id, subscriber_id, amount, type, description, balance_after)
        VALUES ('<shop_id>', '<subscriber_id>', -1, 'daily_deduction', 'Daily billing for subscriber', <new_balance>);
        ```
      - Update subscriber:
        ```sql
        UPDATE subscribers SET last_billed_date = CURRENT_DATE WHERE id = '<subscriber_id>';
        ```
   c. If balance < 1:
      - Expire subscriber:
        ```sql
        UPDATE subscribers SET status = 'expired', expires_at = NOW() WHERE id = '<subscriber_id>';
        ```
      - Send IPC to remove peer from VPN server
      - Send email to shop: "Subscriber expired due to insufficient points"

4. Write usage logs to PostgreSQL (from Redis):
   ```sql
   INSERT INTO usage_logs (subscriber_id, date, data_used_mb, data_cap_mb)
   VALUES ('<subscriber_id>', '2025-12-18', 4850.2, 5120);
   ```
5. Reset Redis data counters:
   ```redis
   DEL usage:<config_id>:2025-12-18  # Delete yesterday's counter
   ```
6. Log billing summary: "Processed 500 subscribers, deducted 500 points, expired 5 subscribers"

---

### Workflow 6: Subscriber Disconnects

**Actors:** Mobile app, netcloak-engine

**Steps:**

1. Subscriber taps "Disconnect" in mobile app
2. App stops WireGuard interface
3. WireGuard handshake stops (120 seconds keepalive timeout)
4. netcloak-engine detects peer inactivity (orphan cleanup goroutine)
5. Engine removes WireGuard peer:
   ```bash
   wg set wg0 peer <public_key> remove
   ```
6. Engine deletes Redis active connection:
   ```redis
   DEL active_conn:<config_id>
   ```
7. Engine updates PostgreSQL:
   ```sql
   UPDATE connections
   SET disconnected_at = NOW(), disconnect_reason = 'normal'
   WHERE subscriber_id = '<subscriber_id>' AND disconnected_at IS NULL;
   ```
8. Engine removes TC traffic class
9. Mobile app shows "Disconnected"

**Result:** Subscriber can reconnect immediately (or connect from different device)

---

## Security Model

### Threat Model

**Assumptions:**
- Shops are semi-trusted (verified business, but may try to abuse)
- Subscribers are untrusted (will attempt to share configs, exceed limits)
- VPN servers are trusted (we control infrastructure)
- Internet is hostile (attackers may attempt to MITM, DoS)

**Attack Scenarios:**

1. **Subscriber shares config with friend** → Multi-server abuse prevention (Redis active connection check)
2. **Shop tries to create subscribers without paying** → Points balance enforced at API layer
3. **Attacker brute-forces shop passwords** → Rate limiting (5 attempts/min), bcrypt with cost 12
4. **Attacker intercepts config link** → Config contains full private key (HTTPS required)
5. **Compromised netcloak-edge** → Cannot modify WireGuard (privilege separation)
6. **Redis goes down** → Fail open (allow connections, log warning)
7. **PostgreSQL injection** → Parameterized queries, no raw SQL
8. **DDoS on VPN server** → Connection rate limiting, WireGuard built-in DDoS protection

---

### Authentication & Authorization

#### Shop Authentication (JWT)

**Flow:**
1. Shop logs in: `POST /auth/login` with email/password
2. Server verifies bcrypt hash (cost 12)
3. Generate JWT token:
   ```json
   {
     "sub": "shop_id",
     "email": "shop@example.com",
     "iat": 1703000000,
     "exp": 1703086400  // 24 hours
   }
   ```
4. Sign with HMAC-SHA256 (secret key from environment variable)
5. Return token to client
6. Client includes in `Authorization: Bearer <token>` header
7. Server verifies signature, checks expiration, extracts shop_id

**Token Expiration:** 24 hours (refresh by re-login)

**Security:**
- HTTPS required (token transmitted over TLS)
- HttpOnly cookie option (prevent XSS, future enhancement)
- No refresh tokens (keep simple for MVP)

---

#### Subscriber Authentication (WireGuard Keypair)

**No traditional authentication** - WireGuard public/private key IS the credential

**Security Properties:**
- Private key never leaves subscriber's device
- Public key is identity (stored in PostgreSQL)
- WireGuard handshake proves possession of private key (cryptographic proof)
- Cannot be brute-forced (Curve25519 elliptic curve)

**Revocation:**
- Remove peer from WireGuard: `wg set wg0 peer <public_key> remove`
- Delete from PostgreSQL: `UPDATE subscribers SET status = 'expired'`
- Subscriber can no longer connect

---

### Privilege Separation (Engine/Edge)

**Why:** Minimize attack surface if netcloak-edge is compromised

**Design:**

**netcloak-engine (Root Privileged):**
- Must run as root (manage WireGuard kernel module, TC, iptables)
- No network exposure (listens only on Unix socket)
- Minimal code surface (core VPN logic only)
- No HTTP parsing (attack surface)

**netcloak-edge (Unprivileged):**
- Runs as `netcloak` user (no root)
- Exposes HTTP API (attack surface)
- Parses HTTP requests (potential vulnerabilities)
- If compromised: Cannot modify WireGuard, TC, or iptables

**Communication:** Unix domain socket with restricted permissions

```bash
/var/run/netcloak/engine.sock
Owner: root:netcloak
Permissions: 0660 (rw-rw----)
```

**IPC Authorization:**
- Edge connects to socket as `netcloak` group member
- Engine validates group membership
- No authentication within IPC (socket permissions are sufficient)

---

### Network Security

#### VPN Server Firewall (iptables)

```bash
# Allow WireGuard
-A INPUT -p udp --dport 51820 -j ACCEPT

# Allow SSH (management)
-A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS (for health checks, internal only)
-A INPUT -p tcp --dport 8081 -s 10.0.0.0/8 -j ACCEPT  # Internal network only

# Drop all other inbound
-A INPUT -j DROP

# Allow established connections
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# WireGuard forwarding (NAT)
-A FORWARD -i wg0 -j ACCEPT
-A FORWARD -o wg0 -j ACCEPT
-t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE
```

---

#### DDoS Protection

**WireGuard Built-in:**
- Cookie-based handshake (prevents amplification)
- Rate limiting on handshake responses
- Stateless until handshake complete

**Additional (netcloak-edge):**
- Rate limit connection attempts: 5 per IP per minute
- Fail2ban: Block IPs with >20 failed auth attempts in 10 minutes

---

### Data Security

#### Encryption in Transit

- **VPN Tunnel:** WireGuard (ChaCha20-Poly1305 or AES-256-GCM)
- **HTTPS:** TLS 1.3 (Let's Encrypt certificates)
- **Database:** PostgreSQL SSL mode (require)
- **Redis:** TLS optional (if Redis is remote, enable AUTH + TLS)

#### Encryption at Rest

**PostgreSQL:**
- Private keys encrypted with shop-specific key (AES-256-GCM)
- Shop keys derived from master key + shop_id (HKDF)
- Master key stored in environment variable (separate from codebase)

**Why encrypt private keys?**
- Database backup leak doesn't expose subscriber VPN credentials
- Attacker needs both database AND master key

**Implementation:**
```go
func encryptPrivateKey(privateKey, shopID string) string {
    shopKey := deriveShopKey(masterKey, shopID)  // HKDF-SHA256
    ciphertext := aesGCMEncrypt(privateKey, shopKey)
    return base64.StdEncoding.EncodeToString(ciphertext)
}
```

---

#### PII Handling

**Minimalistic Data Collection Philosophy:**

NetCloak collects the absolute minimum data required for operations. This approach provides:
- **Better privacy** for shops and subscribers
- **Lower compliance burden** (GDPR, data retention laws)
- **Reduced attack surface** (less data to protect)
- **Simpler architecture** (fewer fields to maintain)

**What we collect:**

**Shops (Business Customers):**
- Name, email, password (authentication only)
- Points balance (billing)
- That's it. No phone, address, TIN, or business documents

**Subscribers (End Users):**
- ZERO personal data
- Only technical VPN config (WireGuard keys, IP addresses)
- Shops track their own customer relationships externally

**What we explicitly DO NOT collect:**
- ❌ Subscriber names, emails, phone numbers
- ❌ Device identifiers (IMEI, MAC addresses)
- ❌ Browsing activity (DNS queries, HTTP requests, URLs visited)
- ❌ Public IP addresses (client IPs not logged)
- ❌ Traffic content (only byte counts for billing)
- ❌ Location data (no GPS, no IP geolocation)

**Data Retention:**
- Connection logs: 90 days (automatic deletion)
- Usage logs: 90 days (for billing disputes)
- Deleted subscriber data: Immediate CASCADE deletion (no soft deletes)

**GDPR Compliance:**
- Right to deletion: `DELETE FROM shops WHERE id = ?` → CASCADE deletes all data
- Data export: API endpoint returns shop data as JSON
- Privacy policy: "We don't log what you do online. Period."

---

### Abuse Prevention

#### Multi-Server Abuse (Config Sharing)

**Detection:** Redis active connection check (see Multi-Server Architecture section)

**Response:**
- Reject new connection attempt
- Log to PostgreSQL: `abuse_logs` table (future)
- After 5 attempts: Flag subscriber for review
- Shop receives email: "Subscriber possibly sharing config"

---

#### Daily Data Cap Evasion

**Attack:** Subscriber modifies iptables counters on their device

**Mitigation:** Counters are server-side (iptables/eBPF on VPN server, subscriber has no access)

---

#### Shop Creates Subscribers Without Paying

**Prevention:** Points balance checked before subscriber creation:
```go
if shop.PointsBalance < 1 {
    return errors.New("insufficient points")
}
```

**Enforcement:** PostgreSQL transaction (atomic deduction)

---

#### Reverse Engineering Mobile App

**Risk:** Attacker extracts API keys, endpoints from decompiled app

**Mitigation:**
- No API keys in app (subscriber auth is WireGuard keypair)
- Config download link is public (no auth needed)
- Shop API requires JWT (attacker can't create subscribers without shop credentials)

---

## Migration from PoC

### PoC Architecture Summary

**netcloak-engine (PoC):**
- SQLite database (sessions table)
- Anonymous session creation
- Dynamic bandwidth tiers (5 tiers: 5/15/30/50/100 Mbps)
- Session expiration (time-based)

**netcloak-edge (PoC):**
- Gin HTTP framework
- JWT authentication (for anonymous users)
- Session CRUD API
- Decoy pages (traffic obfuscation)

---

### Migration Strategy

#### Phase 1: Database Migration (Week 1)

**Tasks:**
1. Create PostgreSQL schema (shops, subscribers, point_transactions, usage_logs, connections, servers)
2. Migrate data model:
   - `sessions` → `subscribers` (persistent accounts)
   - Add `shops` table (new)
   - Add `point_transactions` table (new)
3. Deploy PostgreSQL on VPS or use managed service (DigitalOcean Managed DB: $15/month)
4. Run schema migrations with `golang-migrate`

---

#### Phase 2: Engine Refactor (Week 2)

**Changes:**

1. **Remove SQLite, add PostgreSQL + Redis clients:**
   ```go
   // Remove
   db, _ := sql.Open("sqlite3", "./netcloak.db")

   // Add
   pgConn := pgx.Connect(context.Background(), os.Getenv("DATABASE_URL"))
   redisClient := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
   ```

2. **Simplify bandwidth tiers:**
   ```go
   // Remove dynamic tiers
   func getBandwidthTier(tier int) int { ... }

   // Add fixed tiers
   func getBandwidthMbps(plan string) int {
       if plan == "premium" {
           return 40
       }
       return 15  // fast
   }
   ```

3. **Add daily data cap enforcement:**
   ```go
   func checkDailyUsage(configID string) (bool, error) {
       today := time.Now().UTC().Format("2006-01-02")
       key := fmt.Sprintf("usage:%s:%s", configID, today)
       bytesUsed, err := redisClient.Get(ctx, key).Int64()
       if err == redis.Nil {
           return true, nil  // No usage today
       }
       cap := int64(5 * 1024 * 1024 * 1024)  // 5 GB
       return bytesUsed < cap, nil
   }
   ```

4. **Add multi-server abuse check:**
   ```go
   func checkActiveConnection(configID string) (bool, error) {
       key := fmt.Sprintf("active_conn:%s", configID)
       exists, err := redisClient.Exists(ctx, key).Result()
       return exists == 0, err  // Return true if NOT active
   }
   ```

5. **Keep WireGuard peer management (no changes)**

6. **Keep TC traffic control (update to 2 tiers)**

7. **Keep orphan cleanup (no changes)**

**Estimated effort:** 3-4 days

---

#### Phase 3: Edge Refactor (Week 3)

**Changes:**

1. **Remove anonymous session API:**
   - Delete `/sessions/create` endpoint
   - Delete `/sessions/delete` endpoint
   - Delete JWT authentication for users

2. **Remove decoy pages:**
   - Delete `/decoy/*` handlers

3. **Keep health check:**
   - `/health` endpoint (no changes)

4. **Add internal endpoints:**
   ```go
   router.POST("/internal/reset-daily", resetDailyHandler)
   router.GET("/capacity", capacityHandler)
   ```

5. **Add connection event reporting:**
   ```go
   func reportConnectionEvent(subscriberID, serverID, eventType string) {
       // Write to PostgreSQL connections table
   }
   ```

**Estimated effort:** 2 days

---

#### Phase 4: Build netcloak-admin (Week 4-5)

**New component from scratch:**

1. Shop authentication (email/password, JWT)
2. Shop dashboard (Go templates + Tailwind)
3. Shop API (subscriber CRUD, points management)
4. Wise webhook integration
5. Config download endpoint

**Estimated effort:** 1.5 weeks

---

#### Phase 5: Testing & Deployment (Week 6)

**Tasks:**
1. Integration testing (create subscriber → connect VPN → usage tracking → daily billing)
2. Load testing (simulate 50 concurrent connections)
3. Deploy to production VPS
4. DNS setup (vpn-01.netcloak.app, api.netcloak.app)
5. SSL certificates (Let's Encrypt)
6. Systemd services (netcloak-engine, netcloak-edge, netcloak-admin)

---

### Reusability Assessment

| Component | PoC | New System | Reusability | Changes Needed |
|-----------|-----|------------|-------------|----------------|
| WireGuard peer management | ✅ | ✅ | 100% | None |
| Traffic control (TC) | ✅ | ✅ | 90% | Update to 2 fixed tiers |
| IP allocation | ✅ | ✅ | 100% | None |
| Orphan cleanup | ✅ | ✅ | 100% | None |
| IPC protocol | ✅ | ✅ | 100% | Add new commands |
| Health monitoring | ✅ | ✅ | 100% | None |
| Gin HTTP framework | ✅ | ✅ | 80% | Remove decoy pages |
| Rate limiting | ✅ | ✅ | 100% | None |
| Session API | ✅ | ❌ | 0% | Delete (replaced by subscriber API) |
| SQLite database | ✅ | ❌ | 0% | Migrate to PostgreSQL |
| Anonymous auth | ✅ | ❌ | 0% | Delete (subscribers use WireGuard keys) |

**Summary:**
- **Engine:** 80% reusable (core VPN logic intact)
- **Edge:** 30% reusable (HTTP framework + health checks, rest is refactored)
- **Database:** 0% reusable (SQLite → PostgreSQL migration)

---

## Deployment Architecture

### Production Deployment (MVP)

**Components:**

1. **Web Server (api.netcloak.app):**
   - Hosting: DigitalOcean Droplet ($6/month) or Contabo VPS
   - OS: Ubuntu 22.04 LTS
   - Services:
     - nginx (reverse proxy, static files, TLS termination)
     - netcloak-admin (Go binary, systemd service)
     - PostgreSQL 15 (Docker or native install)
     - Redis 7 (Docker or native install)

2. **VPN Server 1 (vpn-01.netcloak.app):**
   - Hosting: Contabo Cloud VPS 20 ($4.77/month)
   - OS: Ubuntu 22.04 LTS
   - Services:
     - netcloak-engine (Go binary, systemd service, root)
     - netcloak-edge (Go binary, systemd service, unprivileged)
     - WireGuard kernel module

---

### Directory Structure

**Web Server:**
```
/opt/netcloak/
  ├── admin/              # netcloak-admin binary
  │   ├── netcloak-admin
  │   ├── templates/      # Go html templates
  │   └── static/         # CSS, JS, images
  ├── config/
  │   └── admin.env       # Environment variables
  └── logs/
      └── admin.log

/var/lib/postgresql/15/   # PostgreSQL data directory
/var/lib/redis/           # Redis data directory

/etc/nginx/
  ├── sites-available/
  │   └── netcloak.conf   # nginx config
  └── ssl/
      ├── netcloak.app.crt
      └── netcloak.app.key
```

**VPN Server:**
```
/opt/netcloak/
  ├── engine/             # netcloak-engine binary
  │   └── netcloak-engine
  ├── edge/               # netcloak-edge binary
  │   └── netcloak-edge
  ├── config/
  │   ├── engine.env      # Environment variables
  │   └── edge.env
  └── logs/
      ├── engine.log
      └── edge.log

/var/run/netcloak/
  └── engine.sock         # Unix socket (IPC)

/etc/wireguard/
  └── wg0.conf            # WireGuard interface config (managed by engine)
```

---

### Systemd Services

**netcloak-admin.service:**
```ini
[Unit]
Description=NetCloak Admin API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=netcloak
Group=netcloak
WorkingDirectory=/opt/netcloak/admin
EnvironmentFile=/opt/netcloak/config/admin.env
ExecStart=/opt/netcloak/admin/netcloak-admin
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

**netcloak-engine.service:**
```ini
[Unit]
Description=NetCloak VPN Engine
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/netcloak/engine
EnvironmentFile=/opt/netcloak/config/engine.env
ExecStart=/opt/netcloak/engine/netcloak-engine
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

**netcloak-edge.service:**
```ini
[Unit]
Description=NetCloak VPN Edge API
After=network.target netcloak-engine.service

[Service]
Type=simple
User=netcloak
Group=netcloak
WorkingDirectory=/opt/netcloak/edge
EnvironmentFile=/opt/netcloak/config/edge.env
ExecStart=/opt/netcloak/edge/netcloak-edge
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

### Nginx Configuration

**api.netcloak.app:**
```nginx
upstream netcloak_admin {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name api.netcloak.app;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.netcloak.app;

    ssl_certificate /etc/letsencrypt/live/api.netcloak.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.netcloak.app/privkey.pem;

    # Static files
    location /static/ {
        alias /opt/netcloak/admin/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API and dashboard
    location / {
        proxy_pass http://netcloak_admin;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### Environment Variables

**admin.env:**
```bash
DATABASE_URL=postgres://netcloak:password@localhost:5432/netcloak
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=<random-256-bit-secret>
MASTER_ENCRYPTION_KEY=<random-256-bit-key>
WISE_WEBHOOK_SECRET=<wise-provided-secret>
PORT=8080
```

**engine.env:**
```bash
DATABASE_URL=postgres://netcloak:password@api.netcloak.app:5432/netcloak
REDIS_URL=redis://api.netcloak.app:6379/0
WIREGUARD_INTERFACE=wg0
WIREGUARD_PORT=51820
SERVER_ID=vpn-01
IPC_SOCKET_PATH=/var/run/netcloak/engine.sock
```

**edge.env:**
```bash
IPC_SOCKET_PATH=/var/run/netcloak/engine.sock
PORT=8081
SERVER_ID=vpn-01
```

---

### Monitoring & Logs

**Application Logs:**
```bash
# JSON structured logs
journalctl -u netcloak-admin -f
journalctl -u netcloak-engine -f
journalctl -u netcloak-edge -f
```

**Database Monitoring:**
```sql
-- PostgreSQL slow query log
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second
SELECT pg_reload_conf();

-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

**Redis Monitoring:**
```bash
redis-cli INFO stats
redis-cli MONITOR  # Live command stream
```

---

### Backup Strategy

**PostgreSQL (Daily Backups):**
```bash
#!/bin/bash
# /opt/netcloak/scripts/backup-postgres.sh

pg_dump -U netcloak netcloak | gzip > /backup/netcloak-$(date +%Y%m%d).sql.gz

# Retain last 30 days
find /backup -name "netcloak-*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp /backup/netcloak-$(date +%Y%m%d).sql.gz s3://netcloak-backups/
```

**Cron:**
```cron
0 2 * * * /opt/netcloak/scripts/backup-postgres.sh
```

---

### Deployment Process (CI/CD - Future)

**GitHub Actions (Week 2+):**

```yaml
name: Deploy NetCloak

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build binaries
        run: |
          go build -o netcloak-admin ./cmd/admin
          go build -o netcloak-engine ./cmd/engine
          go build -o netcloak-edge ./cmd/edge

      - name: Run tests
        run: go test ./...

      - name: Deploy to VPS
        run: |
          scp netcloak-admin vpn:/opt/netcloak/admin/
          ssh vpn 'sudo systemctl restart netcloak-admin'

      - name: Health check
        run: curl -f https://api.netcloak.app/health
```

---

## Summary

This architecture document defines a **complete, implementable system** for the NetCloak B2B VPN platform:

**Key Design Decisions:**

1. **Simple Monolith** - Single Go service per tier (admin/edge/engine), scale horizontally
2. **Independent Servers** - VPN servers are autonomous, coordinated via central Redis + PostgreSQL
3. **Privilege Separation** - Unprivileged HTTP API, root-only VPN engine, Unix socket IPC
4. **B2B-First** - Shops are customers, subscribers are products, points-based billing
5. **Daily Caps** - 5 GB/day resets at midnight UTC (natural load balancing)
6. **Flat Rates** - 15 Mbps or 40 Mbps (no bursting, simple enforcement)

**Migration Path:** 80% of PoC engine code reusable, 30% of edge code reusable, new admin component

**Next Steps:**
1. Review and validate this architecture with stakeholders
2. Create PostgreSQL schema migrations
3. Begin engine refactor (Week 2)
4. Build netcloak-admin (Week 4-5)
5. Deploy MVP (Week 6)

This document is **open-handed** - no component is too big to change as requirements evolve. However, the core design principles (simple, stateless servers, B2B model, privilege separation) should remain stable.
