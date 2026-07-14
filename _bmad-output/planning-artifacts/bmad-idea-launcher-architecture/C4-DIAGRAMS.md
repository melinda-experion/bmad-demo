---
title: BMAD Idea Launcher - C4 Architecture Diagrams
status: draft
created: 2026-07-13
updated: 2026-07-13
---

# System Architecture Diagrams (C4 Model)

This document provides visual representations of the BMAD Idea Launcher architecture at multiple levels of detail: System Context, Container, Component, and Code views.

---

## Level 1: System Context Diagram

Shows the BMAD Idea Launcher and its external dependencies.

```mermaid
graph TB
    User["👤 User<br/>(BMAD Learner)"]
    Browser["🌐 Web Browser<br/>(Frontend App)"]
    Backend["🖥️ Backend Server<br/>(REST API)"]
    LLM["🧠 OpenAI API<br/>(GPT-4 or equivalent)"]
    LocalStorage["💾 localStorage<br/>(Browser Storage)"]

    User -->|Uses| Browser
    Browser -->|HTTP POST<br/>/api/ideas| Backend
    Backend -->|API Call<br/>GPT-4| LLM
    LLM -->|JSON Response<br/>3 ideas| Backend
    Backend -->|HTTP 200<br/>{ideas: [...]}| Browser
    Browser -->|Read/Write| LocalStorage
    Browser -->|Display Results| User
    User -->|Save to favorites| Browser
```

**Key Interactions:**

- User enters prompt in browser
- Browser sends prompt to backend
- Backend calls OpenAI (or pluggable provider)
- Backend returns exactly 3 ideas
- Browser renders ideas and manages favorite state locally

---

## Level 2: Container Diagram

Shows the major components and how they communicate.

```mermaid
graph TB
    subgraph Client["Client (Browser)"]
        direction TB
        HTML["HTML/CSS<br/>(Static Markup)"]
        JS["JavaScript<br/>(Application Logic)"]
        Storage["localStorage<br/>(Favorite State)"]
        DOM["DOM<br/>(Rendered UI)"]
    end

    subgraph Server["Backend Server"]
        direction TB
        API["REST API<br/>/api/ideas"]
        Validator["Input Validator<br/>(Prompt validation)"]
        Provider["LLM Provider<br/>(OpenAI Adapter)"]
    end

    subgraph External["External Services"]
        direction TB
        OpenAI["OpenAI API<br/>(GPT-4)"]
    end

    User["👤 User"]

    User -->|1. Enter prompt| DOM
    DOM -->|2. Read input| JS
    JS -->|3. Fetch POST| API
    API -->|4. Validate| Validator
    Validator -->|5. Generate| Provider
    Provider -->|6. Call LLM| OpenAI
    OpenAI -->|7. Response| Provider
    Provider -->|8. Return JSON| API
    API -->|9. Return 3 ideas| JS
    JS -->|10. Render cards| DOM
    JS -->|11. Hydrate favorites| Storage
    Storage -->|12. Read state| JS
    JS -->|13. Mark favorites| Storage
    DOM -->|14. Show results| User
```

**Key Containers:**

- **Client (Browser):** HTML markup, JS logic, localStorage
- **Backend Server:** REST API, input validation, LLM provider abstraction
- **External Services:** OpenAI or other LLM provider

---

## Level 3: Component Diagram (Frontend)

Shows the frontend component tree and data flow.

```mermaid
graph TB
    subgraph App["App (Root)"]
        direction TB
        Header["Header<br/>(Branding)"]

        subgraph MainContainer["Main Container"]
            direction TB
            PromptSection["PromptSection<br/>├─ Input field<br/>├─ Generate button<br/>└─ Help text"]

            ResultsSection["ResultsSection (Conditional)<br/>├─ CardList<br/>│  ├─ IdeaCard #1<br/>│  ├─ IdeaCard #2<br/>│  └─ IdeaCard #3<br/>└─ Reset button"]

            ErrorSection["ErrorSection (Conditional)<br/>├─ Error message<br/>└─ Retry button"]
        end

        Footer["Footer (Optional)<br/>(Links, version)"]
    end

    State["App State<br/>├─ prompt: string<br/>├─ isLoading: bool<br/>├─ error: null|string<br/>├─ ideas: Idea[]<br/>└─ favorites: Idea[]"]

    Storage["localStorage<br/>bmad-launcher-favorites"]

    PromptSection -->|setPrompt| State
    ResultsSection -->|Read ideas| State
    ResultsSection -->|Read favorites| State
    ErrorSection -->|Read error| State
    State -->|Write favorites| Storage
    Storage -->|Load on init| State

    subgraph IdeaCard["IdeaCard Component<br/>(Props)"]
        direction LR
        Title["title: string<br/>(max 60 chars)"]
        Desc["description: string<br/>(max 200 chars)"]
        Fav["isFavorited: bool"]
        Handler["onToggleFavorite:<br/>callback"]
    end

    ResultsSection -->|Pass props| IdeaCard
```

