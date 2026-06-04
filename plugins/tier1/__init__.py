"""
Tier 1 command plugin.

Registers a pre_gateway_dispatch hook that intercepts '!' commands and
executes them directly via tier1_commands.handle(), bypassing the LLM.

Returns {"action": "skip"} so the gateway drops the message without a
model call. Anything not starting with '!' falls through to normal dispatch.
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Make tier1_commands importable
HOOKS_DIR = str(Path.home() / ".hermes" / "hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)


def _pre_gateway_dispatch(event=None, gateway=None, session_store=None, **kwargs):
    """Intercept '!' commands and handle them directly."""
    if event is None:
        return None
    text = getattr(event, "text", "") or ""
    if not text.strip().startswith("!"):
        return None
    try:
        from tier1_commands import handle as tier1_handle
        if tier1_handle(text):
            return {"action": "skip", "reason": "tier1"}
    except Exception as exc:
        logger.warning("tier1 plugin error: %s", exc)
        try:
            with open(Path.home() / ".hermes" / "logs" / "tier1_errors.log", "a") as f:
                import traceback
                f.write(f"tier1 plugin error: {exc}\ntext: {text}\n{traceback.format_exc()}\n\n")
        except Exception:
            pass
    return None


def register(ctx):
    """Plugin entrypoint — called by Hermes PluginManager at load time."""
    ctx.register_hook("pre_gateway_dispatch", _pre_gateway_dispatch)
    logger.info("tier1 plugin registered pre_gateway_dispatch hook")
