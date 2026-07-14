---
title: BMAD Idea Launcher - System Design Deep Dive
status: draft
created: 2026-07-13
updated: 2026-07-13
---

# System Design: BMAD Idea Launcher

This document expands on the [Architecture Spine](./ARCHITECTURE-SPINE.md) with implementation details, component specs, API contracts, and deployment guidance. It serves as a reference for developers building the MVP.

---

## 1. Frontend Architecture

### 1.1 Component Tree

```
App (root)
├─ Header
│  └─ Branding + minimal nav
├─ MainContainer
│  ├─ PromptSection
│  │  ├─ PromptInput (textarea)
│  │  ├─ GenerateButton
│  │  └─ HelpText
│  ├─ ResultsSection (conditional, shown after generation)
│  │  ├─ IdeaCardList
│  │  │  ├─ IdeaCard #1
│  │  │  ├─ IdeaCard #2
│  │  │  └─ IdeaCard #3
│  │  └─ ActionBar (reset/start over)
│  └─ ErrorSection (conditional, shown on error)
│     └─ ErrorMessage + RetryButton
└─ Footer (optional)
   └─ Links + version info
```

### 1.2 IdeaCard Component Contract

**Props:**

- `title: string` — Idea title (max 60 chars, enforced by backend)
- `description: string` — Idea description (max 200 chars, enforced by backend)
- `isFavorited: boolean` — Whether this card is in favorites
- `onToggleFavorite: (title, description) => void` — Callback on favorite button click
- `generatedAt: ISO8601 timestamp` — When this idea was generated (used for uniqueness check)

**Rendering:**

- Card displays `title` as a heading (e.g., `<h3>`)
- `description` below title as body text
- Favorite button (icon or text) with clear visual state (filled/outlined star, etc.)
- No other controls or edit affordances (read-only in MVP)

**CSS Classes:**

- `.idea-card` — base card
- `.idea-card.favorited` — when isFavorited is true
- `.idea-card__title` — title heading
- `.idea-card__description` — description text
- `.idea-card__favorite-button` — button styling

### 1.3 State Management

**Local React state (or vanilla JS object):**

```javascript
{
  prompt: "",           // current input value
  isLoading: false,     // true during generation
  error: null,          // error message or null
  ideas: [              // current result set (empty initially)
    { title: "...", description: "...", generatedAt: "2026-07-13T..." },
    // ...
  ],
  favorites: [          // favorited ideas (hydrated from localStorage)
    { title: "...", description: "...", generatedAt: "2026-07-13T..." },
    // ...
  ]
}
```

**localStorage Keys:**

- `bmad-launcher-favorites` — JSON array of favorited ideas
  ```json
  [
    { "title": "...", "description": "...", "generatedAt": "2026-07-13T..." },
    { "title": "...", "description": "...", "generatedAt": "2026-07-13T..." }
  ]
  ```

### 1.4 Event Flow

```
User types in PromptInput
  → setPrompt(value)
  → isValid = prompt.trim().length > 0
  → GenerateButton [disabled] or [enabled]

User clicks GenerateButton
  → setIsLoading(true)
  → POST /api/ideas { prompt: prompt }
  → on success:
      - setIdeas(response.ideas)
      - setError(null)
      - setIsLoading(false)
      - show ResultsSection
  → on error:
      - setError(response.message || "Generation failed")
      - setIsLoading(false)
      - show ErrorSection

User clicks favorite star on IdeaCard
  → toggleFavorite(idea)
    - find idea in localStorage favorites by (title + description)
    - if found: remove
    - if not found: add { title, description, generatedAt: now() }
    - write back to localStorage
    - re-render card with new isFavorited state

On page load (or app init):
  → hydrateFavoritesFromLocalStorage()
  → compare current ideas.title+description to favorites
  → set isFavorited flag for each card
```

### 1.5 Responsive CSS Strategy

**Mobile-first breakpoints:**

