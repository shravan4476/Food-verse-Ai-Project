# Food Verse AI

A multimodal, AI-powered food intelligence platform that combines computer vision, video analysis and
LLM-driven reasoning for:

| Epic | Module | Folder |
|------|--------|--------|
| 1 | Requirements & environment setup | `docs/`, `requirements.txt`, `Dockerfile`, `scripts/` |
| 2 | Food recognition & nutrition | `app/modules/food_recognition/` |
| 3 | Freshness & spoilage detection | `app/modules/freshness/` |
| 4 | Restaurant hygiene & smart kitchen | `app/modules/hygiene/`, `app/modules/kitchen/` |
| 5 | Personalized meal planner | `app/modules/planner/` |
| 6 | Interface, testing, deployment | `app/main.py`, `ui/`, `tests/`, `Dockerfile` |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-core.txt                    # light install (API, planner, freshness, tests)
pip install -r requirements.txt                         # full install (adds PyTorch, transformers, OpenCV)
cp .env.example .env                                    # then edit values

uvicorn app.main:app --reload                           # API  -> http://localhost:8000/docs
streamlit run ui/streamlit_app.py                       # UI   -> http://localhost:8501
pytest                                                  # run tests
```

Set `FOODVERSE_BACKEND=dummy` in `.env` to try the API without downloading any vision model.
Set `ANTHROPIC_API_KEY` to enable LLM reasoning (cooking assistant, plan explanations); without it,
the system falls back to deterministic rule-based answers.

## How it works

- **Food recognition**: a Food-101 image classifier (Hugging Face `nateraw/food`) returns top-k dishes,
  which are mapped to calories/macros in `data/nutrition_db.csv` and scaled by portion size.
- **Freshness**: an explainable colour/texture analysis (browning, dark spots, saturation loss, texture
  noise) produces a 0-100 score with reasons. Swap in a trained CNN via `FreshnessDetector.model`.
- **Hygiene**: video frames are sampled, a pluggable detector (YOLO weights optional) finds PPE items
  (gloves, hairnet, apron, mask), and a rules engine produces a compliance score and violation timeline.
- **Smart kitchen**: ingredient-based recipe suggestions and step-by-step guidance with timers (LLM or fallback).
- **Meal planner**: Mifflin-St Jeor BMR -> TDEE -> goal calories/macros -> 7-day plan from `data/recipes.json`,
  respecting dietary restrictions and allergies.

## Important notes

- Freshness and hygiene outputs are **decision-support estimates, not food-safety certifications**.
  Always follow official food safety guidance when in doubt.
- Nutrition values are approximate per-100g reference data; extend `data/nutrition_db.csv` for your region.
- Users keep control: nothing is stored by default, and every result includes its confidence and reasoning.

## Project layout

```
food_verse_ai/
  app/            FastAPI backend + modules
  ui/             Streamlit front end
  data/           nutrition DB, recipes
  docs/           SRS, architecture, backlog, test plan
  tests/          pytest suite
  scripts/        environment setup
```
