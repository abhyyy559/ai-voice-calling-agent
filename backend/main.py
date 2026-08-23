"""Legacy entrypoint — kept as a thin re-export of the app factory.

``uvicorn main:app`` (older compose command) and ``uvicorn app.main:app``
(current) both work. The canonical application lives in ``app.main``.
"""
from app.main import app

__all__ = ["app"]
