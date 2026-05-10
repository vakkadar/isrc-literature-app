---
name: cursor-usage
description: >-
  Where to see Cursor plan usage, limits, and rate limiting; session opener for
  the human; habits to save work and plan before throttling. Use at the start
  of every Cursor Agent (or Chat) session, when the user asks about billing,
  quotas, being throttled, fear of being cut off mid-work, or “where am I on
  usage?”. Claude Code equivalent: same ritual at session start—this skill is
  Cursor-side.
---

# Cursor usage and limits

## When to apply

- **Start of a new Cursor Agent / Chat thread** (first assistant message in that thread).
- When the user asks about **usage, limits, rate limits, billing, Pro, “running out”**, **being cut off**, **when to save**, or **“where am I?”** / **how much is left** (quota).

## Limitations (tell the user honestly)

- **Live numbers** (remaining fast/premium requests, reset dates, exact caps) are **not** available in the repo, terminal, or to tools. Only **Cursor’s app** and your **signed-in account on the web** are authoritative.
- You **cannot** state their exact remaining quota or the precise minute they will be limited.
- If they ask **“where am I?”** / **“how much do I have left?”** from **chat** — say clearly: **this chat cannot read their Cursor account**; they must open **Cursor Settings → Usage / Account** (or the signed-in **cursor.com** account area) for real figures. Do **not** invent or estimate usage numbers.

## User visibility block (first message in a new thread)

On the **first assistant message** in a thread where **no prior assistant messages** appear in context, **start your reply** with a short block **for the human** (plain text at the top). **Keep it compact** — about **five short lines** total (merge bullets if needed) unless they ask for more.

Include:

1. **Check usage:** Open **Cursor Settings** (not VS Code settings) — **Linux/Windows:** `Ctrl+Shift+J` — **macOS:** `Cmd+Shift+J` — then **Account**, **Subscription**, **Usage**, or **Billing** (labels vary by version).
2. **Web:** Signed in at [https://cursor.com](https://cursor.com) → **Settings / Account / Billing** (exact menu names may change).
3. **When limited:** Expect **throttling**, **non-premium / slower** paths, or **upgrade prompts**; details depend on **plan and app version**—trust the in-app or web usage screen.
4. **Stay safe:** Cursor does **not** warn this chat before limits hit — **save all**, **commit to git** at natural stops, and **check Usage before** a long Agent run.

If this thread **already has** earlier assistant messages, **do not** repeat this block unless the user asks about usage, billing, limits, or **continuity / saving work**.

## If they ask for exact numbers

Say you **don’t have account access**; they must read **Cursor Settings** or the **web account** page for current counts and reset dates.

Same answer if they ask from chat **“where am I on usage?”** — **no numbers from here**; only the app or website shows the truth.

## Continuity — save work and plan around limits

The product usually gives **no reliable in-chat countdown** before throttling or downgrade. What survives is **files on disk** and **git history**; long threads and half-finished plans in chat are the fragile part.

**Habits for the human:**

1. **Before a long Agent session** — open **Usage** in Cursor Settings; if you are already tight on quota, **shrink the ask** (one deliverable, one PR-sized slice) instead of a mega task.
2. **During work** — **save often**; use **Save All** before breaks; **commit** at sensible checkpoints (green tests, one feature, one bugfix) so “cut off” only pauses you—it does not orphan code.
3. **Chunking** — prefer **sequential** agent goals (“do A, then we’ll do B”) over one enormous prompt when usage is uncertain.
4. **Handoff line** — before you step away or Usage looks low, drop **one line** in chat or a small note in the repo: *current goal + next step* so a **new thread** can resume.

**If they say Cursor cut them off before:**

- Empathize briefly; stress **git + saved files** as the real backup.
- Point them to **Usage** for planning; suggest **smaller agent tasks** and **commits per slice** next time.

## Copies on this machine

- **Per project:** `.cursor/skills/cursor-usage/SKILL.md` at the repo root (versioned with the project).
- **All projects on this PC:** `~/.cursor/skills/cursor-usage/SKILL.md`.

Keep both files in sync when you edit the workflow.
