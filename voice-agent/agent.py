"""LiveKit Agents worker entrypoint for the voice calling runtime.

Handles playground-* (browser) and phone-* (Twilio bridge) rooms.

Run locally:
    python agent.py dev        # dev worker against LIVEKIT_URL
    python agent.py start      # production mode
"""

from __future__ import annotations

import logging
import sys

from livekit import agents
from livekit.agents import JobContext, WorkerOptions, cli

from app.config import get_settings
from app.pipeline import run_session
from app.rooms import is_handled_room

logger = logging.getLogger("voice_agent")


async def entrypoint(ctx: JobContext) -> None:
    """Job callback: accept playground rooms, close anything else.

    Returning from this function ends the job for the room gracefully while
    the worker keeps serving other rooms.
    """
    room_name = ctx.room.name or ""
    if not is_handled_room(room_name):
        logger.info("Ignoring job for unhandled room %r", room_name)
        return

    settings = get_settings()
    for missing in settings.missing_required():
        logger.error("Missing required environment variable: %s", missing)

    await run_session(ctx, settings)


def main() -> None:
    """Configure logging and start the LiveKit worker."""
    # Bare `python agent.py` (docker compose, systemd) defaults to dev mode
    # instead of printing usage and exiting.
    if len(sys.argv) < 2:
        sys.argv = [sys.argv[0], "dev"]
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger.info("Starting voice-agent worker (playground + phone rooms)")
    agents.cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint)
    )


if __name__ == "__main__":
    main()
