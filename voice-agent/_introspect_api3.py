"""Temp introspection round 3b (delete after use)."""
import livekit.api as lapi

cands = [n for n in dir(lapi) if "room" in n.lower()]
print("livekit.api room-ish:", cands)

import inspect
from livekit.api import LiveKitAPI

meths = [m for m in dir(LiveKitAPI) if "metadata" in m.lower() or ("room" in m.lower())]
print("LiveKitAPI room/metadata methods:", meths)
print(inspect.signature(LiveKitAPI.room_service.update_room_metadata))

from livekit.agents.metrics import EOUMetrics, LLMMetrics, TTSMetrics
print("EOU type default:", EOUMetrics.model_fields["type"].default)
print("LLM type default:", LLMMetrics.model_fields["type"].default)
print("TTS type default:", TTSMetrics.model_fields["type"].default)