```css
/* Base (mobile, ≤600px) */
.main-container {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  gap: 1.5rem;
}

.idea-card-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.idea-card {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* Tablet & desktop (>600px) */
@media (min-width: 601px) {
  .idea-card-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }
}

/* Desktop (>1000px) */
@media (min-width: 1001px) {
  .main-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }
}
```

---

## 2. Backend Architecture

### 2.1 REST API Contract

**Endpoint:** `POST /api/ideas`

**Request:**

```json
{
  "prompt": "I want to build a tool that helps non-technical people organize their photos"
}
```

**Validation:**

- `prompt` is required
- `prompt.trim().length > 0`
- `prompt.length <= 500` (max input size)
- Return 400 Bad Request if invalid

**Response (Success, 200 OK):**

```json
{
  "ideas": [
    {
      "title": "Photo Library Assistant",
      "description": "An app that auto-categorizes photos by date, location, and detected subjects."
    },
    {
      "title": "Photo Quiz Game",
      "description": "A fun game that guesses photo locations and timestamps, teaching organizational patterns."
    },
    {
      "title": "Photo Time Capsule",
      "description": "A tool that presents photos chronologically with memories, creating a time-based narrative."
    }
  ]
}
```

**Response (LLM Error, 500 or 503):**

```json
{
  "error": "Ideas couldn't generate. Try again."
}
```

**Response (Bad Request, 400):**

```json
{
  "error": "Prompt is required and must not be empty"
}
```

### 2.2 LLM Provider Abstraction

**Interface:**

```python
class IdeaProvider:
    async def generate_ideas(self, prompt: str) -> List[Idea]:
        """
        Accept a user prompt, return exactly 3 ideas.
        Raises: ProviderError on failure (network, timeout, quota, etc.)
        """
        pass

@dataclass
class Idea:
    title: str        # max 60 chars
    description: str  # max 200 chars
```

**OpenAI Implementation (Default):**

```python
class OpenAIProvider(IdeaProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    async def generate_ideas(self, prompt: str) -> List[Idea]:
        system_message = """
        You are a creative ideation assistant. Generate exactly 3 unique, actionable project ideas.
        For each idea, provide a concise title (max 60 chars) and one-sentence description (max 200 chars).
        Return response as JSON array: [{"title": "...", "description": "..."}, ...]
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            response_text = response.choices[0].message.content
            parsed = json.loads(response_text)

            # Validate exactly 3 ideas, enforce field limits
            ideas = [
                Idea(
                    title=idea["title"][:60],
                    description=idea["description"][:200]
                )
                for idea in parsed[:3]
            ]

            # Pad to 3 if fewer returned
            while len(ideas) < 3:
                ideas.append(Idea(
                    title="Consider this angle",
                    description="Reflect on what you're solving before diving deeper."
                ))

            return ideas[:3]

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise ProviderError(f"Failed to generate ideas: {str(e)}")
```

**Adding a New Provider (e.g., Anthropic):**

```python
class AnthropicProvider(IdeaProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def generate_ideas(self, prompt: str) -> List[Idea]:
        # Implement Anthropic API call, return List[Idea]
        pass
```

### 2.3 Error Handling & Logging

**Error Cases:**

1. **Bad Request (400)** — Validation failure
   - Prompt is empty or too long
   - Return user-safe message
2. **Provider Error (500/503)** — LLM call fails
   - Network timeout
   - Quota exceeded
   - API error
   - Log full error server-side; return generic message to user
3. **Unexpected (500)** — Server bug
   - Log full traceback
   - Return generic error message

**Logging Pattern:**

```python
logger.info(f"Generation request: prompt_len={len(prompt)}")
logger.info(f"Generation successful: 3 ideas, response_time={elapsed_ms}ms")
logger.error(f"Generation failed: provider={provider}, error={e}, prompt_len={len(prompt)}")
```

