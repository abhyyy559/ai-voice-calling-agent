# P2 Exit Gates (must all record a result before P2 starts)

P2 = web-call concurrency/interruption tuning. Real calls to real numbers are
also gated on items 1-3 and 6.

| # | Gate | How to verify | Result | Date | Evidence |
|---|------|---------------|--------|------|----------|
| 1 | Agent speaks first, names real | Web test call; no `[...]` in speech/transcript | | | |
| 2 | Agent only responds to the caller | Web test call with background noise / second voice; count false turns | | | |
| 3 | Extraction persists + exports | Web test call → fields on Call Detail → Excel export has rows | | | |
| 4 | Latency measured, decision recorded | Fresh STT p50/p95 + E2E p50/p95 vs NFR-1 (900/1500 ms) | | | |
| 5 | No echo/replay | TTS→STT loopback check with current knobs | | | |
| 6 | Compliance | Disclosure-first, consent recorded, calling-hours enforced, DLT/DPDP sign-off | | | |
