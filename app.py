import streamlit as st
import math
import plotly.graph_objects as go
import random
import string

st.set_page_config(
    page_title="Password Security Analyzer | Kel. 2 PTIK-D UNIMED",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def hitung_k(lo, up, dg, sy):
    k = 0
    if lo: k += 26
    if up: k += 26
    if dg: k += 10
    if sy: k += 32
    return k if k > 0 else 26

def get_tingkat(H):
    if H >= 100: return ("Sangat Kuat",  "🏆", "#22c55e",  "rgba(34,197,94,.14)",   "rgba(34,197,94,.4)",   "great")
    if H >= 80:  return ("Kuat",         "✅", "#38bdf8",  "rgba(56,189,248,.14)",  "rgba(56,189,248,.4)",  "good")
    if H >= 56:  return ("Sedang",       "⚡", "#f59e0b",  "rgba(245,158,11,.14)",  "rgba(245,158,11,.4)",  "medium")
    if H >= 40:  return ("Lemah",        "⚠️", "#f97316",  "rgba(249,115,22,.14)",  "rgba(249,115,22,.4)",  "bad")
    return             ("Sangat Lemah", "💀", "#ef4444",  "rgba(239,68,68,.14)",   "rgba(239,68,68,.4)",   "danger")

def fmt_n(n):
    return f"{int(n):,}".replace(",", ".")

def fmt_w(s):
    s = int(s)
    if s < 60:             return f"{fmt_n(s)} detik"
    if s < 3600:           return f"{fmt_n(s//60)} menit"
    if s < 86400:          return f"{fmt_n(s//3600)} jam"
    if s < 86400*365:      return f"{fmt_n(s//86400)} hari"
    if s < 86400*365*1000: return f"{fmt_n(s//(86400*365))} tahun"
    if s < 86400*365*1e6:  return f"{fmt_n(s//(86400*365*1000))} ribu tahun"
    if s < 86400*365*1e9:  return f"{fmt_n(s//(86400*365*1000000))} juta tahun"
    return f"{fmt_n(s//(86400*365*1000000000))} miliar tahun"

def suggest_password_improvements(original_pwd, n_suggestions=3):
    symbols = "!@#$%^&*_+-="
    suggestions = []
    leet_map = {'a':'@','A':'@','e':'3','E':'3','i':'!','I':'!',
                'o':'0','O':'0','s':'$','S':'$'}
    for attempt in range(80):
        if len(suggestions) >= n_suggestions:
            break
        mode = attempt % 5
        if mode == 0:
            prefix = random.choice(string.ascii_uppercase) + random.choice(string.digits)
            suffix = random.choice(symbols) + random.choice(string.digits) + random.choice(string.ascii_uppercase)
            candidate = prefix + original_pwd + suffix
        elif mode == 1:
            modified = ""
            for ch in original_pwd:
                if ch in leet_map and random.random() > 0.5:
                    modified += leet_map[ch]
                else:
                    modified += ch
            if modified == modified.lower():
                pos = random.randint(0, max(0, len(modified)-1))
                modified = modified[:pos] + modified[pos].upper() + modified[pos+1:]
            candidate = modified + random.choice(symbols) + str(random.randint(10,99))
        elif mode == 2:
            base = list(original_pwd)
            ins_pos1 = random.randint(0, len(base))
            ins_pos2 = random.randint(0, len(base)+1)
            base.insert(ins_pos1, random.choice(symbols))
            base.insert(ins_pos2, str(random.randint(0,9)))
            if not any(c.isupper() for c in base):
                base[0] = base[0].upper()
            candidate = ''.join(base) + random.choice(string.ascii_uppercase)
        elif mode == 3:
            yr = str(random.randint(2025, 2099))
            sym = random.choice(symbols)
            candidate = original_pwd + sym + yr + random.choice(string.ascii_uppercase)
        else:
            modified = ""
            for ch in original_pwd:
                if ch in leet_map:
                    modified += leet_map[ch]
                else:
                    modified += ch
            candidate = modified + random.choice(symbols)*2 + str(random.randint(100,999))
        has_lo = any(c.islower() for c in candidate)
        has_up = any(c.isupper() for c in candidate)
        has_dg = any(c.isdigit() for c in candidate)
        has_sy = any(not c.isalnum() for c in candidate)
        if has_lo and has_up and has_dg and has_sy and len(candidate) >= 12:
            H_val = len(candidate) * math.log2(94)
            if H_val >= 80:
                suggestions.append((candidate, H_val, len(candidate)))
    while len(suggestions) < n_suggestions:
        length = max(14, len(original_pwd) + 4)
        chars_all = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%^&*_+-="
        for _ in range(100):
            pwd = original_pwd[:min(4, len(original_pwd))] + ''.join(random.choices(chars_all, k=length - min(4, len(original_pwd))))
            if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd)
                    and any(c.isdigit() for c in pwd) and any(not c.isalnum() for c in pwd)):
                H_v = len(pwd) * math.log2(94)
                if H_v >= 80:
                    suggestions.append((pwd, H_v, len(pwd)))
                    break
    return suggestions[:n_suggestions]

def highlight_additions(original, suggestion):
    orig_set = set(original)
    result = ""
    for ch in suggestion:
        if ch not in orig_set or ch in "!@#$%^&*_+-=0123456789":
            result += f'<span style="color:#fde68a;font-weight:700;">{ch}</span>'
        else:
            result += ch
    return result

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin:0; padding:0; }
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

