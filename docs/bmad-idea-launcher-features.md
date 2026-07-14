# BMAD Idea Launcher Feature List

## Core Features

1. Prompt Input
   - Single text input for the problem or topic
   - Placeholder text: "Describe the problem or experiment prompt..."

2. Generate Ideas
   - A prominent `Generate ideas` button
   - Triggers creation of three starter ideas based on the prompt

3. Idea Cards
   - Display exactly three ideas
   - Each card includes:
     - Idea title
     - One-sentence description
     - Favorite toggle button

4. Favorite Action
   - The user can mark one idea as favorite
   - Favorite state visually highlights the selected card

5. Local Runtime State
   - Session-only state stored in the page
   - If desired, optionally persist favorite selection in local storage

## Interaction Flow

1. User enters a problem prompt
2. User clicks `Generate ideas`
3. App renders three idea cards
4. User reviews cards and optionally marks one as favorite
5. Optionally, user may enter a new prompt and generate another set

## UX Details

- Minimal, single-screen layout
- Responsive design for desktop and mobile widths
- Clear success state after generation
- Lightweight visual styling to keep focus on content

## Implementation Notes

- Use plain HTML/CSS/JavaScript for fastest build
- Keep application logic small and readable
- Use a simple function to generate example ideas
- Favorite state can be modeled as an index or boolean per idea

## Optional Enhancements (if time allows)

- Save the favorite idea in `localStorage`
- Add a `Clear` button to reset the prompt and results
- Add a small `How it works` note showing BMAD learning intent
- Add a tiny `Next step` hint: “Try `bmad-ux` to sketch this idea”

## BMAD Workflow Artifacts

- Brainstorming: the three generated ideas are the core output
- UX: the single-screen idea launcher experience
- Architecture: the minimal data model for prompt + ideas + favorite
- Implementation story: build and review the MVP within 1–2 hours
