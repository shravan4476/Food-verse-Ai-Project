# Software Requirements Specification - Food Verse AI (Epic 1)

## 1. Purpose
Food decisions are fragmented: calories are estimated by hand, freshness is judged by eye, hygiene is checked
periodically, and recipes are static. Food Verse AI unifies vision, video and LLM reasoning into one modular platform.

## 2. Scope
Five capabilities: food recognition & nutrition, freshness/spoilage detection, restaurant hygiene monitoring,
smart cooking assistance, personalized meal planning - exposed through a REST API and a web UI.

## 3. Users
| Persona | Needs |
|---------|-------|
| Home user | Quick calorie info, "is this still good?", what to cook tonight, weekly plan |
| Fitness / diet follower | Goal-based calories & macros, allergy-safe plans |
| Restaurant manager | Continuous hygiene compliance evidence from kitchen video |

## 4. Functional requirements
| ID | Requirement | Epic |
|----|-------------|------|
| FR-1 | Upload a food photo, get top-k dish predictions with confidence | 2 |
| FR-2 | Map the dish and portion (grams) to calories, protein, carbs, fat, fibre | 2 |
| FR-3 | Upload a produce photo, get freshness score (0-100), label and reasons | 3 |
| FR-4 | Upload kitchen video, get PPE compliance score and violation timeline | 4 |
| FR-5 | Suggest recipes from available ingredients | 4 |
| FR-6 | Step-by-step cooking guidance with timers | 4 |
| FR-7 | Generate 7-day plan from age, sex, height, weight, activity, goal | 5 |
| FR-8 | Respect dietary preferences and allergies in every plan | 5 |
| FR-9 | Web UI covering every module | 6 |
| FR-10 | REST API with OpenAPI docs | 6 |

## 5. Non-functional requirements
- **Transparency**: every result shows confidence and the reasoning behind it.
- **User control**: no uploads are persisted by default; no account required.
- **Modularity**: each module is independently replaceable (model backends are pluggable).
- **Performance**: image endpoints respond in < 3 s on CPU with the dummy/light backend; video is sampled, not fully decoded.
- **Graceful degradation**: LLM features fall back to rule-based output when no API key is set.
- **Safety**: freshness/hygiene outputs are advisory, never certifications.

## 6. Constraints & assumptions
Python 3.10+, CPU-only baseline, Food-101 classes for recognition, small bundled nutrition and recipe datasets
(extend for production).

## 7. Environment setup
See `scripts/setup_env.sh`, `requirements-core.txt`, `requirements.txt`, `.env.example`, `Dockerfile`.
