"""Temp introspection round 2 (delete after use)."""
import livekit.agents.voice.events as eve

print("EventTypes:", eve.EventTypes)

from livekit.agents.metrics import EOUMetrics, LLMMetrics, TTSMetrics

for cls in (EOUMetrics, LLMMetrics, TTSMetrics):
    print(cls.__name__, list(cls.model_fields.keys()))

from livekit.agents import MetricsCollectedEvent
print("MetricsCollectedEvent fields:", list(MetricsCollectedEvent.model_fields.keys()))

# user_input_transcribed / conversation_item_added shapes
from livekit.agents import UserInputTranscribedEvent, ConversationItemAddedEvent
print("UserInputTranscribedEvent:", list(UserInputTranscribedEvent.model_fields.keys()))
print("ConversationItemAddedEvent:", list(ConversationItemAddedEvent.model_fields.keys()))
