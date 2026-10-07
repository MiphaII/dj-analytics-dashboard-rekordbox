import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Ajoute src au path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from parser import parse_rekordbox_xml
from metrics import compute_dj_stats, get_capsule_recommendations, generate_m3u_playlist, get_top_stats, get_80_20_tracks, get_extended_wrapped_stats

# Configuration de la page
st.set_page_config(page_title="DJ Analytics Dashboard", page_icon="🪩", layout="wide")

if "current_view" not in st.session_state:
    st.session_state.current_view = "dashboard"

# Style : Dark mode VIBRANT & Animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .main { background-color: #0d0d0f; color: #f4f4f6; }

    /* Blocs de métriques */
    div[data-testid="stMetric"] { background: linear-gradient(145deg, #16161a 0%, #1e1e24 100%); border-top: 4px solid #1db954; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: transform 0.2s ease, box-shadow 0.2s ease; }
    div[data-testid="stMetric"]:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(29,185,84,0.2); }
    div[data-testid="stMetric"]:nth-child(2) { border-top-color: #ff4b4b; } 
    div[data-testid="stMetric"]:nth-child(2):hover { box-shadow: 0 12px 30px rgba(255,75,75,0.2); }
    div[data-testid="stMetric"]:nth-child(3) { border-top-color: #9d4edd; } 
    div[data-testid="stMetric"]:nth-child(3):hover { box-shadow: 0 12px 30px rgba(157,78,221,0.2); }
    div[data-testid="stMetric"]:nth-child(4) { border-top-color: #ff9f1c; } 
    div[data-testid="stMetric"]:nth-child(4):hover { box-shadow: 0 12px 30px rgba(255,159,28,0.2); }

    div[data-testid="stMetric"] label { color: #a0a0b0 !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 1px; font-size: 13px !important; }
    div[data-testid="stMetricValue"] { background: -webkit-linear-gradient(45deg, #ffffff, #a0a0b0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900 !important; font-size: 2.2rem !important; }

    /* Menus déroulants */
    div[data-testid="stExpander"] { background-color: #16161a; border: 1px solid #2a2a30; border-radius: 12px; margin-bottom: 10px; }
    div[data-testid="stExpander"] summary { font-weight: 800; font-size: 18px; color: #ffffff; padding: 10px; }

    /* Le Wrapped */
    .wrapped-slide { border-radius: 24px; color: #ffffff; text-align: center; min-height: 520px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 15px 50px rgba(0,0,0,0.6); padding: 40px; }
    .wrapped-tag { font-size: 14px; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; background: rgba(0,0,0,0.3); padding: 6px 16px; border-radius: 20px; margin-bottom: 20px; }
    .wrapped-title { font-size: 32px; font-weight: 900; margin-bottom: 30px; text-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .wrapped-card-item { background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); padding: 16px 24px; border-radius: 16px; width: 90%; margin: 8px 0; display: flex; justify-content: space-between; align-items: center; font-size: 16px; font-weight: 600; transition: transform 0.2s; }
    .wrapped-card-item:hover { transform: translateY(-3px) scale(1.02); background: rgba(0, 0, 0, 0.6); }
    .highlight-val { font-size: 20px; font-weight: 900; color: #ffffff !important; text-shadow: 0 2px 10px rgba(0,0,0,0.8); text-align: right; }
    
    /* Boutons */
    .kpi-btn button { margin-top: -15px; border: 1px solid #2a2a30; background: #16161a; color: #a0a0b0; }
    .kpi-btn button:hover { background: #2a2a30; color: #ffffff; border-color: #ffffff; }
    .back-btn button { background: #ff4b4b; color: white; border: none; font-weight: 800; padding: 10px 20px; }
    .back-btn button:hover { background: #ff7676; }
    </style>
""", unsafe_allow_html=True)

# Titre
st.title("🪩 DJ Analytics Dashboard")
st.markdown("<p style='color: #9898a6; margin-top: -10px;'>Your library, uncensored. Drop the data, get the insights.</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
st.sidebar.header("📁 Upload Library")
uploaded_file = st.sidebar.file_uploader("Upload Rekordbox XML", type=["xml"])

if uploaded_file is not None:
    temp_path = os.path.join("data", "uploaded_library.xml")
    os.makedirs("data", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    df = parse_rekordbox_xml(temp_path)
    st.sidebar.success("Library loaded! 🚀")
else:
    df = parse_rekordbox_xml()
    st.sidebar.info("Demo Mode 🧪 (Test data)")

if df.empty:
    st.warning("⚠️ No tracks found in the XML file.")
else:
    stats = compute_dj_stats(df)
    top_stats = get_top_stats(df)
    df_8020 = get_80_20_tracks(df)
    ext_stats = get_extended_wrapped_stats(df)

    # --- SECTION 1 : KPI ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="🎯 80/20 Core Tracks", value=f"{stats['pct_library_80']}%", delta=f"{stats['tracks_80_pct']} tracks make 80% of sets")
        st.markdown('<div class="kpi-btn">', unsafe_allow_html=True)
        if st.button("📂 View Tracks", key="btn_8020", use_container_width=True): st.session_state.current_view = "8020"
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.metric(label="💤 Sleeping (> 6m)", value=f"{stats['pct_sleeping']}%", delta=f"{stats['sleeping_count']} tracks untouched")
        st.markdown('<div class="kpi-btn">', unsafe_allow_html=True)
        if st.button("📂 View Tracks", key="btn_sleep", use_container_width=True): st.session_state.current_view = "sleeping"
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.metric(label="👻 Ghost Tracks (< 3)", value=f"{stats['pct_ghosts']}%", delta=f"{stats['ghost_count']} unplayed")
        st.markdown('<div class="kpi-btn">', unsafe_allow_html=True)
        if st.button("📂 View Tracks", key="btn_ghosts", use_container_width=True): st.session_state.current_view = "ghosts"
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.metric(label="🔥 Energy (Avg BPM)", value=f"{stats['avg_bpm']}", delta="Beats Per Minute")
        st.markdown('<div class="kpi-btn">', unsafe_allow_html=True)
        if st.button("📂 Full Library", key="btn_all", use_container_width=True): st.session_state.current_view = "all"
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    now = pd.Timestamp.now()
    six_months_ago = now - pd.Timedelta(days=180)

    # --- LISTES DYNAMIQUES (Le clic sur les KPI) ---
    if st.session_state.current_view != "dashboard":
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅️ Back to Dashboard"):
            st.session_state.current_view = "dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.current_view == "8020":
            st.subheader("🎯 The Core: Your 80/20 Rule")
            if not df_8020.empty:
                st.download_button("📥 Export as .m3u Playlist", generate_m3u_playlist(df_8020), "core_8020.m3u", key="export_8020_view")
                st.dataframe(df_8020[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)
                
        elif st.session_state.current_view == "sleeping":
            st.subheader("💤 Sleeping Tracks (Not played in 6+ months)")
            sleeping_df = df[(df["LastPlayed"].isna()) | (df["LastPlayed"] < six_months_ago)]
            if not sleeping_df.empty:
                st.download_button("📥 Export as .m3u Playlist", generate_m3u_playlist(sleeping_df), "sleeping_tracks.m3u", key="export_sleep_view")
                st.dataframe(sleeping_df[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)
                
        elif st.session_state.current_view == "ghosts":
            st.subheader("👻 Ghost Tracks (Played less than 3 times)")
            ghosts_df = df[df["PlayCount"] < 3]
            if not ghosts_df.empty:
                st.download_button("📥 Export as .m3u Playlist", generate_m3u_playlist(ghosts_df), "ghost_tracks.m3u", key="export_ghosts_view")
                st.dataframe(ghosts_df[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)
                
        elif st.session_state.current_view == "all":
            st.subheader("📚 Full Library Explorer")
            search_query = st.text_input("🔍 Search artist or track name:", "", key="search_full_view")
            filtered_df = df
            if search_query:
                filtered_df = df[df["Name"].str.contains(search_query, case=False, na=False) | df["Artist"].str.contains(search_query, case=False, na=False)]
            st.dataframe(filtered_df[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)

    # --- LE DASHBOARD PRINCIPAL ---
    else:
        col_wrap, col_charts = st.columns([1.2, 1])

        with col_wrap:
            st.subheader("🎁 Wrapped 2026")
            
            if "slide_idx" not in st.session_state:
                st.session_state.slide_idx = 0

            total_slides = 7 # 🔥 On passe à 7 Slides
            
            col_prev, col_indicator, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("👈 Previous") and st.session_state.slide_idx > 0:
                    st.session_state.slide_idx -= 1
                    st.rerun()
            with col_indicator:
                st.markdown(f"<p style='text-align: center; color: #a0a0b0; font-weight: 900; letter-spacing: 2px;'>STORY {st.session_state.slide_idx + 1} / {total_slides}</p>", unsafe_allow_html=True)
            with col_next:
                if st.button("Next 👉") and st.session_state.slide_idx < total_slides - 1:
                    st.session_state.slide_idx += 1
                    st.rerun()

            idx = st.session_state.slide_idx

            bg_colors = [
                "linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%)", # Recap
                "linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%)", # Heavy Rotation
                "linear-gradient(135deg, #11998E 0%, #38EF7D 100%)", # Headliners
                "linear-gradient(135deg, #FF0099 0%, #493240 100%)", # Persona (Synthwave)
                "linear-gradient(135deg, #2193b0 0%, #6dd5ed 50%, #cc2b5e 50%, #753a88 100%)", # Rollercoaster (Scindé bleu/rouge)
                "linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%)", # Time Capsule
                "linear-gradient(135deg, #D4AF37 0%, #835915 100%)"  # Digging (Or)
            ]
            bg = bg_colors[idx]

            # 1. Recap
            if idx == 0:
                st.markdown(f"""
                    <div class="wrapped-slide" style="background: {bg};">
                        <div class="wrapped-tag">🎉 2026 Recap</div>
                        <div class="wrapped-title">Your Year in Sound 🍾</div>
                        <div class="wrapped-card-item"><span>Total Library Tracks</span><span class="highlight-val">{stats['total_tracks']} 💿</span></div>
                        <div class="wrapped-card-item"><span>Total Times You Hit Play</span><span class="highlight-val">{stats['total_plays']} ▶️</span></div>
                        <div class="wrapped-card-item"><span>Average Set Energy</span><span class="highlight-val">{stats['avg_bpm']} BPM ⚡</span></div>
                    </div>
                """, unsafe_allow_html=True)
            # 2. Top Tracks
            elif idx == 1:
                tracks_html = "".join([f"<div class='wrapped-card-item'><span><b>#{i+1}</b> {t['Name']} <br><span style='font-size:12px; font-weight:400;'>{t['Artist']}</span></span><span class='highlight-val'>{t['PlayCount']} Plays 🔥</span></div>" for i, t in enumerate(top_stats["top_tracks"])])
                st.markdown(f"<div class='wrapped-slide' style='background: {bg};'><div class='wrapped-tag'>🚀 Heavy Rotation</div><div class='wrapped-title'>Your Absolute Anthems 🎧</div>{tracks_html}</div>", unsafe_allow_html=True)
            # 3. Top Artists
            elif idx == 2:
                artists_html = "".join([f"<div class='wrapped-card-item'><span><b>#{i+1}</b> {a['Artist']}</span><span class='highlight-val'>{a['PlayCount']} Plays 🌟</span></div>" for i, a in enumerate(top_stats["top_artists"])])
                st.markdown(f"<div class='wrapped-slide' style='background: {bg};'><div class='wrapped-tag'>👑 The Headliners</div><div class='wrapped-title'>Artists You Abused 🎤</div>{artists_html}</div>", unsafe_allow_html=True)
            # 4. DJ Persona (Genres)
            elif idx == 3:
                genres_html = "".join([f"<div class='wrapped-card-item'><span><b>#{i+1}</b> {g['genre']}</span><span class='highlight-val'>{g['pct']}% of sets 🧬</span></div>" for i, g in enumerate(ext_stats.get("top_genres", []))])
                if not genres_html: genres_html = "<div class='wrapped-card-item'><span>Not enough genre data.</span></div>"
                st.markdown(f"<div class='wrapped-slide' style='background: {bg};'><div class='wrapped-tag'>🧬 Musical DNA</div><div class='wrapped-title'>Your DJ Persona</div><p style='margin-bottom: 20px;'>Your core musical identity defined by your sets.</p>{genres_html}</div>", unsafe_allow_html=True)
            # 5. Rollercoaster (BPM)
            elif idx == 4:
                min_b = ext_stats.get("bpm_min")
                max_b = ext_stats.get("bpm_max")
                if min_b and max_b:
                    roller_html = f"""
                        <div class='wrapped-card-item' style='background: rgba(28, 181, 224, 0.4); border-color: rgba(28, 181, 224, 1);'>
                            <span><b>🥶 The Deep Chill</b><br><span style='font-size:12px; font-weight:400;'>{min_b['Name']} — {min_b['Artist']}</span></span>
                            <span class='highlight-val'>{min_b['BPM']} BPM</span>
                        </div>
                        <div style='margin: 15px 0; font-size: 24px; font-weight: 900; color: #fff;'>🌪️ VS 🌪️</div>
                        <div class='wrapped-card-item' style='background: rgba(255, 75, 75, 0.4); border-color: rgba(255, 75, 75, 1);'>
                            <span><b>🔥 Peak Time Violence</b><br><span style='font-size:12px; font-weight:400;'>{max_b['Name']} — {max_b['Artist']}</span></span>
                            <span class='highlight-val'>{max_b['BPM']} BPM</span>
                        </div>
                    """
                else:
                    roller_html = "<div class='wrapped-card-item'><span>Not enough BPM data tracked.</span></div>"
                st.markdown(f"<div class='wrapped-slide' style='background: {bg};'><div class='wrapped-tag'>🎢 The Rollercoaster</div><div class='wrapped-title'>The Grand Écart</div><p style='margin-bottom: 20px;'>From warmup grooves to peak time destruction.</p>{roller_html}</div>", unsafe_allow_html=True)
            # 6. Time Capsule
            elif idx == 5:
                forgotten_html = "".join([f"<div class='wrapped-card-item'><span><b>#{i+1}</b> {f['Name']} <br><span style='font-size:12px; font-weight:400;'>{f['Artist']}</span></span><span class='highlight-val'>{f['PlayCount']} Past Plays 💀</span></div>" for i, f in enumerate(top_stats["top_forgotten"])])
                st.markdown(f"<div class='wrapped-slide' style='background: {bg};'><div class='wrapped-tag'>🕰️ Time Capsule Alert</div><div class='wrapped-title'>The Forgotten Bangers 🪦</div><p style='font-size: 15px; font-weight: 600; margin-bottom: 20px;'>You spammed these, then completely ignored them.</p>{forgotten_html}</div>", unsafe_allow_html=True)
            # 7. Digging Score
            elif idx == 6:
                new_t = ext_stats.get('new_tracks_count', 0)
                score = ext_stats.get('digging_score_pct', 0)
                emoji = "🔥" if score > 30 else ("👍" if score > 10 else "🕸️")
                st.markdown(f"""
                    <div class="wrapped-slide" style="background: {bg};">
                        <div class="wrapped-tag">⛏️ The Crate Digger</div>
                        <div class="wrapped-title">Your Digging Score</div>
                        <p style="margin-bottom: 25px;">How fresh is your arsenal?</p>
                        <div class="wrapped-card-item"><span>Tracks Added This Year</span><span class="highlight-val">{new_t} 💿</span></div>
                        <div class="wrapped-card-item"><span>Freshness Score</span><span class="highlight-val">{score}% {emoji}</span></div>
                    </div>
                """, unsafe_allow_html=True)

        with col_charts:
            st.subheader("📊 Visual Breakdown")
            if "Genre" in df.columns and not df["Genre"].dropna().empty:
                genre_counts = df["Genre"].value_counts().reset_index()
                genre_counts.columns = ["Genre", "Count"]
                fig_genre = px.pie(genre_counts, names="Genre", values="Count", hole=0.5, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Bold)
                fig_genre.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=0, r=0), height=500)
                st.plotly_chart(fig_genre, use_container_width=True)

        st.markdown("---")

        # --- SECTION 3 : EXPLORATEUR DE DONNÉES ---
        st.subheader("📂 Data Explorer & Exports")
        st.markdown("Unfold a category below to see the exact tracks and export them to Rekordbox.")

        with st.expander("🎯 View & Export The 80/20 Core Tracks"):
            if not df_8020.empty:
                st.download_button("📥 Export 80/20 Core (.m3u)", generate_m3u_playlist(df_8020), "core_8020.m3u", key="exp_8020_bottom")
                st.dataframe(df_8020[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)

        with st.expander("💤 View & Export Sleeping Tracks (> 6 months)"):
            sleeping_df = df[(df["LastPlayed"].isna()) | (df["LastPlayed"] < six_months_ago)]
            if not sleeping_df.empty:
                st.download_button("📥 Export Sleeping Tracks (.m3u)", generate_m3u_playlist(sleeping_df), "sleeping_tracks.m3u", key="exp_sleep_bottom")
                st.dataframe(sleeping_df[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)

        with st.expander("👻 View & Export Ghost Tracks (< 3 plays)"):
            ghosts_df = df[df["PlayCount"] < 3]
            if not ghosts_df.empty:
                st.download_button("📥 Export Ghost Tracks (.m3u)", generate_m3u_playlist(ghosts_df), "ghost_tracks.m3u", key="exp_ghost_bottom")
                st.dataframe(ghosts_df[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)

        with st.expander("⏳ View & Export Time Capsule (Forgotten Bangers)"):
            capsule_df = get_capsule_recommendations(df, top_n=10)
            if not capsule_df.empty:
                st.download_button("📥 Export Time Capsule (.m3u)", generate_m3u_playlist(capsule_df), "time_capsule.m3u", key="exp_capsule_bottom")
                st.dataframe(capsule_df[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)

        with st.expander("📚 Search Full Library"):
            search_query_exp = st.text_input("🔍 Search artist or track name:", "", key="search_all_exp_bottom")
            filtered_df_exp = df
            if search_query_exp:
                filtered_df_exp = df[df["Name"].str.contains(search_query_exp, case=False, na=False) | df["Artist"].str.contains(search_query_exp, case=False, na=False)]
            st.dataframe(filtered_df_exp[["Name", "Artist", "Genre", "BPM", "PlayCount", "LastPlayed"]], use_container_width=True, hide_index=True)