### 2.4 Environment Configuration

**Required env vars:**

```bash
LLM_PROVIDER=openai          # openai, anthropic, etc.
OPENAI_API_KEY=sk-...        # if provider=openai
ANTHROPIC_API_KEY=...        # if provider=anthropic
LOG_LEVEL=info
PORT=3000
```

**Factory Pattern for Provider Selection:**

```python
def get_provider() -> IdeaProvider:
    provider_name = os.getenv("LLM_PROVIDER", "openai")

    if provider_name == "openai":
        return OpenAIProvider(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4")
        )
    elif provider_name == "anthropic":
        return AnthropicProvider(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
```

---

## 3. Data Model & Contracts

### 3.1 Idea Schema

**Backend (internal representation):**

```python
@dataclass
class Idea:
    title: str
    description: str
    # Optional (internal use only, not sent to client):
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    id: UUID = Field(default_factory=uuid4)
```

**API Response (sent to client):**

```json
{
  "title": "Photo Library Assistant",
  "description": "An app that auto-categorizes photos by date, location, and detected subjects."
}
```

**localStorage (client):**

```json
{
  "title": "Photo Library Assistant",
  "description": "An app that auto-categorizes photos by date, location, and detected subjects.",
  "generatedAt": "2026-07-13T14:32:00Z"
}
```

### 3.2 Favorite Uniqueness

**Key logic:**
Favorites are matched by `(title, description)` equality. If a user regenerates and gets the same title/description, it's considered the same idea.

**Implementation:**

```javascript
function isFavorited(idea, favorites) {
  return favorites.some(
    (fav) => fav.title === idea.title && fav.description === idea.description,
  );
}

function toggleFavorite(idea, favorites) {
  const index = favorites.findIndex(
    (fav) => fav.title === idea.title && fav.description === idea.description,
  );

  if (index >= 0) {
    // Remove
    return favorites.slice(0, index).concat(favorites.slice(index + 1));
  } else {
    // Add
    return [...favorites, { ...idea, generatedAt: new Date().toISOString() }];
  }
}
```

---

## 4. Deployment & Operations

### 4.1 Recommended Deployment Stack

**Frontend:**

- **Build:** No build step (vanilla JS) or minimal bundler (Vite for Alpine.js variant)
- **Hosting:** Netlify, Vercel, GitHub Pages, or simple static server
- **CDN:** Cloudflare (optional, speeds up asset delivery)

**Backend:**

- **Runtime:** Node.js 18+ (LTS) or Python 3.10+
- **Framework:** Express (Node) or FastAPI (Python)
- **Hosting:** Heroku, Render, Railway, DigitalOcean App Platform
- **Environment:** Managed PostgreSQL or SQLite (no DB needed for MVP; can skip)

**LLM API:**

- **OpenAI:** API key from platform.openai.com
- **Backup/Alternative:** Anthropic, Cohere, Replicate, or local LLM

### 4.2 Local Development Setup

**Frontend:**

```bash
# No installation needed; open index.html in browser
# Or use a simple local server:
python3 -m http.server 8000
# Visit http://localhost:8000
```

**Backend (Node + Express):**

```bash
npm init -y
npm install express cors dotenv axios      # or similar LLM client
# Create server.js
node server.js
# Backend runs on http://localhost:3000
```

**Backend (Python + FastAPI):**

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install fastapi uvicorn openai python-dotenv
# Create main.py
uvicorn main:app --reload
# Backend runs on http://localhost:8000
```

### 4.3 Environment File Example

**.env (local development):**

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
LOG_LEVEL=debug
PORT=3000
CORS_ORIGIN=http://localhost:5000
```

**.env (production, Render/Heroku):**

```
LLM_PROVIDER=openai
OPENAI_API_KEY=<set via UI or secrets manager>
OPENAI_MODEL=gpt-4
LOG_LEVEL=info
PORT=<auto-assigned by platform>
CORS_ORIGIN=https://www.yourdomain.com
```

