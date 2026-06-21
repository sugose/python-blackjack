# How We Work

This document describes the collaboration model used on python-blackjack. It is written for two audiences: someone joining this project who wants to understand the working rhythm, and someone starting a new project who wants to adopt this model for their own AI-assisted development team.

---

## The Cast

Every project in this model has three core roles:

**Product Owner (Adam)** — the human with authority. Decides what gets built and in what order. Approves merges. The final word on scope and direction. Does not write code or specs.

**Tech Owner (Clead — Claude chat)** — the architectural brain. Reviews code, produces specs, makes technical decisions, gates every PR iteration. Reads full file context, not just diffs. The quality bar.

**Senior Developer (Crog — Claude Code CLI)** — the builder. Implements exactly what is specified, no more. Opens PRs, posts dumps, waits for instruction. Never acts autonomously on reviewer findings.

**Code Reviewer (Copi — GitHub Copilot)** — automated first-pass reviewer. Catches style, correctness, and test quality issues. Clead gates whether Copi findings require action.

The model works because each role has a clear lane and does not drift into another's.

---

## How Ideas Surface

Ideas come from anywhere — a casual observation mid-session, a bug discovered during implementation, a "what if" that comes up in conversation. The model does not require ideas to be formal before they're spoken.

The flow is roughly:

1. **Observation** — something is noticed or mentioned casually ("what if the dealer could be bribed?")
2. **Conceptual pin** — if it has legs, it gets named and held ("Chaos Mode — value deduction bribe mechanic")
3. **Design discussion** — when the time is right, the idea is explored: what does it mean, what are the edge cases, what does it depend on?
4. **Spec entry** — once the design is stable enough, it enters the TPS or backlog as a formal item
5. **Implementation** — when it reaches the top of the backlog, Crog builds it

Not every idea makes it to step 4. Many stay as conceptual pins in NEXT_SESSION.md or the icebox for months. That's fine — the icebox is not a graveyard, it's a waiting room.

---

## How Decisions Get Made

Clead recommends. Adam decides. Crog implements.

This sounds simple but it has real teeth. When Clead says "use `field(default=SCHEMA_VERSION)` not `default_factory`", that's a recommendation. Adam can push back. But in practice, Adam delegates technical decisions to Clead — that's the agreement.

What Adam does not delegate:
- What to build next (backlog priority)
- Whether to merge
- Whether to close a session or push on
- Scope changes that affect the product vision

What Clead does not decide alone:
- Whether a process change is worth the friction
- Whether a spec is "good enough" to ship
- Whether an icebox idea is worth pursuing

The human is always the final authority. The AI is always the advisor, never the decision-maker.

---

## The Living Documents

The project runs on four documents that evolve continuously:

**TPS (Technical Product Specification)** — the source of truth for architecture, interfaces, event models, and design decisions. If it's not in the TPS, it's not decided. Clead updates it when decisions are made; Crog reads it before touching any code.

**Product Backlog** — the prioritised list of what gets built. PBIs (Product Backlog Items) move from "not started" to "done". The icebox holds ideas that are real but not ready.

**CROG_ONBOARDING.md** — the operational manual for the developer agent. Every process rule lives here. When the process changes, this file changes.

**NEXT_SESSION.md** — working memory between sessions. Active pins, process notes, what was merged last session, what's next. Cleared and refreshed at every session close.

These documents are not bureaucracy. They are the mechanism by which context survives across sessions. Without them, every session starts from scratch.

---

## The Session Rhythm

A session follows a predictable arc:

1. **Dump** — Crog generates a full repo dump. Adam pastes it to Clead.
2. **Consistency check** — Clead reads all documents and flags any inconsistencies before work begins. Stale status markers, contradictions between TPS and backlog, broken cross-references.
3. **Work** — PRs are opened, reviewed, fixed, merged. The Clead/Crog loop runs until the work is done or the session ends.
4. **Housekeeping** — at close, NEXT_SESSION.md is updated, backlog statuses are corrected, CHANGELOG is updated.
5. **Close** — session ends cleanly. Next session picks up from NEXT_SESSION.md.