.stApp { background: #04080f; min-height: 100vh; }

.bg-mesh {
    position:fixed; inset:0; pointer-events:none; z-index:0;
    background:
        radial-gradient(ellipse 70% 55% at 8% 8%,   rgba(56,189,248,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 55% 45% at 92% 85%,  rgba(168,85,247,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 45% 40% at 50% 50%,  rgba(34,197,94,0.05)  0%, transparent 60%),
        radial-gradient(ellipse 80% 60% at 20% 80%,  rgba(251,113,133,0.06) 0%, transparent 60%);
    animation: meshPulse 10s ease-in-out infinite alternate;
}
@keyframes meshPulse { 0%{opacity:.6;transform:scale(1)} 100%{opacity:1;transform:scale(1.03)} }

.bg-grid {
    position:fixed; inset:0; pointer-events:none; z-index:0;
    background-image:
        linear-gradient(rgba(56,189,248,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
}

.particles { position:fixed; inset:0; pointer-events:none; z-index:0; overflow:hidden; }
.p { position:absolute; border-radius:50%; animation:rise linear infinite; opacity:0; }
@keyframes rise {
    0%  {transform:translateY(105vh) scale(0);opacity:0;}
    6%  {opacity:.7;}
    94% {opacity:.4;}
    100%{transform:translateY(-5vh) scale(1.5);opacity:0;}
}

/* ======= HERO LANDING ======= */
.hero-wrap {
    position:relative; z-index:1; margin-bottom:2rem;
    border-radius:28px; overflow:hidden;
    border:1px solid rgba(56,189,248,0.2);
    box-shadow: 0 0 0 1px rgba(56,189,248,0.05), 0 32px 64px rgba(0,0,0,0.7),
                inset 0 1px 0 rgba(255,255,255,0.06),
                0 0 80px rgba(56,189,248,0.04);
    background: linear-gradient(135deg,
        rgba(4,14,32,0.99) 0%, rgba(6,20,50,0.97) 40%,
        rgba(4,14,32,0.99) 100%);
}
.hero-topbar {
    height:3px; width:100%;
    background: linear-gradient(90deg,
        transparent 0%, #38bdf8 15%, #a855f7 50%, #22c55e 85%, transparent 100%);
    animation: topLine 4s ease infinite;
}
@keyframes topLine { 0%,100%{opacity:.6} 50%{opacity:1} }

.hero-body {
    display:flex; align-items:center; gap:3rem;
    padding: 2.75rem 3.5rem 2.25rem;
}
.hero-left  { flex:1.3; }
.hero-right { flex:0.7; display:flex; justify-content:center; align-items:center; }

.hero-eyebrow {
    display:inline-flex; align-items:center; gap:8px;
    font-family:'JetBrains Mono',monospace;
    font-size:11px; font-weight:600; letter-spacing:.15em; text-transform:uppercase;
    color:#38bdf8;
    background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.22);
    border-radius:20px; padding:5px 14px; margin-bottom:1.2rem;
}
.hero-dot {
    width:6px; height:6px; border-radius:50%; background:#38bdf8;
    box-shadow:0 0 8px #38bdf8; animation:blink 2s ease infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }

.hero-h1 {
    font-family:'Orbitron',sans-serif;
    font-size:3.2rem;
    font-weight:900;
    line-height:1.08;
    letter-spacing:3px;
    margin-bottom:1rem;

    background:linear-gradient(
        135deg,
        #e0f2fe 0%,
        #38bdf8 25%,
        #a855f7 55%,
        #22c55e 85%,
        #e0f2fe 100%
    );

    background-size:300% 300%;

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;

    animation:
        neonMove 6s ease infinite,
        titleFloat 4s ease-in-out infinite;

    text-shadow:
        0 0 10px rgba(56,189,248,.25),
        0 0 20px rgba(168,85,247,.18);

    position:relative;
}
}
@keyframes neonMove{
    0%{
        background-position:0% 50%;
    }
    50%{
        background-position:100% 50%;
    }
    100%{
        background-position:0% 50%;
    }
}

@keyframes titleFloat{
    0%,100%{
        transform:translateY(0px);
    }
    50%{
        transform:translateY(-6px);
    }
}

.hero-tujuan {
    background:rgba(56,189,248,0.06);
    border:1px solid rgba(56,189,248,0.15);
    border-left:3px solid #38bdf8;
    border-radius:0 12px 12px 0;
    padding:14px 18px; margin-bottom:1rem;
}
.hero-tujuan-title {
    font-size:10px; font-weight:700; text-transform:uppercase;
    letter-spacing:.12em; color:#38bdf8; margin-bottom:8px;
}
.hero-tujuan-list {
    list-style:none; padding:0; margin:0;
}
.hero-tujuan-list li {
    font-size:12.5px; color:#94a3b8; line-height:1.7;
    display:flex; align-items:flex-start; gap:8px;
}
.hero-tujuan-list li::before {
    content:'▸'; color:#38bdf8; font-size:10px; margin-top:3px; flex-shrink:0;
}
.hero-tujuan-list li strong { color:#cbd5e1; }

.math-strip {
    display:flex; gap:8px; flex-wrap:wrap; margin-bottom:1rem;
}
.math-chip {
    font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:600;
    padding:5px 11px; border-radius:8px; border:1px solid;
    cursor:default; transition:all .2s;
}
.math-chip:hover { transform:translateY(-2px); }
.mc1{background:rgba(56,189,248,.07);border-color:rgba(56,189,248,.2);color:#7dd3fc;}
.mc2{background:rgba(168,85,247,.07);border-color:rgba(168,85,247,.2);color:#c4b5fd;}
.mc3{background:rgba(34,197,94,.07);border-color:rgba(34,197,94,.2);color:#86efac;}
.mc4{background:rgba(245,158,11,.07);border-color:rgba(245,158,11,.2);color:#fde68a;}

.privacy-note {
    display:flex; align-items:center; gap:9px;
    background:rgba(34,197,94,.07); border:1px solid rgba(34,197,94,.2);
    border-radius:10px; padding:10px 14px;
    font-size:12px; color:#86efac; font-weight:500; margin-bottom:1.1rem;
}

.hero-badges { display:flex; gap:6px; flex-wrap:wrap; }
.bdg {
    font-size:11px; font-weight:600; padding:5px 12px; border-radius:16px;
    border:1px solid; cursor:default; transition:transform .2s;
}
.bdg:hover{transform:translateY(-3px);}
.b1{background:rgba(56,189,248,.08);border-color:rgba(56,189,248,.25);color:#7dd3fc;}
.b2{background:rgba(168,85,247,.08);border-color:rgba(168,85,247,.25);color:#c4b5fd;}
.b3{background:rgba(34,197,94,.08);border-color:rgba(34,197,94,.25);color:#86efac;}
.b4{background:rgba(245,158,11,.08);border-color:rgba(245,158,11,.25);color:#fde68a;}
.b5{background:rgba(244,63,94,.08);border-color:rgba(244,63,94,.25);color:#fda4af;}

/* Shield */
.shield-wrap { position:relative; width:180px; height:180px; }
.orbit-ring {
    position:absolute; border-radius:50%; border:1px solid;
    top:50%; left:50%; transform:translate(-50%,-50%);
    animation:spin linear infinite;
}
@keyframes spin { to{transform:translate(-50%,-50%) rotate(360deg)} }
.shield-center {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-52%);
    animation:shieldFloat 4s ease-in-out infinite;
    filter:drop-shadow(0 0 24px rgba(56,189,248,.45));
}
@keyframes shieldFloat { 0%,100%{transform:translate(-50%,-52%) translateY(0)} 50%{transform:translate(-50%,-52%) translateY(-10px)} }

/* Hero bottom bar */
.hero-bottom {
    border-top:1px solid rgba(255,255,255,.05);
    padding:1rem 3.5rem;
    display:flex; justify-content:space-between; align-items:center;
    background:rgba(0,0,0,.2);
}
.made-tag { font-size:12px; color:#475569; }
.made-tag strong { color:#64748b; }
.formula-strip-bot {
    display:flex; gap:16px;
    font-family:'JetBrains Mono',monospace; font-size:11px; color:#334155;
}
.formula-strip-bot span:hover { color:#38bdf8; cursor:default; transition:color .2s; }

/* ======= GLASS CARD ======= */
.gc {
    background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.08);
    border-radius:20px; padding:1.75rem; backdrop-filter:blur(20px);
    box-shadow:0 8px 32px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.05);
    position:relative; overflow:hidden;
    transition:border-color .3s, box-shadow .3s;
}
.gc:hover { border-color:rgba(56,189,248,.1); }
.gc::after {
    content:''; position:absolute; top:0; left:-100%; width:100%; height:1px;
    background:linear-gradient(90deg,transparent,rgba(56,189,248,.2),transparent);
    animation:shimLine 6s ease infinite;
}
@keyframes shimLine { 0%{left:-100%} 100%{left:100%} }

.ct {
    font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.12em;
    color:#475569; margin-bottom:1.25rem;
    display:flex; align-items:center; gap:8px;
}
.ct::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(255,255,255,.07),transparent); }

/* ======= FORMULA CARDS ======= */
.formula-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.fcard {
    background:rgba(255,255,255,.02); border:1px solid rgba(255,255,255,.07);
    border-radius:14px; padding:14px 16px; position:relative; overflow:hidden;
    transition:all .3s; cursor:default;
}
.fcard:hover { transform:translateY(-4px); }
.fcard::before {
    content:''; position:absolute; top:0; left:0; width:3px; height:100%; border-radius:2px 0 0 2px;
}
.fc1::before{background:#38bdf8;} .fc1:hover{border-color:rgba(56,189,248,.25);background:rgba(56,189,248,.04);}
.fc2::before{background:#a855f7;} .fc2:hover{border-color:rgba(168,85,247,.25);background:rgba(168,85,247,.04);}
.fc3::before{background:#22c55e;} .fc3:hover{border-color:rgba(34,197,94,.25);background:rgba(34,197,94,.04);}
.fc4::before{background:#f59e0b;} .fc4:hover{border-color:rgba(245,158,11,.25);background:rgba(245,158,11,.04);}
.fc5{grid-column:1/-1;}
.fc5::before{background:#f43f5e;} .fc5:hover{border-color:rgba(244,63,94,.25);background:rgba(244,63,94,.04);}

.fcard-num  { font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:#334155; margin-bottom:4px; }
.fcard-eq   { font-family:'JetBrains Mono',monospace; font-size:1.05rem; font-weight:700; margin-bottom:4px; line-height:1.3; }
.fcard-desc { font-size:11px; color:#64748b; line-height:1.5; }
.fcard-icon { font-size:1.3rem; float:right; margin-top:-2px; }
.fc1 .fcard-eq{color:#7dd3fc;} .fc2 .fcard-eq{color:#c4b5fd;}
.fc3 .fcard-eq{color:#86efac;} .fc4 .fcard-eq{color:#fde68a;} .fc5 .fcard-eq{color:#fda4af;}

/* ======= LEVEL BOX ======= */
.lvl {
    border-radius:20px; padding:1.75rem 1.5rem; text-align:center;
    margin-bottom:1.25rem; border:1px solid; position:relative; overflow:hidden;
    animation:lvlIn .7s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes lvlIn { from{opacity:0;transform:scale(.88)} to{opacity:1;transform:scale(1)} }
.lvl-icon { font-size:2.8rem; display:block; margin-bottom:8px; animation:iconBounce 2s ease infinite; }
@keyframes iconBounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
.lvl-lbl  {
    font-family:'Orbitron',sans-serif;
    font-size:2rem; font-weight:800; letter-spacing:3px; text-transform:uppercase;
}
.lvl-sub  { font-size:12px; opacity:.8; margin-top:7px; font-family:'JetBrains Mono',monospace; color:#94a3b8; }

/* ======= STAT CARDS ======= */
.sc {
    border-radius:16px; padding:1.1rem 1.25rem;
    border:1px solid; background:rgba(255,255,255,.02);
    transition:all .3s ease;
}
.sc:hover { transform:translateY(-5px); box-shadow:0 12px 28px rgba(0,0,0,.4); }
.sc-lbl { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:#334155; margin-bottom:5px; }
.sc-val { font-family:'Orbitron',sans-serif; font-size:1.3rem; font-weight:700; line-height:1.2; }
.sc-sub { font-size:10px; color:#334155; margin-top:4px; font-family:'JetBrains Mono',monospace; }

/* ======= PERHITUNGAN TABLE ======= */
.calc-section-head {
    background:rgba(56,189,248,.07); border:1px solid rgba(56,189,248,.12);
    border-radius:10px; padding:8px 14px;
    font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700;
    color:#38bdf8; letter-spacing:.08em; text-transform:uppercase;
    margin-bottom:6px; margin-top:10px;
    display:flex; align-items:center; gap:8px;
}
.calc-row {
    display:flex; align-items:center;
    background:rgba(255,255,255,.015); border:1px solid rgba(255,255,255,.05);
    border-radius:10px; padding:10px 16px; margin-bottom:5px; gap:12px;
    transition:all .2s;
}
.calc-row:hover { background:rgba(56,189,248,.05); border-color:rgba(56,189,248,.15); }
.calc-label { font-family:'JetBrains Mono',monospace; font-size:12px; color:#475569; min-width:140px; }
.calc-op    { font-family:'JetBrains Mono',monospace; font-size:13px; color:#a855f7; font-weight:700; min-width:24px; text-align:center; }
.calc-expr  { font-family:'JetBrains Mono',monospace; font-size:12px; color:#94a3b8; flex:1; }
.calc-result{ font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:700; min-width:130px; text-align:right; }
.calc-note  { font-size:11px; color:#475569; font-style:italic; min-width:190px; text-align:right; }

/* ======= CHAR PILLS ======= */
.cpill {
    display:inline-flex; align-items:center; gap:6px;
    padding:6px 12px; border-radius:20px; margin:3px;
    font-size:12px; font-weight:600; border:1px solid; cursor:default; transition:all .3s;
}
.cpill:hover{transform:scale(1.05);}
.cpill.on  {background:rgba(56,189,248,.1);border-color:rgba(56,189,248,.3);color:#7dd3fc;}
.cpill.off {background:rgba(255,255,255,.02);border-color:rgba(255,255,255,.06);color:#2d3748;}
.pdot{width:6px;height:6px;border-radius:50%;}
.on .pdot {background:#7dd3fc;box-shadow:0 0 8px #38bdf8;}
.off .pdot{background:#1e293b;}

/* ======= REKOMENDASI BOX ======= */
.rk {
    border-radius:16px; padding:1.25rem 1.5rem;
    font-size:13.5px; line-height:1.8; border:1px solid;
}
.rk.great  {background:rgba(34,197,94,.08);border-color:rgba(34,197,94,.3);color:#86efac;}
.rk.good   {background:rgba(56,189,248,.08);border-color:rgba(56,189,248,.3);color:#7dd3fc;}
.rk.medium {background:rgba(245,158,11,.08);border-color:rgba(245,158,11,.3);color:#fde68a;}
.rk.bad    {background:rgba(249,115,22,.08);border-color:rgba(249,115,22,.3);color:#fdba74;}
.rk.danger {background:rgba(239,68,68,.08);border-color:rgba(239,68,68,.3);color:#fca5a5;}
.rk strong {font-weight:800;}

/* ======= SARAN PASSWORD ======= */
.pwd-item {
    display:flex; align-items:center; justify-content:space-between;
    background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.08);
    border-radius:12px; padding:12px 16px; margin-bottom:7px;
    transition:all .3s; cursor:default; gap:12px;
}
.pwd-item:hover{background:rgba(56,189,248,.07);border-color:rgba(56,189,248,.25);transform:translateX(4px);}
.pwd-left{flex:1;}
.pwd-text{font-family:'JetBrains Mono',monospace;font-size:13.5px;color:#e2e8f0;letter-spacing:.03em;margin-bottom:4px;}
.pwd-meta{font-size:11px;color:#475569;}
.pwd-badge{font-size:10px;font-weight:700;padding:4px 10px;border-radius:10px;background:rgba(34,197,94,.15);color:#86efac;white-space:nowrap;}
.pwd-change-note{font-size:11px;color:#38bdf8;margin-top:2px;font-style:italic;}

/* ======= FOOTER ======= */
.footer-wrap {
    position:relative; z-index:1; margin-top:3rem;
    border-top:1px solid rgba(56,189,248,.1);
    padding:2.5rem 2rem 2rem;
    text-align:center;
    background:linear-gradient(180deg, transparent 0%, rgba(4,14,32,.6) 100%);
}
.footer-title {
    font-family:'Orbitron',sans-serif;
    font-size:1rem; font-weight:700; letter-spacing:2px; text-transform:uppercase;
    background:linear-gradient(135deg,#7dd3fc,#c4b5fd);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    margin-bottom:1rem;
}
.footer-team {
    display:flex; justify-content:center; align-items:center;
    flex-wrap:wrap; gap:6px 0; margin-bottom:0.75rem;
}
.ft-name {
    font-family:'Space Grotesk',sans-serif; font-size:13px; font-weight:600;
    color:#7dd3fc;
    text-shadow:0 0 12px rgba(56,189,248,.6), 0 0 24px rgba(56,189,248,.3);
    padding:0 12px; position:relative;
    transition:text-shadow .3s, color .2s;
}
.ft-name:hover {
    color:#bae6fd;
    text-shadow:0 0 18px rgba(56,189,248,.9), 0 0 36px rgba(56,189,248,.5);
}
.ft-sep { color:#1e3a5f; font-size:10px; }
.footer-univ {
    font-size:13px; color:#64748b; margin-bottom:4px;
}
.footer-univ strong { color:#7dd3fc; }
.footer-dosen {
    font-size:12px; color:#475569; margin-top:6px;
}
.footer-dosen .dname {
    color:#93c5fd;
    text-shadow:0 0 10px rgba(147,197,253,.5);
    font-weight:600;
}
.footer-formula {
    display:flex; justify-content:center; gap:14px; flex-wrap:wrap;
    margin-top:1.25rem; padding-top:1.25rem;
    border-top:1px solid rgba(255,255,255,.04);
}
.footer-formula span {
    font-family:'JetBrains Mono',monospace; font-size:11px; color:#1e3a5f;
    padding:4px 10px; border-radius:6px; border:1px solid rgba(56,189,248,.08);
    transition:color .2s, border-color .2s; cursor:default;
}
.footer-formula span:hover { color:#38bdf8; border-color:rgba(56,189,248,.25); }

/* ======= STREAMLIT OVERRIDES ======= */
div[data-testid="stTextInput"] input {
    background:rgba(255,255,255,.03) !important; border:1px solid rgba(255,255,255,.1) !important;
    border-radius:14px !important; color:#e2e8f0 !important;
    font-family:'JetBrains Mono',monospace !important; font-size:16px !important;
    padding:14px 16px !important; transition:all .3s !important; letter-spacing:.02em !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color:rgba(56,189,248,.5) !important;
    box-shadow:0 0 0 3px rgba(56,189,248,.12) !important;
    background:rgba(56,189,248,.04) !important;
}
div[data-testid="stTextInput"] label {
    color:#64748b !important; font-size:11px !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:.1em !important;
}
.stTabs [data-baseweb="tab-list"] {
    background:rgba(255,255,255,.02) !important; border-radius:12px !important;
    gap:3px !important; padding:4px !important; border:1px solid rgba(255,255,255,.06) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius:8px !important; color:#475569 !important;
    font-weight:600 !important; font-size:13px !important;
    font-family:'Space Grotesk',sans-serif !important;
}
.stTabs [aria-selected="true"] { background:rgba(56,189,248,.15) !important; color:#7dd3fc !important; }
div[data-testid="stSelectSlider"] > label {
    color:#64748b !important; font-size:11px !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:.1em !important;
}
div[data-testid="stMarkdownContainer"] p { color:#94a3b8 !important; }
.stCaption { color:#64748b !important; }
hr { border-color:rgba(255,255,255,.06) !important; }
</style>

<div class="bg-mesh"></div>
<div class="bg-grid"></div>
<div class="particles" id="pts"></div>
<script>
(function(){
    var c=['#38bdf8','#a855f7','#22c55e','#f59e0b','#f43f5e','#06b6d4'];
    var el=document.getElementById('pts');
    if(!el)return;
    for(var i=0;i<28;i++){
        var p=document.createElement('div'); p.className='p';
        var s=Math.random()*2.5+1;
        p.style.cssText='width:'+s+'px;height:'+s+'px;background:'+c[~~(Math.random()*c.length)]+';left:'+Math.random()*100+'%;animation-duration:'+(Math.random()*20+14)+'s;animation-delay:'+(Math.random()*14)+'s;';
        el.appendChild(p);
    }
})();
</script>
""", unsafe_allow_html=True)

# ============================================================
# HERO SECTION — NEW CYBER DASHBOARD
# ============================================================

st.markdown("""
<div style="
position:relative;
overflow:hidden;
border-radius:30px;
padding:0;
margin-bottom:2rem;
background:
linear-gradient(135deg,
rgba(2,6,23,0.98) 0%,
rgba(8,15,35,0.98) 40%,
rgba(3,7,18,0.98) 100%);
border:1px solid rgba(56,189,248,.15);
box-shadow:
0 0 0 1px rgba(56,189,248,.04),
0 25px 60px rgba(0,0,0,.65),
0 0 80px rgba(56,189,248,.05);
">

<!-- TOP GLOW -->
<div style="
height:3px;
background:linear-gradient(90deg,
transparent,
#38bdf8,
#a855f7,
#22c55e,
transparent);
"></div>

<div style="
display:flex;
flex-wrap:wrap;
align-items:center;
justify-content:space-between;
gap:3rem;
padding:3rem;
">

<!-- LEFT -->
<div style="flex:1;min-width:320px;">

<div style="
display:inline-flex;
align-items:center;
gap:10px;
padding:7px 16px;
border-radius:999px;
background:rgba(56,189,248,.08);
border:1px solid rgba(56,189,248,.2);
margin-bottom:1.5rem;
font-size:12px;
font-weight:700;
letter-spacing:.12em;
text-transform:uppercase;
color:#7dd3fc;
font-family:'JetBrains Mono',monospace;
">
<div style="
width:7px;
height:7px;
border-radius:50%;
background:#38bdf8;
box-shadow:0 0 12px #38bdf8;
animation:blink 2s infinite;
"></div>
WEB SECURITY ANALYZER
</div>

<div style="
font-family:'Orbitron',sans-serif;
font-size:3.4rem;
font-weight:900;
line-height:1.1;
letter-spacing:2px;
margin-bottom:1rem;
background:linear-gradient(
135deg,
#e0f2fe 0%,
#7dd3fc 25%,
#c4b5fd 60%,
#86efac 100%);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
">
ANALISIS<br>
KEAMANAN<br>
PASSWORD
</div>

<div style="
font-size:15px;
line-height:1.9;
color:#94a3b8;
max-width:700px;
margin-bottom:1.8rem;
">
Web ini dibuat untuk menganalisis tingkat keamanan password secara real-time
menggunakan teori <strong style="color:#38bdf8;">Matematika Terapan</strong>
seperti
<strong style="color:#7dd3fc;">Kombinatorika</strong>,
<strong style="color:#c4b5fd;">Entropi Shannon</strong>,
<strong style="color:#86efac;">Teori Peluang</strong>,
dan
<strong style="color:#fde68a;">Estimasi Brute Force</strong>.
            

<strong style="color:#38bdf8;">Disclaimer password anda tidak akan di simpan </strong>.
</div>

<!-- FEATURES -->
<div style="
display:flex;
flex-wrap:wrap;
gap:10px;
margin-bottom:1.8rem;
">

<div style="
padding:10px 14px;
border-radius:14px;
background:rgba(56,189,248,.08);
border:1px solid rgba(56,189,248,.18);
font-size:12px;
font-weight:700;
color:#7dd3fc;
">
📐 Kombinatorika
</div>

<div style="
padding:10px 14px;
border-radius:14px;
background:rgba(168,85,247,.08);
border:1px solid rgba(168,85,247,.18);
font-size:12px;
font-weight:700;
color:#c4b5fd;
">
📊 Entropi Shannon
</div>

<div style="
padding:10px 14px;
border-radius:14px;
background:rgba(34,197,94,.08);
border:1px solid rgba(34,197,94,.18);
font-size:12px;
font-weight:700;
color:#86efac;
">
🎲 Teori Peluang
</div>

<div style="
padding:10px 14px;
border-radius:14px;
background:rgba(245,158,11,.08);
border:1px solid rgba(245,158,11,.18);
font-size:12px;
font-weight:700;
color:#fde68a;
">
⏱ Brute Force
</div>

</div>

<!-- FORMULA -->
<div style="
display:flex;
flex-wrap:wrap;
gap:10px;
">

<div style="
padding:9px 14px;
border-radius:12px;
background:rgba(255,255,255,.03);
border:1px solid rgba(255,255,255,.07);
font-family:'JetBrains Mono',monospace;
font-size:13px;
color:#7dd3fc;
">
C = kⁿ
</div>

<div style="
padding:9px 14px;
border-radius:12px;
background:rgba(255,255,255,.03);
border:1px solid rgba(255,255,255,.07);
font-family:'JetBrains Mono',monospace;
font-size:13px;
color:#c4b5fd;
">
P = M / C
</div>

<div style="
padding:9px 14px;
border-radius:12px;
background:rgba(255,255,255,.03);
border:1px solid rgba(255,255,255,.07);
font-family:'JetBrains Mono',monospace;
font-size:13px;
color:#86efac;
">
H = n·log₂(k)
</div>

<div style="
padding:9px 14px;
border-radius:12px;
background:rgba(255,255,255,.03);
border:1px solid rgba(255,255,255,.07);
font-family:'JetBrains Mono',monospace;
font-size:13px;
color:#fde68a;
">
T = C / R
</div>

</div>

</div>

<!-- RIGHT -->
<div style="
width:340px;
display:flex;
justify-content:center;
align-items:center;
position:relative;
">

<div style="
position:relative;
width:270px;
height:270px;
border-radius:50%;
background:
radial-gradient(circle,
rgba(56,189,248,.18) 0%,
rgba(56,189,248,.04) 40%,
transparent 70%);
display:flex;
justify-content:center;
align-items:center;
">

<div style="
position:absolute;
width:230px;
height:230px;
border-radius:50%;
border:1px solid rgba(56,189,248,.12);
animation:spin 18s linear infinite;
"></div>

<div style="
position:absolute;
width:180px;
height:180px;
border-radius:50%;
border:1px solid rgba(168,85,247,.15);
animation:spin 12s linear infinite reverse;
"></div>

<div style="
position:absolute;
width:130px;
height:130px;
border-radius:50%;
border:1px solid rgba(34,197,94,.15);
animation:spin 8s linear infinite;
"></div>

<div style="
font-size:5rem;
filter:drop-shadow(0 0 35px rgba(56,189,248,.45));
animation:float 4s ease-in-out infinite;
">
🔐
</div>

</div>

</div>

</div>

<!-- BOTTOM -->
<div style="
display:flex;
justify-content:space-between;
flex-wrap:wrap;
gap:1rem;
padding:1.2rem 3rem;
border-top:1px solid rgba(255,255,255,.05);
background:rgba(0,0,0,.18);
">

<div style="
font-size:12px;
color:#64748b;
">
Kelompok 2 Matematika Terapan• PTIK-D • Universitas Negeri Medan
</div>

<div style="
font-size:12px;
color:#475569;
font-family:'JetBrains Mono',monospace;
">
Password Security Analyzer v3.0
</div>

</div>

</div>

<style>

@keyframes spin{
from{transform:rotate(0deg);}
to{transform:rotate(360deg);}
}

@keyframes float{
0%,100%{transform:translateY(0px);}
50%{transform:translateY(-12px);}
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# INPUT + MODEL MATEMATIS
# ============================================================
col_kiri, col_kanan = st.columns([1.2, 1], gap="large")

with col_kiri:
    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="ct">🔑 Input Password</div>', unsafe_allow_html=True)
    password = st.text_input("Password", type="password",
                             placeholder="Ketik password di sini...",
                             label_visibility="collapsed")
    R_opt = st.select_slider(
        "⚡ Kecepatan serangan (tebakan/detik)",
        options=[100_000, 1_000_000, 10_000_000, 1_000_000_000],
        value=1_000_000,
        format_func=lambda x: f"{x:,}".replace(",",".")
    )
    st.markdown("""
    <div style="margin-top:.75rem;padding:12px 14px;
                background:rgba(56,189,248,.05);border:1px solid rgba(56,189,248,.1);border-radius:12px;
                font-size:12px;color:#64748b;line-height:1.8;">
      <span style="color:#7dd3fc;font-weight:700;">Cara kerja:</span>
      Ketik password di atas, sistem langsung menghitung
      <strong style="color:#94a3b8;">kombinasi total C = k<sup>n</sup></strong>,
      <strong style="color:#94a3b8;">entropi H = n&middot;log&#x2082;(k)</strong>,
      <strong style="color:#94a3b8;">peluang P = M/C</strong>, dan
      <strong style="color:#94a3b8;">waktu retas T = C/R</strong> secara real-time.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_kanan:
    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="ct">📐 Model Matematis</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="formula-grid">
      <div class="fcard fc1">
        <div class="fcard-icon">📐</div>
        <div class="fcard-num">Konsep 1 &middot; Kombinatorika</div>
        <div class="fcard-eq">C = k<sup>n</sup></div>
        <div class="fcard-desc">k = ragam karakter, n = panjang. Total ruang kunci yang harus ditebak.</div>
      </div>
      <div class="fcard fc2">
        <div class="fcard-icon">🎲</div>
        <div class="fcard-num">Konsep 2 &middot; Teori Peluang</div>
        <div class="fcard-eq">P = M / C</div>
        <div class="fcard-desc">M = jumlah percobaan. Makin kecil P, makin sulit password diretas.</div>
      </div>
      <div class="fcard fc3">
        <div class="fcard-icon">📊</div>
        <div class="fcard-num">Konsep 3 &middot; Entropi Shannon</div>
        <div class="fcard-eq">H = n &middot; log&#x2082;(k)</div>
        <div class="fcard-desc">Mengukur keacakan dalam satuan bit. Standar NIST: &ge;80 bit = Kuat.</div>
      </div>
      <div class="fcard fc4">
        <div class="fcard-icon">⏱</div>
        <div class="fcard-num">Konsep 4 &middot; Waktu Retas</div>
        <div class="fcard-eq">T = C / R</div>
        <div class="fcard-desc">R = kecepatan serangan brute force (tebakan per detik).</div>
      </div>
      <div class="fcard fc5">
        <div class="fcard-icon">📈</div>
        <div class="fcard-num">Konsep 5 &middot; Pertumbuhan Eksponensial</div>
        <div class="fcard-eq">C &rarr; k<sup>n</sup> saat n &uarr;</div>
        <div class="fcard-desc">Setiap +1 karakter melipatgandakan ruang kunci. Panjang password adalah kunci utama keamanan.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ANALISIS
# ============================================================
if password:
    n  = len(password)
    lo = any(c.islower()     for c in password)
    up = any(c.isupper()     for c in password)
    dg = any(c.isdigit()     for c in password)
    sy = any(not c.isalnum() for c in password)
    k  = hitung_k(lo, up, dg, sy)
    M  = 1_000_000

    C  = k ** n
    H  = n * math.log2(k)
    Hi = math.floor(H)
    P  = M / C if C > 0 else 0
    T  = C // R_opt

    label, ikon, color, bg_c, border_c, cls = get_tingkat(H)

    kP = []
    if lo: kP.append("26")
    if up: kP.append("26")
    if dg: kP.append("10")
    if sy: kP.append("32")
    kEq  = " + ".join(kP) + f" = {k}"
    CStr = fmt_n(C)
    TStr = fmt_n(T)
    RStr = fmt_n(R_opt)
    MStr = fmt_n(M)

    st.markdown("---")

    # ===== LEVEL BOX =====
    st.markdown(f"""
    <div class="lvl" style="background:{bg_c};border-color:{border_c};">
        <span class="lvl-icon">{ikon}</span>
        <div class="lvl-lbl" style="color:{color};text-shadow:0 0 20px {color}80;">{label}</div>
        <div class="lvl-sub">Entropi H = {H:.2f} bit &nbsp;&middot;&nbsp; Panjang {n} karakter &nbsp;&middot;&nbsp; Ruang karakter k = {k}</div>
    </div>""", unsafe_allow_html=True)

    # ===== CHAR PILLS =====
    pills = ""
    for active, txt, delay in [
        (lo, "Huruf kecil (a-z) +26", "0.1s"),
        (up, "Huruf besar (A-Z) +26", "0.2s"),
        (dg, "Angka (0-9) +10",       "0.3s"),
        (sy, "Simbol +32",            "0.4s"),
    ]:
        cp = "on" if active else "off"
        mark = "✓" if active else "✗"
        pills += f'<span class="cpill {cp}" style="animation-delay:{delay}"><span class="pdot"></span>{mark} {txt}</span>'
    st.markdown(pills + "<br><br>", unsafe_allow_html=True)

    # ===== STAT CARDS =====
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "Panjang (n)",          str(n),       "karakter",        "#7dd3fc", "rgba(56,189,248,.12)",  "rgba(56,189,248,.25)"),
        (c2, "Ruang karakter (k)",   str(k),       kEq,               "#c4b5fd", "rgba(168,85,247,.12)",  "rgba(168,85,247,.25)"),
        (c3, "Entropi (H)",          f"{Hi} bit",  "n × log₂(k)",     "#86efac", "rgba(34,197,94,.12)",   "rgba(34,197,94,.25)"),
        (c4, "Estimasi Waktu Retas", fmt_w(T),     "T = C / R",       "#fde68a", "rgba(245,158,11,.12)",  "rgba(245,158,11,.25)"),
    ]
    for col, lbl, val, sub, clr, bg2, bd2 in stats:
        with col:
            st.markdown(f"""
            <div class="sc" style="border-color:{bd2};background:{bg2};">
                <div class="sc-lbl">{lbl}</div>
                <div class="sc-val" style="color:{clr}">{val}</div>
                <div class="sc-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # ===== PERHITUNGAN RAPI =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="ct">🧮 Perhitungan Lengkap</div>', unsafe_allow_html=True)

    def calc_row(label, op, expr, result, result_color="#86efac", note=""):
        note_html = f'<span class="calc-note">{note}</span>' if note else ''
        return f"""
        <div class="calc-row">
            <span class="calc-label">{label}</span>
            <span class="calc-op">{op}</span>
            <span class="calc-expr">{expr}</span>
            <span class="calc-result" style="color:{result_color}">{result}</span>
            {note_html}
        </div>"""

    # Konsep 1
    st.markdown('<div class="calc-section-head">📐 Konsep 1 · Kombinatorika &nbsp;|&nbsp; C = kⁿ</div>', unsafe_allow_html=True)
    k_parts = []
    if lo: k_parts.append("<span style='color:#7dd3fc'>26</span><small style='color:#334155'>(kecil)</small>")
    if up: k_parts.append("<span style='color:#c4b5fd'>26</span><small style='color:#334155'>(besar)</small>")
    if dg: k_parts.append("<span style='color:#86efac'>10</span><small style='color:#334155'>(angka)</small>")
    if sy: k_parts.append("<span style='color:#fde68a'>32</span><small style='color:#334155'>(simbol)</small>")
    st.markdown(calc_row("k (ruang karakter)", "=", " + ".join(k_parts), f"<b>{k}</b>", "#7dd3fc", "total karakter tersedia"), unsafe_allow_html=True)
    st.markdown(calc_row("C (total kombinasi)", "=", f"k<sup>n</sup> = {k}<sup>{n}</sup>", CStr, "#7dd3fc", "total ruang kunci password"), unsafe_allow_html=True)

    # Konsep 2
    st.markdown('<div class="calc-section-head">🎲 Konsep 2 · Teori Peluang &nbsp;|&nbsp; P = M / C</div>', unsafe_allow_html=True)
    st.markdown(calc_row("M (percobaan)", "=", "1.000.000 tebakan", MStr, "#c4b5fd", "asumsi serangan standar"), unsafe_allow_html=True)
    st.markdown(calc_row("P (peluang retas)", "=", f"M / C = {MStr} / {CStr}", f"{P:.2e}", "#c4b5fd", "mendekati nol = sangat sulit"), unsafe_allow_html=True)

    # Konsep 3
    st.markdown('<div class="calc-section-head">📊 Konsep 3 · Entropi Shannon &nbsp;|&nbsp; H = n · log₂(k)</div>', unsafe_allow_html=True)
    st.markdown(calc_row("H (entropi)", "=", f"n × log₂(k) = {n} × log₂({k}) = {n} × {math.log2(k):.4f}", f"{H:.4f} bit", "#86efac", "≥80 bit = kuat, ≥100 bit = sangat kuat"), unsafe_allow_html=True)

    # Konsep 4
    st.markdown('<div class="calc-section-head">⏱ Konsep 4 · Estimasi Waktu Retas &nbsp;|&nbsp; T = C / R</div>', unsafe_allow_html=True)
    st.markdown(calc_row("R (kecepatan)", "=", f"{RStr} tebakan/detik", RStr, "#fde68a", "kecepatan serangan dipilih"), unsafe_allow_html=True)
    st.markdown(calc_row("T (waktu retas)", "=", f"C / R = {CStr} / {RStr}", f"{TStr} detik", "#fde68a", f"≈ {fmt_w(T)}"), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ===== GRAFIK =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="ct">📊 Visualisasi Interaktif</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📈 Pertumbuhan Kombinasi",
        "🔥 Perbandingan Entropi",
        "⏱ Estimasi Waktu Retas"
    ])

    BG = "#04080f"; GRID = "#0d1829"; FONT = "#475569"
    clr_map = {"Sangat Lemah":"#ef4444","Lemah":"#f97316","Sedang":"#eab308","Kuat":"#38bdf8","Sangat Kuat":"#22c55e"}

    def dark_fig(title):
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=title, font=dict(color="#94a3b8", size=13, family="Space Grotesk")),
            plot_bgcolor=BG, paper_bgcolor=BG,
            font=dict(color=FONT, family="Space Grotesk"),
            legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e293b", font=dict(color="#64748b")),
            xaxis=dict(gridcolor=GRID, color=FONT, zerolinecolor=GRID),
            yaxis=dict(gridcolor=GRID, color=FONT, zerolinecolor=GRID),
            height=390, margin=dict(t=50, b=40, l=55, r=20),
        )
        return fig

    with tab1:
        st.caption("**Konsep 5:** Pertumbuhan eksponensial C = kⁿ — semakin panjang password, kombinasi meledak secara eksponensial")
        lengths = list(range(4, 26))
        fig1 = dark_fig("Pertumbuhan Kombinasi C = kⁿ (skala log₁₀) vs Panjang Password")
        scenarios = [
            ("Huruf kecil (k=26)",  26, "#7dd3fc"),
            ("Huruf+Angka (k=62)",  62, "#c4b5fd"),
            ("Semua+Simbol (k=94)", 94, "#86efac"),
            (f"Password kamu (k={k})", k, "#fde68a"),
        ]
        for name, kv, clr in scenarios:
            y_vals = [math.log10(kv**l) for l in lengths]
            fig1.add_trace(go.Scatter(
                x=lengths, y=y_vals, name=name,
                line=dict(color=clr, width=2.5), mode='lines+markers',
                marker=dict(size=6, color=clr, line=dict(color=BG, width=2)),
            ))
        fig1.add_vline(x=n, line_dash="dash", line_color="#fde68a", line_width=1.5,
                       annotation_text=f"  n={n} (passwordmu)",
                       annotation_font_color="#fde68a", annotation_font_size=11)
        fig1.update_xaxes(title_text="Panjang Password (n)")
        fig1.update_yaxes(title_text="log₁₀(C)")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.caption("**Konsep 3:** Perbandingan Entropi Shannon H = n·log₂(k) — semakin tinggi H, semakin aman password")
        types_lbl = ["Huruf kecil<br>k=26","Huruf+Angka<br>k=36",
                     "Besar+Kecil<br>k=52","Huruf+Angka<br>k=62",
                     "Semua+Simbol<br>k=94",f"Password kamu<br>k={k}"]
        ks2 = [26, 36, 52, 62, 94, k]
        hs2 = [n * math.log2(kv) for kv in ks2]
        clrs2 = [clr_map[get_tingkat(hv)[0]] for hv in hs2]
        fig2 = dark_fig(f"Perbandingan Entropi Shannon H (n = {n} karakter)")
        fig2.add_trace(go.Bar(
            x=types_lbl, y=hs2,
            marker=dict(color=clrs2, line=dict(color=BG, width=1)),
            text=[f"{h:.1f} bit" for h in hs2],
            textposition='outside', textfont=dict(color="#94a3b8", size=11),
        ))
        for val, clr2, lbl2 in [(40,"#ef4444","40 bit — Minimum"),(80,"#38bdf8","80 bit — Kuat"),(100,"#22c55e","100 bit — Sangat Kuat")]:
            fig2.add_hline(y=val, line_dash="dot", line_color=clr2, line_width=1.5,
                           annotation_text=f"  {lbl2}",
                           annotation_font_color=clr2, annotation_font_size=11)
        fig2.update_xaxes(title_text="Jenis Karakter")
        fig2.update_yaxes(title_text="Entropi H (bit)")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.caption("**Konsep 4:** Estimasi Waktu Retas T = C/R — semakin panjang password, semakin lama waktu yang dibutuhkan")
        lens3 = list(range(4, 22))
        wlog3 = []
        for l in lens3:
            c_val = k ** l
            t_val = c_val // R_opt
            wlog3.append(math.log10(max(1, t_val)))
        clrs3 = [clr_map[get_tingkat(l * math.log2(k))[0]] for l in lens3]
        fig3 = dark_fig(f"Estimasi Waktu Retas T = C/R (k={k}, R={RStr} tebakan/dtk)")
        fig3.add_trace(go.Bar(
            x=lens3, y=wlog3,
            marker=dict(color=clrs3, line=dict(color=BG, width=1)),
            text=[f"n={l}" for l in lens3],
            textposition='inside', textfont=dict(color="white", size=10),
        ))
        fig3.add_vline(x=n, line_dash="dash", line_color="#fde68a", line_width=1.5,
                       annotation_text=f"  n={n}",
                       annotation_font_color="#fde68a", annotation_font_size=11)
        fig3.update_xaxes(title_text="Panjang Password (n)")
        fig3.update_yaxes(title_text="log₁₀(T detik)")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ===== REKOMENDASI =====
    st.markdown("<br>", unsafe_allow_html=True)
    rk_map = {
        "great":  f"🏆 <strong>Luar biasa!</strong> Entropi {H:.2f} bit jauh melampaui standar NIST 100 bit. Dengan T = {CStr} / {RStr} = {TStr} detik &asymp; {fmt_w(T)}, password ini hampir mustahil diretas dengan teknologi komputasi saat ini!",
        "good":   f"✅ <strong>Password kuat dan aman!</strong> Entropi {H:.2f} bit melampaui standar NIST 80 bit. Estimasi waktu retas mencapai {fmt_w(T)}. Aman untuk penggunaan sehari-hari.",
        "medium": f"⚡ <strong>Cukup aman, namun perlu ditingkatkan.</strong> Entropi {H:.2f} bit masih di bawah standar 80 bit. Estimasi waktu retas hanya {fmt_w(T)}. Tambahkan 2&ndash;3 karakter dan sisipkan simbol.",
        "bad":    f"⚠️ <strong>Password berisiko tinggi!</strong> Entropi hanya {H:.2f} bit. Estimasi waktu retas {fmt_w(T)}. Segera ganti dengan minimal 12 karakter kombinasi huruf besar, kecil, angka, dan simbol.",
        "danger": f"💀 <strong>Sangat berbahaya!</strong> Entropi hanya {H:.2f} bit, jauh di bawah standar minimum 40 bit NIST. Password ini bisa diretas hanya dalam {fmt_w(T)}! Ganti segera!",
    }
    st.markdown(f'<div class="rk {cls}">{rk_map[cls]}</div>', unsafe_allow_html=True)

    # ===== SARAN PASSWORD =====
    if cls != "great":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="gc">', unsafe_allow_html=True)
        st.markdown('<div class="ct">💡 Saran Perkuat Password Kamu</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:12.5px;color:#64748b;margin-bottom:14px;line-height:1.8;">
          Berikut versi password kamu yang sudah <strong style="color:#94a3b8;">diperkuat</strong>
          menggunakan teknik leet substitution, penambahan simbol, dan pemanjangan.
          <span style="color:#fde68a;font-weight:600;">Karakter kuning</span> = bagian yang ditambahkan atau diubah.
        </div>""", unsafe_allow_html=True)
        sarans = suggest_password_improvements(password, n_suggestions=3)
        for pwd_s, H_s, len_s in sarans:
            T_s = (94 ** len_s) // R_opt
            strength, _, s_color, _, _, _ = get_tingkat(H_s)
            highlighted = highlight_additions(password, pwd_s)
            st.markdown(f"""
            <div class="pwd-item">
                <div class="pwd-left">
                    <div class="pwd-text">{highlighted}</div>
                    <div class="pwd-change-note">Dimodifikasi dari password aslimu</div>
                    <div class="pwd-meta">
                        Panjang {len_s} karakter &nbsp;&middot;&nbsp; k = 94 &nbsp;&middot;&nbsp;
                        H = {H_s:.1f} bit &nbsp;&middot;&nbsp; Waktu retas &asymp; {fmt_w(T_s)}
                    </div>
                </div>
                <span class="pwd-badge">{strength}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:11px;color:#64748b;margin-top:10px;padding:10px 14px;
                    background:rgba(251,113,133,0.05);border:1px solid rgba(251,113,133,0.12);border-radius:10px;">
          ⚠️ <strong style="color:#94a3b8;">Catatan:</strong>
          Jangan gunakan saran di atas secara persis karena sudah tampil di layar.
          Gunakan sebagai inspirasi pola dan kembangkan versimu sendiri.
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:4.5rem 2rem;position:relative;z-index:1;">
      <div style="font-size:3.5rem;margin-bottom:1.25rem;filter:drop-shadow(0 0 24px rgba(56,189,248,.4));">🔐</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;font-weight:700;color:#94a3b8;margin-bottom:10px;letter-spacing:2px;">
        MASUKKAN PASSWORD UNTUK ANALISIS
      </div>
      <div style="font-size:13px;color:#475569;max-width:420px;margin:0 auto;line-height:1.8;">
        Sistem akan langsung menghitung kekuatan password menggunakan
        Kombinatorika, Teori Peluang, Entropi Shannon, dan Estimasi Waktu Retas.
      </div>
      <div style="display:flex;justify-content:center;gap:14px;margin-top:2rem;flex-wrap:wrap;">
        <div style="background:rgba(56,189,248,.06);border:1px solid rgba(56,189,248,.15);border-radius:12px;padding:12px 18px;font-size:12px;color:#7dd3fc;font-family:'JetBrains Mono',monospace;">C = k<sup>n</sup></div>
        <div style="background:rgba(168,85,247,.06);border:1px solid rgba(168,85,247,.15);border-radius:12px;padding:12px 18px;font-size:12px;color:#c4b5fd;font-family:'JetBrains Mono',monospace;">P = M / C</div>
        <div style="background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.15);border-radius:12px;padding:12px 18px;font-size:12px;color:#86efac;font-family:'JetBrains Mono',monospace;">H = n&middot;log&#x2082;(k)</div>
        <div style="background:rgba(245,158,11,.06);border:1px solid rgba(245,158,11,.15);border-radius:12px;padding:12px 18px;font-size:12px;color:#fde68a;font-family:'JetBrains Mono',monospace;">T = C / R</div>
      </div>
    </div>""", unsafe_allow_html=True)

# ============================================================
# FOOTER — BERCAHAYA BIRU
# ============================================================
st.markdown("""
<div class="footer-wrap">

  <div class="footer-title">Kelompok 2 &nbsp;&middot;&nbsp; Matematika Terapan</div>

  <div class="footer-team">
    <span class="ft-name">Marwasas Pardede</span>
    <span class="ft-sep">◆</span>
    <span class="ft-name">Muhammad Fazry Chandra</span>
    <span class="ft-sep">◆</span>
    <span class="ft-name">Ester Oktaviani Sinaga</span>
    <span class="ft-sep">◆</span>
    <span class="ft-name">Yola Claudia Sinaga</span>
    <span class="ft-sep">◆</span>
    <span class="ft-name">MHD. Ghifari</span>
  </div>

  <div class="footer-univ">
    <strong>Prodi PTIK</strong> &nbsp;&middot;&nbsp; <strong>Universitas Negeri Medan</strong> &nbsp;&middot;&nbsp; <strong>2026</strong>
  </div>

  <div class="footer-dosen">
    Dosen Pengampu:&nbsp;
    <span class="dname">Dr. Amirhud Dalimunthe, S.T., M.Kom</span>
    &nbsp;&middot;&nbsp;
    <span class="dname">Novialdi Ashari, S.Stat., M.T.I</span>
  </div>

  <div class="footer-formula">
    <span>C = k<sup>n</sup> &nbsp;(Kombinatorika)</span>
    <span>P = M / C &nbsp;(Teori Peluang)</span>
    <span>H = n &middot; log&#x2082;(k) &nbsp;(Entropi Shannon)</span>
    <span>T = C / R &nbsp;(Estimasi Waktu Retas)</span>
  </div>

</div>
""", unsafe_allow_html=True)
