# Product Brief: BMAD Idea Launcher

## Executive Summary

BMAD Idea Launcher is a tiny learning project that turns a simple problem prompt into three starter ideas. It is designed to be built in 1–2 hours as a single-screen experiment with a lean front-end flow. The goal is to learn the BMAD framework by building and using a lightweight tool that embodies ideation, UX clarity, and rapid implementation.

## The Problem

People often have a good problem or topic but struggle to move from that prompt to concrete project ideas. Existing idea generation tools can feel generic, overloaded, or too heavy for quick experimentation. For someone learning BMAD, the immediate need is a minimal, practical workflow that captures how the method turns an input into actionable output without requiring a full product.

## The Solution

Build a micro web app called BMAD Idea Launcher that:

- accepts a short problem or experiment prompt
- generates three starter ideas
- displays the ideas as simple cards
- allows the user to mark one idea as a favorite
- keeps the experience intentionally tiny and interactive

This makes the ideation step feel concrete, fast, and repeatable.

## What Makes This Different

- Focused on BMAD learning, not on building a large product
- Delivers a complete, usable idea flow in a very small scope
- Uses the idea of an experimentation launcher rather than a full idea management app
- Designed to exercise BMAD workflows: ideation, UX, architecture, and implementation in one rapid cycle

## Who This Serves

Primary user:

- A BMAD learner who wants a hands-on, 1–2 hour experiment
- Someone who wants a quick way to turn a prompt into actionable project ideas

Secondary user:

- A developer who wants a minimal demo of idea generation and concept validation
- A BMAD practitioner who wants a compact artifact for teaching or experimentation

## Success Criteria

- User can enter a prompt and generate three idea cards in under 30 seconds
- The UI is clear and requires only one screen: input, generate, results
- The app supports marking one idea as favorite
- The project is buildable in a single front-end session (HTML/CSS/JS or small framework)
- The app serves as a launch point for a BMAD learning cycle: brainstorm → define → build

## Scope

In scope:

- Single prompt input field
- Generate button
- Display exactly three idea cards with title + short description
- Favorite/save action per card
- Basic local state for current results
- One-screen responsive layout
- Minimal styling to keep focus on the ideas

Out of scope:

- Backend API integration
- Persistent storage beyond runtime or local browser storage
- Full idea management (edit, delete, tag, search)
- Complex authentication or multi-user support

## Vision

If successful, BMAD Idea Launcher becomes a reusable learning utility for rapid experiments. The next version could add:

- guided idea categories aligned to BMAD phases
- a tiny workflow helper showing next BMAD steps
- export of the favorite idea into a brief or story

## BMAD Learning Angle

This project is explicitly a BMAD experiment:

- `bmad-brainstorming`: the core product idea is an ideation tool
- `bmad-ux`: one-screen experience and clear interaction design
- `bmad-architecture`: minimal data shape and application spine
- `bmad-create-story`: one implementation story for the MVP
- `bmad-help`: a follow-on artifact that can recommend next steps after the launcher is built
