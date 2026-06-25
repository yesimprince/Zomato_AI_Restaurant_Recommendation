/* ═══════════════════════════════════════════════════════════
   Zomato AI Recommender — Application Logic
   API integration, state management, DOM manipulation
   ═══════════════════════════════════════════════════════════ */

const API_BASE = 'https://web-production-a1de8.up.railway.app/';

// ── SVG Icon templates ──
const Icons = {
  mapPin: (size = 11) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>`,
  wallet: (size = 11) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>`,
  star: (size = 13) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.12 2.12 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.12 2.12 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.12 2.12 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.12 2.12 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.12 2.12 0 0 0 1.597-1.16z"/></svg>`,
  starFill: (size = 13) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.12 2.12 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.12 2.12 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.12 2.12 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.12 2.12 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.12 2.12 0 0 0 1.597-1.16z"/></svg>`,
  utensils: (size = 11) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20m14-7V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2zm0 0v7"/></svg>`,
  sparkles: (size = 15) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594zM20 2v4m2-2h-4"/><circle cx="4" cy="20" r="2"/></svg>`,
  x: (size = 10) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>`,
  alertTriangle: (size = 16) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 3.98 21h16.04a2 2 0 0 0 1.71-3z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>`,
  alertCircle: (size = 16) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>`,
};

// ── Budget display map ──
const BUDGET_LABELS = {
  low: 'Under ₹500',
  medium: '₹500–₹1200',
  high: 'Above ₹1200',
};

// ── App State ──
const state = {
  location: '',
  budget: 'medium',
  min_rating: 4.0,
  cuisine: '',
  additional: '',
  isLoading: false,
  results: null,
  apiConnected: false,
};

// ── DOM Elements ──
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const els = {
  statusDot: $('#status-dot'),
  statusText: $('#status-text'),
  locationSelect: $('#location-select'),
  budgetGroup: $('#budget-group'),
  ratingSlider: $('#rating-slider'),
  ratingValue: $('#rating-value'),
  sliderFill: $('#slider-fill'),
  sliderThumb: $('#slider-thumb'),
  cuisineSelect: $('#cuisine-select'),
  additionalInput: $('#additional-input'),
  submitBtn: $('#submit-btn'),
  form: $('#preference-form'),
  filtersBar: $('#filters-bar'),
  filterChipsContainer: $('#filter-chips-container'),
  resultsArea: $('#results-area'),
  emptyState: $('#empty-state'),
  sidebar: $('#sidebar'),
  sidebarOverlay: $('#sidebar-overlay'),
  mobileMenuBtn: $('#mobile-menu-btn'),
};


/* ═══════════════════════════════════════════════════════════
   INITIALIZATION
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  initBudgetSelector();
  initRatingSlider();
  initMobileSidebar();
  initFormSubmit();
  fetchHealth();
  fetchLocations();
  fetchCuisines();
});


/* ═══════════════════════════════════════════════════════════
   API CALLS
   ═══════════════════════════════════════════════════════════ */

async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    state.apiConnected = data.status === 'ok';
    els.statusDot.classList.toggle('disconnected', !state.apiConnected);
    els.statusText.textContent = state.apiConnected
      ? `API connected · ${data.restaurant_count?.toLocaleString() || 0} restaurants`
      : 'API error';
  } catch {
    state.apiConnected = false;
    els.statusDot.classList.add('disconnected');
    els.statusText.textContent = 'API disconnected';
  }
}

async function fetchLocations() {
  try {
    const res = await fetch(`${API_BASE}/locations`);
    const data = await res.json();
    const select = els.locationSelect;
    // Keep the placeholder
    data.locations.sort().forEach((loc) => {
      const opt = document.createElement('option');
      opt.value = loc;
      opt.textContent = loc;
      select.appendChild(opt);
    });
    // Default to Bangalore if available
    if (data.locations.includes('Bangalore')) {
      select.value = 'Bangalore';
      state.location = 'Bangalore';
    }
  } catch (err) {
    console.error('Failed to fetch locations:', err);
  }
}

async function fetchCuisines() {
  try {
    const res = await fetch(`${API_BASE}/cuisines`);
    const data = await res.json();
    const select = els.cuisineSelect;
    data.cuisines.sort().forEach((c) => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Failed to fetch cuisines:', err);
    // Fallback options
    const select = els.cuisineSelect;
    ['Italian', 'Indian', 'Chinese', 'Mexican', 'Japanese', 'Continental'].forEach((c) => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      select.appendChild(opt);
    });
  }
}

async function submitRecommendation() {
  if (state.isLoading) return;

  // Validate
  state.location = els.locationSelect.value;
  if (!state.location) {
    els.locationSelect.focus();
    return;
  }

  state.additional = els.additionalInput.value.trim() || null;
  const cuisineStr = els.cuisineSelect.value || null;

  const payload = {
    location: state.location,
    budget: state.budget,
    min_rating: state.min_rating,
  };
  if (cuisineStr) payload.cuisine = cuisineStr;
  if (state.additional) payload.additional = state.additional;

  setLoading(true);
  renderFiltersBar(payload);

  try {
    const res = await fetch(`${API_BASE}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      let errMsg = `Server error (${res.status})`;
      if (err.detail) {
        errMsg = Array.isArray(err.detail) ? err.detail.map(d => d.msg).join(', ') : err.detail;
      }
      throw new Error(errMsg);
    }

    const data = await res.json();
    state.results = data;
    renderResults(data);
  } catch (err) {
    renderError(err.message);
  } finally {
    setLoading(false);
  }
}


