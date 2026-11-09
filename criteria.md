# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
4 of 5 and not 5 of 5 because my search is just keyword matching. If someone
types "band tee" and the listing says "graphic tee", it can miss. The model can
also have a bad moment. One miss in five feels fair for that.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
5 of 5 because this path never calls the model. It's one if-statement on an
empty list, so there's nothing random in it. If it fails once, that's a real
bug and not bad luck.

---

## 3. Something about state

The item the search picked is the same item the outfit step gets. In 5 of 5
tries on a matching query, the item id in the session matches the item id that
was passed to suggest_outfit, and the fit card mentions that item's price.

**Why this target:**
5 of 5 because this is just passing a value along, no model or luck involved.
If the id ever differs, the state is broken. I check the price in the caption
too since that's something I can see with my own eyes.

---

## 4. Something about the fit card

A fit card is 2 to 4 sentences and mentions the item's price and platform. In
at least 4 of 5 tries on the same item, it does both.

**Why this target:**
4 of 5 because the model sometimes forgets a detail or writes a long one. The
words will be different each time and that's fine, so I only check the stuff I
asked for. 5 of 5 would be too much to ask from a model.

---

## 5. Your choice

With an empty wardrobe, the agent still returns an outfit suggestion and a fit
card instead of crashing or giving a blank, in 4 of 5 tries.

**Why this target:**
I picked this one because an empty wardrobe is what a new user would have on
day one. 4 of 5 since it calls the model twice, so there are two chances for a
bad answer.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
