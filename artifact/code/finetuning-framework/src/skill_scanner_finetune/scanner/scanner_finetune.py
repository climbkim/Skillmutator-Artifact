"""scanner_finetune.py -- fine-tuned scanner variant of the baseline scanner.

Differs from the baseline scanner in two places:

1. **System prompt injection.** The fine-tuned model was trained with a
   system+user chat layout that mentions the 4-Phase analysis schema. We
   prepend the same system message to every call.
2. **Forced Prefix Pre-filling.** We append an `assistant` turn whose content
   is exactly the canonical heading of the final phase
   (`## Phase 4: Category Mapping`), then turn on vLLM's
   `continue_final_message=True` extension so the server treats the assistant
   turn as a continuation rather than starting a new turn. The model is
   thereby forced to land at the categorical verdict stage instead of
   regenerating Phases 1-3 at inference time.

   This prefill is a vLLM extension; raw OpenAI ignores it. When the
   endpoint rejects the extension we fall back to a plain call (no prefill).

Usage:
    python -m skill_scanner_finetune.scanner.scanner_finetune \\
        -p openai -s skills/pdf -m /path/to/merged_model \\
        -u http://localhost:8000/v1 -o /tmp/out -t 12000

The Phase 4 heading must match the marker emitted by
`dataset_builder/formatter_v3.py`. Keep them in sync if the schema is changed.
"""

import argparse
import os
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

import scanner_base as base  # noqa: E402


# ----------------------------------------------------------------------
# System prompt for the fine-tuned model -- describes the 4-Phase schema
# (must match the prompt used during training; see formatter_v3.py).
# ----------------------------------------------------------------------
FT_SYSTEM_PROMPT = (
    "You are an expert AI agent security analyst specializing in LLM-powered agent skill security. "
    "Your task is to analyze agent skills -- composed of SKILL.md instruction documents and Python helper "
    "scripts -- and produce a structured 4-Phase security analysis. "
    "Reason step-by-step, cite specific file locations and code patterns as evidence, "
    "and distinguish what a skill claims to do versus what it actually does. "
    "Your final output must list security findings with attack categories."
)

# Canonical Forced Prefix Pre-filling heading. Must match the final phase
# marker emitted by dataset_builder/formatter_v3.py
# (## Phase 4: Category Mapping).
PHASE4_PREFIX = "## Phase 4: Category Mapping\n\n\n"

# Sampling used for the paper's fine-tuned-scanner scans: greedy decoding with
# frequency_penalty=0.3 (suppresses long repetition loops) and the Phase 4
# prefill. max_tokens=None leaves the completion length to the server (the
# 76-case benchmark scans); the ClawHub in-the-wild scans used max_tokens=2048.
# The CLI below overrides these values.
SAMPLING = {
    "prefill": PHASE4_PREFIX,     # None disables the prefill turn
    "temperature": 0.0,
    "frequency_penalty": 0.3,
    "max_tokens": None,           # completion-token cap
}


