# Task 4 Brief: worker accepts phone-* rooms

**Files:**
- Create: `voice-agent/app/rooms.py`
- Modify: `voice-agent/agent.py` (entrypoint filter only)
- Test: `voice-agent/tests/test_rooms.py`

**Interfaces (locked):**
- Produces: `is_handled_room(name: str) -> bool` from `app.rooms`; `HANDLED_PREFIXES = ("playground-", "phone-")`.

## Step 1: Failing tests — create `voice-agent/tests/test_rooms.py`

```python
"""Room-name routing for the worker (playground vs phone legs)."""
from app.rooms import HANDLED_PREFIXES, is_handled_room


def test_playground_rooms_handled():
    assert is_handled_room("playground-1-abc")


def test_phone_rooms_handled():
    assert is_handled_room("phone-42")
    assert is_handled_room("phone-84")


def test_other_rooms_rejected():
    assert not is_handled_room("campaign-x")
    assert not is_handled_room("random-room")
    assert not is_handled_room("")
    assert not is_handled_room(None) if False else not is_handled_room("phone")  # prefix needs dash+id


def test_prefixes_constant():
    assert HANDLED_PREFIXES == ("playground-", "phone-")
```

## Step 2: Run → expect FAIL

Run (repo root): `backend\.venv\Scripts\python.exe -m pytest voice-agent\tests\test_rooms.py -q`
Expected: ModuleNotFoundError for app.rooms.

## Step 3: Implement

Create `voice-agent/app/rooms.py` with exactly:

```python
"""Which LiveKit rooms this worker serves. Kept free of livekit imports."""
from __future__ import annotations

HANDLED_PREFIXES = ("playground-", "phone-")


def is_handled_room(name: str) -> bool:
    """True when a room should get the conversational agent."""
    clean = (name or "").strip()
    return any(clean.startswith(p) and len(clean) > len(p) for p in HANDLED_PREFIXES)
```

Modify `voice-agent/agent.py`:
1. Update module docstring line about dormancy to: "Handles playground-* (browser) and phone-* (Twilio bridge) rooms."
2. Replace the pipeline import line `from app.pipeline import PLAYGROUND_PREFIX, run_session` with `from app.pipeline import run_session`.
3. Add import: `from app.rooms import is_handled_room`.
4. Replace the entrypoint filter block:

```python
    room_name = ctx.room.name or ""
    if not room_name.startswith(PLAYGROUND_PREFIX):
        logger.info(
            "Ignoring job for room %r - only %s* rooms are handled this phase",
            room_name,
            PLAYGROUND_PREFIX,
        )
        return
```

with:

```python
    room_name = ctx.room.name or ""
    if not is_handled_room(room_name):
        logger.info("Ignoring job for unhandled room %r", room_name)
        return
```

5. In `main()`, update the log line to: `"Starting voice-agent worker (playground + phone rooms)"`.

## Step 4: Verify

1. `backend\.venv\Scripts\python.exe -m pytest voice-agent\tests\test_rooms.py -q` → 4 passed
2. Whole offline suite: `backend\.venv\Scripts\python.exe -m pytest voice-agent\tests -q` → all green
3. Syntax check agent.py still imports offline-safe pieces: `backend\.venv\Scripts\python.exe -c "import ast; ast.parse(open(r'voice-agent/agent.py', encoding='utf-8').read())"` → exit 0

## Step 5: Report

Full report to `.superpowers/sdd/t4-report.md`. Return ONLY status / files / one-line results / concerns.

## Global Constraints

PowerShell 5.1 · NO git commands · touch ONLY the three listed files · do NOT modify app/pipeline.py.
