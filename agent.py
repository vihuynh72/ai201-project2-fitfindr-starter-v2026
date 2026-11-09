"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import suggest_outfit, create_fit_card
from mcp_client import call_tool, MCPError
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "outfit_item_id": None,      # id of the item suggest_outfit actually received
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)

    # Each pass looks at the session and does the next thing that's missing.
    count = 0
    try:
        while session["fit_card"] is None and not session["error"]:
            count += 1
            trace.check_iterations(count)

            if not session["parsed"]:
                session["parsed"] = _parse(session["query"])
                trace.step("parse query", inputs=session["query"], returned=session["parsed"])

            elif session["selected_item"] is None:
                p = session["parsed"]
                session["search_results"] = call_tool("search_listings", {
                    "description": p["description"],
                    "size": p["size"],
                    "max_price": p["max_price"],
                })
                trace.step("search_listings (via MCP)", inputs=p, returned=session["search_results"])
                if not session["search_results"]:
                    # the branch: nothing found, so stop here
                    session["error"] = _no_results_message(p)
                    trace.step("branch", note="search came back empty, stopping before suggest_outfit")
                else:
                    session["selected_item"] = session["search_results"][0]

            elif session["outfit_suggestion"] is None:
                item = session["selected_item"]
                session["outfit_item_id"] = item["id"]  # what actually went into the tool, for checking state
                session["outfit_suggestion"] = suggest_outfit(item, session["wardrobe"])
                trace.step("suggest_outfit", inputs=f"{item['title']} + {len(session['wardrobe'].get('items', []))} wardrobe items",
                           returned=session["outfit_suggestion"])

            else:
                session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])
                trace.step("create_fit_card", inputs=session["selected_item"], returned=session["fit_card"])

    except ModelUnavailable as exc:
        session["error"] = (f"I couldn't reach the model, so I can't write the outfit or the caption. {exc} "
                            f"Fix that, or wait a minute if you were going fast, then ask again.")
        trace.step("model unavailable", note="stopped")
    except MCPError as exc:
        session["error"] = (f"The search tool didn't respond, so I couldn't look for listings. {exc} "
                            f"Check that 'python mcp_server.py' starts on its own, then ask again.")
        trace.step("search server unavailable", note="stopped")

    return session


def _parse(query: str) -> dict:
    """Pull a price and a size out of the query with regex. Whatever is left is the description."""
    price = re.search(r"(?:under|below|\$)\s*\$?\s*(\d+(?:\.\d+)?)", query, re.I)
    size = re.search(r"\bsize\s+(xxs|xs|xxl|xl|s|m|l|[a-z]*\d+(?:\.\d+)?)\b", query, re.I)
    description = query
    for found in (price, size):
        if found:
            description = description.replace(found.group(0), " ")
    return {
        "description": " ".join(description.split()).strip(" ,.;"),
        "size": size.group(1) if size else None,
        "max_price": float(price.group(1)) if price else None,
    }


def _no_results_message(p: dict) -> str:
    asked = f"'{p['description']}'"
    if p["size"]:
        asked += f" in size {p['size']}"
    if p["max_price"] is not None:
        asked += f" under ${p['max_price']:.0f}"
    return (f"Nothing matched {asked}. Try a higher price, leave out the size, "
            f"or use fewer or simpler words (like 'tee' instead of 'graphic band tee').")


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