### 4.4 Deployment Checklist

- [ ] Frontend assets are minified and cacheable
- [ ] Backend has error logging and monitoring (e.g., Sentry)
- [ ] API rate limiting is configured (to prevent LLM quota abuse)
- [ ] CORS headers allow frontend-to-backend cross-origin requests
- [ ] LLM API key is stored securely (env var, secrets manager)
- [ ] Health check endpoint `/health` or `/ping` exists (for monitoring)
- [ ] Graceful shutdown: backend drains in-flight requests on stop

---

## 5. Testing Strategy

### 5.1 Frontend Unit Tests

**Example (Jest + @testing-library/react):**

```javascript
describe("IdeaCard", () => {
  it("renders title and description", () => {
    const idea = {
      title: "My Idea",
      description: "A cool description",
      generatedAt: "2026-07-13T...",
    };
    const { getByText } = render(
      <IdeaCard {...idea} isFavorited={false} onToggleFavorite={() => {}} />,
    );
    expect(getByText("My Idea")).toBeInTheDocument();
    expect(getByText("A cool description")).toBeInTheDocument();
  });

  it("toggles favorite on button click", () => {
    const onToggle = jest.fn();
    const { getByRole } = render(
      <IdeaCard
        title="Test"
        description="Desc"
        isFavorited={false}
        onToggleFavorite={onToggle}
        generatedAt="2026-07-13T..."
      />,
    );
    fireEvent.click(getByRole("button", { name: /favorite/i }));
    expect(onToggle).toHaveBeenCalled();
  });
});
```

### 5.2 Backend Integration Tests

**Example (pytest + httpx):**

```python
@pytest.mark.asyncio
async def test_generate_ideas_success():
    client = AsyncClient(app=app, base_url="http://test")
    response = await client.post("/api/ideas", json={
        "prompt": "Build a photo organizer"
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["ideas"]) == 3
    assert all("title" in idea and "description" in idea for idea in data["ideas"])

@pytest.mark.asyncio
async def test_generate_ideas_empty_prompt():
    client = AsyncClient(app=app, base_url="http://test")
    response = await client.post("/api/ideas", json={
        "prompt": ""
    })

    assert response.status_code == 400
    assert "required" in response.json()["error"].lower()
```

### 5.3 E2E Tests

**Example (Cypress):**

```javascript
describe("BMAD Idea Launcher E2E", () => {
  it("generates ideas from a prompt and favorites one", () => {
    cy.visit("http://localhost:5000");

    // Enter prompt
    cy.get("input[placeholder*='prompt']").type("Build a habit tracker");

    // Generate
    cy.get("button").contains("Generate ideas").click();

    // Wait for results
    cy.get(".idea-card").should("have.length", 3);

    // Favorite the first card
    cy.get(".idea-card").first().find("button[title*='favorite']").click();
    cy.get(".idea-card").first().should("have.class", "favorited");

    // Reload and check persistence
    cy.reload();
    cy.get(".idea-card").first().should("have.class", "favorited");
  });
});
```

### 5.4 Success Metrics (from PRD)

- **SM-1:** First-time user can enter prompt, generate ideas, and mark favorite in <2 min without help.
- **SM-2:** App is usable on desktop and mobile without layout failure.

**Test criteria:**

- Automated: Cypress E2E on multiple screen sizes.
- Manual: Usability testing with 3+ first-time users; measure task time and error count.

---

## 6. Known Limitations & Future Enhancements

### 6.1 MVP Limitations

- **No history:** Each generation overwrites prior results (unless favorited).
- **No editing:** Ideas cannot be modified or deleted once generated.
- **No sharing:** Cannot export ideas as JSON, PDF, or link.
- **No authentication:** No per-user accounts or multi-device sync.
- **Single LLM provider at runtime:** Must restart backend to switch providers.

### 6.2 Post-MVP Enhancements

