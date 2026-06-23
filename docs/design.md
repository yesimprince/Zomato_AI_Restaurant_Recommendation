# Frontend Design Specification — Zomato AI Recommender

> Extracted from Banani UI design export. This document is the single source of truth for the frontend implementation.

---

## 1. Design Tokens

### 1.1 Color Palette

| Token                     | Value      | Usage                                     |
|---------------------------|------------|-------------------------------------------|
| `--color-background`      | `#f9f9f8`  | Page background                           |
| `--color-foreground`      | `#111111`  | Primary text                              |
| `--color-border`          | `#e4e4e0`  | Borders, dividers                         |
| `--color-input`           | `#ffffff`  | Input field backgrounds                   |
| `--color-primary`         | `#e23744`  | Zomato red — buttons, accents, active     |
| `--color-primary-foreground` | `#ffffff` | Text on primary backgrounds              |
| `--color-secondary`       | `#fef2f3`  | Light red tint — selected chip/card bg    |
| `--color-muted`           | `#f1f0ee`  | Muted surfaces (slider track, filter bar) |
| `--color-muted-foreground`| `#888884`  | Secondary/helper text                     |
| `--color-sidebar`         | `#ffffff`  | Sidebar & header background               |
| `--color-card`            | `#ffffff`  | Recommendation card background            |
| `--color-rank-gold`       | `#f59e0b`  | Rank #1 badge                             |
| `--color-rank-silver`     | `#9ca3af`  | Rank #2 badge                             |
| `--color-rank-bronze`     | `#c97c4a`  | Rank #3 badge                             |
| `--color-success`         | `#16a34a`  | API connected dot, positive indicators    |
| `--color-ai-bg`           | `#f0f7ff`  | AI summary section background             |
| `--color-ai-border`       | `#bfdbfe`  | AI summary section border                 |

### 1.2 Typography

| Token             | Value  | Usage                                |
|-------------------|--------|--------------------------------------|
| `--font-body`     | Inter  | All body text                        |
| `--font-headings` | Inter  | Headings, brand text                 |
| `--text-xs`       | 11px   | Chip labels, micro-text              |
| `--text-sm`       | 13px   | Form labels, descriptions, metadata  |
| `--text-base`     | 14px   | Default body text                    |
| `--text-lg`       | 16px   | Section headings, brand name         |
| `--text-xl`       | 20px   | Card restaurant names, major titles  |

**Font import** (Google Fonts):
```
Inter:wght@100;200;300;400;500;600;700;800;900
```

### 1.3 Spacing

Base unit: `0.25rem` (4px). All spacing is multiples of this base.

| Usage             | Value     | Pixels |
|-------------------|-----------|--------|
| Tiny gap          | `0.5`     | 2px    |
| Small gap         | `1`       | 4px    |
| Medium gap        | `1.5`     | 6px    |
| Default gap       | `2`       | 8px    |
| Section gap       | `3`       | 12px   |
| Large gap         | `6`       | 24px   |
| Page padding      | `6`       | 24px   |
| Card padding      | `4`       | 16px   |

### 1.4 Border Radii

| Token          | Value  | Usage                         |
|----------------|--------|-------------------------------|
| `--radius-sm`  | 4px    | Small elements                |
| `--radius-md`  | 8px    | Inputs, budget selectors      |
| `--radius-lg`  | 12px   | Cards, buttons, brand badge   |
| `full`         | 9999px | Chips, status dot, slider     |

### 1.5 Shadows

| Name        | Value                                                    | Usage           |
|-------------|----------------------------------------------------------|-----------------|
| `shadow-sm` | `0 1px 3px rgb(0 0 0 / 0.1), 0 1px 2px rgb(0 0 0 / 0.1)` | Cards, slider thumb |

---