**Key Components:**

- **PromptSection** — Input field + button
- **ResultsSection** — Grid of 3 idea cards
- **ErrorSection** — Error message + retry
- **IdeaCard** — Reusable card component

**Key State:**

- `prompt` — Current input
- `isLoading` — Generation in progress
- `ideas` — Current result set (3 items)
- `favorites` — Persisted favorite set

---

## Level 3: Component Diagram (Backend)

Shows the backend component tree and dependencies.

```mermaid
graph TB
    subgraph API["REST API Layer"]
        direction TB
        Handler["POST /api/ideas<br/>(Request handler)"]
    end

    subgraph Business["Business Logic Layer"]
        direction TB
        Validator["Validator<br/>├─ Check non-empty<br/>├─ Check max length<br/>└─ Reject invalid"]

        Generator["Generator<br/>├─ Call provider<br/>├─ Enforce 3 ideas<br/>└─ Handle errors"]
    end

    subgraph Provider["LLM Provider Layer"]
        direction TB
        Abstract["IdeaProvider<br/>(Abstract Interface)"]
        OpenAI["OpenAIProvider<br/>├─ Format prompt<br/>├─ Call OpenAI<br/>└─ Parse response"]
        Anthropic["AnthropicProvider<br/>(Stub for future)"]
    end

    subgraph Error["Error Handling"]
        direction TB
        ErrorHandler["ErrorHandler<br/>├─ Wrap exceptions<br/>├─ Log server-side<br/>└─ Return 400/500"]
    end

    Config["Environment Config<br/>LLM_PROVIDER<br/>OPENAI_API_KEY"]

    Handler -->|Validate| Validator
    Validator -->|OK| Generator
    Validator -->|Invalid| ErrorHandler
    Generator -->|Call| Abstract
    Config -->|Select| Abstract
    Abstract -->|OpenAI| OpenAI
    Abstract -->|Anthropic| Anthropic
    OpenAI -->|Success| Handler
    OpenAI -->|Error| ErrorHandler
    ErrorHandler -->|Return error| Handler
```

**Key Layers:**

- **API Layer** — HTTP request handling
- **Business Logic** — Validation, generation, error wrapping
- **Provider Layer** — LLM abstraction (pluggable)
- **Error Handling** — Graceful failure, user-safe messages

**Key Principle:** Backend is thin and stateless; all state lives on the client or in localStorage.

---

## Level 4: Code Structure Diagram

Shows file organization and module relationships.

```
Frontend (Client-Side)
└── index.html                          (Single page entry point)
    ├── <style>                         (Inline or external CSS)
    │   ├── .main-container
    │   ├── .prompt-section
    │   ├── .results-section
    │   ├── .idea-card-list
    │   ├── .idea-card
    │   ├── .idea-card.favorited
    │   └── media queries (mobile-first)
    │
    ├── <script>                        (Vanilla JS application logic)
    │   ├── const API_BASE
    │   ├── let state = {...}           (Local app state)
    │   ├─ function loadFavoritesFromStorage()
    │   ├─ function saveFavoritesToStorage()
    │   ├─ async function handleGenerate()
    │   ├─ function renderResults()
    │   ├─ function handleToggleFavorite()
    │   ├─ function handleReset()
    │   ├─ function handleRetry()
    │   └─ ... utility functions
    │
    └── localStorage key: "bmad-launcher-favorites"
        └── [{title, description, generatedAt}, ...]

Backend (Server-Side)
├── server.js (or main.py)              (Express app entry point)
│
├── routes/
│   └── api.js (or api.py)
│       └── POST /api/ideas
│
├── middleware/
│   ├── validation.js                   (Prompt validation)
│   └── errorHandler.js                 (Error wrapping)
│
├── services/
│   ├── ideaService.js                  (Generation logic)
│   └── providers/
│       ├── ideaProvider.js             (Abstract interface)
│       ├── openaiProvider.js           (OpenAI implementation)
│       └── anthropicProvider.js        (Anthropic stub)
│
├── utils/
│   ├── logger.js                       (Logging)
│   └── config.js                       (Env var loading)
│
└── .env                                (Environment variables)
    ├── LLM_PROVIDER=openai
    ├── OPENAI_API_KEY=...
    ├── LOG_LEVEL=info
    └── PORT=3000
```

