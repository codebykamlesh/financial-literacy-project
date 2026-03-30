/* ========================================================
   SMART STOCK INSIGHT PLATFORM — APP.JS
   Version 3.0 — Advanced AI Multi-Factor Analysis
   ======================================================== */

const API_BASE = "http://127.0.0.1:5000";

// ─── FINANCIAL LITERACY DATA ───
const LITERACY_CARDS = [
  { icon: "📊", title: "What is a Stock?", desc: "A stock represents ownership in a company. When you buy a stock, you become a partial owner and may benefit from the company's profits." },
  { icon: "🔖", title: "What is a Share?", desc: "A share is a single unit of stock. If a company has 1,000 shares and you own 10, you own 1% of that company." },
  { icon: "💼", title: "Investment", desc: "Investment means putting money into assets like stocks or bonds with the expectation of generating profit over time." },
  { icon: "💰", title: "Profit", desc: "Profit is the financial gain when selling price exceeds buying price. Net profit = Selling Price − Buying Price − Costs." },
  { icon: "⚠️", title: "Risk", desc: "Risk is the possibility of losing money. Higher potential returns usually come with higher risk. Diversification helps manage it." },
  { icon: "🏦", title: "Dividend", desc: "A dividend is a portion of a company's earnings paid to shareholders — a reward for holding the stock." },
  { icon: "📈", title: "Bull vs Bear Market", desc: "Bull market = rising prices & optimism. Bear market = falling prices (20%+ drop) & pessimism." },
  { icon: "🔍", title: "P/E Ratio", desc: "Price-to-Earnings ratio measures valuation. High P/E may mean overvalued; low P/E may mean undervalued." },
  { icon: "🛡️", title: "Diversification", desc: "Don't put all eggs in one basket. Spread investments across sectors and asset classes to reduce risk." }
];

// ─── DOM ELEMENTS ───
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const el = {
  stockSelect:     $('#stock-select'),
  refreshBtn:      $('#refresh-btn'),
  stockName:       $('#stock-name'),
  stockTicker:     $('#stock-ticker'),
  stockPrice:      $('#stock-price'),
  stockChange:     $('#stock-change'),
  stockDesc:       $('#stock-desc'),
  stockMeta:       $('#stock-meta'),
  statHigh:        $('#stat-high'),
  statLow:         $('#stat-low'),
  statOpen:        $('#stat-open'),
  statPrev:        $('#stat-prev'),
  fetchedAt:       $('#fetched-at'),
  stockCard:       $('#stock-card'),
  loadingOverlay:  $('#loading-overlay'),
  errorBanner:     $('#error-banner'),
  errorText:       $('#error-text'),
  errorRetryBtn:   $('#error-retry-btn'),
  literacyGrid:    $('#literacy-grid'),
  trendTbody:      $('#trend-tbody'),
  // AI Signal
  signalBadge:     $('#signal-badge'),
  signalIcon:      $('#signal-icon'),
  signalFill:      $('#signal-fill'),
  signalConfidence:$('#signal-confidence'),
  // AI Score Meter
  scorePointer:    $('#score-pointer'),
  aiScoreValue:    $('#ai-score-value'),
  subScoresDisplay:$('#sub-scores-display'),
  // Predicted Price
  predictedPrice:  $('#predicted-price'),
  predictedChange: $('#predicted-change'),
  predictedDirection: $('#predicted-direction'),
  momentumBadge:   $('#momentum-badge'),
  // Trend Strength
  strengthFill:    $('#strength-fill'),
  strengthVerdict: $('#strength-verdict'),
  strengthDirection: $('#strength-direction'),
  // Risk
  riskBadge:       $('#risk-badge'),
  riskDots:        $('#risk-dots'),
  // Support & Resistance
  srResistance:    $('#sr-resistance'),
  srSupport:       $('#sr-support'),
  srPriceMarker:   $('#sr-price-marker'),
  srAlertBadge:    $('#sr-alert-badge'),
  srHint:          $('#sr-hint'),
  // Technical Indicators
  rsiValue:        $('#rsi-value'),
  rsiNeedle:       $('#rsi-needle'),
  rsiHint:         $('#rsi-hint'),
  sma5Val:         $('#sma5-val'),
  sma10Val:        $('#sma10-val'),
  smaSignal:       $('#sma-signal'),
  smaHint:         $('#sma-hint'),
  volPct:          $('#vol-pct'),
  volBadge:        $('#vol-badge'),
  volChangePct:    $('#vol-change-pct'),
  volTrendBadge:   $('#vol-trend-badge'),
  // Insight
  insightText:     $('#insight-text'),
  // Other
  mobileMenuBtn:   $('#mobile-menu-btn'),
  mainNav:         $('#main-nav'),
  priceChart:      $('#price-chart')
};

