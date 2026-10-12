#!/usr/bin/env python3
"""Test Home Assistant custom sentences offline, the way Assist matches them.

Loads Home Assistant's built-in sentences for a language, merges every file in
homeassistant/custom_sentences/<lang>/ on top (marked as custom, so they win
over built-in matches exactly as in Home Assistant's default agent), and checks
each test phrase against the intent and slots it should produce.

    pip install hassil home-assistant-intents pyyaml
    python scripts/test_sentences.py it homeassistant/tests/it/timers.txt
    python scripts/test_sentences.py it homeassistant/tests/it/timers.txt --builtin-only

Test file lines:  <phrase> => <Intent> [slot=value ...]   (use _ for spaces)
                  <phrase> => none                         (must not match)
Lines starting with # are comments. Exit code 1 if any phrase fails.

Entities and areas are faked (see SLOT_LISTS), so built-in sentences that need
real devices may not match here; the timer and status sentences do not.
"""
import argparse
import sys
from pathlib import Path

import yaml
from hassil import Intents, recognize_best
from hassil.intents import TextSlotList
from hassil.util import merge_dict
from home_assistant_intents import get_intents

ROOT = Path(__file__).resolve().parent.parent
# Home Assistant marks custom sentences with this metadata key and prefers them.
CUSTOM_KEY = "hass_custom_sentence"


def text_list(*values: str) -> TextSlotList:
    return TextSlotList.from_tuples([(v, v) for v in values])


SLOT_LISTS = {
    "name": text_list("luce cucina", "tapparella", "televisione"),
    "area": text_list("cucina", "soggiorno", "camera"),
    "floor": text_list("piano terra"),
}


def load(lang: str, builtin_only: bool) -> tuple[Intents, list[str]]:
    data = get_intents(lang)
    if data is None:
        sys.exit(f"No built-in sentences for language '{lang}'")
    if not builtin_only:
        for path in sorted((ROOT / "homeassistant" / "custom_sentences" / lang).glob("*.yaml")):
            custom = yaml.safe_load(path.read_text(encoding="utf-8"))
            for intent in custom.get("intents", {}).values():
                for block in intent.get("data", []):
                    block.setdefault("metadata", {})[CUSTOM_KEY] = True
            merge_dict(data, custom)
    return Intents.from_dict(data), data.get("skip_words", [])


def same(got, want: str) -> bool:
    try:
        return float(got) == float(want)
    except (TypeError, ValueError):
        return str(got) == want


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("lang")
    parser.add_argument("tests", type=Path)
    parser.add_argument("--builtin-only", action="store_true", help="ignore the custom sentences")
    parser.add_argument("-v", "--verbose", action="store_true", help="print passing phrases too")
    args = parser.parse_args()

    intents, skip_words = load(args.lang, args.builtin_only)
    passed = failed = 0
    for line in args.tests.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        phrase, _, expected = line.partition("=>")
        phrase, expected = phrase.strip(), expected.split()

        result = recognize_best(
            phrase,
            intents,
            slot_lists=SLOT_LISTS,
            skip_words=skip_words,
            language=args.lang,
            best_metadata_key=CUSTOM_KEY,
            best_slot_name="name",
        )
        got_intent = result.intent.name if result else "none"
        got_slots = {k: e.value for k, e in result.entities.items()} if result else {}
        custom = bool(result and result.intent_metadata and result.intent_metadata.get(CUSTOM_KEY))

        ok = bool(expected) and expected[0] == got_intent
        for pair in expected[1:]:
            slot, _, value = pair.partition("=")
            ok = ok and same(got_slots.get(slot), value.replace("_", " "))

        passed += ok
        failed += not ok
        if not ok or args.verbose:
            tag = "ok  " if ok else "FAIL"
            print(f"{tag} {phrase!r} -> {got_intent} {got_slots}{' [custom]' if custom else ''}"
                  + ("" if ok else f"   expected: {' '.join(expected)}"))

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
