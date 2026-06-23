# Edge Cases & Corner Scenarios

> Comprehensive catalog of edge cases for the AI-Powered Restaurant Recommendation System.
> Organized by architectural layer as defined in [architecture.md](file:///Users/iamprince/Desktop/Zomato-milestone-1/architecture.md).

---

## 1. Data Ingestion Layer

### 1.1 Dataset Loading (`DatasetLoader`)

| # | Scenario | Expected Behavior |
|---|---|---|
| DL-01 | Hugging Face API is unreachable (network down) | Attempt to load from local cache; if no cache exists, raise a clear error with retry instructions. |
| DL-02 | Hugging Face dataset has been deleted or renamed | Catch `DatasetNotFoundError`; display a human-readable message identifying the missing dataset. |
| DL-03 | Hugging Face rate limits the download (HTTP 429) | Retry with exponential backoff (max 3 attempts); fall back to cached copy if available. |
| DL-04 | Local cache file is corrupted (partial download, invalid parquet) | Detect read failure, delete the corrupted cache, re-download from Hugging Face. |
| DL-05 | Dataset schema changes upstream (columns renamed/removed) | Preprocessor should fail fast with a descriptive error listing expected vs. actual columns. |
| DL-06 | Dataset is empty (0 rows) | Raise an error at startup: *"Dataset loaded but contains no rows."* |
| DL-07 | Disk is full — cannot write cache | Catch `OSError`; log a warning and proceed with in-memory-only data (skip caching). |
| DL-08 | Multiple simultaneous processes try to write the same cache file | Use atomic write (write to a temp file, then rename) to avoid corrupt partial writes. |

### 1.2 Data Preprocessing (`DataPreprocessor`)

| # | Scenario | Expected Behavior |
|---|---|---|
| DP-01 | `rating` column contains non-numeric strings (e.g., `"NEW"`, `"-"`, `"N/A"`) | Coerce to `NaN`; either drop or impute with a configurable default (e.g., `0.0`). |
| DP-02 | `cost_for_two` is `null`, `0`, or negative | Treat as invalid; drop the row or assign to `"unknown"` budget tier. |
| DP-03 | `cuisines` field is empty string, `null`, or `"NA"` | Normalize to an empty list `[]`; these restaurants should still appear when no cuisine filter is set. |
| DP-04 | `cuisines` contains malformed separators (e.g., `"Italian;Chinese"`, `"Italian / Chinese"`) | Support multiple delimiter patterns (`","`, `"/"`, `";"`) during parsing. |
| DP-05 | `cuisines` has trailing/leading whitespace or inconsistent casing (`" italian "`, `"ITALIAN"`) | Trim whitespace and title-case all cuisine tokens. |
| DP-06 | `location` is `null` or empty string | Drop the row — location is essential for filtering. Log the count of dropped rows. |
| DP-07 | `location` has inconsistent casing or aliases (`"bangalore"`, `"Bengaluru"`, `"BANGALORE"`) | Normalize via title-case and apply an alias map (`{"Bengaluru": "Bangalore", ...}`). |
| DP-08 | `name` is `null` or empty | Drop the row or assign a placeholder like `"Unknown Restaurant"`. |
| DP-09 | Duplicate restaurant entries (same name + location + cuisine) | De-duplicate keeping the entry with the highest votes or most recent data. |
| DP-10 | `votes` is `null` or negative | Default to `0`. |
| DP-11 | `rating` is outside `[0.0, 5.0]` (e.g., `5.5`, `-1.0`) | Clamp to `[0.0, 5.0]` or drop the row. |
| DP-12 | `cost_for_two` is extremely large (e.g., `999999`) | Keep it but flag as `"high"` budget tier; optionally log an outlier warning. |
| DP-13 | Dataset contains restaurants from unexpected countries/cities not in the expected scope | Allow all locations — the filter will handle scope; but log a warning if location distribution is unexpected. |

### 1.3 Budget Tier Derivation

| # | Scenario | Expected Behavior |
|---|---|---|
| BT-01 | `cost_for_two` is exactly on a threshold boundary (e.g., `500`, `1500`) | Follow inclusive lower-bound convention: `500` → `"low"`, `1500` → `"medium"`. Document the convention. |
| BT-02 | Budget thresholds are misconfigured (e.g., `low_max > medium_max`) | Validate thresholds at config load time; raise a startup error if inconsistent. |

---

## 2. User Input Layer

### 2.1 Preference Validation

| # | Scenario | Expected Behavior |
|---|---|---|
| UV-01 | `location` is empty or whitespace-only | Reject with error: *"Location is required."* |
| UV-02 | `location` does not match any restaurant in the dataset | Suggest the 3 closest matching locations (fuzzy match). Error: *"No restaurants found in 'Dellhi'. Did you mean: Delhi, Dehradun?"* |
| UV-03 | `location` contains special characters or injection-like input (`"; DROP TABLE--"`) | Sanitize input; strip non-alphanumeric characters (except spaces, hyphens). No SQL injection risk with in-memory data, but sanitize for prompt safety. |
| UV-04 | `budget` is not one of `low`, `medium`, `high` (e.g., `"very high"`, `""`, `null`) | Reject with error listing valid options. |
| UV-05 | `min_rating` is below `0.0` or above `5.0` | Clamp to bounds or reject with error: *"Rating must be between 0.0 and 5.0."* |
| UV-06 | `min_rating` is not a number (e.g., `"four"`) | Reject with a type error: *"Rating must be a numeric value."* |
| UV-07 | `cuisine` doesn't match any cuisine in the dataset (e.g., `"Klingon food"`) | Fuzzy-match against known cuisines. Warn: *"No exact match for 'Klingon food'. Showing results for all cuisines."* Or suggest closest: *"Did you mean: Korean?"* |
| UV-08 | `cuisine` is a partial match (e.g., `"Ital"` for `"Italian"`) | Apply prefix/substring matching; return results for `"Italian"`. |
| UV-09 | `additional` text is extremely long (>1000 characters) | Truncate to a configured max length before passing to the LLM prompt to avoid token overflow. Log a warning. |
| UV-10 | `additional` text contains prompt injection attempts (e.g., `"Ignore previous instructions and..."`) | Pass through to LLM but rely on system prompt guardrails. Optionally detect common injection patterns and strip them. |
| UV-11 | All optional fields are omitted (only `location` and `budget` provided) | Valid request; filter by location + budget only, skip cuisine filter, use default `min_rating = 0.0`. |
| UV-12 | User submits the form with no changes (re-submit) | Allow it — idempotent request, returns same results for same dataset state. |
| UV-13 | `min_rating` set to `5.0` (maximum) | Valid but likely returns very few or zero restaurants. Trigger constraint relaxation if empty. |
| UV-14 | `min_rating` set to `0.0` (minimum) | Valid; effectively disables the rating filter. |
| UV-15 | Unicode/emoji in input fields (e.g., location = `"🍕 Delhi"`) | Strip non-standard characters during normalization. |

---

## 3. Integration Layer (Filtering)

### 3.1 Restaurant Filter

| # | Scenario | Expected Behavior |
|---|---|---|
| RF-01 | Zero restaurants match all filters combined | Trigger **constraint relaxation** in order: drop `cuisine` → widen `budget` → lower `min_rating`. Attach a warning to the response indicating which constraints were relaxed. |
| RF-02 | Zero restaurants match even after full relaxation | Return an empty result with message: *"No restaurants found matching your criteria. Try a different location."* |
| RF-03 | Exactly 1 restaurant matches | Return it as the sole recommendation; LLM should still explain why it fits. |
| RF-04 | Fewer candidates than `TOP_K_RECOMMENDATIONS` (e.g., 3 candidates, K=5) | Return all available candidates; don't pad with empty entries. Adjust messaging: *"Found 3 restaurants matching your preferences."* |
| RF-05 | More than `MAX_CANDIDATES_FOR_LLM` match (e.g., 500 restaurants in the location) | Cap at `MAX_CANDIDATES_FOR_LLM` (15–20) after sorting by rating/votes. Log the total matched count for transparency. |
| RF-06 | Multiple restaurants have identical ratings and votes (tie) | Apply deterministic tie-breaking: alphabetical by name, then by `id`. Ensure results are stable across requests. |
| RF-07 | Location filter matches multiple similar locations (e.g., "New Delhi" vs "Delhi") | Use contains/substring matching or alias map to unify. Alternatively, match all locations containing the query. |
| RF-08 | Cuisine filter matches a restaurant with multiple cuisines (e.g., searching `"Italian"` matches a restaurant with `["Italian", "Chinese"]`) | Include it — any-match semantics: restaurant is included if any of its cuisines matches the filter. |
| RF-09 | Budget filter mismatch: user selects `"low"` but all good restaurants in the area are `"high"` | Constraint relaxation kicks in; surface a message: *"No low-budget options found. Showing medium and high budget restaurants."* |
| RF-10 | Dataset has restaurants with `rating = 0.0` and `min_rating = 0.0` | Include them — `0.0 ≥ 0.0` is valid. These are likely unrated rather than terrible. |

---

## 4. Recommendation Engine (LLM Layer)

### 4.1 Prompt Builder

| # | Scenario | Expected Behavior |
|---|---|---|
| PB-01 | Candidate list is very large (hitting token limits) | Truncate candidate list to `MAX_CANDIDATES_FOR_LLM`; use compact JSON (remove optional fields like `rest_type` if needed to stay within context window). |
| PB-02 | `additional` preferences contain conflicting requirements (e.g., `"cheap but luxurious"`) | Pass through to LLM; let the model resolve conflicts in its reasoning. It may note the contradiction in the explanation. |
| PB-03 | Candidate restaurants have missing fields (e.g., no `votes`) | Omit missing fields from the candidate JSON or use sensible defaults (`votes: 0`). Don't let `null` values break JSON parsing. |
| PB-04 | Restaurant names contain special characters or quotes that break JSON | Ensure proper JSON escaping of all string fields before embedding in the prompt. |
| PB-05 | Only 1 candidate is passed to the LLM | LLM should still provide an explanation for why it's a good match. Prompt should handle singular case gracefully. |

### 4.2 Groq LLM Client

| # | Scenario | Expected Behavior |
|---|---|---|
| GC-01 | `GROQ_API_KEY` is missing or empty | Fail fast at startup with error: *"GROQ_API_KEY is not set. Please configure it in your .env file."* |
| GC-02 | `GROQ_API_KEY` is invalid/expired | Catch `AuthenticationError` from Groq SDK; return heuristic fallback with message: *"AI explanation unavailable — invalid API key."* |
| GC-03 | Groq API returns HTTP 429 (rate limit) | Retry with exponential backoff (1s → 2s → 4s, max 3 attempts). If all retries fail, fall back to heuristic ranking. |
| GC-04 | Groq API returns HTTP 500/502/503 (server error) | Retry once; then fall back to heuristic ranking with message: *"AI service temporarily unavailable."* |
| GC-05 | Groq API times out (>30s response time) | Set a request timeout (e.g., 30s). On timeout, fall back to heuristic ranking. |
| GC-06 | Network connection drops mid-request | Catch `ConnectionError`; fall back to heuristic ranking. |
| GC-07 | Selected model (`llama-3.3-70b-versatile`) is unavailable on Groq | Try fallback model (`llama-3.1-8b-instant`). If both fail, fall back to heuristic ranking. |
| GC-08 | Response exceeds max output tokens (truncated JSON) | Detect incomplete JSON; retry with a shorter candidate list or simpler prompt. |
| GC-09 | Groq returns an empty response body | Treat as LLM failure; fall back to heuristic ranking. |
| GC-10 | Groq response contains `finish_reason: "length"` (output truncated) | Detect truncation; retry with reduced `TOP_K_RECOMMENDATIONS` or fall back. |

### 4.3 Response Parser

| # | Scenario | Expected Behavior |
|---|---|---|
| RP-01 | LLM returns valid JSON but wrong schema (e.g., missing `recommendations` key) | Raise a parse error; retry with lower temperature (0.1). If retry fails, fall back. |
| RP-02 | LLM returns JSON with extra/unexpected fields | Ignore unknown fields; extract only expected fields. |
| RP-03 | LLM returns `recommendations` with an `id` that doesn't match any candidate | Skip that recommendation entry; log a warning. If all IDs are invalid, fall back. |
| RP-04 | LLM returns duplicate `id` values in recommendations | De-duplicate, keeping the first occurrence. |
| RP-05 | LLM returns fewer recommendations than requested `TOP_K` | Accept whatever is returned (e.g., 3 of 5). Don't pad with empty entries. |
| RP-06 | LLM returns more recommendations than requested `TOP_K` | Truncate to `TOP_K`, keeping the top-ranked ones. |
| RP-07 | LLM returns plain text instead of JSON (ignores `response_format`) | Attempt to extract JSON from the text (regex for `{...}`). If extraction fails, retry then fall back. |
| RP-08 | LLM returns JSON wrapped in markdown code fences (` ```json ... ``` `) | Strip code fence markers before parsing. |
| RP-09 | LLM `explanation` field is empty or null for a recommendation | Use a generic fallback explanation: *"This restaurant matches your preferences."* |
| RP-10 | LLM fabricates a restaurant not in the candidate list | Detect by checking `id`/`name` against candidates. Drop fabricated entries; log a warning. |
| RP-11 | LLM `rank` values are not sequential (e.g., `[1, 3, 5]`) | Re-number ranks sequentially starting from 1, preserving the LLM's order. |
| RP-12 | LLM returns recommendations in random order (ranks not sorted) | Sort by the `rank` field before returning. |
| RP-13 | LLM `summary` contains hallucinated facts (wrong city, wrong cuisine) | Cannot fully prevent; but cross-validate summary claims against actual filter/candidate data where feasible. |

### 4.4 Heuristic Fallback

| # | Scenario | Expected Behavior |
|---|---|---|
| HF-01 | All LLM retries exhausted | Return top-K candidates sorted by `rating DESC`, `votes DESC` with explanation: *"Ranked by rating and popularity. AI explanation temporarily unavailable."* |
| HF-02 | Fallback candidates have identical ratings and votes | Apply deterministic tie-breaking (alphabetical by name). |

---

## 5. Output Display Layer

### 5.1 Streamlit UI

| # | Scenario | Expected Behavior |
|---|---|---|
| UI-01 | User submits while dataset is still loading | Show a loading spinner: *"Loading restaurant data… This may take a moment on first run."* Block form submission until data is ready. |
| UI-02 | LLM response takes >10 seconds | Show a progress indicator: *"Our AI is analyzing restaurants for you…"* Don't timeout the UI. |
| UI-03 | Very long restaurant name overflows card layout | Truncate with ellipsis (`...`) after a configurable character limit; show full name on hover/tooltip. |
| UI-04 | Very long AI explanation overflows card | Use expandable/collapsible text (Streamlit `expander`). Show first 2–3 lines with "Read more". |
| UI-05 | Cuisine list is very long (>5 cuisines) | Show first 3 cuisines + `"+N more"` badge. |
| UI-06 | User rapidly clicks "Get Recommendations" multiple times | Debounce or disable the button while a request is in progress. Prevent duplicate API calls. |
| UI-07 | Browser window is very narrow (mobile viewport) | Cards should stack vertically; text should wrap cleanly. Ensure minimum-width usability. |
| UI-08 | Summary banner is `null` (LLM didn't generate one) | Simply hide the summary banner section. Don't show an empty banner. |
| UI-09 | Constraint relaxation was applied | Show a warning banner above results: *"⚠ We relaxed your cuisine filter to find more results."* |
| UI-10 | Zero results after all relaxation | Show an empty state with constructive suggestions: *"No restaurants found. Try selecting a different location or lowering your minimum rating."* |
| UI-11 | Network error during recommendation fetch | Show error toast/banner: *"Something went wrong. Please check your connection and try again."* Keep the form populated so the user can retry. |

### 5.2 Optional REST API

| # | Scenario | Expected Behavior |
|---|---|---|
| API-01 | `POST /recommend` with malformed JSON body | Return `400 Bad Request` with validation error details. |
| API-02 | `POST /recommend` with empty body | Return `422 Unprocessable Entity` listing required fields. |
| API-03 | `GET /health` before dataset is loaded | Return `503 Service Unavailable` with `{"status": "loading", "dataset_loaded": false}`. |
| API-04 | Concurrent requests exceed Groq rate limit | Queue or reject excess requests with `429 Too Many Requests` and a `Retry-After` header. |
| API-05 | Extremely large request payload (>1MB) | Reject with `413 Payload Too Large`. |

---

## 6. Configuration & Environment

| # | Scenario | Expected Behavior |
|---|---|---|
| CF-01 | `.env` file is missing entirely | Fall back to environment variables. If `GROQ_API_KEY` is not set anywhere, fail fast at startup. |
| CF-02 | `GROQ_MODEL` is set to an unsupported model name | Catch model-not-found error from Groq; try fallback model. If that also fails, surface error. |
| CF-03 | `MAX_CANDIDATES_FOR_LLM` is set to `0` or negative | Validate at config load; raise error: *"MAX_CANDIDATES_FOR_LLM must be a positive integer."* |
| CF-04 | `TOP_K_RECOMMENDATIONS` > `MAX_CANDIDATES_FOR_LLM` | Clamp `TOP_K` to `MAX_CANDIDATES_FOR_LLM` and log a warning. |
| CF-05 | `GROQ_TEMPERATURE` is outside `[0.0, 2.0]` | Clamp to valid range and log a warning. |
| CF-06 | `DATA_CACHE_PATH` points to a read-only directory | Catch `PermissionError`; log warning and proceed without caching. |

---

## 7. Cross-Cutting Concerns

### 7.1 Concurrency & State

| # | Scenario | Expected Behavior |
|---|---|---|
| CC-01 | Streamlit reruns the script on every interaction (its execution model) | Ensure dataset is loaded once and cached in `st.cache_resource` / `st.session_state`. Don't re-download on every button click. |
| CC-02 | Multiple Streamlit users share the same server process | Repository is read-only, so sharing is safe. LLM calls are stateless per-request. No cross-user data leakage. |

### 7.2 Security

| # | Scenario | Expected Behavior |
|---|---|---|
| SC-01 | User input injected into LLM prompt to override system instructions | System prompt includes guardrails: *"Only recommend from the provided candidate list."* Additional: detect common injection patterns. |
| SC-02 | API key accidentally logged in plaintext | Logging config must redact any value matching `GROQ_API_KEY` pattern. Never log the full prompt in production. |
| SC-03 | `.env` file committed to Git | `.gitignore` must include `.env`. Pre-commit hook recommended. |

### 7.3 Performance

| # | Scenario | Expected Behavior |
|---|---|---|
| PF-01 | Dataset is very large (>100K rows) and filtering is slow | Use pandas vectorized operations, not Python loops. Profile and optimize if `filter()` takes >500ms. |
| PF-02 | LLM latency is high (>5s) | Show progressive UI feedback. Log latency. Consider caching repeated identical queries in session. |
| PF-03 | User makes the exact same query twice in a session | Optionally cache the `RecommendationResponse` keyed on `(location, budget, cuisine, min_rating, additional)` in session state. |

---

## Edge Case Priority Matrix

| Priority | Category | Count | Rationale |
|---|---|---|---|
| 🔴 **Critical** | LLM failures (GC-01 to GC-10), Zero-result filtering (RF-01, RF-02) | ~12 | These break the core user experience if unhandled. |
| 🟠 **High** | Data preprocessing (DP-01 to DP-06), Response parsing (RP-01 to RP-10) | ~16 | Dirty data or bad LLM output causes silent incorrect results. |
| 🟡 **Medium** | Input validation (UV-01 to UV-10), UI display (UI-01 to UI-11) | ~21 | UX degradation but app doesn't crash. |
| 🟢 **Low** | Configuration (CF-01 to CF-06), Performance (PF-01 to PF-03) | ~9 | Rare in typical development; important for production. |

---

## Related Documents

- [architecture.md](file:///Users/iamprince/Desktop/Zomato-milestone-1/architecture.md) — system architecture and component design
- [context.md](file:///Users/iamprince/Desktop/Zomato-milestone-1/context.md) — product requirements and workflow
- [problemStatement.txt](file:///Users/iamprince/Desktop/Zomato-milestone-1/problemStatement.txt) — original problem statement
