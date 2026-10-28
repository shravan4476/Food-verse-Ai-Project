# Architecture

```
                 +----------------------+
 Streamlit UI -->|  FastAPI  app/main.py |<-- REST clients
                 +----------+-----------+
     +------------+----------+-----------+-------------+
     |            |          |           |             |
 food_recognition freshness  hygiene   kitchen       planner
 (HF classifier   (colour/   (frame    (recipes +    (BMR/TDEE +
  + nutrition DB)  texture)   sampler + guidance)     recipe catalog)
                              PPE rules)
     |                                    |             |
     +------------- core/llm.py (optional Anthropic client, rule-based fallback) ---+
```

## Design principles
- **Pluggable backends**: `FOODVERSE_BACKEND=hf|dummy`; `PPEDetector` protocol for YOLO or any detector;
  `FreshnessDetector.model` hook for a trained CNN.
- **Lazy heavy imports**: torch, transformers and cv2 are imported only when used, so the core install stays light.
- **LLM as reasoning layer, not source of truth**: numbers (calories, scores) come from deterministic code; the LLM
  only explains or composes text, and every call has a rule-based fallback.
- **Stateless API**: uploads are processed in memory.

## Data flow examples
1. *Recognize*: image -> classifier -> top-k labels -> nutrition lookup x portion -> JSON.
2. *Hygiene*: video -> sample 1 frame / N sec -> detector -> per-frame PPE set -> rules -> score + violations.
3. *Plan*: profile -> BMR -> TDEE -> calorie/macro targets -> filter recipes -> greedy daily selection -> optional LLM summary.