# ----------------------------------------------------------------------
# Monkey-patch the baseline scanner's _call_openai to use prefilling.
#
# Original signature:
#     _call_openai(client, model_name, prompt: str, use_reasoning) -> dict
#     -- internally builds messages = [{"role":"user","content":prompt}].
#
# New behavior:
#     1. messages = [system, user(prompt), assistant(PHASE4_PREFIX)]
#     2. enable vLLM continue_final_message via extra_body
#     3. prepend PHASE4_PREFIX to the response so the saved markdown still
#        carries the Phase 4 heading.
# ----------------------------------------------------------------------
def _call_openai_finetune(client, model_name: str, messages_or_prompt, use_reasoning: bool) -> dict:
    """Call the OpenAI-compatible API with vLLM assistant prefill enabled.

    Depending on the baseline scanner version `messages_or_prompt` may be:
    - str (older): the raw user prompt
    - list (newer): a [system, user] messages list
    """
    if isinstance(messages_or_prompt, list):
        # Newer scanner: extract the user message content from the list.
        user_content = ""
        for m in messages_or_prompt:
            if m.get("role") == "user":
                user_content = m.get("content", "")
                break
        prompt = user_content
    else:
        prompt = messages_or_prompt

    prefill = SAMPLING["prefill"]
    messages = [
        {"role": "system", "content": FT_SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]
    extra = {}
    if prefill:
        messages.append({"role": "assistant", "content": prefill})
        extra = {"continue_final_message": True, "add_generation_prompt": False}

    sampling = {"frequency_penalty": SAMPLING["frequency_penalty"]}
    if SAMPLING["max_tokens"]:
        sampling["max_tokens"] = SAMPLING["max_tokens"]

    def _create(msgs, body, **kw):
        return client.chat.completions.create(
            model=model_name, messages=msgs, **kw, **sampling,
            **({"extra_body": body} if body else {}),
        )

    try:
        if use_reasoning:
            response = _create(messages, extra, reasoning_effort="medium")
        else:
            response = _create(messages, extra, temperature=SAMPLING["temperature"])
    except Exception as e:
        err = str(e).lower()
        if "temperature" in err and "unsupported" in err:
            print(f"\n    [!] Model '{model_name}' does not support temperature; using default.")
            response = _create(messages, extra)
        elif prefill and ("extra_body" in err or "continue_final_message" in err or "unexpected keyword" in err):
            # Endpoint does not support assistant prefilling -- fall back
            # to a plain call without the prefill turn.
            print(f"\n    [!] Endpoint does not support assistant prefill; falling back without it.")
            prefill = None
            response = _create(messages[:-1], {}, temperature=SAMPLING["temperature"])
        else:
            raise

    usage = response.usage
    raw = response.choices[0].message.content or ""
    # Restore the prefix in the saved markdown so the final report carries
    # the canonical Phase 4 heading.
    content = (prefill or "") + raw
    return {
        "content":           content,
        "prompt_tokens":     usage.prompt_tokens if usage else 0,
        "completion_tokens": usage.completion_tokens if usage else 0,
        "total_tokens":      usage.total_tokens if usage else 0,
    }


# Replace the baseline _call_openai with the fine-tuned variant.
base._call_openai = _call_openai_finetune


# ----------------------------------------------------------------------
# CLI -- mirrors the baseline scanner.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agent Skill Vulnerability Scanner -- fine-tuned variant"
    )
    parser.add_argument("-s", "--skill", type=str)
    parser.add_argument("-p", "--provider", type=str, choices=base.SUPPORTED_PROVIDERS)
    parser.add_argument("-m", "--model", type=str)
    parser.add_argument("-r", "--reasoning", action="store_true")
    parser.add_argument("-o", "--output-dir", type=str, default=None)
    parser.add_argument("-u", "--base-url", type=str, default=None)
    parser.add_argument("-t", "--max-tokens", type=int, default=None,
                        help="Per-request INPUT token budget used to chunk large skills.")
    parser.add_argument("--prefill", type=str, default=PHASE4_PREFIX,
                        help="Assistant-turn prefix (Forced Prefix Pre-filling).")
    parser.add_argument("--no-prefill", action="store_true",
                        help="Disable the prefill turn.")
    parser.add_argument("--temperature", type=float, default=SAMPLING["temperature"])
    parser.add_argument("--frequency-penalty", type=float, default=SAMPLING["frequency_penalty"])
    parser.add_argument("--max-new-tokens", type=int, default=None,
                        help="Completion-token cap (default: none; 2048 for the ClawHub scans).")

    args = parser.parse_args()
    use_reasoning = args.reasoning
    SAMPLING.update(
        prefill=None if args.no_prefill else args.prefill,
        temperature=args.temperature,
        frequency_penalty=args.frequency_penalty,
        max_tokens=args.max_new_tokens,
    )

    provider = args.provider
    if not provider:
        print("-" * 50)
        print(f"[?] Choose an LLM provider: {base.SUPPORTED_PROVIDERS}")
        provider = input("    > ").strip().lower()
        if provider not in base.SUPPORTED_PROVIDERS:
            print(f"[error] Unsupported provider: {provider}")
            sys.exit(1)

    if args.model:
        model_name = args.model
    else:
        model_name = (base.DEFAULT_REASONING_MODELS[provider] if use_reasoning
                      else base.DEFAULT_MODELS[provider])

    skill_name = args.skill
    if not skill_name:
        print("-" * 50)
        skill_name = input("[?] Enter the agent-skill folder to analyze: ").strip()

    if os.path.isabs(skill_name) or (os.path.sep in skill_name) or ("/" in skill_name):
        target_directory = skill_name
        display_name = os.path.basename(skill_name.rstrip("/\\"))
    else:
        target_directory = os.path.join(os.getcwd(), "skills", skill_name)
        display_name = skill_name

    print("-" * 50)
    if not skill_name:
        print("[error] no folder name provided.")
    elif os.path.isdir(target_directory):
        client = base.create_client(provider, base_url=args.base_url)
        base.evaluate_agent_skills(
            client, provider, target_directory, display_name, model_name,
            use_reasoning, args.output_dir, max_input_tokens=args.max_tokens,
        )
    else:
        print(f"\n[error] Path not found: {target_directory}")
