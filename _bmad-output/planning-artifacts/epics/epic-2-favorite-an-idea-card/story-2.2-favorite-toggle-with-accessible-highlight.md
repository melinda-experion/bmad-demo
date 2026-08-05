# Story 2.2: Favorite Toggle with Accessible Highlight

As a user reviewing generated ideas,
I want to mark exactly one idea card as my favorite with a highlight I can perceive without relying on color,
So that I can clearly track which idea I've chosen to focus on.

**Acceptance Criteria:**

**Given** three idea cards are rendered
**When** the user clicks the favorite toggle on a card
**Then** `state.favoritedIndex` is set to that card's index and the card is visibly highlighted using more than color alone — e.g. a distinct border plus an icon/label change (FR2, NFR4, AD-4)

**Given** a card is already favorited
**When** the user clicks the favorite toggle on a different card
**Then** the previous card's highlight is removed and the newly clicked card becomes the sole favorited card — at most one favorited card at any time (FR2, AD-4)

**Given** a card is already favorited
**When** the user clicks the favorite toggle on that same card again
**Then** the card is un-favorited and `state.favoritedIndex` returns to `null` (AD-4)

**Given** a favorite is set
**When** the user clicks `Generate ideas` to request a new set of ideas
**Then** the favorite highlight is cleared and `state.favoritedIndex` resets to `null`, consistent with Story 2.1's reset behavior (FR2, AD-3)
