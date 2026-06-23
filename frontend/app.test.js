/**
 * @jest-environment jsdom
 */

// Setup DOM elements required by app.js initialization
document.body.innerHTML = `
  <div id="results-area"></div>
  <div id="status-dot"></div>
  <div id="status-text"></div>
  <select id="location-select"></select>
  <div id="budget-group"></div>
  <input id="rating-slider" />
  <span id="rating-value"></span>
  <div id="slider-fill"></div>
  <div id="slider-thumb"></div>
  <select id="cuisine-select"></select>
  <input id="additional-input" />
  <button id="submit-btn"><span class="icon"></span><span></span></button>
  <form id="preference-form"></form>
  <div id="filters-bar"></div>
  <div id="filter-chips-container"></div>
  <div id="empty-state"></div>
  <div id="sidebar"></div>
  <div id="sidebar-overlay"></div>
  <button id="mobile-menu-btn"></button>
`;

// Mock Icons to prevent errors
window.Icons = new Proxy({}, {
  get: () => () => '<svg></svg>'
});

const { escapeHtml, renderResults, createRecCard, els } = require('./app');

describe('Frontend Edge Cases', () => {
  beforeEach(() => {
    els.resultsArea.innerHTML = '';
  });

  test('escapeHtml handles null, undefined, and falsey values safely', () => {
    expect(escapeHtml(null)).toBe('');
    expect(escapeHtml(undefined)).toBe('');
    expect(escapeHtml('')).toBe('');
    expect(escapeHtml(0)).toBe('0');
    expect(escapeHtml(false)).toBe('false');
    // jsdom handles DOM-based escaping, which may use character entities or not depending on parsing
    const escaped = escapeHtml('<script>');
    expect(escaped).toContain('&lt;script&gt;');
  });

  test('renderResults appends empty state and preserves warnings when no recommendations exist', () => {
    const data = {
      warnings: ['Relaxed budget constraint.'],
      recommendations: []
    };

    renderResults(data);

    expect(els.resultsArea.querySelector('.warning-banner')).not.toBeNull();
    expect(els.resultsArea.querySelector('.warning-banner').textContent).toContain('Relaxed budget constraint.');
    expect(els.resultsArea.querySelector('.empty-state')).not.toBeNull();
    expect(els.resultsArea.querySelector('.empty-state h3').textContent).toBe('No Restaurants Found');
  });

  test('createRecCard gracefully handles null estimated_cost', () => {
    const rec = {
      rank: 1,
      name: 'Test Rest',
      cuisine: 'Italian',
      rating: 4.5,
      estimated_cost: null,
      explanation: 'Because it is good.'
    };

    const card = createRecCard(rec);
    const costText = card.querySelector('.card-cost').textContent;
    expect(costText).toContain('₹N/A for two');
  });
});
