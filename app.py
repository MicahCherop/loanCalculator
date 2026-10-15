import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta
from decimal import Decimal
from calculator import calculate_loan, calculate_default_limit, LOYALTY_RATES

# =====================================================================
# Page config
# =====================================================================
st.set_page_config(
    page_title="Loan Calculator",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =====================================================================
# Session state
# =====================================================================
for key, default in {
    "active_page": "Loan calculator",
    "loan_calc": False,
    "def_calc": False,
    "scroll_to_result": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def set_page(page_name):
    st.session_state.active_page = page_name


def trigger_loan_calc():
    st.session_state.loan_calc = True
    st.session_state.scroll_to_result = True


def trigger_def_calc():
    st.session_state.def_calc = True
    st.session_state.scroll_to_result = True


def reset_loan():
    st.session_state.loan_calc = False
    for k in ["l_prin", "l_reg", "l_band", "l_start", "l_end", "l_part"]:
        if k in st.session_state:
            del st.session_state[k]


def reset_default():
    st.session_state.def_calc = False
    for k in ["d_amt", "d_days"]:
        if k in st.session_state:
            del st.session_state[k]


# =====================================================================
# Styling
# Palette: navy (primary), amber (accent), soft slate neutrals
# Type scale: 15px body, 13px captions, 22/20px headline (desktop/mobile)
# =====================================================================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

    :root {
        --navy: #0b2545;
        --navy-2: #13315c;
        --amber: #f5b301;
        --amber-dark: #d99f00;
        --amber-soft: #fff4d6;
        --bg: #f5f7fb;
        --surface: #ffffff;
        --border: #e3e8ef;
        --text: #1f2937;
        --muted: #64748b;
    }

    html, body, [class*="st-"], .stMarkdown, input, textarea, button {
        font-family: 'Poppins', sans-serif;
    }
    html, body { font-size: 15px; }

    /* App chrome */
    .stApp { background: var(--bg); }
    header[data-testid="stHeader"], #MainMenu, footer,
    [data-testid="collapsedControl"], [data-testid="stToolbar"] { display: none !important; }

    .block-container {
        max-width: 1040px;
        padding: 1rem 1.25rem 3rem !important;
    }

    /* Hide Streamlit Cloud badge, profile avatar and "Manage app" button */
    [class*="viewerBadge"], [class*="_profileContainer_"], [class*="_terminalButton_"],
    [class*="_container_gzau3"], [data-testid="manage-app-button"],
    [data-testid="stAppDeployButton"], .stAppDeployButton,
    [data-testid="stStatusWidget"], [data-testid="stDecoration"] { display: none !important; }

    /* ---------- Brand bar ---------- */
    .brand-bar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.75rem 1rem; margin-bottom: 1rem;
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 14px;
    }
    .brand { display: flex; align-items: center; gap: 10px; font-weight: 600; color: var(--navy); font-size: 0.95rem; letter-spacing: 0.4px; }
    .brand-icon {
        width: 32px; height: 32px; border-radius: 9px; background: var(--navy);
        display: flex; align-items: center; justify-content: center;
    }
    .brand-tag { color: var(--muted); font-size: 0.78rem; }

    /* ---------- Tabs (segmented control) ---------- */
    .st-key-nav [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important; gap: 0.35rem !important;
        background: #e9edf4; padding: 4px; border-radius: 12px;
    }
    .st-key-nav [data-testid="stColumn"], .st-key-nav [data-testid="column"] {
        min-width: 0 !important; flex: 1 1 0 !important; width: auto !important;
    }
    .st-key-nav button {
        min-height: 2.5rem; border-radius: 9px !important; border: none !important;
        font-weight: 500 !important; font-size: 0.88rem !important;
        padding: 0.25rem 0.5rem !important; box-shadow: none !important;
        background: transparent !important; color: var(--muted) !important;
    }
    .st-key-nav button[kind="primary"] {
        background: var(--surface) !important; color: var(--navy) !important;
        box-shadow: 0 1px 3px rgba(11, 37, 69, 0.12) !important; font-weight: 600 !important;
    }
    .st-key-nav button p { font-size: 0.88rem !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    /* ---------- Headings ---------- */
    .eyebrow { color: var(--amber-dark); font-size: 0.72rem; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; margin: 1.25rem 0 0.2rem; }
    .page-title { color: var(--navy); font-size: 1.6rem; font-weight: 600; line-height: 1.25; margin: 0 0 1.1rem; }
    .section-head { display: flex; align-items: center; gap: 10px; color: var(--navy); font-weight: 600; font-size: 1rem; margin-bottom: 0.9rem; }
    .section-num {
        background: var(--amber-soft); color: #946b00; border-radius: 8px;
        padding: 2px 9px; font-size: 0.75rem; font-weight: 600;
    }

    /* ---------- Form card ---------- */
    .st-key-form_card {
        background: var(--surface); border: 1px solid var(--border) !important;
        border-radius: 16px; padding: 1.25rem 1.25rem 1rem;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }
    .stNumberInput label, .stSelectbox label, .stDateInput label, .stCheckbox label,
    [data-testid="stWidgetLabel"] p {
        font-size: 0.85rem !important; font-weight: 500; color: var(--text);
    }
    /* 16px inputs stop iOS from zooming on focus */
    input, [data-baseweb="select"] div { font-size: 16px !important; }
    [data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="base-input"] {
        border-radius: 10px !important;
    }
    [data-testid="stCaptionContainer"] p, .stCaption { font-size: 0.78rem !important; color: var(--muted) !important; }

    .rate-chip {
        display: flex; justify-content: space-between; align-items: center;
        background: var(--amber-soft); border: 1px solid #f6e3a6; border-radius: 10px;
        padding: 8px 12px; font-size: 0.82rem; margin: -0.25rem 0 0.9rem;
    }
    .rate-chip span:first-child { color: #6b5200; }
    .rate-chip span:last-child { color: #7a5800; font-weight: 600; }

    .info-pill {
        display: flex; align-items: center; gap: 8px;
        background: #eef3fb; color: var(--navy-2); border-radius: 10px;
        padding: 9px 12px; font-size: 0.82rem; margin: 0.25rem 0 1rem;
    }

    .stAlert { border-radius: 10px; font-size: 0.85rem; }

    /* ---------- Buttons ---------- */
    .stButton > button { min-height: 2.9rem; border-radius: 12px; font-weight: 600; font-size: 0.92rem; transition: all .15s ease; }
    .stButton > button[kind="primary"] { background: var(--navy); color: #fff; border: none; }
    .stButton > button[kind="primary"]:hover { background: var(--navy-2); color: #fff; }
    .stButton > button[kind="secondary"] { background: var(--surface); color: var(--navy); border: 1px solid var(--border); }
    .stButton > button[kind="secondary"]:hover { background: #f1f4f9; border-color: #cbd5e1; color: var(--navy); }
    .st-key-actions [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0.6rem !important; }
    .st-key-actions [data-testid="stColumn"], .st-key-actions [data-testid="column"] { min-width: 0 !important; }

    /* ---------- Result card ---------- */
    .result-box {
        background: linear-gradient(160deg, var(--navy) 0%, var(--navy-2) 100%);
        color: #fff; padding: 1.4rem; border-radius: 18px;
        box-shadow: 0 10px 24px rgba(11, 37, 69, 0.18);
    }
    .result-box * { color: #fff; }
    .result-top { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .result-title { font-size: 0.95rem; font-weight: 600; margin: 0; }
    .badge { border: 1px solid rgba(255,255,255,0.35); border-radius: 999px; padding: 3px 11px; font-size: 0.72rem; white-space: nowrap; }
    .label-sm { font-size: 0.8rem; opacity: 0.75; margin-top: 1.1rem; }
    .prominent { font-size: 2rem; font-weight: 600; line-height: 1.2; margin: 0.15rem 0 0.2rem; color: var(--amber) !important; }
    .note-sm { font-size: 0.75rem; opacity: 0.7; }
    .highlight-sm { color: var(--amber) !important; font-size: 0.75rem; font-weight: 500; margin-top: 0.3rem; }
    .divider { border-top: 1px solid rgba(255,255,255,0.14); margin: 1.1rem 0 0.9rem; }
    .flex-row { display: flex; justify-content: space-between; gap: 12px; padding: 5px 0; font-size: 0.85rem; }
    .flex-row span:first-child { opacity: 0.78; }
    .flex-row span:last-child { font-weight: 500; text-align: right; }
    .sub-card { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 0.9rem; margin-top: 1rem; }
    .sub-card .title { font-size: 0.82rem; font-weight: 600; }
    .sub-card .hint { font-size: 0.72rem; opacity: 0.7; margin: 2px 0 8px; }
    .bar { width: 100%; height: 6px; background: rgba(255,255,255,0.18); border-radius: 99px; overflow: hidden; margin-top: 8px; }
    .bar > div { height: 100%; background: var(--amber); border-radius: 99px; }
    .big-amber { color: var(--amber) !important; font-size: 1.4rem; font-weight: 600; }
    .empty-state {
        display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 6px;
        min-height: 240px; text-align: center; padding: 1.5rem;
        background: var(--surface); border: 1.5px dashed #cbd5e1; border-radius: 18px;
        color: var(--muted); font-size: 0.88rem;
    }
    .empty-state .icon { font-size: 1.6rem; }

    /* ---------- Tablet / Mobile ---------- */
    @media (max-width: 768px) {
        html, body { font-size: 15px; }
        .block-container { padding: 0.75rem 0.9rem 2.5rem !important; }
        .brand-bar { padding: 0.6rem 0.8rem; border-radius: 12px; }
        .brand-tag { display: none; }
        .page-title { font-size: 1.35rem; margin-bottom: 0.9rem; }
        .eyebrow { margin-top: 1rem; }
        .st-key-form_card { padding: 1rem 0.95rem 0.8rem; border-radius: 14px; }
        .result-box { padding: 1.15rem; border-radius: 16px; margin-top: 0.5rem; }
        .prominent { font-size: 1.75rem; }
        .flex-row { font-size: 0.83rem; }
    }
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================================
# Helpers
# =====================================================================
def section_head(num: str, title: str):
    st.markdown(
        f'<div class="section-head"><span class="section-num">{num}</span>{title}</div>',
        unsafe_allow_html=True,
    )


def row(label: str, value: str) -> str:
    return f'<div class="flex-row"><span>{label}</span><span>{value}</span></div>'


def scroll_to_result_once():
    """On narrow screens the result stacks below the form; bring it into view."""
    if st.session_state.scroll_to_result:
        st.session_state.scroll_to_result = False
        components.html(
            """
            <script>
              const doc = window.parent.document;
              setTimeout(() => {
                const el = doc.getElementById('result-anchor');
                if (el && window.parent.innerWidth <= 768) {
                  el.scrollIntoView({behavior: 'smooth', block: 'start'});
                }
              }, 250);
            </script>
            """,
            height=0,
        )


# =====================================================================
# Brand bar
# =====================================================================
st.markdown(
    """
<div class="brand-bar">
    <div class="brand">
        <div class="brand-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f5b301" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="4" y="2" width="16" height="20" rx="2"></rect>
                <line x1="8" y1="6" x2="16" y2="6"></line>
                <path d="M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01M16 18h.01"></path>
            </svg>
        </div>
        LOAN CALCULATOR
    </div>
    <div class="brand-tag">A clearer view of your repayment</div>
</div>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# Tab navigation (active tab is the "primary" button)
# =====================================================================
LOAN_TAB = "Loan calculator"
DEFAULT_TAB = "Consequences of default"

with st.container(key="nav"):
    n1, n2 = st.columns(2)
    with n1:
        st.button(
            LOAN_TAB, key="nav_loan", on_click=set_page, args=(LOAN_TAB,),
            type="primary" if st.session_state.active_page == LOAN_TAB else "secondary",
            use_container_width=True,
        )
    with n2:
        st.button(
            DEFAULT_TAB, key="nav_default", on_click=set_page, args=(DEFAULT_TAB,),
            type="primary" if st.session_state.active_page == DEFAULT_TAB else "secondary",
            use_container_width=True,
        )

# Swipe between tabs (ignores swipes on inputs/pickers and mostly-vertical scrolls)
components.html(
    """
<script>
(function () {
  const doc = window.parent.document;
  if (doc.__swipeBound) return;
  doc.__swipeBound = true;
  let sx = 0, sy = 0, skip = false;

  doc.addEventListener('touchstart', e => {
    const t = e.changedTouches[0];
    sx = t.screenX; sy = t.screenY;
    skip = !!e.target.closest('input, textarea, select, [data-baseweb="select"], [data-baseweb="calendar"], [role="listbox"], [data-baseweb="popover"]');
  }, {passive: true});

  doc.addEventListener('touchend', e => {
    if (skip) return;
    const t = e.changedTouches[0];
    const dx = t.screenX - sx, dy = t.screenY - sy;
    if (Math.abs(dx) < 90 || Math.abs(dx) < Math.abs(dy) * 1.8) return;
    const btns = Array.from(doc.querySelectorAll('.st-key-nav button'));
    if (btns.length < 2) return;
    (dx < 0 ? btns[1] : btns[0]).click();
  }, {passive: true});
})();
</script>
""",
    height=0,
)

# =====================================================================
# Hide platform badge (JS fallback) + PWA install button (bottom right)
# The manifest and icons are generated in the browser, so no static files
# (and no extra network requests) are needed.
# =====================================================================
components.html(
    """
<script>
(function () {
  let host;
  try { void window.top.document.body; host = window.top; } catch (e) { host = window.parent; }
  if (host.__appShellInit) return;
  host.__appShellInit = true;

  const docs = [];
  [host, window.parent].forEach(w => {
    try { if (w.document && docs.indexOf(w.document) === -1) docs.push(w.document); } catch (e) {}
  });
  const hdoc = host.document;

  /* ---------- 1. Hide Streamlit Cloud badge / Manage app button ---------- */
  const HIDE = [
    '[class*="viewerBadge"]', '[class*="_profileContainer_"]', '[class*="_terminalButton_"]',
    '[class*="_container_gzau3"]', '[data-testid="manage-app-button"]',
    '[data-testid="stAppDeployButton"]', '.stAppDeployButton'
  ];
  docs.forEach(d => {
    try {
      if (d.getElementById('hide-platform-badges')) return;
      const st = d.createElement('style');
      st.id = 'hide-platform-badges';
      st.textContent = HIDE.join(',') + '{display:none !important;}';
      d.head.appendChild(st);
    } catch (e) {}
  });
  function hideBadges() {
    docs.forEach(d => HIDE.forEach(s => {
      try { d.querySelectorAll(s).forEach(n => n.style.setProperty('display', 'none', 'important')); } catch (e) {}
    }));
  }
  hideBadges();
  docs.forEach(d => {
    try { new MutationObserver(hideBadges).observe(d.body, {childList: true, subtree: true}); } catch (e) {}
  });

  /* ---------- 2. Manifest + icons, built in the browser ---------- */
  function rr(g, x, y, w, h, r) {
    g.beginPath(); g.moveTo(x + r, y);
    g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r);
    g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
  }
  function drawIcon(size) {
    const c = hdoc.createElement('canvas');
    c.width = size; c.height = size;
    const g = c.getContext('2d');
    const k = size / 512;
    const amber = '#f5b301';
    g.fillStyle = '#0b2545'; g.fillRect(0, 0, size, size);
    rr(g, 136 * k, 96 * k, 240 * k, 320 * k, 36 * k);
    g.fillStyle = '#13315c'; g.fill();
    g.lineWidth = 14 * k; g.strokeStyle = amber; g.stroke();
    rr(g, 176 * k, 140 * k, 160 * k, 56 * k, 12 * k);
    g.fillStyle = amber; g.fill();
    [246, 306, 366].forEach((y, r) => [196, 256, 316].forEach((x, cI) => {
      g.beginPath(); g.arc(x * k, y * k, 15 * k, 0, Math.PI * 2);
      g.fillStyle = (r === 2 && cI === 2) ? amber : '#ffffff'; g.fill();
    }));
    return c.toDataURL('image/png');
  }

  try {
    const origin = host.location.origin;
    const icon192 = drawIcon(192), icon512 = drawIcon(512);
    const manifest = {
      id: origin + '/',
      name: 'Loan Calculator',
      short_name: 'Loan Calc',
      description: 'A clearer view of your loan repayment.',
      start_url: origin + host.location.pathname,
      scope: origin + '/',
      display: 'standalone',
      orientation: 'portrait',
      background_color: '#f5f7fb',
      theme_color: '#0b2545',
      icons: [
        {src: icon192, sizes: '192x192', type: 'image/png', purpose: 'any'},
        {src: icon512, sizes: '512x512', type: 'image/png', purpose: 'any'},
        {src: icon512, sizes: '512x512', type: 'image/png', purpose: 'maskable'}
      ]
    };
    const url = URL.createObjectURL(new Blob([JSON.stringify(manifest)], {type: 'application/manifest+json'}));
    hdoc.querySelectorAll('link[rel="manifest"]').forEach(n => n.remove());
    const add = (tag, attrs) => {
      const el = hdoc.createElement(tag);
      Object.keys(attrs).forEach(k => el.setAttribute(k, attrs[k]));
      hdoc.head.appendChild(el);
    };
    add('link', {rel: 'manifest', href: url});
    add('link', {rel: 'apple-touch-icon', href: icon192});
    add('meta', {name: 'theme-color', content: '#0b2545'});
    add('meta', {name: 'apple-mobile-web-app-capable', content: 'yes'});
    add('meta', {name: 'mobile-web-app-capable', content: 'yes'});
    add('meta', {name: 'apple-mobile-web-app-title', content: 'Loan Calc'});
  } catch (e) {}

  /* ---------- 3. Offline notice ---------- */
  const note = hdoc.createElement('div');
  note.id = 'pwa-offline-note';
  note.textContent = 'You are offline. Calculations need an internet connection.';
  Object.assign(note.style, {
    position: 'fixed', top: '12px', left: '50%', transform: 'translateX(-50%)',
    zIndex: '2147483000', display: 'none', maxWidth: '90vw', textAlign: 'center',
    padding: '9px 16px', borderRadius: '999px', background: '#0b2545', color: '#fff',
    font: '500 13px Poppins, system-ui, sans-serif', boxShadow: '0 8px 20px rgba(11, 37, 69, 0.25)'
  });
  hdoc.body.appendChild(note);
  const syncOnline = () => { note.style.display = host.navigator.onLine ? 'none' : 'block'; };
  host.addEventListener('online', syncOnline);
  host.addEventListener('offline', syncOnline);
  syncOnline();

  /* ---------- 4. Install button, bottom right (always visible in a browser tab) ---------- */
  const standalone = host.matchMedia('(display-mode: standalone)').matches || host.navigator.standalone === true;
  if (standalone) return;

  const btn = hdoc.createElement('button');
  btn.id = 'pwa-install-btn';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Install app');
  btn.innerHTML =
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f5b301" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m7 11 5 5 5-5"/><path d="M5 20h14"/></svg><span>Install app</span>';
  Object.assign(btn.style, {
    position: 'fixed', right: '16px', bottom: 'calc(16px + env(safe-area-inset-bottom, 0px))',
    zIndex: '2147483000', display: 'inline-flex', alignItems: 'center', gap: '8px',
    padding: '11px 16px', border: 'none', borderRadius: '999px',
    background: '#0b2545', color: '#ffffff',
    font: '600 14px Poppins, system-ui, sans-serif',
    boxShadow: '0 8px 20px rgba(11, 37, 69, 0.28)', cursor: 'pointer'
  });
  hdoc.body.appendChild(btn);

  function showTip(text) {
    const tip = hdoc.createElement('div');
    tip.textContent = text;
    Object.assign(tip.style, {
      position: 'fixed', right: '16px', bottom: 'calc(72px + env(safe-area-inset-bottom, 0px))',
      zIndex: '2147483000', maxWidth: '260px', padding: '10px 14px', borderRadius: '12px',
      background: '#ffffff', color: '#0b2545', border: '1px solid #e3e8ef',
      font: '500 13px Poppins, system-ui, sans-serif', boxShadow: '0 8px 20px rgba(11, 37, 69, 0.18)'
    });
    hdoc.body.appendChild(tip);
    setTimeout(() => tip.remove(), 7000);
  }

  let deferred = null;
  host.addEventListener('beforeinstallprompt', e => { e.preventDefault(); deferred = e; });
  host.addEventListener('appinstalled', () => { btn.style.display = 'none'; deferred = null; });

  const isIOS = /iphone|ipad|ipod/i.test(host.navigator.userAgent);
  btn.addEventListener('click', async () => {
    if (deferred) {
      deferred.prompt();
      try { await deferred.userChoice; } catch (e) {}
      deferred = null;
    } else if (isIOS) {
      showTip('Tap the Share icon, then choose "Add to Home Screen".');
    } else {
      showTip('Open your browser menu and choose "Install app" or "Add to Home screen".');
    }
  });
})();
</script>
""",
    height=0,
)

# =====================================================================
# Page 1: Loan calculator
# =====================================================================
if st.session_state.active_page == LOAN_TAB:
    st.markdown('<div class="eyebrow">Plan with confidence</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Your loan. Clearly calculated.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 1], gap="large")

    with col1:
        with st.container(border=True, key="form_card"):
            section_head("01", "Loan details")

            principal = st.number_input(
                "Loan amount (KSh)", min_value=5000.0, value=None, step=500.0,
                format="%.2f", placeholder="e.g. 5000.00", key="l_prin",
            )
            st.caption("Minimum loan amount: KSh 5,000")

            add_reg_fee = st.checkbox("Add KSh 500 registration fee", key="l_reg")

            loyalty_band = st.selectbox(
                "Loyalty band", options=list(LOYALTY_RATES.keys()), index=None,
                placeholder="Select a loyalty band", key="l_band",
            )
            if loyalty_band:
                current_rate = LOYALTY_RATES[loyalty_band] * 100
                st.markdown(
                    f'<div class="rate-chip"><span>Daily interest rate</span>'
                    f"<span>{current_rate:g}% per day</span></div>",
                    unsafe_allow_html=True,
                )

            c_start, c_end = st.columns(2)
            with c_start:
                start_date = st.date_input(
                    "Disbursement date", value=None, min_value=date(2000, 1, 1),
                    max_value=date(2100, 1, 1), key="l_start",
                )
            with c_end:
                if start_date:
                    end_date = st.date_input(
                        "End date", value=None, min_value=start_date,
                        max_value=start_date + timedelta(days=30), key="l_end",
                    )
                else:
                    end_date = st.date_input("Repayment Date", value=None, disabled=True, key="l_end")

            if start_date and end_date:
                days = (end_date - start_date).days
                st.markdown(
                    f'<div class="info-pill">📅 <span><b>{days} days</b> with loan · Maximum 30 days</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="info-pill">📅 <span>Select a start and end date · Maximum 30 days</span></div>',
                    unsafe_allow_html=True,
                )

            partial_payment = st.number_input(
                "Partial payment already made (KSh)", min_value=0.0, value=None,
                step=100.0, format="%.2f", placeholder="e.g. 0.00", key="l_part",
            )
            st.caption("Deducted from the total after interest is calculated.")

            st.write("")
            with st.container(key="actions"):
                b1, b2 = st.columns([2, 1])
                with b1:
                    st.button("Calculate repayment →", type="primary",
                              on_click=trigger_loan_calc, use_container_width=True)
                with b2:
                    st.button("Reset", type="secondary", on_click=reset_loan, use_container_width=True)

    with col2:
        st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
        if st.session_state.loan_calc:
            if principal is None or loyalty_band is None or start_date is None or end_date is None:
                st.warning("Please fill out the loan amount, loyalty band, and both dates to calculate.")
            else:
                try:
                    pp_val = Decimal(str(partial_payment)) if partial_payment is not None else Decimal("0.0")

                    res = calculate_loan(Decimal(str(principal)), loyalty_band, start_date, end_date, pp_val)

                    # Registration fee injection
                    reg_fee = Decimal("500.00") if add_reg_fee else Decimal("0.00")
                    res["total_before_payment"] += reg_fee
                    res["payable_amount"] = max(Decimal("0"), res["total_before_payment"] - pp_val)

                    res["expected_payment_30_days"] += reg_fee
                    res["remaining_payment_30_days"] = max(Decimal("0"), res["expected_payment_30_days"] - pp_val)

                    daily_int = res["principal"] * res["daily_rate"]
                    tenure_pct = min(100, max(0, int(res["actual_days"]) / 30 * 100))

                    rows = row("Loan principal", f"KSh {res['principal']:,.2f}")
                    if reg_fee > 0:
                        rows += row("Registration fee", f"KSh {reg_fee:,.2f}")
                    rows += row("Daily interest charged", f"KSh {daily_int:,.2f}")
                    rows += row(f"Interest ({res['interest_days']} days)", f"KSh {res['interest']:,.2f}")
                    rows += row("Total before payment", f"KSh {res['total_before_payment']:,.2f}")
                    rows += row("Partial payment", f"- KSh {res['partial_payment']:,.2f}")

                    st.markdown(
                        f"""
                        <div class="result-box">
                            <div class="result-top">
                                <p class="result-title">Repayment summary</p>
                                <span class="badge">{loyalty_band}</span>
                            </div>
                            <div class="label-sm">Payable amount</div>
                            <div class="prominent">KSh {res['payable_amount']:,.2f}</div>
                            <div class="note-sm">For your selected loan period ({res['actual_days']} days)</div>
                            <div class="bar"><div style="width:{tenure_pct:.0f}%"></div></div>
                            <div class="divider"></div>
                            {rows}
                            <div class="sub-card">
                                <div class="title">Expected payment in 30 days</div>
                                <div class="hint">Principal + 30 days of interest, before partial payments</div>
                                {row("After partial payment", f"KSh {res['remaining_payment_30_days']:,.2f}")}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    scroll_to_result_once()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.markdown(
                '<div class="empty-state"><div class="icon">🧾</div>'
                "<div><b>Your summary will appear here</b><br>Fill in the details and tap Calculate.</div></div>",
                unsafe_allow_html=True,
            )

# =====================================================================
# Page 2: Consequences of default
# =====================================================================
elif st.session_state.active_page == DEFAULT_TAB:
    st.markdown('<div class="eyebrow">Understand your next limit</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Consequences of default</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 1], gap="large")

    with col1:
        with st.container(border=True, key="form_card"):
            section_head("01", "Default details")

            disbursed = st.number_input(
                "Disbursement amount defaulted (KSh)", min_value=5000.0, value=None,
                step=500.0, placeholder="e.g. 10000.00", key="d_amt",
            )
            st.caption("Original disbursement amount · Minimum KSh 5,000")

            total_days_input = st.number_input(
                "Total days with the loan", min_value=30, value=None, step=1,
                placeholder="e.g. 42", key="d_days",
            )
            st.caption("Total days including the maximum 30-day loan tenure.")

            st.write("")
            with st.container(key="actions"):
                b1, b2 = st.columns([2, 1])
                with b1:
                    st.button("Calculate adjusted limit →", type="primary",
                              on_click=trigger_def_calc, use_container_width=True)
                with b2:
                    st.button("Reset", type="secondary", on_click=reset_default, use_container_width=True)

    with col2:
        st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
        if st.session_state.def_calc:
            if disbursed is None or total_days_input is None:
                st.warning("Please fill out both the disbursement amount and total days.")
            else:
                try:
                    days_in_default = total_days_input - 30
                    res = calculate_default_limit(Decimal(str(disbursed)), int(days_in_default))

                    tenure_ratio = (Decimal("1") - (Decimal(res["retained_limit_pct"]) / 100)) * 100
                    rows = (
                        row("Disbursement amount", f"KSh {res['original_amount']:,.2f}")
                        + row("Total days with loan", f"{res['total_days']} days")
                        + row("Tenure ratio", f"{tenure_ratio:.2f}%")
                        + row("Retain limit", f"{res['retained_limit_pct']}%")
                        + row("Adjusted amount", f"KSh {res['adjusted_amount']:,.2f}")
                    )

                    st.markdown(
                        f"""
                        <div class="result-box">
                            <div class="result-top"><p class="result-title">Adjusted loan limit</p></div>
                            <div class="label-sm">Final amount</div>
                            <div class="prominent">KSh {res['final_limit']:,.2f}</div>
                            <div class="note-sm">Rounded down to the nearest KSh 100</div>
                            <div class="highlight-sm">34–119 total days · Variable retention applies</div>
                            <div class="divider"></div>
                            {rows}
                            <div class="sub-card">
                                <div class="title">Reduction from original disbursement</div>
                                <div class="big-amber">KSh {res['original_amount'] - res['final_limit']:,.2f}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    scroll_to_result_once()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.markdown(
                '<div class="empty-state"><div class="icon">📉</div>'
                "<div><b>Your adjusted limit will appear here</b><br>Fill in the details and tap Calculate.</div></div>",
                unsafe_allow_html=True,
            )