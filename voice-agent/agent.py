"""LiveKit Agents worker entrypoint for the voice calling runtime.

Accepts agent jobs for rooms prefixed ``playground-`` (the web playground
this phase). Rooms with any other prefix are closed gracefully — the phone
path is dormant this phase and NO outbound calls of any kind are placed here.

Run locally:
    python agent.py dev        # dev worker against LIVEKIT_URL
    python agent.py start      # production mode
"""

from __future__ import annotations

import logging

from livekit import agents
from livekit.agents import JobContext, WorkerOptions, cli

from app.config import get_settings
from app.pipeline import PLAYGROUND_PREFIX, run_session

logger = logging.getLogger("voice_agent")


async def entrypoint(ctx: JobContext) -> None:
    """Job callback: accept playground rooms, close anything else.

    Returning from this function ends the job for the room gracefully while
    the worker keeps serving other rooms.
    """
    room_name = ctx.room.name or ""
    if not room_name.startswith(PLAYGROUND_PREFIX):
        logger.info(
            "Ignoring job for room %r - only %s* rooms are handled this phase",
            room_name,
            PLAYGROUND_PREFIX,
        )
        return

    settings = get_settings()
    for missing in settings.missing_required():
        logger.error("Missing required environment variable: %s", missing)

    await run_session(ctx, settings)


def main() -> None:
    """Configure logging and start the LiveKit worker."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger.info("Starting voice-agent worker (playground rooms only)")
    agents.cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint)
    )


if __name__ == "__main__":
    main()
