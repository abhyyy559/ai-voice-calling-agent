Use the qa-eval-agent to run (or, if no test calls exist yet, set up) the latency measurement harness against the current voice-agent build.

Report: median and P95 end-of-caller-speech-to-start-of-agent-speech latency, broken down by stage (STT first-partial, LLM first-token, TTS first-audio, network/orchestration overhead) if that breakdown is available in the logs.

Compare against the targets in PRD.md NFR-1 (median ≤900ms, P95 ≤1.5s) and state clearly whether the current build meets them. If it doesn't, identify which stage is the biggest contributor to the gap before proposing a fix, and say which agent (voice-pipeline-agent, most likely) should own the fix.
