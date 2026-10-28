# Product Backlog

## Epic 1 - Requirements Specification & Environment Setup
- US-1.1 As a developer I can set up the project with one script. *AC: `scripts/setup_env.sh` creates venv and installs deps.*
- US-1.2 As a stakeholder I can read the SRS. *AC: `docs/01_requirements_spec.md` lists FRs/NFRs.*
- US-1.3 As a developer I can run the stack in Docker. *AC: `docker compose up` serves API :8000 and UI :8501.*

## Epic 2 - Food Recognition & Nutrition
- US-2.1 Upload a photo, see top-3 dishes with confidence. *AC: `/api/food/recognize`.*
- US-2.2 See calories/macros scaled by portion grams. *AC: nutrition lookup with unknown-food fallback.*
- Tasks: swap in a fine-tuned regional-cuisine model; add portion-size estimation; expand nutrition DB.

## Epic 3 - Freshness & Spoilage Detection
- US-3.1 Upload produce photo, get 0-100 score and label. *AC: `/api/freshness/analyze`.*
- US-3.2 See why (browning, dark spots, dullness). *AC: reasons list returned.*
- Tasks: collect labelled fresh/rotten dataset; train CNN; plug into `FreshnessDetector.model`.

## Epic 4 - Restaurant Hygiene & Smart Kitchen
- US-4.1 Upload kitchen video, get compliance score. *AC: `/api/hygiene/analyze`.*
- US-4.2 See timestamped violations. *AC: timeline in response.*
- US-4.3 Get recipes from my ingredients. *AC: `/api/kitchen/suggest`.*
- US-4.4 Get step-by-step guidance with timers. *AC: `/api/kitchen/guide`.*
- Tasks: train PPE YOLO model; add live-stream support; alerting.

## Epic 5 - Personalized Meal Planner
- US-5.1 Enter profile and goal, get daily calorie/macro targets. *AC: Mifflin-St Jeor + activity factor.*
- US-5.2 Get a 7-day plan avoiding allergens/restrictions. *AC: `/api/planner/generate`.*
- Tasks: grocery list; weekly progress feedback loop; larger recipe catalog.

## Epic 6 - Interface, Testing & Deployment
- US-6.1 Use every module from one web UI. *AC: `ui/streamlit_app.py` tabs.*
- US-6.2 Automated tests pass in CI. *AC: `pytest` green.*
- US-6.3 Deploy via Docker. *AC: `Dockerfile`, `docker-compose.yml`.*