// ─── HELPERS ───
function fmt(val) {
  return '₹' + val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fmtVol(val) {
  if (val >= 10000000) return (val / 10000000).toFixed(1) + ' Cr';
  if (val >= 100000) return (val / 100000).toFixed(1) + ' L';
  if (val >= 1000) return (val / 1000).toFixed(1) + ' K';
  return val.toString();
}

function showLoading() { el.loadingOverlay.style.display = 'flex'; el.stockCard.style.display = 'none'; el.errorBanner.style.display = 'none'; }
function hideLoading() { el.loadingOverlay.style.display = 'none'; }
function showError(msg) { hideLoading(); el.stockCard.style.display = 'none'; el.errorBanner.style.display = 'flex'; el.errorText.textContent = msg; }
function showCard() { hideLoading(); el.errorBanner.style.display = 'none'; el.stockCard.style.display = 'block'; }

// ─── FETCH DATA ───
async function fetchStockData(key) {
  showLoading();
  try {
    const res = await fetch(`${API_BASE}/api/stock/${key}`);
    if (!res.ok) { const err = await res.json(); throw new Error(err.error || `HTTP ${res.status}`); }
    const data = await res.json();
    renderStockCard(data);
    renderTrend(data);
    renderAnalysis(data);
    renderChart(data);
    showCard();
  } catch (err) {
    console.error("Fetch error:", err);
    showError(`Failed to fetch data: ${err.message}. Ensure server is running (python server.py).`);
  }
}

// ─── STOCK CARD ───
function renderStockCard(data) {
  el.stockName.textContent = data.name;
  el.stockTicker.textContent = data.ticker_display;
  animateValue(el.stockPrice, data.current_price);
  const pos = data.change_val >= 0;
  const s = pos ? '+' : '';
  el.stockChange.textContent = `${s}${data.change_val.toFixed(2)} (${s}${data.change_pct.toFixed(2)}%)`;
  el.stockChange.className = `stock-change ${pos ? 'positive' : 'negative'}`;
  el.stockDesc.textContent = data.description;
  el.stockMeta.innerHTML = '';
  data.sectors.forEach(sec => {
    const c = document.createElement('div'); c.className = 'meta-chip';
    c.innerHTML = `<span class="chip-dot ${sec.cls}"></span>${sec.label}`; el.stockMeta.appendChild(c);
  });
  const mc = document.createElement('div'); mc.className = 'meta-chip';
  mc.textContent = `📊 Market Cap: ${data.market_cap}`; el.stockMeta.appendChild(mc);
  el.statHigh.textContent = fmt(data.day_high);
  el.statLow.textContent  = fmt(data.day_low);
  el.statOpen.textContent  = fmt(data.open);
  el.statPrev.textContent  = fmt(data.prev_close);
  el.fetchedAt.textContent = `Last updated: ${data.fetched_at}`;
  el.stockCard.style.animation = 'none'; el.stockCard.offsetHeight;
  el.stockCard.style.animation = 'slideInUp 0.45s ease-out';
}

function animateValue(element, target) {
  const dur = 600, start = performance.now();
  const from = parseFloat(element.textContent.replace(/[₹,]/g, '')) || 0;
  function update(now) {
    const p = Math.min((now - start) / dur, 1);
    element.textContent = fmt(from + (target - from) * (1 - Math.pow(1 - p, 3)));
    if (p < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ═══════════════════════════════════════════
// RENDER AI ANALYSIS (all new components)
// ═══════════════════════════════════════════
function renderAnalysis(data) {
  const a = data.analysis;
  if (!a || a.error) return;

  // 1. Signal Card
  el.signalBadge.textContent = a.overall_signal;
  el.signalBadge.className = 'signal-badge';
  if (a.signal_color === 'green') { el.signalBadge.classList.add('buy'); el.signalIcon.textContent = '📈'; }
  else if (a.signal_color === 'red') { el.signalBadge.classList.add('sell'); el.signalIcon.textContent = '📉'; }
  else { el.signalBadge.classList.add('hold'); el.signalIcon.textContent = '📊'; }
  el.signalConfidence.textContent = `Confidence: ${a.confidence}%`;
  el.signalFill.style.width = '0%';
  setTimeout(() => { el.signalFill.style.width = a.confidence + '%'; }, 200);

  // 2. AI Score Meter (-10 to +10 → position 0% to 100%)
  const scorePct = ((a.ai_score + 10) / 20) * 100; // map -10..+10 to 0..100
  el.scorePointer.style.left = '50%';
  setTimeout(() => { el.scorePointer.style.left = scorePct + '%'; }, 200);
  el.aiScoreValue.textContent = (a.ai_score >= 0 ? '+' : '') + a.ai_score;
  el.aiScoreValue.style.color = a.signal_color === 'green' ? '#34d399' : a.signal_color === 'red' ? '#f87171' : '#fbbf24';

  // Sub-scores breakdown
  if (a.sub_scores) {
    const labels = { rsi: 'RSI', sma: 'SMA', volume: 'Volume', volatility: 'Volatility', momentum: 'Momentum' };
    el.subScoresDisplay.innerHTML = Object.entries(a.sub_scores).map(([k, v]) => {
      const cls = v > 0 ? 'sub-pos' : v < 0 ? 'sub-neg' : 'sub-neutral';
      return `<span class="sub-score-chip ${cls}">${labels[k]}: ${v > 0 ? '+' : ''}${v}</span>`;
    }).join('');
  }

  // 3. Predicted Price
  el.predictedPrice.textContent = fmt(a.predicted_price);
  const ps = a.predicted_change >= 0 ? '+' : '';
  el.predictedChange.textContent = `${ps}${a.predicted_change.toFixed(2)} (${ps}${a.predicted_change_pct.toFixed(2)}%)`;
  el.predictedChange.className = 'predicted-change ' + a.price_direction.toLowerCase();
  const dirMap = { UP: '🔺 Price Expected to Rise', DOWN: '🔻 Price Expected to Fall', FLAT: '➡️ Price Expected Stable' };
  el.predictedDirection.textContent = dirMap[a.price_direction] || '—';
  el.predictedDirection.className = 'predicted-direction ' + a.price_direction.toLowerCase();
  // Momentum badge
  const mSign = a.momentum_3d >= 0 ? '+' : '';
  el.momentumBadge.textContent = `3d Momentum: ${mSign}${a.momentum_3d}%`;
  el.momentumBadge.className = 'momentum-badge ' + (a.momentum_3d > 0.5 ? 'up' : a.momentum_3d < -0.5 ? 'down' : 'flat');

  // 4. Trend Strength
  el.strengthFill.style.width = '0%';
  setTimeout(() => { el.strengthFill.style.width = a.trend_strength_value + '%'; }, 300);
  el.strengthVerdict.textContent = a.trend_strength;
  el.strengthVerdict.className = 'strength-verdict ' + a.trend_strength.toLowerCase();
  const dirText = a.trend_direction === 'UP' ? '↗ Upward direction' : a.trend_direction === 'DOWN' ? '↘ Downward direction' : '→ Sideways movement';
  el.strengthDirection.textContent = dirText;

  // 5. Risk Level
  el.riskBadge.textContent = a.risk_level;
  el.riskBadge.className = 'risk-badge ' + a.risk_level.toLowerCase();
  const dots = el.riskDots.querySelectorAll('.risk-dot');
  const activeDots = a.risk_level === 'HIGH' ? 5 : a.risk_level === 'MEDIUM' ? 3 : 1;
  dots.forEach((dot, i) => {
    dot.className = 'risk-dot' + (i < activeDots ? ' active' : '');
    dot.style.background = i < activeDots
      ? (a.risk_level === 'HIGH' ? '#f87171' : a.risk_level === 'MEDIUM' ? '#fbbf24' : '#34d399')
      : 'rgba(255,255,255,0.08)';
  });

  // 6. Support & Resistance
  el.srResistance.textContent = fmt(a.resistance);
  el.srSupport.textContent = fmt(a.support);
  // Position marker: pct_from_support 0=at support, 100=at resistance
  const markerPct = Math.max(2, Math.min(98, a.pct_from_support));
  el.srPriceMarker.style.left = '0%';
  setTimeout(() => { el.srPriceMarker.style.left = markerPct + '%'; }, 300);
  el.srAlertBadge.textContent = a.sr_alert;
  el.srAlertBadge.className = 'sr-alert-badge ' + (a.sr_alert === 'NEAR SUPPORT' ? 'support' : a.sr_alert === 'NEAR RESISTANCE' ? 'resistance' : 'mid');
  el.srHint.textContent = a.sr_alert_detail;

  // 7. RSI
  el.rsiValue.textContent = a.rsi;
  el.rsiValue.style.color = a.rsi < 30 ? '#34d399' : a.rsi > 70 ? '#f87171' : '#fbbf24';
  el.rsiHint.textContent = a.rsi < 30 ? 'Oversold — potential bounce' : a.rsi > 70 ? 'Overbought — may correct' : 'Neutral zone';
  setTimeout(() => { el.rsiNeedle.style.left = a.rsi + '%'; }, 200);

  // 8. SMA
  el.sma5Val.textContent = fmt(a.sma5);
  el.sma10Val.textContent = fmt(a.sma10);
  el.smaSignal.textContent = a.sma_signal;
  el.smaSignal.className = 'sma-signal-badge ' + a.sma_signal.toLowerCase();
  el.smaHint.textContent = a.sma_detail;

  // 9. Volatility & Volume
  el.volPct.textContent = a.volatility_pct + '%';
  el.volBadge.textContent = a.volatility_label;
  el.volBadge.className = 'vol-badge ' + a.volatility_label.toLowerCase();
  const vs = a.volume_change_pct >= 0 ? '+' : '';
  el.volChangePct.textContent = vs + a.volume_change_pct + '%';
  el.volTrendBadge.textContent = a.volume_trend;
  el.volTrendBadge.className = 'vol-trend-badge ' + a.volume_trend.toLowerCase();

  // 10. Smart Insight
  el.insightText.textContent = a.insight;
}

// ─── TREND TABLE ───
function renderTrend(data) {
  const h = data.history;
  if (!h || h.length < 5) { el.trendTbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">Insufficient data</td></tr>'; return; }
  const last5 = h.slice(-5);
  el.trendTbody.innerHTML = '';
  last5.forEach((day, i) => {
    const tr = document.createElement('tr');
    const chg = i > 0 ? ((day.close - last5[i-1].close) / last5[i-1].close * 100).toFixed(2) : null;
    const cls = chg === null ? '' : (parseFloat(chg) >= 0 ? 'change-positive' : 'change-negative');
    const s = (chg !== null && parseFloat(chg) >= 0) ? '+' : '';
    tr.innerHTML = `<td>Day ${i+1}</td><td>${day.date}</td><td>${fmt(day.close)}</td><td>${fmtVol(day.volume)}</td><td class="${cls}">${chg===null?'—':s+chg+'%'}</td>`;
    tr.style.animation = `fadeUp 0.4s ease ${i*0.06}s both`;
    el.trendTbody.appendChild(tr);
  });
}

// ─── JS-BASED CHART PREDICTION LOGIC ───
function calculateFuturePredictions(closes) {
  if (closes.length < 5) return null;

  const n = closes.length;
  const last5 = closes.slice(-5);
  // Moving average (SMA-5)
  const sma5 = last5.reduce((a, b) => a + b, 0) / 5;
  
  // Momentum: Calculate average daily absolute change and current trajectory
  const recentChange = (closes[n - 1] - closes[n - 5]) / closes[n - 5];
  
  let trend = 'FLAT';
  if (recentChange > 0.015) trend = 'UP';
  else if (recentChange < -0.015) trend = 'DOWN';

  // Calculate generic confidence (50% to 95%) based on momentum magnitude
  let confidence = 50 + (Math.abs(recentChange) * 100 * 8); 
  confidence = Math.min(95, Math.max(50, confidence));

  const lastPrice = closes[n - 1];
  
  // Base daily step based on momentum and volatility
  let dailyStep = (lastPrice * recentChange) / 4; 

  // If the trend is very weak, lightly pull it towards the moving average
  if (Math.abs(dailyStep) < lastPrice * 0.001) {
    dailyStep = (sma5 - lastPrice) * 0.2;
    trend = dailyStep > 0 ? 'UP' : 'DOWN';
  }

  // Generate 3 future points
  // Dampening the step each day creates a smooth, visually realistic curve (asymptotic)
  const p1 = lastPrice + dailyStep;
  const p2 = p1 + (dailyStep * 0.85);
  const p3 = p2 + (dailyStep * 0.65);

  let rgb = '251, 191, 36'; // YELLOW (Stable)
  if (trend === 'UP') rgb = '52, 211, 153'; // GREEN (Uptrend)
  else if (trend === 'DOWN') rgb = '248, 113, 113'; // RED (Downtrend)

  return { points: [p1, p2, p3], trend, confidence, rgb };
}

// ─── CHART WITH SUPPORT/RESISTANCE + JS PREDICTION ───
let chartInstance = null;

function renderChart(data) {
  const h = data.history;
  if (!h || h.length === 0) return;
  const a = data.analysis;

  const labels = h.map(d => d.date);
  const closes = h.map(d => d.close);
  const highs  = h.map(d => d.high);
  const lows   = h.map(d => d.low);

  // Calculate JS-based future prediction
  const pred = calculateFuturePredictions(closes);

  // Extend data arrays with 3 future points
  if (pred) {
    labels.push('Future 1', 'Future 2', 'Future 3');
    closes.push(null, null, null);
    highs.push(null, null, null);
    lows.push(null, null, null);
  }

  // Construct prediction line overlapping the last known real point
  const predLine = new Array(labels.length).fill(null);
  if (pred) {
    const lastRealIndex = h.length - 1;
    predLine[lastRealIndex] = closes[lastRealIndex];
    predLine[lastRealIndex + 1] = pred.points[0];
    predLine[lastRealIndex + 2] = pred.points[1];
    predLine[lastRealIndex + 3] = pred.points[2];
  }

  // Extend Support & Resistance horizontal lines to the very end
  const srLen = labels.length;
  const supportLine = new Array(srLen).fill(a ? a.support : null);
  const resistanceLine = new Array(srLen).fill(a ? a.resistance : null);

  const ctx = el.priceChart.getContext('2d');
  if (chartInstance) chartInstance.destroy();

  const grad = ctx.createLinearGradient(0, 0, 0, 380);
  grad.addColorStop(0, 'rgba(99,102,241,0.3)'); grad.addColorStop(1, 'rgba(99,102,241,0.0)');

  const datasets = [
    { 
      label: `Real Data (${data.ticker_display})`, 
      data: closes, borderColor: '#818cf8', backgroundColor: grad, 
      borderWidth: 2.5, pointBackgroundColor: '#6366f1', pointBorderColor: '#1e1b4b', 
      pointBorderWidth: 2, pointRadius: 4, pointHoverRadius: 7, 
      fill: true, tension: 0.35, spanGaps: false 
    }
  ];

  // Support line
  if (a && a.support) {
    datasets.push({
      label: `Support`, data: supportLine,
      borderColor: 'rgba(52,211,153,0.5)', borderWidth: 1.5, borderDash: [10, 5],
      pointRadius: 0, fill: false, tension: 0
    });
  }
  // Resistance line
  if (a && a.resistance) {
    datasets.push({
      label: `Resistance`, data: resistanceLine,
      borderColor: 'rgba(248,113,113,0.5)', borderWidth: 1.5, borderDash: [10, 5],
      pointRadius: 0, fill: false, tension: 0
    });
  }

  // Add the Smooth Predicted Curve
  if (pred) {
    const alpha = (pred.confidence / 100).toFixed(2);
    const pColorFull = `rgba(${pred.rgb}, 1)`;
    const pColorAlpha = `rgba(${pred.rgb}, ${alpha})`;

    datasets.push({
      label: `🔮 Predicted Future Line (Conf: ${Math.round(pred.confidence)}%)`, 
      data: predLine,
      borderColor: pColorAlpha, 
      borderWidth: 3, 
      borderDash: [8, 6],
      pointBackgroundColor: pColorFull, 
      pointBorderColor: '#fff', 
      pointBorderWidth: 2,
      // Highlight: Last real point and final predicted point
      pointRadius: (context) => {
        const index = context.dataIndex;
        if (index === h.length - 1) return 6; // Last real price
        if (index === predLine.length - 1) return 8; // Final predicted price
        return 0; // Hide intermediate points for clean curve
      },
      pointHoverRadius: 10, fill: false, 
      tension: 0.4, // Smooth curve
      spanGaps: true
    });
  }

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true, maintainAspectRatio: true,
      animation: {
        duration: 2500,
        easing: 'easeOutQuart'
      },
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { 
          labels: { color: '#64748b', font: { family: "'Inter',sans-serif", size: 12, weight: 600 }, usePointStyle: true, pointStyle: 'circle', padding: 20 } 
        },
        tooltip: {
          backgroundColor: 'rgba(6,8,15,0.92)', titleColor: '#f1f5f9', bodyColor: '#94a3b8',
          borderColor: 'rgba(99,102,241,0.2)', borderWidth: 1, padding: 12, cornerRadius: 10,
          titleFont: { family: "'Inter',sans-serif", weight: 600 }, bodyFont: { family: "'Inter',sans-serif" },
          callbacks: { 
            title: (ctxItems) => {
              if (ctxItems[0].label.includes('Future')) return "🔮 " + ctxItems[0].label;
              return ctxItems[0].label;
            },
            label: (c) => c.parsed.y === null ? null : ` ${c.dataset.label}: ₹${c.parsed.y.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` 
          }
        }
      },
      scales: {
        x: { 
          ticks: { 
            color: (c) => c.tick.label && c.tick.label.includes('Future') ? '#a78bfa' : '#475569', 
            font: { family: "'Inter',sans-serif", size: 11, weight: (c) => c.tick.label && c.tick.label.includes('Future') ? 'bold' : 'normal' }, 
            maxRotation: 45 
          }, 
          grid: { color: 'rgba(255,255,255,0.03)' } 
        },
        y: { 
          ticks: { color: '#475569', font: { family: "'Inter',sans-serif", size: 11 }, callback: (v) => '₹' + v.toLocaleString('en-IN') }, 
          grid: { color: 'rgba(255,255,255,0.03)' } 
        }
      }
    }
  });
}

// ─── LITERACY CARDS ───
function renderLiteracyCards() {
  el.literacyGrid.innerHTML = '';
  LITERACY_CARDS.forEach((card, i) => {
    const div = document.createElement('div');
    div.className = 'literacy-card reveal';
    div.style.transitionDelay = `${i * 0.06}s`;
    div.innerHTML = `<span class="literacy-icon">${card.icon}</span><h3>${card.title}</h3><p>${card.desc}</p>`;
    div.addEventListener('mousemove', (e) => {
      const r = div.getBoundingClientRect();
      div.style.setProperty('--mouse-x', `${e.clientX - r.left}px`);
      div.style.setProperty('--mouse-y', `${e.clientY - r.top}px`);
    });
    el.literacyGrid.appendChild(div);
  });
}

// ─── UTILS ───
function initScrollReveal() {
  const obs = new IntersectionObserver((e) => e.forEach(en => { if (en.isIntersecting) { en.target.classList.add('visible'); obs.unobserve(en.target); } }), { threshold: 0.1 });
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
}
function initNavHighlight() {
  const secs = $$('section[id]'), links = $$('.nav-link');
  const obs = new IntersectionObserver((e) => e.forEach(en => { if (en.isIntersecting) links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + en.target.id)); }), { threshold: 0.3 });
  secs.forEach(s => obs.observe(s));
}
function initMobileMenu() {
  el.mobileMenuBtn.addEventListener('click', () => { el.mainNav.classList.toggle('open'); el.mobileMenuBtn.classList.toggle('active'); });
  $$('.nav-link').forEach(l => l.addEventListener('click', () => { el.mainNav.classList.remove('open'); el.mobileMenuBtn.classList.remove('active'); }));
}
function initHeaderScroll() {
  const h = $('#main-header');
  window.addEventListener('scroll', () => h.classList.toggle('scrolled', window.scrollY > 40), { passive: true });
}

// ─── INIT ───
document.addEventListener('DOMContentLoaded', () => {
  renderLiteracyCards();
  fetchStockData('reliance');
  el.stockSelect.addEventListener('change', (e) => fetchStockData(e.target.value));
  el.refreshBtn.addEventListener('click', () => { fetchStockData(el.stockSelect.value); el.refreshBtn.style.transform = 'scale(0.95)'; setTimeout(() => el.refreshBtn.style.transform = 'scale(1)', 150); });
  el.errorRetryBtn.addEventListener('click', () => fetchStockData(el.stockSelect.value));
  initNavHighlight(); initMobileMenu(); initHeaderScroll();
  requestAnimationFrame(() => initScrollReveal());
  setInterval(() => fetchStockData(el.stockSelect.value), 30000);
});
