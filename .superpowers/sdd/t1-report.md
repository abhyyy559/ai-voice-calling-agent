# Task 1 Report: g711 codec module

**Status:** DONE (with deviations — see Concerns)

## Files changed
- Created `backend/tests/test_g711.py` (verbatim from brief)
- Created `backend/app/services/g711.py` (from brief + 2 bug fixes, see Concerns)
- Environment only: installed `audioop-lts==0.2.2` into `backend\.venv` via uv (see Concerns)

## TDD evidence

### Step 2 — failing run (before implementation)

Command (workdir `backend`): `.venv\Scripts\python.exe -m pytest tests\test_g711.py -q`

```
=================================== ERRORS ====================================
_____________________ ERROR collecting tests/test_g711.py _____________________
ImportError while importing test module 'C:\Users\home\OneDrive\Documents\work\projects\ai voice calling agent\backend\tests\test_g711.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\home\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_g711.py:2: in <module>
    from app.services.g711 import downsample_pcm16, pcm16_to_ulaw, ulaw_to_pcm16
E   ModuleNotFoundError: No module named 'app.services.g711'
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\home\OneDrive\Documents\work\projects\ai voice calling agent\backend\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
ERROR tests/test_g711.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 warning, 1 error in 1.15s
```

Expected failure confirmed (`No module named 'app.services.g711'`).

Note discovered here: venv is **Python 3.13.5**, where stdlib `audioop` was removed (PEP 594). Installed `audioop-lts==0.2.2` (official maintained backport of the same C module) so the brief's `import audioop` works unmodified.

### Intermediate — first run after verbatim brief implementation (3 failed)

The brief's reference code fails its own tests:

```
FAILED tests/test_g711.py::test_roundtrip_silence - TypeError: lin2ulaw expected 2 arguments, got 1
FAILED tests/test_g711.py::test_roundtrip_tone_lengths - TypeError: lin2ulaw expected 2 arguments, got 1
FAILED tests/test_g711.py::test_downsample_factor6 - AssertionError: assert 342 == ((2048 // 6) * 2)   [342 vs 682]
3 failed, 1 passed
```

- `audioop.lin2ulaw(data)` raises `TypeError` on every CPython/audioop-lts version — the width argument has always been mandatory (`audioop.lin2ulaw(fragment, width)`).
- Downsample stride `2 * factor` yields 342 bytes; the test contract requires `(len(data) // factor) * 2` = 682 bytes for the given input.

Fixes applied (public names/signatures/semantics per tests unchanged):
1. `pcm16_to_ulaw`: `audioop.lin2ulaw(data)` → `audioop.lin2ulaw(data, 2)` (width=2, matches docstring).
2. `downsample_pcm16`: stride `factor` over `range(0, len(data) - factor + 1, factor)` → output length is exactly `(len(data) // factor) * 2`. Docstring updated to describe actual behavior (one 2-byte sample kept per `factor`-byte chunk).
3. No change needed for `import audioop` once `audioop-lts` is present in the venv.

### Step 4 — passing run (final)

Command (workdir `backend`): `.venv\Scripts\python.exe -m pytest tests\test_g711.py -q`

```
....                                                                     [100%]
============================== warnings summary ==============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\home\OneDrive\Documents\work\projects\ai voice calling agent\backend\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
4 passed, 1 warning in 0.03s
```

## Concerns
1. **Dependency not recorded:** `audioop-lts==0.2.2` is installed in `backend\.venv` but NOT added to `backend/requirements.txt` (task forbids touching a third file). A fresh environment rebuild will fail on `import audioop` until someone adds `audioop-lts>=0.2 ; python_version >= "3.13"` (or equivalent) to requirements.
2. **Venv is Python 3.13.5**, not Python 3.12 as stated in the task header. The audioop removal is why the backport is required at all.
3. **Brief's reference code was buggy:** it could not pass its own Step 4 even on genuine Python 3.12 stdlib audioop (missing `lin2ulaw` width arg; wrong downsample stride). Deviations above are minimal and preserve the specified interfaces that later tasks import.
4. **Downsample semantics note:** the test-defined behavior decimates by *bytes* (keeps one sample per `factor` bytes ≈ every 3rd sample at factor 6), not every 6th *sample* as the original docstring claimed. Flagging in case later bridge tasks assume true 6:1 sample decimation (48k→8k); if so, stride should be `2*factor` AND the test updated.
