import os
"""Shared rate-limiter singleton.

Defined in its own module so that route files can import the limiter
without triggering a circular import through ``app.main``.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Security: Rate limiting prevents API key exhaustion from automated abuse on
# the free Gemini tier. storage_uri=os.getenv("REDIS_URL", "memory://") uses an in-process store;
# for multi-worker deployments replace this with a Redis URI.
limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv("REDIS_URL", "memory://"))

