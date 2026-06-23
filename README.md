# 🍽️ AI Restaurant Recommender

An AI-powered restaurant recommendation system built on the Zomato dataset (40,000+ restaurants). Uses deterministic filtering combined with Groq's LLM (`llama-3.3-70b-versatile`) to deliver personalized, explainable restaurant recommendations.

## ✨ Features

- **Smart Filtering** — Deterministic pipeline filters by location, budget, cuisine, and rating before the LLM sees the data
- **AI-Powered Ranking** — Groq LLM ranks and explains why each restaurant is recommended
- **Constraint Relaxation** — Automatically broadens filters when no exact matches are found, with transparent warnings
- **Graceful Fallback** — Falls back to heuristic ranking when the LLM is unavailable
- **Local Caching** — Downloads the dataset once and caches it as Parquet for fast reloads

## 🏗️ Architecture

```
UserPreferences
  → RestaurantFilter.filter(prefs)        → candidates (≤15)
  → PromptBuilder.build(prefs, candidates) → structured prompt
  → LLMClient.complete(prompt)             → raw JSON
  → ResponseParser.parse(raw)              → validated response
  → RecommendationEnricher.enrich(parsed)  → RecommendationResponse
```

### Project Structure

```
zomato-milestone-1/
├── src/
│   ├── config.py                  # Centralized settings (pydantic-settings)
│   ├── main.py                    # Entry point (--mode cli/streamlit/api)
│   ├── models/
│   │   ├── restaurant.py          # Restaurant data model
│   │   ├── preferences.py         # UserPreferences + validation
│   │   └── recommendation.py      # Recommendation response models
│   ├── data/
│   │   ├── loader.py              # HF dataset download + caching
│   │   ├── preprocessor.py        # Column mapping, type coercion, normalization
│   │   └── repository.py          # In-memory query interface
│   ├── services/
│   │   ├── filter.py              # Deterministic filter + constraint relaxation
│   │   ├── prompt_builder.py      # Structured LLM prompt construction
│   │   ├── llm_client.py          # Groq API adapter with retry & rate-limit handling
│   │   └── recommendation.py      # Orchestrator + parser + enricher
├── docs/
│   ├── architecture.md            # System architecture
│   ├── context.md                 # Project context
│   └── problemStatement.txt       # Original problem statement
├── data/                          # Cached dataset (gitignored)
├── .env.example                   # Environment variable template
├── .gitignore
└── requirements.txt
```

## 🚀 Setup

### 1. Clone & Install

```bash
git clone <repository-url>
cd zomato-milestone-1

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com/).

### 3. Verify Recommendation Pipeline

```bash
python3 -m src.main
```

This downloads the dataset from Hugging Face (first run only), preprocesses it, filters using default preferences, and generates an AI recommendation.

## 🔧 Configuration

All settings are managed via environment variables (`.env` file):

| Variable                  | Default                                           | Description                        |
|---------------------------|---------------------------------------------------|------------------------------------|
| `GROQ_API_KEY`            | *(required)*                                      | Groq API key for LLM calls         |
| `GROQ_MODEL`              | `llama-3.3-70b-versatile`                         | LLM model identifier               |
| `GROQ_TEMPERATURE`        | `0.3`                                             | Sampling temperature                |
| `HF_DATASET_NAME`         | `ManikaSaini/zomato-restaurant-recommendation`    | Hugging Face dataset ID             |
| `DATA_CACHE_PATH`         | `./data`                                          | Local cache directory               |
| `MAX_CANDIDATES_FOR_LLM`  | `15`                                              | Max restaurants sent to LLM         |
| `TOP_K_RECOMMENDATIONS`   | `5`                                               | Final recommendations count         |

## 🛡️ Error Handling

| Scenario                    | Behavior                                                     |
|-----------------------------|--------------------------------------------------------------|
| No restaurants match        | Relaxes constraints: cuisine → budget → min_rating           |
| LLM returns invalid JSON    | Retries with lower temperature; falls back to heuristic      |
| LLM timeout / rate limit    | Exponential backoff; returns heuristic ranking with notice    |
| Unknown location            | Suggests valid locations from dataset (fuzzy match)           |
| Dataset download fails      | Retries; shows clear error message                           |

## 📦 Tech Stack

| Layer        | Technology                      |
|--------------|--------------------------------|
| Data         | Hugging Face `datasets`, Pandas, PyArrow |
| Models       | Pydantic v2, pydantic-settings  |
| LLM          | Groq SDK (`llama-3.3-70b-versatile`) |
| Config       | python-dotenv, pydantic-settings |
