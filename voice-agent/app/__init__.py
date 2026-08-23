"""Voice agent runtime package (LiveKit Agents worker).

Modules:
- config: environment-driven settings (no secrets in code).
- backend_client: HTTP client for the FastAPI backend's internal service API.
- prompting: pure system-prompt rendering (offline unit-testable).
- extraction_tools: extraction bookkeeping + framework-agnostic tool logic.
- pipeline: cascaded STT -> LLM -> TTS AgentSession wiring (requires livekit).
"""
