                User / AI Agent
                      │
                      ▼
            Prompt Gateway API
                      │
      ┌───────────────┼────────────────┐
      │               │                │
      ▼               ▼                ▼
 Rule Engine     ML Classifier    Local LLM
      │               │                │
      └───────────────┼────────────────┘
                      │
            Validation Decision
                      │
          ┌───────────┴───────────┐
          │                       │
       Reject                 Approved
          │                       │
      Return Error          Prompt Processor
                                  │
                                  ▼
                         OpenAI / Claude /
                       Bedrock / Gemini etc.