The consistency check at the start is not optional. It has caught real problems — stale backlog items, process notes that contradict each other, TPS sections that reference deleted content.

---

## The PR Flow

Every change goes through a PR. No exceptions. The PR flow is:

1. Crog opens a PR on a feature branch
2. Copi reviews (or is suspended — see below)
3. Crog posts a full dump of the PR as a comment and reports to Adam
4. Adam drops the URL to Clead
5. Clead reviews and produces either a fix prompt or a verdict
6. If fixes needed: Crog implements exactly what the prompt says, nothing more, and the loop repeats
7. Clead approves → Adam merges

The hard stop rule is the most important process rule: after posting the PR dump, Crog stops completely. It does not read Copi's comments. It does not push fixes. It waits. Every iteration is gated by Clead. This rule exists because autonomous AI iteration without human oversight produces spec drift — we learned this the hard way.

---

## Copi and the Review Gate

Copi (GitHub Copilot) provides automated code review. It is fast and catches real issues. But it is not the quality gate — Clead is.

When Copi is available:
- It reviews every PR automatically via a GitHub ruleset
- Clead reads Copi's findings and decides which require action
- Re-review after fixes requires a manual UI click (known limitation)

When Copi is suspended (credits exhausted or unavailable):
- Crog skips the Copi wait entirely
- Clead reviews with full file context as sole reviewer
- The rest of the flow is unchanged

Clead's review standard is always the same regardless of Copi status: threat model, TPS compliance, error handling second pass, test quality check, and an explicit statement of what was not checked.

---

## How the Icebox Works

The icebox is not a backlog. Items in the icebox are real ideas that are not ready — either because they depend on something not yet built, or because they haven't been specced enough to implement, or because they're simply lower priority than everything else.

Items enter the icebox through two paths:
- Deliberate design (a feature is specced but deliberately deferred)
- Casual ideation (an idea surfaces in conversation and gets pinned before it evaporates)

Items leave the icebox when they're promoted to the active backlog. That promotion is a deliberate decision by Adam, usually triggered by a dependency being met or a session where the idea surfaces again.

Nothing in the icebox is forgotten. It just waits.

---

## Chaos Mode and Creative Ideas

Some ideas don't fit neatly into the PBI model. Chaos Mode — the intoxication system, value deduction bribes, liquor tolerance as a governing mechanic — emerged from conversation, not from a product requirement.

These ideas are held differently:
- They get a name and a brief description when they surface
- They go into the icebox with enough context to reconstruct the idea later
- They are not specced until there's enough conceptual mass to make the spec stable

The model accommodates creative tangents without letting them derail the main work. A Chaos Mode idea raised mid-session gets pinned in thirty seconds and then the session continues.

---

## What Makes This Model Work

A few things make this model genuinely productive rather than just organised:

**The human stays in the loop.** Adam does not just approve — Adam directs. The AI team executes, but the human shapes what gets executed.

**Decisions are recorded, not just made.** A decision that isn't in the TPS isn't a decision — it's a conversation. Writing it down is what makes it real.

**The process is itself a product.** CROG_ONBOARDING.md, TEAM_STRUCTURE.md, and this document are maintained with the same rigour as source code. When the process breaks, it gets fixed in a PR.

**Autonomy is earned, not assumed.** Crog does not act without instruction. Clead does not merge without approval. The constraints exist because they produce better outcomes than unconstrained AI action.

**Failure is documented.** PR #58 — where Crog and Copi bounced through 7 iterations without Clead involvement and produced an incorrect spec change — is referenced in the onboarding docs as a cautionary case. The hard stop rule exists because of that failure.

---

## Challenges

