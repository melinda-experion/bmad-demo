---
title: Support Ticket Triage
approval_status: approved
created: 2026-08-14
updated: 2026-08-14
confidence: 68
confidence_label: Medium
confidence_rationale: Fast-path run with 3 unresolved [ASSUMPTION] tags (Problem section is illustrative/unresearched by design; the reusable-harness framing is inferred); however scope, persona-realism, success-criteria priority, and the project-naming decision were explicitly confirmed via direct Q&A rather than guessed, and both structure and prose review passes came back clean.
version: 1
---

# Product Brief: Support Ticket Triage

## Executive Summary

Support Ticket Triage is a single-screen micro app: a user pastes raw customer
support ticket text into one field and submits it; an LLM call returns a
category (bug / billing / feature-request / question), a priority (low /
medium / high), a one-sentence summary, and a draft first-response the agent
can copy and send. No accounts, no queue, no persistence — one input, one
LLM call, one result, gone when the tab closes.

**Demo Context [ASSUMPTION carried from user intent, not inferred]:** this
product is the vehicle, not the point. It exists to demonstrate an
AI-governed SDLC — brief → PRD → architecture → epics/stories → sprint →
plan-gated dev → confidence-scored code → fresh-session review — ending in
real, working code generated from a generated PRD, for a customer audience.
It shares its architectural shape (Node core `http`, vanilla JS client, no
framework, no persistence) with a prior demo run in this same repo, so the
governance chain can be shown fresh without re-deriving the shape from
scratch.

Honestly, nothing differentiates this as a product — the real
differentiation is one layer up, in the governance chain that builds it,
not in the app itself. [ASSUMPTION] That also sets where this repo is
headed: a reusable demo harness where the specific product idea can be
swapped for a future demo without changing the chain underneath it.

## The Problem

[ASSUMPTION — demo-persona framing, not researched against a real support
team] Support agents triaging inbound tickets manually read each one,
decide what kind of issue it is, judge how urgent it is, and draft a first
reply — repeatedly, for every ticket, with no consistency check across
agents or across a single agent's day. The cost is time (context-switching
per ticket) and inconsistency (two agents categorize or prioritize the same
kind of ticket differently). This is illustrative of a real, common support
pain — it is not validated against an actual support team's workflow, and
the brief does not claim it is.

## The Solution

Paste ticket text → get triage back: category, priority, one-line summary,
draft reply. The agent reads the result, edits the draft if needed, and
sends it through whatever real channel they already use — this app does not
integrate with a ticketing system, it produces a decision and a draft an
agent can act on elsewhere.

## Who This Serves

**Primary (in-app, illustrative):** a generic customer-support agent
persona — demo-only, not modeled on a specific real team or researched
against actual support workflows. Success for this persona: paste a ticket,
get a usable triage in seconds, spend less time deciding what a ticket is
before acting on it.

**Primary (actual audience):** the customer watching the demo. Success here
means seeing the governed pipeline — approval gates, the plan-first hard
gate, confidence scoring, fresh-session review — run against a real feature
and produce real code, not judging the triage tool itself.

## Success Criteria

Two separate yardsticks, kept explicit rather than blended:

**Demo-process success** (what actually matters here):
- Brief → PRD → architecture → epics/stories → sprint → story chain runs
  without a gate being silently skippable.
- The plan-first hard gate refuses a bare "yes"/"looks good" and requires
  the exact approval phrase before code generation starts.
- Every generated file gets a deterministic, tool-measured confidence score
  (not a model self-assessment) logged to the audit CSV.
- Code review runs in a fresh session and performs diff-to-plan
  reconciliation, catching any file touched outside the approved plan.

**Product-fiction success** (illustrative only, not measured against real
users):
- Triage categorization is plausible for the four listed categories on
  reasonably clear ticket text.
- The draft reply is usable with light editing, not a non-sequitur.

## Scope

**In for v1:**
- One screen: a text area for raw ticket content, a submit action, a result
  area showing category, priority, summary, and draft reply.
- One API call per submission; no caching, no memoization — every submit is
  a fresh LLM call.
- Session-only state; nothing persists past a page reload.

**Explicitly out for v1:**
- Any real support-tool integration (Zendesk, Intercom, email, etc.).
- User accounts, auth, or multi-tenant anything.
- A saved/favorited-triage step — considered and deferred, not rejected;
  see `addendum.md` for the rationale and why it may return as a second
  epic later.
- Multi-turn conversation or follow-up questions on a single ticket.
