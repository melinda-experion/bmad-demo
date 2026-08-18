---
title: Broker Book-of-Business View (Client Portfolio)
created: 2026-08-17
updated: 2026-08-17
approval_status: approved
confidence: 74
confidence_label: Medium
confidence_rationale: Executive Summary, Problem, Solution, Who This Serves, Scope, and Constraints are directly traceable to the user's detailed write-up. Success Criteria and Vision carry unresolved [ASSUMPTION] tags since no target metrics or forward vision were specified, and this was a Fast-path run with no back-and-forth to confirm them.
version: 1
---

# Product Brief: Broker Book-of-Business View (Client Portfolio)

## Executive Summary

Broker Native ("Sage") is an AI-native platform for employee-benefits insurance brokers. The Broker Book-of-Business View is the broker's daily home screen within the Broker Dashboard unit (B1) of the confirmed MVP: a single, sortable, filterable table of every active client the broker manages. Today that picture lives scattered across spreadsheets — client details, premiums, renewal dates, and funding types kept and reconciled by hand. This feature gives the broker one place to see the whole book at a glance and immediately spot which clients need attention, starting with renewals coming due. It is a pure visibility feature: no live data integration, no predictive logic, no PHI — just the seeded data a broker already has, organized so it's usable.

## The Problem

A broker managing dozens of employer clients has no single source of truth for the state of their book. Client name, carrier, premium, employee count, funding type, and renewal date each live in different rows of different spreadsheets, updated inconsistently. To answer a simple question — "which of my clients have a renewal coming up that I haven't touched yet?" — the broker has to manually scan and cross-reference multiple sheets. There's no at-a-glance signal for urgency; a renewal 20 days out looks the same as one 200 days out until someone notices the date. The likely cost: renewals get worked reactively instead of proactively, and the broker's attention goes wherever they last looked rather than where it's actually needed — a plausible consequence of the current setup, not one measured against actual missed renewals or lost clients.

## The Solution

A single table view, scoped to the broker's own active clients, that surfaces exactly the fields that matter for triage: client name, carrier, premium, EE count, funding type, renewal date, and a derived status (On Track / At Risk / Urgent) based on proximity to renewal. The broker can sort by renewal date or premium and filter by funding type or status, turning "which clients need attention" from a manual scan into a two-click answer. As a stretch, clicking a row opens a simple detail view with the same attributes, giving a slightly deeper look without leaving the flow. The feature runs on seeded/sample data for this stage — it's establishing the view and the interaction model, not the data pipeline.

## Who This Serves

**Primary user: the Broker / Consultant** — one internal role, "Consultant" being an alternate title for the same job, not a distinct persona. They own a book of employer clients and are accountable for renewals landing on time and premiums staying visible. Today they piece this together from spreadsheets; success for them looks like opening one screen each morning and knowing immediately which two or three clients need action this week. There is no secondary or employer-facing user in this feature — access is internal-only.

## Scope

**In for this version:**
- Table of the broker's active clients with: client name, carrier, premium, EE count, funding type (fully insured / level-funded / ASO), renewal date, and status (On Track / At Risk / Urgent, derived from proximity to renewal date)
- Sort by renewal date and by premium
- Filter by funding type and by status
- Seeded/sample client data (no upload, parsing, or external data integration)

**Stretch:** clicking a client row opens a simple detail view repeating the same attributes.

**Explicitly out:**
- Authentication / SSO
- Multi-tenant isolation
- Claims data
- Predictive or AI-generated recommendations
- Document upload
- Employer-facing portal access

**Constraints:** No PHI is involved anywhere in this feature. It has no dependency on the actuarial engine or on any architecture decision that isn't already settled — this is a self-contained visibility/display feature on top of static seeded data.

## Success Criteria

[ASSUMPTION] No target metrics were specified; the following are proposed as directionally reasonable for an MVP visibility feature and should be corrected if off:
- A broker can identify every At Risk / Urgent client in their book within a few seconds of opening the view, without cross-referencing anything else.
- Sorting and filtering behave predictably and cover the two axes brokers actually triage by (time-to-renewal, premium).
- The status derivation (On Track / At Risk / Urgent) matches what a broker would flag by eye, given a renewal date — i.e., it's a trustworthy first read, not just a decoration.

**Counter-metric:** the view should not become another place brokers have to double-check against their spreadsheets — if it does, it has failed at its one job.

## Vision

[ASSUMPTION] Not specified by the user; kept intentionally modest since this is one screen within a larger confirmed MVP. In its next steps, this view is the natural home for replacing seeded data with the broker's real book (live upload or integration), and for the "At Risk / Urgent" status to eventually draw on more than proximity-to-renewal alone. Both are explicitly out of scope here and belong to later units, not this feature.
