# Nexus-MCP

> **Authorization and audit gateway for AI agent tool calls.**

Nexus-MCP is a Python MCP server that decides, **before execution**, whether an AI agent is allowed to run a tool, and records every attempt in an audit log.

Built for the **Build, Ship, Shape: Amazon Developer Hackathon 2026** (Alexa+ track) as a self-hosted MCP server, and as a hands-on project to learn Python backend development, MCP and OAuth.

```text
User
  ↓
Alexa+ (MCP client)
  ↓ MCP / Streamable HTTP
Nexus-MCP
  ↓
Authentication     who is making the request?
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

Example: a user asks Alexa+ to cancel order `1042`. Alexa+ requests `cancel_order(order_id=1042)`, Nexus authenticates the request, the policy returns `DENY`, the tool is never invoked, an audit event is written with `execution_status = NOT_EXECUTED`, and the denial is returned to Alexa+.

## Tech stack

| Area | Choice |
|---|---|
| Language | Python |
| Protocol | MCP (minimum spec version 2025-11-25) |
| Transport | Streamable HTTP |
| MCP implementation | Official MCP Python SDK (2.x) |
| Authentication | OAuth model required by Alexa+ (bearer tokens, protected resource metadata) |
| Authorization policy | Python mapping, deny by default |
| Audit | Append-only JSONL |
| Testing | pytest |
| Architecture | Modular monolith |

The reasoning behind each choice is recorded in [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Project status

🟡 **Sprint 1 in progress. NX-00 to NX-03 are complete.**

```text
Project definition      ✅
Architecture            ✅ (conceptual)
Technical decisions     🟡 (some provisional)
Repository / env        ✅
MCP server skeleton     ✅ (tools listed, not yet wired to the gateway)
Simulated tools         ✅
Authorization engine    ✅
Gateway + audit         ⚪ (next)
Integration tests       ⚪
Authentication          ⚪
Remote deployment       ⚪
Alexa+ integration      ⚪
Demo                    ⚪
Submission              ⚪
```

> The server currently exposes the three tools with placeholder bodies. They are intentionally **not** connected to the real tool functions until the gateway enforces authorization (next feature), so no tool can run without a policy decision.

## Getting started

Requires Python 3.10 or later.

```bash
git clone https://github.com/javtl/nexus-mcp.git
cd nexus-mcp

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
cp .env.example .env               # never commit .env

pytest                             # unit tests should pass
python -m nexus_mcp.server         # MCP server over Streamable HTTP
```

You can inspect the running server with the MCP Inspector (see its documentation for connecting over Streamable HTTP).

Environment variables are not loaded from `.env` automatically. Export them in your shell, for example:

```bash
set -a; source .env; set +a
```

## Repository layout

```text
src/nexus_mcp/
├── server.py          MCP entry point (HTTP/MCP boundary)
├── config.py          settings from environment variables
├── authorization/     policy and ALLOW/DENY engine            ✅
├── tools/             simulated business tools                ✅
├── gateway.py         authorization → tool → audit            (planned)
├── audit/             audit events and JSONL writer           (planned)
└── auth/              token validation, resource metadata     (planned)
tests/                 unit and integration tests
docs/                  project documentation
```

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the build order.

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

- Secrets live in `.env`, which is git-ignored. Only `.env.example` is committed.
- Access tokens, client secrets and private keys must never appear in logs or in audit records.
- Authentication and authorization are separate responsibilities: the first answers *who*, the second answers *is it allowed*.
- Authorization denies by default: a tool missing from the policy is blocked, not allowed.

## Not in scope

SaaS features, dashboards, frontends, complex RBAC, multi-tenancy, microservices, real commerce infrastructure, or AI-based authorization decisions. What happens after the hackathon will be decided once the MVP is submitted.

## License

To be decided.
