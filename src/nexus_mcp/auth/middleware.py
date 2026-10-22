"""Pure ASGI middleware: removes WWW-Authenticate from 401 responses.

Alexa+ documents that unauthenticated requests must return 401 WITHOUT this header.
Add it ONLY if the SDK emits the header (verified with curl)."""

from __future__ import annotations


class StripWwwAuthenticateOn401:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start" and message["status"] == 401:
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() != b"www-authenticate"
                ]
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)