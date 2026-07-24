---
title: BMAD Idea Launcher
created: 2026-07-23
updated: 2026-07-23
approval_status: approved
version: 5
---

# Product Brief: BMAD Idea Launcher

## Executive Summary

BMAD Idea Launcher is a tiny learning project that turns a simple problem prompt into three starter ideas. It is designed to be built in 1-2 hours as a single-screen experiment with a lean front-end flow. The goal is to learn the BMAD framework by building and using a lightweight tool that embodies ideation, UX clarity, and rapid implementations.

## The Problem

People often have a good problem or topic but struggle to move from that prompt to concrete project ideas. Existing idea generation tools can feel generic, overloaded, or too heavy for quick experimentation. For someone learning BMAD, the immediate need is a minimal, practical workflow that captures how the method turns an input into actionable output without requiring a full product.

## The Solution

Build a micro web app called BMAD Idea Launcher: the user enters a short problem or experiment prompt, clicks `Generate ideas`, and gets three idea cards with a favorite toggle — all on one responsive screen, with all state session-only. See Scope below for the full feature list. This makes the ideation step feel concrete, fast, and repeatable.

What makes this different:

- Delivers a complete, usable idea flow in a very small scope, rather than a large product
- Frames itself as an experimentation launcher rather than a full idea management app

## Who This Serves

Primary user:

- A BMAD learner who wants a hands-on, 1-2 hour experiment
- Someone who wants a quick way to turn a prompt into actionable project ideas

Secondary user:

- A developer who wants a minimal demo of idea generation and concept validation
- A BMAD practitioner who wants a compact artifact for teaching or experimentation

## Success Criteria

- User can enter a prompt and generate three idea cards in under 30 seconds
- The project is buildable in a single front-end session (HTML/CSS/JS or small framework)
- The app serves as a launch point for a BMAD learning cycle: brainstorm → define → build

## Scope

In scope:

- Single prompt input field with placeholder text ("Describe the problem or experiment prompt...")
- `Generate ideas` button that renders exactly three idea cards
- Each card: title, one-sentence description, favorite toggle
- Favorite/save action per card, with a clear highlighted state
- Basic local runtime state for the current results
- One-screen, responsive layout (desktop and mobile widths)

Out of scope:

- Backend API integration
- Persistent storage beyond runtime, aside from an optional local-storage save of the favorite
- Full idea management (edit, delete, tag, search)
- Complex authentication or multi-user support

Optional enhancements, if time allows:

- Save the favorite idea in `localStorage`
- A `Clear` button to reset the prompt and results
- A small "How it works" note showing the BMAD learning intent
- A tiny "Next step" hint pointing at `bmad-ux`

## Vision

If successful, BMAD Idea Launcher becomes a reusable learning utility for rapid experiments. The next version could add:

- Guided idea categories aligned to BMAD phases
- A tiny workflow helper showing next BMAD steps
- Export of the favorite idea into a brief or story

## BMAD Learning Angle

This project is explicitly a BMAD experiment:

- `bmad-brainstorming` — the core product idea is an ideation tool
- `bmad-ux` — one-screen experience and clear interaction design
- `bmad-architecture` — minimal data shape and application spine
- `bmad-create-story` — one implementation story for the MVP
- `bmad-help` — a follow-on artifact that can recommend next steps after the launcher is built