---

## Data Model Diagram

Shows the structure of data at rest and in transit.

```mermaid
graph TB
    subgraph Request["API Request"]
        ReqBody["POST /api/ideas<br/>{<br/>  prompt: string<br/>}"]
    end

    subgraph Response["API Response (Success)"]
        RespBody["200 OK<br/>{<br/>  ideas: [<br/>    {<br/>      title: string,<br/>      description: string<br/>    },<br/>    ...<br/>  ]<br/>}"]
    end

    subgraph ResponseError["API Response (Error)"]
        ErrorBody["400 or 500<br/>{<br/>  error: string<br/>}"]
    end

    subgraph Storage["localStorage<br/>bmad-launcher-favorites"]
        StorageData["[<br/>  {<br/>    title: string,<br/>    description: string,<br/>    generatedAt: ISO8601<br/>  },<br/>  ...<br/>]"]
    end

    subgraph UI["UI State (Memory)"]
        UIState["{<br/>  prompt: string,<br/>  isLoading: boolean,<br/>  error: null|string,<br/>  ideas: Idea[],<br/>  favorites: Idea[]<br/>}"]
    end

    ReqBody -->|Sent to backend| Response
    Response -->|Returned to frontend| UIState
    ErrorBody -->|On error| UIState
    UIState -->|Persist on toggle| Storage
    Storage -->|Hydrate on load| UIState

    subgraph Constraints["Schema Constraints"]
        direction TB
        C1["• prompt.length > 0 && ≤ 500"]
        C2["• ideas.length == 3 (always)"]
        C3["• title.length ≤ 60"]
        C4["• description.length ≤ 200"]
        C5["• favorites can have duplicates (same idea favorited twice)"]
    end
```

---

## Deployment Architecture Diagram

Shows how components are deployed and communicate.

```mermaid
graph TB
    subgraph Browser["User's Browser<br/>(Client Device)"]
        direction TB
        Client["Frontend App<br/>HTML + CSS + JS"]
        LS["localStorage<br/>(Favorites)"]
    end

    Internet["Internet / Network"]

    subgraph Deployment["Production Deployment"]
        direction TB

        subgraph CDN["CDN / Static Host<br/>(Netlify, Vercel, GitHub Pages)"]
            StaticAssets["Frontend Assets<br/>index.html<br/>app.js<br/>app.css"]
        end

        subgraph BackendServer["Backend Server<br/>(Render, Heroku, Railway)"]
            direction TB
            ExpressApp["Express.js App<br/>/api/ideas endpoint"]
            Config["Config<br/>(Env vars)"]
            Logs["Logging<br/>(Sentry, CloudWatch)"]
        end

        subgraph LLMProvider["LLM Provider<br/>(External SaaS)"]
            OpenAIAPI["OpenAI API<br/>api.openai.com"]
        end
    end

    Browser -->|1. GET index.html| Internet
    Internet -->|2. Fetch| CDN
    CDN -->|3. Return assets| Internet
    Internet -->|4. Load into| Browser

    Browser -->|5. POST /api/ideas| Internet
    Internet -->|6. Route to| BackendServer
    ExpressApp -->|7. Read config| Config
    ExpressApp -->|8. Call LLM| LLMProvider
    LLMProvider -->|9. Response| ExpressApp
    ExpressApp -->|10. Log events| Logs
    ExpressApp -->|11. Return JSON| Internet
    Internet -->|12. Receive| Browser

    Browser <-->|13. Read/Write| LS

    Client -->|API calls| ExpressApp
```

**Deployment Notes:**

- **Frontend:** Static files (CDN or simple server)
- **Backend:** Node.js server on Platform-as-a-Service (Heroku, Render)
- **LLM:** Managed service (OpenAI, Anthropic)
- **Monitoring:** Optional logging service (Sentry, CloudWatch)

---

## Request-Response Flow Diagram

