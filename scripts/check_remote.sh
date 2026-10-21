#!/usr/bin/env bash
# Usage: bash scripts/check_remote.sh https://your-host
# Quick checks of the remote deployment. Does not send any token.
set -euo pipefail
BASE="${1:?usage: check_remote.sh https://your-host}"

echo "== 1. MCP endpoint without a token (expect 401) =="
curl -sS -i -X POST "$BASE/mcp" \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | head -n 15

echo; echo "== 2. Protected resource metadata (RFC 9728) =="
curl -sS -i "$BASE/.well-known/oauth-protected-resource" | head -n 20
echo "-- path-inserted variant --"
curl -sS -i "$BASE/.well-known/oauth-protected-resource/mcp" | head -n 20

if [ -n "${AUTH_ISSUER_URL:-}" ]; then
  echo; echo "== 3. Authorization server metadata =="
  curl -sS -i "${AUTH_ISSUER_URL%/}/.well-known/oauth-authorization-server" | head -n 25
fi