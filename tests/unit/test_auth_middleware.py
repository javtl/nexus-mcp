import asyncio

from nexus_mcp.auth.middleware import StripWwwAuthenticateOn401


def run(status, headers):
    sent = []

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": b""})

    async def send(message):
        sent.append(message)

    asyncio.run(StripWwwAuthenticateOn401(app)({"type": "http"}, None, send))
    return sent[0]["headers"]


def test_401_loses_www_authenticate():
    headers = run(401, [(b"www-authenticate", b"Bearer"), (b"content-type", b"application/json")])
    assert headers == [(b"content-type", b"application/json")]


def test_other_statuses_are_untouched():
    headers = run(200, [(b"www-authenticate", b"Bearer")])
    assert headers == [(b"www-authenticate", b"Bearer")]