1. **Idea History View** — See prior generations side-by-side.
2. **Export & Share** — Download as JSON/CSV; share link with ideas.
3. **Idea Refinement** — "Tell me more about this idea" → iterative details.
4. **Tagging & Search** — Organize favorites by tag; search past ideas.
5. **Collaborative Mode** — Multiple users brainstorm together (requires auth + backend DB).
6. **BMAD Workflow Integration** — Button to "Create a PRD from this idea" (calls bmad-prd skill).

---

## 7. Reference Links & Standards

- **API Docs:** OpenAI API — https://platform.openai.com/docs/api-reference
- **Frontend Testing:** @testing-library — https://testing-library.com
- **Backend Framework (Express):** https://expressjs.com
- **Backend Framework (FastAPI):** https://fastapi.tiangolo.com
- **Accessibility:** WCAG 2.1 AA — https://www.w3.org/WAI/WCAG21/quickref/
- **CSS:** Mobile-first responsive design — https://www.mobileapproaches.com

---

## 8. Appendix: Code Scaffolds

### A. Express.js Backend Scaffold

```javascript
// server.js
const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors({ origin: process.env.CORS_ORIGIN || "*" }));

// Get provider (factory)
const getProvider = () => {
  // Implement based on LLM_PROVIDER env var
  const { OpenAIProvider } = require("./providers/openai");
  return new OpenAIProvider(process.env.OPENAI_API_KEY);
};

app.post("/api/ideas", async (req, res) => {
  const { prompt } = req.body;

  if (!prompt || prompt.trim().length === 0) {
    return res.status(400).json({ error: "Prompt is required" });
  }

  try {
    const provider = getProvider();
    const ideas = await provider.generateIdeas(prompt);
    res.json({ ideas });
  } catch (err) {
    console.error("Generation error:", err);
    res.status(500).json({ error: "Ideas couldn't generate. Try again." });
  }
});

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Backend listening on port ${PORT}`);
});
```

### B. HTML + Vanilla JS Frontend Scaffold

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>BMAD Idea Launcher</title>
    <style>
      * {
        box-sizing: border-box;
      }
      body {
        font-family:
          -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin: 0;
        padding: 1rem;
        background: #f9f9f9;
      }
      .container {
        max-width: 1200px;
        margin: 0 auto;
      }
      .header {
        text-align: center;
        margin-bottom: 2rem;
      }
      .prompt-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 2rem;
      }
      input[type="text"] {
        padding: 0.75rem;
        font-size: 1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
      }
      button {
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        background: #0066cc;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      }
      button:disabled {
        background: #ccc;
        cursor: not-allowed;
      }
      .results-section {
        display: none;
        margin-top: 2rem;
      }
      .results-section.visible {
        display: block;
      }
      .idea-card-list {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
      }
      .idea-card {
        padding: 1.5rem;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
      }
      .idea-card.favorited {
        border-color: #ffd700;
        background: #fffef5;
      }
      .idea-card__title {
        margin: 0 0 0.5rem 0;
        font-size: 1.25rem;
        font-weight: 600;
      }
      .idea-card__description {
        margin: 0 0 1rem 0;
        color: #555;
      }
      .favorite-button {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1.5rem;
        padding: 0;
      }
      .favorite-button.active {
        color: #ffd700;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>BMAD Idea Launcher</h1>
        <p>Turn a prompt into three starter ideas</p>
      </div>

      <div class="prompt-section">
        <input
          type="text"
          id="prompt-input"
          placeholder="What problem or idea are you exploring?"
          maxlength="500"
        />
        <button id="generate-button" onclick="handleGenerate()">
          Generate ideas
        </button>
      </div>

      <div id="results-section" class="results-section">
        <div id="idea-card-list" class="idea-card-list"></div>
        <button onclick="handleReset()" style="margin-top: 1.5rem;">
          Start over
        </button>
      </div>

      <div id="error-section" style="display: none; margin-top: 1rem;">
        <div style="padding: 1rem; background: #fdd; border-radius: 4px;">
          <p id="error-message"></p>
          <button onclick="handleRetry()">Try again</button>
        </div>
      </div>
    </div>

    <script>
      const API_BASE = process.env.API_BASE || "http://localhost:3000";

      let state = {
        prompt: "",
        isLoading: false,
        error: null,
        ideas: [],
        favorites: loadFavoritesFromStorage(),
      };

      function loadFavoritesFromStorage() {
        const stored = localStorage.getItem("bmad-launcher-favorites");
        return stored ? JSON.parse(stored) : [];
      }

      function saveFavoritesToStorage() {
        localStorage.setItem(
          "bmad-launcher-favorites",
          JSON.stringify(state.favorites),
        );
      }

      async function handleGenerate() {
        const input = document.getElementById("prompt-input");
        const prompt = input.value.trim();

        if (!prompt) {
          alert("Please enter a prompt");
          return;
        }

        state.prompt = prompt;
        state.isLoading = true;
        document.getElementById("generate-button").disabled = true;

        try {
          const response = await fetch(`${API_BASE}/api/ideas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt }),
          });

          if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || "Generation failed");
          }

          const data = await response.json();
          state.ideas = data.ideas;
          state.error = null;
          renderResults();
          document.getElementById("results-section").classList.add("visible");
          document.getElementById("error-section").style.display = "none";
        } catch (err) {
          state.error = err.message;
          document.getElementById("error-message").textContent = err.message;
          document.getElementById("error-section").style.display = "block";
          document
            .getElementById("results-section")
            .classList.remove("visible");
        } finally {
          state.isLoading = false;
          document.getElementById("generate-button").disabled = false;
        }
      }

      function renderResults() {
        const list = document.getElementById("idea-card-list");
        list.innerHTML = "";

        state.ideas.forEach((idea) => {
          const isFavorited = state.favorites.some(
            (fav) =>
              fav.title === idea.title && fav.description === idea.description,
          );

          const card = document.createElement("div");
          card.className = `idea-card ${isFavorited ? "favorited" : ""}`;
          card.innerHTML = `
          <h3 class="idea-card__title">${escapeHtml(idea.title)}</h3>
          <p class="idea-card__description">${escapeHtml(idea.description)}</p>
          <button class="favorite-button ${isFavorited ? "active" : ""}" onclick="handleToggleFavorite('${escapeAttr(idea.title)}', '${escapeAttr(idea.description)}')">
            ${isFavorited ? "★" : "☆"}
          </button>
        `;
          list.appendChild(card);
        });
      }

      function handleToggleFavorite(title, description) {
        const index = state.favorites.findIndex(
          (fav) => fav.title === title && fav.description === description,
        );

        if (index >= 0) {
          state.favorites.splice(index, 1);
        } else {
          state.favorites.push({
            title,
            description,
            generatedAt: new Date().toISOString(),
          });
        }

        saveFavoritesToStorage();
        renderResults();
      }

      function handleReset() {
        document.getElementById("prompt-input").value = "";
        state.prompt = "";
        state.ideas = [];
        state.error = null;
        document.getElementById("results-section").classList.remove("visible");
        document.getElementById("error-section").style.display = "none";
      }

      function handleRetry() {
        handleGenerate();
      }

      function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
      }

      function escapeAttr(text) {
        return text.replace(/'/g, "\\'");
      }

      // Hydrate favorites on page load
      renderResults();
    </script>
  </body>
</html>
```

---

## 9. Conclusion

This system design provides implementation teams with:

- Clear API contracts
- Frontend and backend architecture
- Deployment guidance
- Testing strategies
- Code scaffolds to accelerate development

Use the [Architecture Spine](./ARCHITECTURE-SPINE.md) as the consistency contract and this document as the implementation guide.
