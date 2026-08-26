# Task 4 Report: worker accepts phone-* rooms

**Status: DONE_WITH_CONCERNS** — implemented per brief, all verifications pass; one pre-existing environment gap means the brief's Step 4.2 ("whole suite green under backend venv") is literally unachievable in this repo and was verified via a documented split instead (see Verification + Concerns).

## Files changed
1. `voice-agent/app/rooms.py` — NEW. `HANDLED_PREFIXES = ("playground-", "phone-")` and `is_handled_room(name)` exactly as specified in the brief (livekit-import-free).
2. `voice-agent/tests/test_rooms.py` — NEW. 4 tests verbatim from the brief.
3. `voice-agent/agent.py` — the 5 brief edits only: dormancy docstring line → "Handles playground-* (browser) and phone-* (Twilio bridge) rooms."; import line now `from app.pipeline import run_session`; added `from app.rooms import is_handled_room`; entrypoint filter replaced with `is_handled_room(room_name)` + `"Ignoring job for unhandled room %r"` log; `main()` log → "Starting voice-agent worker (playground + phone rooms)". `app/pipeline.py` untouched.

## TDD sequence (actual outputs)

Step 2 FAIL (before implementation):
```
> backend\.venv\Scripts\python.exe -m pytest voice-agent\tests\test_rooms.py -q
E   ModuleNotFoundError: No module named 'app.rooms'
1 error in 3.56s
```
Step 4 PASS:
```
> backend\.venv\Scripts\python.exe -m pytest voice-agent\tests\test_rooms.py -q
....  [100%]  4 passed in 0.24s
```

## Verification

```
1. test_rooms.py under backend venv            -> 4 passed in 0.24s

2a. Whole offline suite, backend venv,
    --ignore=tests/test_stt_latency.py         -> 36 passed in 1.93s

2b. WHOLE suite incl. test_stt_latency.py,
    voice-agent\.venv (has livekit-agents)     -> 38 passed in 98.07s

3. backend venv ast.parse of voice-agent/agent.py -> exit 0
```

### Why 2 was split (pre-existing, not caused by this task)
Brief Step 4.2 expects `backend\.venv ... pytest voice-agent\tests -q` all green, but `voice-agent/tests/test_stt_latency.py:15` does a module-level `import app.pipeline`, and `app/pipeline.py:29` does `from livekit.agents import ...`. The backend venv has **no livekit-agents** — only a namespace `livekit/` dir from `livekit-api` (confirmed: `import livekit` → `__path__ = backend\.venv\Lib\site-packages\livekit`, then `ModuleNotFoundError: No module named 'livekit.agents'`). This matches Task 3's report ("Backend venv has no livekit rtc package; livekit-agents lives in voice-agent\.venv"). The failing import chain involves none of my three files (`pipeline.py` untouched; `rooms.py` imports nothing; tests never import `agent.py`), so the collection error pre-exists this change. 2b proves the complete suite (including stt-latency) is green where its dependencies exist; 2a proves everything offline-safe is green under the mandated backend venv.

## Concerns (for orchestrator)
1. **Pre-existing:** `voice-agent/tests/test_stt_latency.py` can never collect under the backend venv until either `livekit-agents` is installed there or that test gets an import-skip guard. Out of my 3-file scope; did not touch it.
2. Brief's Step 4.2 wording should be amended for future voice-agent tasks to name which venv is expected per suite, or accept the split-verification pattern used here.
3. None of my own making: no deviations from brief code; all four agent.py edits applied verbatim; pipeline.py untouched; no git commands used.