Shows the complete lifecycle of a generation request.

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Backend
    participant LLM as OpenAI API
    participant Storage as localStorage

    User->>Browser: 1. Type prompt
    Browser->>Browser: 2. Update state
    User->>Browser: 3. Click Generate
    Browser->>Browser: 4. Validate prompt
    Browser->>Browser: 5. setIsLoading(true)
    Browser->>Backend: 6. POST /api/ideas {prompt}
    Backend->>Backend: 7. Validate prompt
    Backend->>LLM: 8. POST /chat/completions
    LLM->>LLM: 9. Generate ideas (GPT-4)
    LLM->>Backend: 10. Return response
    Backend->>Backend: 11. Parse & enforce 3 ideas
    Backend->>Browser: 12. 200 OK {ideas: [...]}
    Browser->>Browser: 13. setIdeas(response.ideas)
    Browser->>Browser: 14. setIsLoading(false)
    Browser->>Browser: 15. renderResults()
    Browser->>Browser: 16. Hydrate favorites from Storage
    Browser->>Browser: 17. Re-render with favorite state
    Browser->>User: 18. Display 3 idea cards

    User->>Browser: 19. Click favorite star
    Browser->>Browser: 20. toggleFavorite(idea)
    Browser->>Storage: 21. Write updated favorites
    Browser->>Browser: 22. Re-render card
    Browser->>User: 23. Show filled star

    User->>Browser: 24. Reload page
    Browser->>Storage: 25. Read favorites
    Browser->>Browser: 26. Hydrate app state
    Browser->>User: 27. Display favorited ideas as marked
```

---

## Error Handling Flow Diagram

Shows how errors are handled at each layer.

```mermaid
graph TB
    Start["User submits prompt"]

    Start -->|1. Browser validates| ClientVal{Valid?}
    ClientVal -->|No| ClientError["Show validation error"]
    ClientError -->|Retry| Start

    ClientVal -->|Yes| SendReq["POST /api/ideas"]
    SendReq -->|2. Backend validates| ServerVal{Valid?}
    ServerVal -->|No| Return400["Return 400 Bad Request"]
    Return400 -->|Handle in browser| ShowError["Show 'Prompt required'"]
    ShowError -->|Retry| Start

    ServerVal -->|Yes| CallLLM["Call LLM provider"]
    CallLLM -->|Timeout| LLMError["Catch ProviderError"]
    CallLLM -->|Quota exceeded| LLMError
    CallLLM -->|Network error| LLMError
    CallLLM -->|Parse error| LLMError

    LLMError -->|Log server-side| Logger["logger.error(...)<br/>(full context)"]
    Logger -->|Return 500| Return500["Return 500 Server Error<br/>{error: 'Ideas couldn't generate...'}"]

    Return500 -->|Handle in browser| ShowFriendly["Show user-friendly message<br/>Preserve prompt"]
    ShowFriendly -->|Retry| SendReq

    CallLLM -->|Success| Parse["Parse response"]
    Parse -->|Enforce 3 ideas| Enforce["Pad if <3, truncate if >3"]
    Enforce -->|Return 200| ReturnOK["Return 200 OK<br/>{ideas: [3 items]}"]
    ReturnOK -->|Success flow| Render["Render cards"]
```

---

## State Transition Diagram

Shows how the frontend state machine transitions through different states.

```mermaid
stateDiagram-v2
    [*] --> Initial

    Initial: Initial State
    Initial: prompt=""
    Initial: ideas=[]
    Initial: favorites=[]
    Initial: isLoading=false
    Initial: error=null

    Initial -->|User types| Ready
    Ready: Ready to Generate
    Ready: prompt="..."
    Ready: ideas=[]
    Ready: isLoading=false
    Ready: error=null

    Ready -->|User clicks Generate| Loading
    Loading: Generating Ideas
    Loading: isLoading=true
    Loading: prompt="..."
    Loading: button [disabled]

    Loading -->|Success| Success
    Success: Results Displayed
    Success: ideas=[3 items]
    Success: isLoading=false
    Success: error=null
    Success: favorites hydrated

    Loading -->|Error| Error
    Error: Error State
    Error: error="Ideas couldn't generate..."
    Error: isLoading=false
    Error: ideas=[]
    Error: prompt preserved

    Error -->|User clicks Retry| Loading

    Success -->|User toggles favorite| Success
    Success: (favorites updated,<br/>card re-rendered)

    Success -->|User clicks Reset| Ready
    Ready: ideas=[]
    Ready: error=null
    Ready: prompt=""

    Ready -->|Page reload| Initial
    Initial -->|Hydrate favorites| Ready
