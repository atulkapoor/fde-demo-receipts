"""The one place this project talks to a language model.

Configuration is environment, not code:

- LLM_ENDPOINT   an OpenAI-compatible server on this machine or network
                 (vLLM, Ollama) -- the first-class path, because it works
                 inside a boundary.
- LLM_MODEL      model name for that endpoint (or the hosted default).
- ANTHROPIC_API_KEY  the hosted path -- refused outright when this build
                 carries a boundary, because a brief that may not leave
                 does not get to leave via the judge.
"""

from __future__ import annotations

import json
import os
import urllib.request

# Every answer this project asks for is a short one -- this pipeline asks for
# a single option number. The cap is not tidiness: left unbounded, a small
# local model decodes until it hits its context window, which on the
# engagement's own hardware is two minutes of a person waiting against a 30s
# budget. Bounded here, in the one place that talks to the model, so the
# breach becomes a reply that fails its shape check rather than a hung call.
MAX_ANSWER_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "256"))

# Reasoning is off by default, and the reason is measured rather than
# stylistic. The questions this project asks are closed -- "which of these
# eight lines is the shop's address" -- so a reasoning trace buys no accuracy,
# and on a reasoning model it is charged against the same token budget as the
# answer: the local model left to think spent its whole budget thinking and
# returned empty content, which is indistinguishable downstream from a model
# that declined. Set LLM_REASONING to an effort level where a build's
# questions are genuinely open.
REASONING_EFFORT = os.environ.get("LLM_REASONING", "none")


class ModelUnconfigured(RuntimeError):
    """No model is reachable; nothing here guesses instead."""


def _boundary_present() -> bool:
    try:
        import app.boundary  # noqa: F401
    except ImportError:
        return False
    return True


def complete(prompt: str, timeout: float = 120.0) -> str:
    endpoint = os.environ.get("LLM_ENDPOINT")
    if endpoint:
        body = json.dumps({
            "model": os.environ.get("LLM_MODEL", "default"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": MAX_ANSWER_TOKENS,
            # Named the two ways the local servers spell it; a server that
            # knows neither ignores both, which is the same as today.
            "reasoning_effort": REASONING_EFFORT,
            "chat_template_kwargs": {
                "enable_thinking": REASONING_EFFORT != "none",
            },
        }).encode()
        request = urllib.request.Request(
            endpoint.rstrip("/") + "/v1/chat/completions",
            data=body, headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)["choices"][0]["message"]["content"]

    if os.environ.get("ANTHROPIC_API_KEY"):
        if _boundary_present():
            raise ModelUnconfigured(
                "this build carries a data boundary, so the hosted model is "
                "refused -- point LLM_ENDPOINT at a model inside it"
            )
        import anthropic

        response = anthropic.Anthropic().messages.create(
            model=os.environ.get("LLM_MODEL", "claude-haiku-4-5-20251001"),
            max_tokens=MAX_ANSWER_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in response.content if b.type == "text")

    raise ModelUnconfigured(
        "no model is configured -- set LLM_ENDPOINT to an OpenAI-compatible "
        "local server (vLLM or Ollama), or ANTHROPIC_API_KEY where the "
        "boundary allows it"
    )
