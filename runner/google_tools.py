"""In-process MCP servers for Google Calendar and Gmail (read-only).

Google's first-party MCP endpoints (calendarmcp/gmailmcp.googleapis.com)
return PERMISSION_DENIED to tokens from non-partner OAuth clients even with
correct scopes and the APIs enabled — but the plain REST APIs work fine. So
the runner hosts these thin read-only tools itself via the Agent SDK's
in-process MCP support, reusing the token minted by scripts/google-oauth.py.

Exposed (matching the mcp/servers.template.json "sdk" entries):
  gcal:  list_events
  gmail: search_threads, get_thread
"""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

_TOKEN_HELPER = Path(__file__).resolve().parent.parent / "scripts" / "google-oauth.py"


def _token() -> str:
    proc = subprocess.run(
        [sys.executable, str(_TOKEN_HELPER), "token"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"google token: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _get(url: str, params: dict[str, Any]) -> dict:
    full = (
        url
        + "?"
        + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    )
    req = urllib.request.Request(full, headers={"Authorization": f"Bearer {_token()}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _result(payload: Any) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}]
    }


def _error(err: Exception) -> dict:
    return {"content": [{"type": "text", "text": f"error: {err}"}], "is_error": True}


def _header(message: dict, name: str) -> str:
    for h in message.get("payload", {}).get("headers", []):
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


@tool(
    "list_events",
    "List calendar events across all of the user's calendars in a time window. "
    "Times are RFC3339 (e.g. 2026-07-21T00:00:00Z).",
    {"time_min": str, "time_max": str},
)
async def list_events(args: dict) -> dict:
    try:
        calendars = _get(
            "https://www.googleapis.com/calendar/v3/users/me/calendarList",
            {"maxResults": 20, "minAccessRole": "reader"},
        ).get("items", [])
        events = []
        for cal in calendars:
            if cal.get("selected") is False:
                continue
            items = _get(
                f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(cal['id'])}/events",
                {
                    "timeMin": args["time_min"],
                    "timeMax": args["time_max"],
                    "singleEvents": "true",
                    "orderBy": "startTime",
                    "maxResults": 50,
                },
            ).get("items", [])
            for ev in items:
                me = next((a for a in ev.get("attendees", []) if a.get("self")), {})
                events.append(
                    {
                        "calendar": cal.get("summaryOverride") or cal.get("summary"),
                        "summary": ev.get("summary"),
                        "start": ev.get("start"),
                        "end": ev.get("end"),
                        "organizer_is_me": bool(ev.get("organizer", {}).get("self")),
                        "my_response": me.get("responseStatus"),
                        "attendee_count": len(ev.get("attendees", [])),
                        "location": ev.get("location"),
                        "description_snippet": (ev.get("description") or "")[:200]
                        or None,
                        "html_link": ev.get("htmlLink"),
                    }
                )
        return _result({"events": events})
    except Exception as err:
        return _error(err)


@tool(
    "search_threads",
    "Search Gmail threads with a Gmail query (e.g. 'is:unread newer_than:2d'). "
    "Returns per-thread subject, participants, date and snippet.",
    {"query": str, "max_results": int},
)
async def search_threads(args: dict) -> dict:
    try:
        listing = _get(
            "https://gmail.googleapis.com/gmail/v1/users/me/threads",
            {
                "q": args["query"],
                "maxResults": min(int(args.get("max_results") or 10), 25),
            },
        )
        threads = []
        for t in listing.get("threads", []):
            data = _get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/threads/{t['id']}",
                {
                    "format": "metadata",
                    "metadataHeaders": ["From", "To", "Subject", "Date"],
                },
            )
            msgs = data.get("messages", [])
            if not msgs:
                continue
            first, last = msgs[0], msgs[-1]
            threads.append(
                {
                    "thread_id": t["id"],
                    "subject": _header(first, "Subject"),
                    "from_first": _header(first, "From"),
                    "from_last": _header(last, "From"),
                    "date_last": _header(last, "Date"),
                    "message_count": len(msgs),
                    "snippet": last.get("snippet"),
                    "labels_last": last.get("labelIds", []),
                    "link": f"https://mail.google.com/mail/u/0/#inbox/{t['id']}",
                }
            )
        return _result({"threads": threads})
    except Exception as err:
        return _error(err)


@tool(
    "get_thread",
    "Fetch one Gmail thread's messages (headers + snippets) to check who "
    "replied last and whether the user already responded.",
    {"thread_id": str},
)
async def get_thread(args: dict) -> dict:
    try:
        data = _get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/threads/{args['thread_id']}",
            {
                "format": "metadata",
                "metadataHeaders": ["From", "To", "Subject", "Date"],
            },
        )
        messages = [
            {
                "from": _header(m, "From"),
                "to": _header(m, "To"),
                "date": _header(m, "Date"),
                "subject": _header(m, "Subject"),
                "snippet": m.get("snippet"),
                "labels": m.get("labelIds", []),
            }
            for m in data.get("messages", [])
        ]
        return _result({"thread_id": args["thread_id"], "messages": messages})
    except Exception as err:
        return _error(err)


def gcal_server():
    return create_sdk_mcp_server(name="gcal", version="1.0.0", tools=[list_events])


def gmail_server():
    return create_sdk_mcp_server(
        name="gmail", version="1.0.0", tools=[search_threads, get_thread]
    )
