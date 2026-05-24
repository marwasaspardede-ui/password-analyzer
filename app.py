import streamlit as st
import math
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Analisis Keamanan Password | Kel. 2 PTIK-D UNIMED",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS CUSTOM
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Header utama */
.main-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #4c1d95 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
    text-align: center;
}
.main-header h1 { font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
.main-header p  { font-size: 0.9rem; opacity: 0.8; margin: 6px 0 0; }

/* Badge */
.badge-row { display: flex; gap: 8px; justify-content: center; margin-top: 12px; flex-wrap: wrap; }
.badge {
    font-size: 11px; font-weight: 700; padding: 4px 12px;
    border-radius: 20px; border: 1px solid rgba(255,255,255,0.3);
    background: rgba(255,255,255,0.15); color: white;
}

/* Card rumus */
.rumus-card {
    background: #f8faff;
    border: 1.5px solid #dbeafe;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.rumus-card h4 { color: #1e40af; font-size: 13px; font-weight: 700; margin: 0 0 4px; text-transform: uppercase; letter-spacing: 0.06em; }
.rumus-card p  { color: #1e3a8a; font-size: 18px; font-weight: 700; margin: 0; font-family: monospace; }
.rumus-card small { color: #475569; font-size: 11px; }

/* Metric card */
.metric-card {
    border-radius: 12px;
    padding: 1rem 1.25rem;
    border: 1.5px solid;
    margin-bottom: 0.5rem;
}
.metric-card.blue   { background: #eff6ff; border-color: #bfdbfe; }
.metric-card.purple { background: #f5f3ff; border-color: #ddd6fe; }
.metric-card.green  { background: #f0fdf4; border-color: #bbf7d0; }
.metric-card.orange { background: #fff7ed; border-color: #fed7aa; }
.metric-card label  { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; }
.metric-card .val   { font-size: 22px; font-weight: 800; color: #0f172a; line-height: 1.1; margin: 2px 0; }
.metric-card small  { font-size: 11px; color: #64748b; }

/* Tingkat keamanan */
.level-box {
    border-radius: 12px; padding: 1rem 1.25rem;
    border: 2px solid; text-align: center; margin-bottom: 1rem;
}
.level-box h2 { font-size: 1.5rem; font-weight: 800; margin: 0; }
.level-box p  { font-size: 13px; margin: 4px 0 0; opacity: 0.85; }

/* Hasil perhitungan */
.calc-box {
    background: #0f172a; border-radius: 12px;
    padding: 1.25rem 1.5rem; color: #e2e8f0;
    font-family: monospace; font-size: 13px;
    line-height: 1.8;
}
.calc-key   { color: #60a5fa; font-weight: 700; }
.calc-op    { color: #a78bfa; }
.calc-val   { color: #34d399; }
.calc-note  { color: #94a3b8; }

/* Char pills */
.char-pill {
    display: inline-block; padding: 4px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 600;
    margin: 3px; border: 1.5px solid;
}
.char-pill.on  { background: #eff6ff; border-color: #93c5fd; color: #1e40af; }
.char-pill.off { background: #f8fafc; border-color: #e2e8f0; color: #94a3b8; }

/* Rekomendasi */
.rekom {
    border-radius: 12px; padding: 1rem 1.25rem;
    font-size: 13px; line-height: 1.7; border: 1.5px solid;
}
.rekom.great  { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.rekom.good   { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
.rekom.medium { background: #fffbeb; border-color: #fde68a; color: #92400e; }
.rekom.bad    { background: #fff7ed; border-color: #fed7aa; color: #9a3412; }
.rekom.danger { background: #fef2f2; border-color: #fecaca; color: #991b1b; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# FUNGSI MATEMATIKA
# ============================================================

def hitung_kombinasi(k: int, n: int) -> int:
    """
    Konsep 1: Kombinatorika
    C = k^n
    k = jumlah ragam karakter, n = panjang password
    """
    return k ** n


def hitung_peluang(M: int, C: int) -> float:
    """
    Konsep 2: Teori Peluang
    P = M / C
    M = jumlah percobaan, C = total kombinasi
    """
    if C == 0:
        return 0
    return M / C


def hitung_entropi(n: int, k: int) -> float:
    """
    Konsep 3: Entropi Shannon
    H = n * log2(k)
    H dalam satuan bit
    """
    if k <= 1:
        return 0
    return n * math.log2(k)


def hitung_waktu(C: int, R: int) -> int:
    """
    Konsep 4: Estimasi Waktu (Time-to-Crack)
    T = C / R
    R = kecepatan tebakan per detik
    """
    if R == 0:
        return 0
    return C // R


def hitung_k(ada_lower, ada_upper, ada_digit, ada_simbol) -> int:
    """Menghitung total ruang karakter k"""
    k = 0
    if ada_lower:  k += 26
    if ada_upper:  k += 26
    if ada_digit:  k += 10
    if ada_simbol: k += 32
    return k if k > 0 else 26


def format_angka_besar(n: int) -> str:
    """Format angka besar dengan titik sebagai pemisah ribuan"""
    return f"{n:,}".replace(",", ".")


def format_waktu(detik: int) -> str:
    """Konsep 5: Konversi satuan waktu"""
    if detik < 60:
        return f"{detik:,} detik"
    elif detik < 3600:
        return f"{detik // 60:,} menit"
    elif detik < 86400:
        return f"{detik // 3600:,} jam"
    elif detik < 86400 * 365:
        return f"{detik // 86400:,} hari"
    elif detik < 86400 * 365 * 1_000:
        return f"{detik // (86400 * 365):,} tahun"
    elif detik < 86400 * 365 * 1_000_000:
        return f"{detik // (86400 * 365 * 1_000):,} ribu tahun"
    elif detik < 86400 * 365 * 1_000_000_000:
        return f"{detik // (86400 * 365 * 1_000_000):,} juta tahun"
    else:
        return f"{detik // (86400 * 365 * 1_000_000_000):,} miliar tahun"


def get_tingkat(H: float):
    if H >= 100:
        return ("Sangat Kuat",  "#166534", "#f0fdf4", "#bbf7d0", "great",  "🏆")
    elif H >= 80:
        return ("Kuat",         "#1e40af", "#eff6ff", "#bfdbfe", "good",   "✅")
    elif H >= 56:
        return ("Sedang",       "#92400e", "#fffbeb", "#fde68a", "medium", "⚠️")
    elif H >= 40:
        return ("Lemah",        "#9a3412", "#fff7ed", "#fed7aa", "bad",    "🚨")
    else:
        return ("Sangat Lemah", "#991b1b", "#fef2f2", "#fecaca", "danger", "💀")


# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🔐 Password Security Analyzer</h1>
    <p>Analisis Keamanan Password Berbasis Matematika Terapan · Universitas Negeri Medan 2026</p>
    <div class="badge-row">
        <span class="badge">📐 Kombinatorika</span>
        <span class="badge">🎲 Teori Peluang</span>
        <span class="badge">📊 Entropi Shannon</span>
        <span class="badge">⏱ Estimasi Waktu</span>
        <span class="badge">📈 Pertumbuhan Eksponensial</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# INPUT
# ============================================================
col_input, col_info = st.columns([1.2, 1])

with col_input:
    st.markdown("### 🔑 Masukkan Password")
    password = st.text_input(
        label="Password",
        type="password",
        placeholder="Ketik password di sini...",
        label_visibility="collapsed"
    )
    R = st.select_slider(
        "⚡ Kecepatan serangan (tebakan/detik)",
        options=[100_000, 1_000_000, 10_000_000, 1_000_000_000],
        value=1_000_000,
        format_func=lambda x: f"{x:,}".replace(",", ".")
    )
    M = 1_000_000  # jumlah percobaan

with col_info:
    st.markdown("### 📐 Model Matematis")
    st.markdown("""
    <div class="rumus-card">
        <h4>Konsep 1 · Kombinatorika</h4>
        <p>C = k<sup>n</sup></p>
        <small>k = ragam karakter, n = panjang password</small>
    </div>
    <div class="rumus-card">
        <h4>Konsep 2 · Teori Peluang</h4>
        <p>P = M / C</p>
        <small>M = jumlah percobaan, C = total kombinasi</small>
    </div>
    <div class="rumus-card">
        <h4>Konsep 3 · Entropi Shannon</h4>
        <p>H = n · log₂(k)</p>
        <small>H = tingkat keacakan dalam satuan bit</small>
    </div>
    <div class="rumus-card">
        <h4>Konsep 4 · Estimasi Waktu</h4>
        <p>T = C / R</p>
        <small>R = kecepatan serangan brute force</small>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ANALISIS
# ============================================================
if password:
    # Deteksi karakter
    ada_lower  = any(c.islower()          for c in password)
    ada_upper  = any(c.isupper()          for c in password)
    ada_digit  = any(c.isdigit()          for c in password)
    ada_simbol = any(not c.isalnum()      for c in password)
    n = len(password)
    k = hitung_k(ada_lower, ada_upper, ada_digit, ada_simbol)

    # Hitung semua
    C = hitung_kombinasi(k, n)
    P = hitung_peluang(M, C)
    H = hitung_entropi(n, k)
    T = hitung_waktu(C, R)

    label, fg, bg, border_c, cls, ikon = get_tingkat(H)

    k_parts = []
    if ada_lower:  k_parts.append("26")
    if ada_upper:  k_parts.append("26")
    if ada_digit:  k_parts.append("10")
    if ada_simbol: k_parts.append("32")
    k_eq = " + ".join(k_parts) + f" = {k}"

    st.markdown("---")

    # ===== TINGKAT KEAMANAN =====
    st.markdown(f"""
    <div class="level-box" style="background:{bg};border-color:{border_c};color:{fg}">
        <h2>{ikon} {label}</h2>
        <p>Nilai Entropi H = {H:.2f} bit · Password sepanjang {n} karakter dengan {k} ragam karakter</p>
    </div>
    """, unsafe_allow_html=True)

    # ===== CHAR PILLS =====
    pills_html = ""
    for active, label_p in [
        (ada_lower,  "✓ Huruf kecil (a-z) = 26"),
        (ada_upper,  "✓ Huruf besar (A-Z) = 26"),
        (ada_digit,  "✓ Angka (0-9) = 10"),
        (ada_simbol, "✓ Simbol = 32"),
    ]:
        cls_p = "on" if active else "off"
        txt   = label_p if active else label_p.replace("✓", "✗")
        pills_html += f'<span class="char-pill {cls_p}">{txt}</span>'
    st.markdown(pills_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ===== METRIC CARDS =====
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.markdown(f"""
        <div class="metric-card blue">
            <label>Panjang (n)</label>
            <div class="val">{n}</div>
            <small>karakter</small>
        </div>""", unsafe_allow_html=True)
    with mc2:
        st.markdown(f"""
        <div class="metric-card purple">
            <label>Ruang karakter (k)</label>
            <div class="val">{k}</div>
            <small>{k_eq}</small>
        </div>""", unsafe_allow_html=True)
    with mc3:
        st.markdown(f"""
        <div class="metric-card green">
            <label>Entropi (H)</label>
            <div class="val">{H:.0f} bit</div>
            <small>n × log₂(k)</small>
        </div>""", unsafe_allow_html=True)
    with mc4:
        st.markdown(f"""
        <div class="metric-card orange">
            <label>Estimasi waktu retas</label>
            <div class="val" style="font-size:16px">{format_waktu(T)}</div>
            <small>T = C / R</small>
        </div>""", unsafe_allow_html=True)

    # ===== PERHITUNGAN LENGKAP =====
    st.markdown("### 🧮 Perhitungan Lengkap")
    C_str = format_angka_besar(C)
    T_str = format_angka_besar(T)
    P_str = f"{P:.2e}" if P > 0 else "≈ 0"
    R_str = format_angka_besar(R)

    st.markdown(f"""
    <div class="calc-box">
        <span class="calc-note"># Konsep 1: Kombinatorika — Total ruang kunci</span><br>
        <span class="calc-key">C</span> <span class="calc-op">=</span> k<sup>n</sup> <span class="calc-op">=</span> {k}<sup>{n}</sup> <span class="calc-op">=</span> <span class="calc-val">{C_str}</span><br><br>
        <span class="calc-note"># Konsep 2: Teori Peluang — Kemungkinan tertebak</span><br>
        <span class="calc-key">P</span> <span class="calc-op">=</span> M / C <span class="calc-op">=</span> {format_angka_besar(M)} / {C_str} <span class="calc-op">=</span> <span class="calc-val">{P_str}</span><br><br>
        <span class="calc-note"># Konsep 3: Entropi Shannon — Tingkat keacakan</span><br>
        <span class="calc-key">H</span> <span class="calc-op">=</span> n × log₂(k) <span class="calc-op">=</span> {n} × log₂({k}) <span class="calc-op">=</span> {n} × {math.log2(k):.4f} <span class="calc-op">=</span> <span class="calc-val">{H:.2f} bit</span><br><br>
        <span class="calc-note"># Konsep 4: Estimasi Waktu — Brute force attack</span><br>
        <span class="calc-key">T</span> <span class="calc-op">=</span> C / R <span class="calc-op">=</span> {C_str} / {R_str} <span class="calc-op">=</span> <span class="calc-val">{T_str} detik</span>
    </div>
    """, unsafe_allow_html=True)

    # ===== GRAFIK =====
    st.markdown("### 📊 Visualisasi")

    tab1, tab2, tab3 = st.tabs([
        "📈 Pertumbuhan Kombinasi",
        "🔥 Perbandingan Jenis Karakter",
        "⏱ Estimasi Waktu vs Panjang"
    ])

    # --- TAB 1: Pertumbuhan Eksponensial (Konsep 5) ---
    with tab1:
        st.markdown("**Konsep 5: Pertumbuhan Eksponensial** — C = kⁿ terhadap panjang password")
        lengths = list(range(4, 25))
        fig1 = go.Figure()
        scenarios = [
            ("Huruf kecil saja", 26, "#60a5fa"),
            ("Huruf+Angka", 62, "#a78bfa"),
            ("Huruf+Angka+Simbol", 94, "#34d399"),
            (f"Password kamu (k={k})", k, "#f97316"),
        ]
        for name, k_val, color in scenarios:
            y = [math.log10(k_val ** n_val) for n_val in lengths]
            fig1.add_trace(go.Scatter(
                x=lengths, y=y, name=name,
                line=dict(color=color, width=2.5),
                mode='lines+markers',
                marker=dict(size=5),
            ))
        fig1.update_layout(
            title="Pertumbuhan Kombinasi (skala log₁₀) terhadap Panjang Password",
            xaxis_title="Panjang Password (n)",
            yaxis_title="log₁₀(C) — Jumlah Kombinasi",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font=dict(color="#e2e8f0", family="Plus Jakarta Sans"),
            legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="#334155"),
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b"),
            height=380,
        )
        fig1.add_vline(x=n, line_dash="dash", line_color="#f97316", annotation_text=f"n={n} (passwordmu)", annotation_font_color="#f97316")
        st.plotly_chart(fig1, use_container_width=True)

    # --- TAB 2: Perbandingan Entropi ---
    with tab2:
        st.markdown("**Perbandingan Entropi (H)** — berbagai jenis karakter dengan panjang yang sama")
        types = ["Huruf kecil\n(k=26)", "Huruf+Angka\n(k=36)", "Huruf Besar+Kecil\n(k=52)", "Huruf+Angka\n(k=62)", "Semua+Simbol\n(k=94)", f"Password kamu\n(k={k})"]
        ks    = [26, 36, 52, 62, 94, k]
        hs    = [hitung_entropi(n, ki) for ki in ks]
        colors_bar = []
        for h_val in hs:
            lbl, fg2, *_ = get_tingkat(h_val)
            c_map = {"Sangat Lemah":"#ef4444","Lemah":"#f97316","Sedang":"#eab308","Kuat":"#22c55e","Sangat Kuat":"#8b5cf6"}
            colors_bar.append(c_map[lbl])

        fig2 = go.Figure(go.Bar(
            x=types, y=hs,
            marker_color=colors_bar,
            text=[f"{h:.1f} bit" for h in hs],
            textposition='outside',
            textfont=dict(color="#e2e8f0"),
        ))
        fig2.add_hline(y=40,  line_dash="dot", line_color="#ef4444", annotation_text="40 bit (min aman)", annotation_font_color="#ef4444")
        fig2.add_hline(y=80,  line_dash="dot", line_color="#22c55e", annotation_text="80 bit (Kuat)", annotation_font_color="#22c55e")
        fig2.add_hline(y=100, line_dash="dot", line_color="#8b5cf6", annotation_text="100 bit (Sangat Kuat)", annotation_font_color="#8b5cf6")
        fig2.update_layout(
            title=f"Perbandingan Entropi Shannon (n = {n} karakter)",
            xaxis_title="Jenis Karakter",
            yaxis_title="Entropi H (bit)",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font=dict(color="#e2e8f0", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b"),
            height=400,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- TAB 3: Waktu vs Panjang ---
    with tab3:
        st.markdown("**Estimasi Waktu Retas (T = C/R)** — terhadap panjang password")
        lens2  = list(range(4, 22))
        waktu_log = [math.log10(max(1, (k ** l) // R)) for l in lens2]
        colors_w = []
        for l in lens2:
            H_tmp = hitung_entropi(l, k)
            lbl, fg2, *_ = get_tingkat(H_tmp)
            c_map = {"Sangat Lemah":"#ef4444","Lemah":"#f97316","Sedang":"#eab308","Kuat":"#22c55e","Sangat Kuat":"#8b5cf6"}
            colors_w.append(c_map[lbl])

        fig3 = go.Figure(go.Bar(
            x=lens2, y=waktu_log,
            marker_color=colors_w,
            text=[f"n={l}" for l in lens2],
            textposition='inside',
            textfont=dict(color="white", size=10),
        ))
        fig3.add_vline(x=n, line_dash="dash", line_color="#f97316", annotation_text=f"n={n}", annotation_font_color="#f97316")
        fig3.update_layout(
            title=f"Estimasi Waktu Retas per Panjang Password (k={k}, R={R_str})",
            xaxis_title="Panjang Password (n)",
            yaxis_title="log₁₀(T) — Waktu dalam detik (skala log)",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font=dict(color="#e2e8f0", family="Plus Jakarta Sans"),
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b"),
            height=380,
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ===== REKOMENDASI =====
    st.markdown("### 💡 Rekomendasi")
    rekom_map = {
        "great":  f"🏆 <b>Luar biasa!</b> Password kamu memiliki entropi {H:.2f} bit, jauh melampaui standar NIST 100 bit. Dengan R = {R_str} tebakan/detik, dibutuhkan waktu {format_waktu(T)} untuk meretas seluruh ruang kunci. Hampir mustahil ditembus teknologi saat ini!",
        "good":   f"✅ <b>Password kuat dan aman!</b> Entropi {H:.2f} bit sudah melewati ambang NIST 80 bit. Estimasi waktu retas {format_waktu(T)}. Aman untuk penggunaan sehari-hari.",
        "medium": f"⚠️ <b>Cukup aman, tapi bisa lebih baik.</b> Entropi {H:.2f} bit masih di bawah 80 bit. Estimasi retas {format_waktu(T)}. Tambah 2-3 karakter lagi dan variasikan simbol.",
        "bad":    f"🚨 <b>Password berisiko tinggi!</b> Entropi hanya {H:.2f} bit. Estimasi retas {format_waktu(T)}. Segera ganti dengan minimal 12 karakter kombinasi huruf besar, kecil, angka, dan simbol.",
        "danger": f"💀 <b>Sangat berbahaya!</b> Entropi hanya {H:.2f} bit, jauh di bawah standar minimum 40 bit NIST. Bisa diretas dalam {format_waktu(T)}! Ganti segera!",
    }
    _, _, bg_r, border_r, cls_r, _ = get_tingkat(H)
    st.markdown(f'<div class="rekom {cls_r}">{rekom_map[cls_r]}</div>', unsafe_allow_html=True)

else:
    st.info("👆 Masukkan password di kolom atas untuk melihat hasil analisis keamanannya.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:12px; line-height:2;">
    <b style="color:#475569">Kelompok 2 Matematika Terapan PTIK-D</b><br>
    Marwasas Pardede · Muhammad Fazry Chandra · Ester Oktaviani Sinaga · Yola Claudia Sinaga · MHD. Ghifari<br>
    <b style="color:#475569">Universitas Negeri Medan · 2026</b><br>
    Dosen: Dr. Amirhud Dalimunthe, S.T., M.Kom · Novialdi Ashari, S.Stat., M.T.I
</div>
""", unsafe_allow_html=True)
