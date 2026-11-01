import sys
import os
import asyncio

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# On Windows sandboxed environments where loopback socketpair hangs due to network isolation,
# mock the internal asyncio self-pipe so async routines run cleanly and reliably.
if sys.platform == "win32":
    try:
        import asyncio.proactor_events

        class DummySock:
            def setblocking(self, b): pass
            def fileno(self): return -1
            def close(self): pass
            def send(self, b): pass

        asyncio.proactor_events.BaseProactorEventLoop._make_self_pipe = (
            lambda self: setattr(self, "_ssock", DummySock())
            or setattr(self, "_csock", DummySock())
            or setattr(self, "_internal_fds", getattr(self, "_internal_fds", 0) + 1)
        )
        asyncio.proactor_events.BaseProactorEventLoop._loop_self_reading = lambda self, f=None: None
    except Exception:
        pass

