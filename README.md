# Nexus-MCP

> **Authorization and audit gateway for AI agent tool calls.**

Nexus-MCP is a Python MCP server that authenticates every request, decides **before execution** whether an AI agent is allowed to run a tool, and records every attempt in an audit log.

Built for the **Build, Ship, Shape: Amazon Developer Hackathon 2026** (Alexa+ track) as a self-hosted MCP server, and as a hands-on project to learn Python backend development, MCP and OAuth.

```text
User
  ↓
Alexa+ (MCP client)
  ↓ MCP / Streamable HTTP + Bearer token
Nexus-MCP
  ↓
Authentication     who is making the request?   (invalid → 401)
  ↓
Authorization      is this tool call allowed?
  ├── ALLOW → tool executes
  └── DENY  → tool is NOT executed
  ↓
Audit              every attempt is recorded
  ↓
MCP response
```

## The problem

AI agents can pick tools and act on behalf of users. Not every action carries the same risk, so a system needs to:

- verify who is calling;
- apply a policy **before** a tool runs;
- allow or block individual tool calls;
- keep a structured, auditable record of every decision.

Nexus-MCP demonstrates this control flow at the MCP layer: **an agent can request an action without automatically getting permission to execute it.**

## MVP

Three simulated tools demonstrate the different outcomes:

| Tool | Action | Risk | Decision |
|---|---|---|---|
| `get_customer` | READ | LOW | ✅ ALLOW |
| `create_order` | WRITE | MEDIUM | ✅ ALLOW |
| `cancel_order` | DESTRUCTIVE | HIGH | ❌ DENY |

Example: a user asks Alexa+ to cancel order `1042`. Alexa+ requests `cancel_order(order_id=1042)`, Nexus validates the bearer token, the policy returns `DENY`, the tool is never invoked, an audit event is written with `execution_status = NOT_EXECUTED`, and the denial is returned to Alexa+.

## Tech stack

| Area | Choice |
|---|---|
| Language | Python |
| Protocol | MCP (minimum spec version 2025-11-25) |
| Transport | Streamable HTTP |
| MCP implementation | Official MCP Python SDK (2.x) |
| Authentication | OAuth 2.1 resource server: bearer JWTs validated locally against the provider's JWKS (PyJWT) |
| Authorization policy | Python mapping, deny by default |
| Audit | Append-only JSONL |
| Testing | pytest |
| Architecture | Modular monolith |

The reasoning behind each choice is recorded in [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Project status

🟡 **Sprint 2 starting. NX-00 to NX-06 are complete.**

```text
Project definition      ✅
Architecture            ✅
Repository / env        ✅
MCP server              ✅
Simulated tools         ✅
Authorization engine    ✅
Gateway + audit         ✅
Integration tests       ✅
Authentication          ✅
Remote deployment       ⚪ (next)
Alexa+ integration      ⚪
End-to-end validation   ⚪
Demo                    ⚪
Submission              ⚪
```

## How a request flows

```text
1. Client → POST /mcp with Authorization: Bearer <token>
2. auth/            validates signature, issuer, expiry and scope → else 401
3. server.py        thin MCP adapter: turns the call into gateway.call(...)
4. gateway.py       the single path to any tool
5. authorization/   authorize(tool_name) → ALLOW | DENY (+ reason)
6. DENY  → tool is not looked up and not called
   ALLOW → tools/ executes the simulated tool
7. audit/           one JSONL event per attempt (arguments sanitized, no secrets)
8. server.py        returns the MCP response (result or denial)
```

Authentication (`auth/`) never knows about the policy, and the policy (`authorization/`) never imports the tools. Architecture tests in `tests/integration/` enforce these boundaries.

## Getting started

Requires Python 3.10 or later.

```bash
git clone https://github.com/javtl/nexus-mcp.git
cd nexus-mcp

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
cp .env.example .env               # fill in your values; never commit .env

pytest                             # unit and integration tests
```

### Configuration

Variables are not loaded from `.env` automatically. Export them in your shell:

```bash
set -a; source .env; set +a
```

| Variable | Purpose |
|---|---|
| `NEXUS_HOST` / `NEXUS_PORT` (or `PORT`) | Bind address and port |
| `NEXUS_PUBLIC_URL` | Public HTTPS URL of this server |
| `AUTH_ISSUER_URL` | OAuth authorization server (token issuer) |
| `AUTH_JWKS_URL` | JWKS endpoint used to verify token signatures |
| `AUTH_AUDIENCE` | Optional expected audience |
| `AUTH_REQUIRED_SCOPES` | Scopes a token must carry |
| `AUDIT_FILE_PATH` | Audit log location (default `data/audit.jsonl`) |

The server **refuses to start** if authentication is not configured. There is intentionally no switch to disable it.

### Run

```bash
python -m nexus_mcp.server
```

Every request to the MCP endpoint needs a valid bearer token from your authorization server. A request without one gets `401`.

### Reading the audit log

```bash
cat data/audit.jsonl
```

Each line records `timestamp`, `request_id`, `tool_name`, sanitized `arguments`, `action_type`, `risk_level`, `decision`, `reason` and `execution_status` (`SUCCESS`, `FAILED` or `NOT_EXECUTED`).

## Repository layout

```text
src/nexus_mcp/
├── server.py          MCP entry point (HTTP/MCP boundary, thin adapters)
├── config.py          settings from environment variables
├── gateway.py         authorize → execute or block → audit
├── auth/              token validation (authentication)
├── authorization/     policy and ALLOW/DENY engine
├── tools/             simulated business tools
└── audit/             audit events, sanitizer, JSONL writer
tests/
├── unit/              per-module tests
└── integration/       end-to-end gateway flow and architecture boundaries
docs/                  project documentation
```

## Documentation

| Document | Purpose |
|---|---|
| [`docs/PROJECT.md`](docs/PROJECT.md) | What we are building and why |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the system is structured |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Technical decisions and their reasons |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Build order and milestones |
| [`docs/TICKETS.md`](docs/TICKETS.md) | Task-level work and Definition of Done |
| [`docs/LEARNING_LOG.md`](docs/LEARNING_LOG.md) | What is being learned along the way |
| [`docs/RISKS-AND-FRICTION.md`](docs/RISKS-AND-FRICTION.md) | Risks and tooling friction |
| [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) | How AI assistants work on this project |

## Development workflow

Lightweight GitFlow:

```text
main      stable milestones
  ↑
develop   integration branch
  ↑
feature/<ticket-id>-<short-name>
```

Each feature gets its own branch, tests and review before merging into `develop`. Learning entries are tracked per feature as `NX-xx`.

## Security notes

- Secrets live in `.env` or in the host's environment settings. `.env` is git-ignored; only `.env.example` is committed.
- Tokens, client secrets and private keys never appear in logs or audit records. Audit arguments are sanitized by key name as a safety net.
- Authentication answers *who*; authorization answers *is it allowed*. They are separate modules.
- Authorization denies by default: a tool missing from the policy is blocked, not allowed.
- Token validation pins the accepted algorithms and requires `iss` and `exp`. Error messages never include the token.
- If the audit writer fails, a denied call is still never executed.

## Not in scope

SaaS features, dashboards, frontends, complex RBAC, multi-tenancy, microservices, real commerce infrastructure, or AI-based authorization decisions. What happens after the hackathon will be decided once the MVP is submitted.

## License

To be decided.