/* ═══════════════════════════════════════════════════════════
   UI COMPONENTS
   ═══════════════════════════════════════════════════════════ */

// ── Budget selector ──
function initBudgetSelector() {
  const options = $$('.budget-option');
  options.forEach((btn) => {
    btn.addEventListener('click', () => {
      options.forEach((b) => {
        b.classList.remove('selected');
        b.setAttribute('aria-checked', 'false');
      });
      btn.classList.add('selected');
      btn.setAttribute('aria-checked', 'true');
      state.budget = btn.dataset.value;
    });
  });
}

// ── Rating slider ──
function initRatingSlider() {
  const slider = els.ratingSlider;
  slider.addEventListener('input', () => {
    const val = parseFloat(slider.value);
    state.min_rating = val;
    updateSliderVisual(val);
  });
}

function updateSliderVisual(val) {
  const pct = (val / 5) * 100;
  els.sliderFill.style.width = `${pct}%`;
  els.sliderThumb.style.left = `calc(${pct}% - 8px)`;
  els.ratingValue.textContent = val.toFixed(1);
}



// ── Mobile sidebar ──
function initMobileSidebar() {
  els.mobileMenuBtn.addEventListener('click', () => {
    els.sidebar.classList.add('open');
    els.sidebarOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  });

  const close = () => {
    els.sidebar.classList.remove('open');
    els.sidebarOverlay.classList.remove('active');
    document.body.style.overflow = '';
  };

  els.sidebarOverlay.addEventListener('click', close);
}

// ── Form submit ──
function initFormSubmit() {
  els.form.addEventListener('submit', (e) => {
    e.preventDefault();
    // Close sidebar on mobile
    if (window.innerWidth < 1024) {
      els.sidebar.classList.remove('open');
      els.sidebarOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }
    submitRecommendation();
  });
}


/* ═══════════════════════════════════════════════════════════
   RENDERING
   ═══════════════════════════════════════════════════════════ */

function setLoading(loading) {
  state.isLoading = loading;
  els.submitBtn.disabled = loading;

  const btnIcon = els.submitBtn.querySelector('.icon');
  if (loading) {
    btnIcon.innerHTML = '<div class="spinner"></div>';
    els.submitBtn.querySelector('span:last-child').textContent = 'Analyzing…';
    renderSkeletons();
  } else {
    btnIcon.innerHTML = Icons.sparkles(15);
    els.submitBtn.querySelector('span:last-child').textContent = 'Find Restaurants';
  }
}

function renderSkeletons() {
  els.emptyState?.remove();
  els.resultsArea.innerHTML = '';

  // Skeleton summary
  const skelSummary = document.createElement('div');
  skelSummary.className = 'skeleton-card';
  skelSummary.innerHTML = `
    <div class="skeleton-header">
      <div class="skeleton-badge"></div>
      <div style="flex:1;display:flex;flex-direction:column;gap:6px">
        <div class="skeleton-line h-4 w-40"></div>
      </div>
    </div>
    <div class="skeleton-line w-full"></div>
    <div class="skeleton-line w-80"></div>
  `;
  els.resultsArea.appendChild(skelSummary);

  // Skeleton cards
  for (let i = 0; i < 3; i++) {
    const card = document.createElement('div');
    card.className = 'skeleton-card';
    card.innerHTML = `
      <div class="skeleton-header">
        <div class="skeleton-badge"></div>
        <div style="flex:1;display:flex;flex-direction:column;gap:6px">
          <div class="skeleton-line h-6 w-60"></div>
          <div class="skeleton-line w-40"></div>
        </div>
      </div>
      <div class="skeleton-line w-40"></div>
      <div class="skeleton-line h-16 w-full"></div>
    `;
    els.resultsArea.appendChild(card);
  }
}