```

---

## Responsive Layout Diagram

Shows how the layout adapts across breakpoints (AD-5).

```
Mobile (≤600px)
┌─────────────────────┐
│      Header         │
├─────────────────────┤
│   [Input field]     │
│  [Generate Button]  │
├─────────────────────┤
│    [Idea Card 1]    │
├─────────────────────┤
│    [Idea Card 2]    │
├─────────────────────┤
│    [Idea Card 3]    │
├─────────────────────┤
│  [Reset Button]     │
└─────────────────────┘

Tablet (601–1000px)
┌──────────────────────────────────────┐
│            Header                    │
├──────────────────────────────────────┤
│   [Input field]  [Generate Button]   │
├──────────────────────────────────────┤
│  [Idea Card 1]    [Idea Card 2]      │
├──────────────────────────────────────┤
│  [Idea Card 3]                       │
├──────────────────────────────────────┤
│  [Reset Button]                      │
└──────────────────────────────────────┘

Desktop (>1000px)
┌────────────────────────────────────────────────────────────┐
│                        Header                              │
├────────────────────────────────────────────────────────────┤
│     [Input field]              [Generate Button]           │
├────────────────────────────────────────────────────────────┤
│  [Idea Card 1]      [Idea Card 2]      [Idea Card 3]       │
├────────────────────────────────────────────────────────────┤
│  [Reset Button]                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Diagram

Shows the complete technology stack and dependencies.

```mermaid
graph TB
    subgraph Frontend["Frontend Layer"]
        direction TB
        HTML["HTML5<br/>(Markup)"]
        CSS["CSS3<br/>(Styling)"]
        JS["ECMAScript 2020+<br/>(Application Logic)"]
    end

    subgraph FrontendLibs["Frontend Libraries (Optional)"]
        direction TB
        Alpine["Alpine.js (if used)<br/>CDN-loaded, <50KB"]
    end

    subgraph Browser["Browser APIs"]
        direction TB
        Fetch["Fetch API<br/>(HTTP requests)"]
        LocalStorage["localStorage<br/>(Persistence)"]
        DOM["DOM API<br/>(Manipulation)"]
    end

    subgraph Backend["Backend (Node.js)"]
        direction TB
        Express["Express.js<br/>(Web framework)"]
        Cors["CORS middleware<br/>(Cross-origin requests)"]
        DotEnv["dotenv<br/>(Env config)"]
    end

    subgraph BackendLibs["Backend Libraries"]
        direction TB
        OpenAI["OpenAI SDK<br/>(LLM client)"]
        Axios["Axios (optional)<br/>(HTTP client)"]
    end

    subgraph LLMProvider["LLM Provider"]
        direction TB
        OpenAIAPI["OpenAI API<br/>(GPT-4)"]
        Anthropic["Anthropic (future)<br/>(Claude)"]
    end

    subgraph Deployment["Deployment"]
        direction TB
        Netlify["Netlify / Vercel<br/>(Frontend CDN)"]
        Render["Render / Heroku<br/>(Backend server)"]
    end

    Frontend --> FrontendLibs
    Frontend --> Browser
    Browser --> Fetch

    Fetch -->|HTTP calls| Backend
    Backend --> Express
    Express --> Cors
    Express --> DotEnv

    Backend --> BackendLibs
    BackendLibs --> OpenAI

    OpenAI -->|API calls| LLMProvider
    LLMProvider --> OpenAIAPI
    LLMProvider --> Anthropic

    Frontend -->|Deploy| Netlify
    Backend -->|Deploy| Render
```

---

## Conclusion

These diagrams provide visual representations of the BMAD Idea Launcher architecture at multiple levels of abstraction:

- **System Context** — External dependencies (user, browser, backend, LLM)
- **Container** — Major components and communication
- **Component** — Frontend and backend component trees
- **Code** — File organization and modules
- **Data Model** — Schema and data flow
- **Deployment** — Production infrastructure
- **Request-Response** — Complete user journey
- **Error Handling** — Failure scenarios
- **State Transitions** — UI state machine
- **Responsive Design** — Layout adaptation
- **Technology Stack** — All dependencies

Use these diagrams to onboard new team members, communicate design decisions, and verify implementation against the architecture.
