# Test & Deployment Plan (Epic 6)

## Testing levels
| Level | Where | What |
|-------|-------|------|
| Unit | `tests/test_nutrition.py`, `test_freshness.py`, `test_hygiene.py`, `test_planner.py`, `test_kitchen.py` | Deterministic logic |
| API | `tests/test_api.py` | Endpoints via FastAPI TestClient (dummy backend) |
| Model eval (manual) | - | Accuracy on Food-101 test split, freshness dataset, PPE video clips |

Run: `pytest -q`

## Deployment
1. `cp .env.example .env`, set `FOODVERSE_BACKEND=hf` and optionally `ANTHROPIC_API_KEY`.
2. `docker compose up --build` -> API http://localhost:8000/docs, UI http://localhost:8501.
3. For production: put behind HTTPS reverse proxy, add auth, set upload size limits, pin model versions.

## Known limitations
- Freshness is a heuristic until a trained model is supplied; lighting affects it.
- Dummy backend returns fixed predictions - for demos/tests only.
- Hygiene detection needs custom PPE weights for real use; without them the detector reports "no detector configured".