function renderResults(data) {
  els.resultsArea.innerHTML = '';

  // Warnings
  if (data.warnings && data.warnings.length > 0) {
    data.warnings.forEach((w) => {
      const banner = document.createElement('div');
      banner.className = 'warning-banner';
      banner.innerHTML = `<span class="icon">${Icons.alertTriangle()}</span><span>${escapeHtml(w)}</span>`;
      els.resultsArea.appendChild(banner);
    });
  }

  // AI Summary
  if (data.summary) {
    const summary = document.createElement('div');
    summary.className = 'ai-summary';
    summary.innerHTML = `
      <div class="ai-summary-header">
        <span class="icon">${Icons.sparkles(15)}</span>
        <span>AI Summary</span>
      </div>
      <p class="ai-summary-text">${escapeHtml(data.summary)}</p>
    `;
    els.resultsArea.appendChild(summary);
  }

  // Recommendation cards
  if (data.recommendations && data.recommendations.length > 0) {
    const container = document.createElement('div');
    container.className = 'cards-container';

    data.recommendations.forEach((rec) => {
      container.appendChild(createRecCard(rec));
    });

    els.resultsArea.appendChild(container);
  } else {
    // No results — show empty state safely without wiping out warnings
    renderEmptyResults();
  }

  // Metadata bar
  if (data.metadata) {
    const meta = document.createElement('div');
    meta.className = 'metadata-bar';
    const items = [];
    items.push(`${data.metadata.candidates_considered} candidates considered`);
    if (data.metadata.model) items.push(`Model: ${data.metadata.model}`);
    if (data.metadata.is_fallback) items.push('⚠ Heuristic fallback');
    meta.innerHTML = items.map((t, i) => {
      const dot = i > 0 ? '<span class="metadata-dot"></span>' : '';
      return `${dot}<span class="metadata-item">${escapeHtml(t)}</span>`;
    }).join('');
    els.resultsArea.appendChild(meta);
  }
}

function createRecCard(rec) {
  const card = document.createElement('div');
  card.className = 'rec-card';

  // Rank class
  let rankClass = 'rank-other';
  if (rec.rank === 1) rankClass = 'rank-1';
  else if (rec.rank === 2) rankClass = 'rank-2';
  else if (rec.rank === 3) rankClass = 'rank-3';

  card.innerHTML = `
    <div class="card-header">
      <div class="rank-badge ${rankClass}">#${rec.rank}</div>
      <div class="card-info">
        <div class="card-name">${escapeHtml(rec.name)}</div>
        <div class="card-cuisine">${escapeHtml(rec.cuisine)}</div>
      </div>
      <div class="rating-pill">
        <span class="icon">${Icons.starFill(13)}</span>
        <span>${rec.rating.toFixed(1)}</span>
      </div>
    </div>
    <div class="card-cost">
      <span class="icon">${Icons.wallet(13)}</span>
      <span>₹${rec.estimated_cost ? rec.estimated_cost.toLocaleString('en-IN') : 'N/A'} for two</span>
    </div>
    <div class="card-explanation">
      <div class="explanation-header">
        <span class="icon">${Icons.sparkles(12)}</span>
        <span>Why this pick</span>
      </div>
      <p class="explanation-text">${escapeHtml(rec.explanation)}</p>
    </div>
  `;

  return card;
}

function renderEmptyResults() {
  const emptyDiv = document.createElement('div');
  emptyDiv.className = 'empty-state';
  emptyDiv.innerHTML = `
    <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20m14-7V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2zm0 0v7"/></svg>
    <h3>No Restaurants Found</h3>
    <p>Try broadening your filters — lower the minimum rating, adjust your budget, or try a different location.</p>
  `;
  els.resultsArea.appendChild(emptyDiv);
}

function renderError(message) {
  els.resultsArea.innerHTML = `
    <div class="error-banner">
      <span class="icon">${Icons.alertCircle()}</span>
      <span>${escapeHtml(message)}</span>
    </div>
    <div class="empty-state">
      <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
      <h3>Something Went Wrong</h3>
      <p>Please check that the API server is running and try again.</p>
    </div>
  `;
}

function renderFiltersBar(payload) {
  els.filtersBar.classList.remove('hidden');
  const container = els.filterChipsContainer;
  container.innerHTML = '';

  // Location chip
  addFilterChip(container, Icons.mapPin(11), payload.location);

  // Budget chip
  addFilterChip(container, Icons.wallet(11), BUDGET_LABELS[payload.budget] || payload.budget);

  // Rating chip
  addFilterChip(container, Icons.star(11), `${payload.min_rating.toFixed(1)}+ rating`);

  // Cuisine chip(s)
  if (payload.cuisine) {
    addFilterChip(container, Icons.utensils(11), payload.cuisine);
  }
}

function addFilterChip(container, iconHtml, text) {
  const chip = document.createElement('span');
  chip.className = 'filter-chip';
  chip.innerHTML = `<span class="icon">${iconHtml}</span><span>${escapeHtml(text)}</span>`;
  container.appendChild(chip);
}


/* ═══════════════════════════════════════════════════════════
   UTILS
   ═══════════════════════════════════════════════════════════ */

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(str);
  return div.innerHTML;
}

// For testing purposes
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    state,
    els,
    escapeHtml,
    renderResults,
    renderEmptyResults,
    renderError,
    createRecCard,
  };
}