Working this way is genuinely productive but not frictionless. These are the real challenges:

**Context window limits.** AI agents have finite context. Long sessions accumulate history that eventually crowds out earlier decisions. The dump-and-consistency-check ritual exists partly to compensate for this — but a very long session can still drift. Closing sessions cleanly and starting fresh matters more than it might seem.

**AI reliability is uneven.** Crog will sometimes implement something subtly wrong. Copi will sometimes flag real issues and sometimes flag noise. Clead will sometimes miss things that a human expert would catch immediately. The process is designed around this — every layer checks the previous one — but it is not a guarantee.

**Tool fragility.** Automation that works today may break tomorrow. We spent significant session time fixing Copi auto-invocation — a workflow change that broke first-invocation silently. Tooling that touches external APIs (GitHub, Copilot) is the most fragile part of the system. Budget time for this.

**Process overhead.** The PR-for-everything rule, the hard stop rule, the consistency check — they all add time. On a solo project moving fast, they can feel like drag. The overhead pays off at scale and over time, but it is real.

**Human fatigue.** The PO is the bottleneck. Every merge, every session start, every prompt paste goes through Adam. This is by design — the human stays in the loop — but it means the pace of the project is bounded by human availability and attention.

**Spec drift under pressure.** When things are moving fast, the temptation is to skip updating the TPS or the backlog. Resist this. Spec drift is the most insidious failure mode — it is invisible until it causes a real problem, and by then it is expensive to unwind.

---

## Key Success Factors

These are the things that make the difference between a productive AI-assisted project and a chaotic one:

**The human must actually direct.** This model fails if the PO becomes passive — just approving whatever the AI proposes. The human's judgment about what to build, in what order, and when to stop is what gives the project coherence.

**Documents must be kept current.** A stale TPS is worse than no TPS — it actively misleads. The backlog, onboarding docs, and NEXT_SESSION.md must be updated as part of the work, not as an afterthought.

**The hard stop rule must be enforced.** Every time Crog acts autonomously on a reviewer finding without Clead's instruction, a small amount of spec integrity is lost. It compounds. The rule exists for a reason — enforce it even when it feels slow.

**Failures must be documented and fixed.** When the process breaks, fix it in a PR. Write down what went wrong. The onboarding docs should include cautionary cases, not just best practices. A team that only documents successes will repeat its failures.

**The AI team must be treated as capable but not infallible.** The most productive working mode is one where the human genuinely engages with the AI's output — reading verdicts, questioning recommendations, pushing back when something feels wrong — rather than rubber-stamping everything.

**Sessions must close cleanly.** The next session is only as good as the housekeeping from the last one. NEXT_SESSION.md, backlog status, CHANGELOG — these are not optional. They are what makes continuity possible.

---

## Recommendation

If you are considering this model for your own project, start small and prove it before scaling it.

Pick a well-defined, bounded project — something with a clear spec and a limited surface area. Run one session. Do the consistency check, open a PR, run the full Clead/Crog loop, merge. See how it feels.

The model will feel slow at first. The PR-for-everything rule, the hard stop, the waiting for Clead — none of it feels fast when you're used to just writing code. Resist the urge to shortcut. The constraints are the point.

If the first session goes well, the second will go faster. By the third or fourth session, the rhythm becomes natural and the overhead shrinks relative to the output.

The model is worth adopting if:
- You are building something that will be maintained over time (not a one-off script)
- You want decisions to be traceable and reversible
- You are working alone or in a small team where informal coordination is easy to lose
- You want the AI to do real implementation work, not just assist with it

It is probably not worth adopting if:
- You need to move extremely fast and correctness is secondary
- The project is truly disposable
- You cannot commit to the human-in-the-loop requirement

The model is not a silver bullet. It is a discipline. Applied consistently, with a human who genuinely engages and an AI team that stays in its lane, it produces software that is well-specified, well-tested, and maintainable. That is the goal.