## 2. Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                         APP HEADER                                  │
│  [Z] Zomato AI Recommender                    ● API connected       │
├──────────────┬──────────────────────────────────────────────────────┤
│              │              ACTIVE FILTERS BAR                      │
│   PREFERENCE │  Filters: [Bangalore ✕] [₹500-₹1200 ✕] [4.0+ ✕]   │
│   SIDEBAR    ├──────────────────────────────────────────────────────┤
│   (320px)    │                                                      │
│              │  AI SUMMARY SECTION (blue)                           │
│  - Location  │  "Based on your preferences..."                     │
│  - Budget    │                                                      │
│  - Rating    ├──────────────────────────────────────────────────────┤
│  - Cuisine   │                                                      │
│  - Notes     │  RECOMMENDATION CARDS (vertically stacked)           │
│              │  ┌─────────────────────────────────────────────┐     │
│  [Find       │  │ #1 🥇  Restaurant Name         4.5 ★       │     │
│   Restaurants│  │        Italian, Continental                 │     │
│   ✨]        │  │        ₹1200 for two                        │     │
│              │  │        AI explanation text...               │     │
│              │  └─────────────────────────────────────────────┘     │
│              │  ┌─────────────────────────────────────────────┐     │
│              │  │ #2 🥈  Restaurant Name         4.3 ★       │     │
│              │  │        ...                                  │     │
│              │  └─────────────────────────────────────────────┘     │
│              │                                                      │
└──────────────┴──────────────────────────────────────────────────────┘
```

- **Overall**: `flex-col`, min-height 900px, `bg-background`, `font-body` (Inter)
- **Header**: Full width, sticky/top
- **Body**: `flex` row — sidebar (fixed 320px) + main content (flex-1, scrollable)

---

## 3. Component Specifications

### 3.1 AppHeader

```
┌───────────────────────────────────────────────────────────┐
│ [Z]  Zomato  AI Recommender              ● API connected  │
└───────────────────────────────────────────────────────────┘
```

| Property       | Value                                        |
|----------------|----------------------------------------------|
| Background     | `--color-sidebar` (#fff)                     |
| Padding        | `px-6 py-4` (24px horizontal, 16px vertical) |
| Border         | 1px bottom, `--color-border`                 |
| Layout         | `flex items-center justify-between`          |

**Left section** (`flex items-center gap-3`):
- **Brand badge**: 32×32px, `rounded-lg`, `bg-primary` → white bold "Z" centered
- **Brand text**: "Zomato" in `font-headings font-semibold text-lg text-foreground`, followed by " AI Recommender" in `font-body text-lg text-muted-foreground font-normal`

**Right section** (`flex items-center gap-2`):
- **Status dot**: 8×8px circle, `bg-success` (#16a34a) when connected
- **Status text**: `text-xs text-muted-foreground` — "API connected · localhost:8000"

---

### 3.2 PreferenceSidebar

| Property       | Value                                        |
|----------------|----------------------------------------------|
| Width          | `w-80` (320px)                               |
| Background     | `--color-sidebar` (#fff)                     |
| Border         | 1px right, `--color-border`                  |
| Layout         | `flex flex-col`, full height                 |

**Header** (`px-6 pt-6 pb-4`):
- Title: "YOUR PREFERENCES" — `text-xs font-semibold uppercase tracking-widest text-muted-foreground`
- Subtitle: "Fill in the details below to get AI-curated picks." — `text-sm text-muted-foreground`

**Form fields** (`px-6 flex flex-col gap-6 pb-6`):

#### 3.2.1 Location Dropdown

- **Label**: icon (map-pin, 14px) + "Location" (`text-sm font-semibold`) + red asterisk
- **Input**: `bg-input border border-border rounded-md px-3 py-2.5 text-sm` with chevron-down icon
- Default value: "Bangalore"

#### 3.2.2 Budget Selector

- **Label**: icon (wallet, 14px) + "Budget" + red asterisk
- **Three buttons** in `flex gap-2`, each `flex-1 rounded-md border px-2 py-2 flex-col items-center gap-0.5`:
  - **Unselected**: `border-border bg-input`, text in `text-foreground`
  - **Selected** (e.g. "Medium"): `border-primary bg-secondary`, text in `text-primary`
  - Each button shows tier name (`text-sm font-semibold`) + price range (`text-xs text-muted-foreground`)

| Tier   | Label      | Range        |
|--------|------------|--------------|
| Low    | Low        | Under ₹500   |
| Medium | Medium     | ₹500–₹1200   |
| High   | High       | Above ₹1200  |

#### 3.2.3 Minimum Rating Slider

- **Label**: icon (star, 14px) + "Minimum Rating" + red asterisk + value on the right (`ml-auto text-primary font-bold text-sm`)
- **Track**: `h-1.5 bg-muted rounded-full`, relative positioning
- **Fill**: absolute, left-0, same height, `bg-primary rounded-full`, width = `(value/5 * 100)%`
- **Thumb**: absolute, centered vertically, 16×16px circle, `bg-primary border-2 border-primary-foreground shadow-sm`, positioned at fill end
- **Range labels**: `flex justify-between text-xs text-muted-foreground` — "0.0" and "5.0"
- Default value: 4.0 (80%)

#### 3.2.4 Cuisine Chips

- **Label**: icon (utensils, 14px) + "Cuisine" + "(optional)" in `text-xs text-muted-foreground font-normal ml-1`
- **Chips** in `flex flex-wrap gap-1.5`:
  - **Unselected**: `px-2.5 py-1 rounded-full text-xs font-medium border bg-input border-border text-foreground`
  - **Selected**: `px-2.5 py-1 rounded-full text-xs font-medium border bg-secondary border-primary text-primary`
- Available cuisines: Italian, Indian, Chinese, Mexican, Japanese, Continental (dynamically loaded from API)

#### 3.2.5 Additional Preferences Textarea

- **Label**: icon (message-square, 14px) + "Additional Preferences" + "(optional)"
- **Input**: `bg-input border border-border rounded-md px-3 py-2.5 text-sm min-h-20`
- Placeholder: "e.g. family-friendly, outdoor seating, quick service..."

#### 3.2.6 Submit Button

- **Style**: `w-full bg-primary text-primary-foreground rounded-lg py-3 text-sm font-semibold`
- **Content**: sparkles icon (15px) + "Find Restaurants"
- Positioned at bottom with `mt-auto`

---

### 3.3 ActiveFiltersBar

```
┌──────────────────────────────────────────────────────────────────┐
│ FILTERS:  [📍 Bangalore ✕]  [💰 ₹500-₹1200 ✕]  [⭐ 4.0+ ✕]   │
└──────────────────────────────────────────────────────────────────┘
```

| Property       | Value                                                  |
|----------------|--------------------------------------------------------|
| Background     | `--color-muted` (#f1f0ee)                              |
| Padding        | `px-6 py-3`                                            |
| Border         | 1px bottom, `--color-border`                           |
| Layout         | `flex items-center gap-2 flex-wrap`                    |

- **Label**: "FILTERS:" — `text-xs font-semibold uppercase tracking-wider text-muted-foreground mr-1`
- **Filter chips**: `flex items-center gap-1.5 bg-sidebar border border-border rounded-full px-3 py-1 text-xs font-medium text-foreground`
  - Each chip: icon (11px) + filter text + "✕" close icon (10px)
  - Filter types shown: Location (map-pin), Budget (wallet), Rating (star), Cuisine (utensils, only if selected)

---

### 3.4 AI Summary Section

```
┌──────────────────────────────────────────────────────────────────┐
│ ✨ AI Summary                                                    │
│                                                                   │
│ Based on your preferences for Medium-budget Italian and Mexican  │
│ restaurants in Bangalore with ratings above 4.0, I've found...   │
└──────────────────────────────────────────────────────────────────┘
```

| Property       | Value                                           |
|----------------|-------------------------------------------------|
| Background     | `--color-ai-bg` (#f0f7ff)                       |
| Border         | 1px, `--color-ai-border` (#bfdbfe)              |
| Border radius  | `rounded-lg` (12px)                             |
| Padding        | `p-4` (16px)                                    |

- **Header**: sparkles icon (15px, `text-primary`) + "AI Summary" (`font-headings font-semibold text-sm text-foreground`)
- **Body**: `text-sm text-foreground leading-relaxed` — LLM-generated summary paragraph

---

### 3.5 Recommendation Card

```
┌──────────────────────────────────────────────────────────────────┐
│  ┌──────┐                                                        │
│  │  #1  │   Restaurant Name                        4.5 ★        │
│  │ RANK │   Italian, Continental                                 │
│  └──────┘                                                        │
│                                                                   │
│  ₹ ₹1200 for two                                                │
│                                                                   │
│  ┌ AI Explanation ──────────────────────────────────────────────┐ │
│  │ This restaurant perfectly matches your preference for...     │ │
│  └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

