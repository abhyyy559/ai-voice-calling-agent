"""Temp introspection of livekit-agents 1.7.0 API surface (delete after use)."""
import inspect
import re

import livekit.agents as la
import livekit.agents.voice.events as eve

names = [n for n in dir(eve) if "Event" in n]
print("events:", names)

src = inspect.getsource(eve)
lits = re.findall(r'literal\["([a-z_]+)"\]', src)
lits2 = re.findall(r"literal\['([a-z_]+)'\]", src)
print("event names:", sorted(set(lits + lits2)))

print(
    "metric-ish attrs on AgentSession:",
    [m for m in dir(la.AgentSession) if "metric" in m.lower()],
)

from livekit.agents.metrics import EOUMetrics, LLMMetrics, TTSMetrics

for cls in (EOUMetrics, LLMMetrics, TTSMetrics):
    print(cls.__name__, [a for a in dir(cls) if not a.startswith("_")])

# Where is the metrics collector attached? Check session source.
sess_src = inspect.getsource(la.AgentSession)
hits = sorted(set(re.findall(r'"(metrics[a-z_]*)"', sess_src)))
print("metrics literals in AgentSession source:", hits)
hits2 = sorted(set(re.findall(r'self\.(metrics\w*)', sess_src)))
print("self.metrics attrs:", hits2)

# rtc Room metadata / remote participants
from livekit import rtc

room_attrs = [m for m in dir(rtc.Room) if not m.startswith("_")]
print("Room attrs:", room_attrs)
