# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

You type what you're looking for, like "vintage graphic tee under $30, size M". FitFindr searches a set of thrift listings, picks the best match, figures out how it would go with stuff in your closet, and writes a caption you could post. If nothing matches, it stops and tells you what to change instead of making something up.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** digs through the listings for stuff that fits what you typed, under your price and in your size, with the closest match first. No model involved.
- **Inputs:** `description` (str, like "vintage graphic tee"), `size` (str, or None if you don't care), `max_price` (float, or None, and the price itself is allowed)
- **Returns:** a list of listing dicts, each with the usual stuff: title, price, size, platform, condition, colors, style tags and so on. Brand is often None, that's normal. Ranked by how many of your words show up, and capped at a handful.
- **When it has nothing:** an empty list. Not None, not an error. The loop relies on that.
- **Sizes:** I'm matching whole pieces of the size, not letters. "M" should find "S/M" and "M/L", but "L" shouldn't grab "XL" and "S" shouldn't grab "US 9".

### `suggest_outfit`

- **What it does:** asks the model for an outfit or two built around the thrifted piece, using things you already own.
- **Inputs:** `new_item` (dict, the listing), `wardrobe` (dict with an `items` list)
- **Returns:** a string with the outfit ideas, never blank. If you have a wardrobe it should name your actual pieces.
- **When it has nothing:** if the wardrobe is empty it still answers, just with general styling tips for the item instead of specific combos.

### `create_fit_card`

- **What it does:** writes a short caption you could actually post about the find.
- **Inputs:** `outfit` (str, the suggestion from the last step), `new_item` (dict, the listing)
- **Returns:** a string, 2 to 4 sentences, that mentions the item, the price and the platform once each. Should sound different from run to run.
- **When it has nothing:** if the outfit is blank, it skips the model and just returns a short message saying there's no outfit to write about.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If the search comes back empty, stop right there. Put a message in the session that tells the user what to try (a higher price, no size, fewer words), and don't run the outfit or caption steps. Otherwise take the first result, save it as the selected item, and move on to the outfit step.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** regex. One pattern grabs a price ("under $30", "below 40", "$30") and one grabs a size ("size M", "size W30"). Whatever is left over is the description. It only catches sizes that come after the word "size".

**What moves through the session:** the query goes in first, then the parsed bits, then the search results. The first result becomes the selected item, which goes into the outfit step, and the outfit goes into the fit card. Each step reads its input back out of the session, and I also save the id of the item the outfit step got, so I can check it's the same one the search picked.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(x['title'], x['price']) for x in search_listings('graphic tee', max_price=30)[:3]])"
[('Y2K Baby Tee — Butterfly Print', 18.0), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0), ('Mesh Long-Sleeve Top — Black', 15.0)]

$ python -c "from tools import search_listings; print(search_listings('designer ballgown', size='XXS', max_price=5))"
[]
```

```
$ python -c "from tools import suggest_outfit; ..."

```

```
$ python -c "from tools import create_fit_card; ..."

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I gave Claude my Tool Inventory spec and asked it to build the three tools.
- *What came back:* search_listings worked and returned an empty list on no match, like my spec said. But for "graphic tee under $30" it also returned a mesh top further down the list, because one matching word is enough to count.
- *What I changed:* nothing yet. The best match comes first and the loop only uses the first result, so I left it. I'd tighten it if the later results start to matter.

**Moment 2**

- *What I asked for:* I asked Claude to write the planning loop and a way to read the price and size out of the query.
- *What came back:* the loop worked, but for "a vintage graphic tee under $30, size M" the description came out as "a vintage graphic tee ," with a stray comma, which would have shown up in the error message.
- *What I changed:* I strip the leftover punctuation off the description. I found it by running a few queries through the parser before trusting it.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Same item reaches suggest_outfit, fit card has its price | 5 of 5 | PASS | PASS | FAIL | PASS | PASS | MISSED (4/5) |
| 4. Fit card is 2-4 sentences with price and platform | 4 of 5 | PASS | PASS | PASS | PASS | FAIL | MET (4/5) |
| 5. Empty wardrobe still gives outfit and fit card | 4 of 5 | PASS | PASS | PASS | PASS | FAIL | MET (4/5) |

Full output is in `results/run_2026-11-08_2343_before.md`.

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes | 4 of 5 | MET | 5 of 5 reached the fit card. |
| 2 | Impossible query stops early | 5 of 5 | MET | 5 of 5 stopped at the branch with a useful message. |
| 3 | Same item + price in card | 5 of 5 | MISSED | 4 of 5. Try 3 had no card. |
| 4 | Fit card format | 4 of 5 | MET | 4 of 5. Try 5 had no card. |
| 5 | Empty wardrobe | 4 of 5 | MET | 4 of 5. Try 5 got no outfit. |

**Diagnoses**

All 3 misses were the same thing: Gemini returned "503 UNAVAILABLE, high demand". That's one problem, not three.

- **Where:** the model. Criteria 3 and 4 failed in `create_fit_card`, criterion 5 in `suggest_outfit`.
- **Why:** the adapter doesn't retry a 503, so the run stopped. My handler worked (no crash), but it prints the raw error.
- **Criterion 3 was badly written.** The price-in-card part depends on the model, so an outage failed a state check. The state itself was fine, the same item went through every time (I matched by title, not id).
- **Criteria 4 and 5** only passed with one try of slack. A second outage would have missed both.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** the model adapter now waits and retries when Gemini says 503 "unavailable", the same way it already did for rate limits. If it still fails after all the attempts, it raises the same error my handler already catches, so it can't crash the run.

**Which failure it was meant to fix:** all 3 misses before were 503 outages, so this one change targets all of them.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Same item reaches suggest_outfit, fit card has its price | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card is 2-4 sentences with price and platform | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe still gives outfit and fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Full output is in `results/run_2026-11-09_1232_after.md`.

**Did it help, and how do I know:** yes. Criterion 3 went from MISSED (4/5) to MET (5/5), and criteria 4 and 5 went from 4/5 to 5/5. Every try finished, none stopped on an outage. The run used 41 model calls against 39 before, which fits one retry that got through.

One caveat: 503s come and go, so a single clean run doesn't prove the fix. Before, I got 3 outages in 20 model runs, and this time I got none that reached the user, but that's one sample. Criterion 3 is also still worded badly, it just got lucky.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