| Property       | Value                                           |
|----------------|-------------------------------------------------|
| Background     | `--color-card` (#fff)                           |
| Border         | 1px, `--color-border`                           |
| Border radius  | `rounded-lg` (12px)                             |
| Shadow         | `shadow-sm`                                     |
| Padding        | `p-4` (16px)                                    |

**Card header** (`flex items-start gap-3`):

- **Rank badge**: 32×32px, `rounded-lg flex items-center justify-center`
  - Rank 1: `bg-rank-gold` (#f59e0b) — bold white "#1"
  - Rank 2: `bg-rank-silver` (#9ca3af) — bold white "#2"
  - Rank 3: `bg-rank-bronze` (#c97c4a) — bold white "#3"
  - Rank 4+: `bg-muted` — bold foreground text
- **Name & cuisine** (`flex-1 min-w-0`):
  - Name: `font-headings font-semibold text-xl text-foreground leading-tight`
  - Cuisine: `text-sm text-muted-foreground mt-0.5`
- **Rating pill** (`ml-auto flex-shrink-0`):
  - `flex items-center gap-1 bg-success/10 text-success px-2 py-0.5 rounded-full text-sm font-semibold`
  - Star icon (13px) + rating value (e.g. "4.5")

**Cost line** (below header, within card body):
- `text-sm text-muted-foreground` with wallet icon — "₹1,200 for two"

**AI Explanation** (inside a sub-card):
- `bg-muted rounded-md p-3`
- Label: sparkles icon + "Why this pick" — `text-xs font-semibold text-foreground`
- Body: `text-sm text-muted-foreground leading-relaxed` — LLM explanation text

---

### 3.6 Loading State (Skeleton)

When the API request is in flight, display skeleton cards:

- Same card structure but with animated placeholder bars
- Use pulsing animation (`@keyframes pulse` — opacity oscillation)
- Skeleton bars: `bg-muted rounded` with varying widths (60%, 40%, 100%, 80%)
- Show 3 skeleton cards while loading
- Replace the AI summary with a skeleton block as well

---

### 3.7 Empty State

When no results are returned (or before the first search):

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│                    🍽️  (utensils icon, large)                     │
│                                                                   │
│              Discover Your Next Favorite Spot                    │
│      Set your preferences and let AI find the perfect            │
│              restaurants for you.                                 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

- Centered vertically and horizontally in the main content area
- Large icon: utensils, 48px, `text-muted-foreground`
- Title: `font-headings font-semibold text-lg text-foreground`
- Subtitle: `text-sm text-muted-foreground`

---

### 3.8 Warning/Error States

When the API returns warnings (e.g. constraint relaxation):

- Displayed between filters bar and results
- `bg-secondary rounded-lg p-3 border border-primary/20`
- Alert icon + warning text in `text-sm text-foreground`

---

## 4. Iconography

All icons use **Lucide** icon set (inline SVGs, `stroke="currentColor"`). Sizes vary by context:

| Context         | Size  |
|-----------------|-------|
| Form labels     | 14px  |
| Submit button   | 15px  |
| Filter chips    | 11px  |
| Close (✕) icons | 10px  |
| Card rating     | 13px  |
| Empty state     | 48px  |

Icons used:
- `map-pin` — Location
- `wallet` — Budget / Cost
- `star` — Rating
- `utensils` — Cuisine / Empty state
- `message-square` — Additional preferences
- `sparkles` — AI features, submit button, AI summary
- `chevron-down` — Dropdown indicator
- `x` — Close/remove filter chip

---

## 5. Interactive Behaviors

### 5.1 Budget Selector
- Single-select toggle: clicking one deselects others
- Selected state: `border-primary bg-secondary text-primary`
- Unselected state: `border-border bg-input text-foreground`
- Transition: smooth border/background color change

### 5.2 Rating Slider
- Draggable thumb on a track
- Fill width updates in real-time
- Value label updates live (top-right of label row)
- Snaps to 0.5 increments

### 5.3 Cuisine Chips
- Multi-select toggle: clicking toggles individual chips
- Selected: `bg-secondary border-primary text-primary`
- Unselected: `bg-input border-border text-foreground`

### 5.4 Filter Chips (in filters bar)
- Auto-generated from current form state
- Clicking "✕" removes the filter and updates the sidebar accordingly

### 5.5 Submit Button
- Hover: slightly darker primary, subtle scale
- Loading: show spinner/pulse animation, disable button

### 5.6 Cards
- Subtle hover: slight elevation increase or border color change
- Entrance animation: fade-in + slide-up when results load

---

## 6. Responsive Breakpoints

| Breakpoint | Behavior                                                     |
|------------|--------------------------------------------------------------|
| ≥1024px    | Full layout: sidebar (320px) + main content side by side     |
| 768–1023px | Sidebar collapses to overlay/drawer, toggle button in header |
| <768px     | Full mobile: stacked layout, sidebar as top drawer           |

---

## 7. API Integration Points

All endpoints are relative to `http://localhost:8000`.

### 7.1 On Page Load
```
GET /api/v1/health       → Update status dot and text
GET /api/v1/locations    → Populate location dropdown
GET /api/v1/cuisines     → Populate cuisine chips
```

### 7.2 On "Find Restaurants" Click
```
POST /api/v1/recommend
Content-Type: application/json

{
  "location": "Bangalore",
  "budget": "medium",
  "min_rating": 4.0,
  "cuisine": "Italian",           // optional, omit if none selected
  "additional": "outdoor seating" // optional, omit if empty
}
```

**Response** (`RecommendationResponse`):
```json
{
  "summary": "Based on your preferences...",
  "recommendations": [
    {
      "rank": 1,
      "name": "Trattoria",
      "cuisine": "Italian, Continental",
      "rating": 4.5,
      "estimated_cost": 1200,
      "explanation": "This restaurant perfectly matches..."
    }
  ],
  "metadata": {
    "candidates_considered": 12,
    "filters_applied": { "location": "Bangalore", "budget": "medium" },
    "model": "llama-3.3-70b-versatile",
    "is_fallback": false
  },
  "warnings": []
}
```

### 7.3 Cuisine Field Behavior

The backend `cuisine` field accepts a **single string** (e.g. `"Italian"`). If multiple cuisines are selected in the UI, join them with a comma: `"Italian, Mexican"`.

---

## 8. State Machine

```
┌──────────┐     Submit      ┌──────────┐     Success    ┌──────────┐
│   IDLE   │ ──────────────→ │ LOADING  │ ─────────────→ │ RESULTS  │
│ (empty   │                 │ (skeleton│                 │ (cards + │
│  state)  │                 │  cards)  │                 │  summary)│
└──────────┘                 └──────────┘                 └──────────┘
                                  │                            │
                                  │ Error                      │ Re-submit
                                  ↓                            ↓
                             ┌──────────┐                 ┌──────────┐
                             │  ERROR   │                 │ LOADING  │
                             │ (error   │                 │          │
                             │  banner) │                 │          │
                             └──────────┘                 └──────────┘
```

- **IDLE**: Empty state illustration shown. No filters bar.
- **LOADING**: Skeleton cards shown. Button disabled with spinner. Filters bar visible.
- **RESULTS**: AI summary + recommendation cards + filters bar. Warnings shown if any.
- **ERROR**: Error banner with retry option. Previous results cleared.

---

## 9. File Map

```
frontend/
├── index.html      # Semantic HTML structure
├── styles.css       # All styles (design tokens + component styles)
└── app.js           # API calls, state management, DOM manipulation
```

Served by FastAPI as static files, mounted at root `/`.
