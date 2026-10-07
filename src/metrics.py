import os
import sys
import pandas as pd
from datetime import datetime

# Ajoute le dossier parent au path pour pouvoir importer parser sans souci
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import parse_rekordbox_xml

def compute_dj_stats(df: pd.DataFrame) -> dict:
    """Calcule toutes les métriques clés et provocantes du dashboard DJ."""
    if df.empty:
        return {}

    total_tracks = len(df)
    
    # 1. Règle des 80/20 (concentration des sets)
    df_sorted = df.sort_values(by="PlayCount", ascending=False)
    total_plays = df_sorted["PlayCount"].sum()
    
    if total_plays > 0:
        df_sorted["CumulativePlays"] = df_sorted["PlayCount"].cumsum()
        threshold_80 = total_plays * 0.8
        tracks_80_pct = len(df_sorted[df_sorted["CumulativePlays"] <= threshold_80])
        pct_library_80 = round((tracks_80_pct / total_tracks) * 100, 1)
    else:
        tracks_80_pct = 0
        pct_library_80 = 0

    # 2. Sons endormis (LastPlayed > 6 mois ou jamais joués)
    now = pd.Timestamp.now()
    six_months_ago = now - pd.Timedelta(days=180)
    sleeping_tracks = df[(df["LastPlayed"].isna()) | (df["LastPlayed"] < six_months_ago)]
    pct_sleeping = round((len(sleeping_tracks) / total_tracks) * 100, 1)

    # 3. Ghost Tracks (joués moins de 3 fois)
    ghost_tracks = df[df["PlayCount"] < 3]
    pct_ghosts = round((len(ghost_tracks) / total_tracks) * 100, 1)

    # 4. BPM moyen
    avg_bpm = round(df["BPM"].mean(), 1) if "BPM" in df.columns else 0

    return {
        "total_tracks": total_tracks,
        "total_plays": int(total_plays),
        "tracks_80_pct": tracks_80_pct,
        "pct_library_80": pct_library_80,
        "sleeping_count": len(sleeping_tracks),
        "pct_sleeping": pct_sleeping,
        "ghost_count": len(ghost_tracks),
        "pct_ghosts": pct_ghosts,
        "avg_bpm": avg_bpm
    }

def get_capsule_recommendations(df: pd.DataFrame, top_n=5) -> pd.DataFrame:
    """La Capsule Temporelle : Pépites oubliées (aimées mais plus jouées)."""
    if df.empty or "LastPlayed" not in df.columns:
        return pd.DataFrame()
        
    played_before = df[df["PlayCount"] >= 2].copy()
    if played_before.empty:
        played_before = df.copy()
        
    played_before = played_before.sort_values(by="LastPlayed", ascending=True)
    return played_before.head(top_n)

def generate_m3u_playlist(df_tracks: pd.DataFrame) -> str:
    """Génère le contenu texte d'une playlist au format M3U pour Rekordbox."""
    m3u_content = "#EXTM3U\n"
    for _, row in df_tracks.iterrows():
        # Si le fichier a un chemin, on l'utilise, sinon on met un nom fictif propre
        path = row.get("Location", f"{row['Artist']} - {row['Name']}.mp3")
        m3u_content += f"#EXTINF:-1,{row['Artist']} - {row['Name']}\n"
        m3u_content += f"{path}\n"
    return m3u_content

def get_top_stats(df: pd.DataFrame) -> dict:
    """Extrait les Top 5 artistes, top tracks et top oubliés pour le Wrapped."""
    if df.empty:
        return {"top_tracks": [], "top_artists": [], "top_forgotten": []}

    # Top 5 tracks les plus joués
    top_tracks = df.sort_values(by="PlayCount", ascending=False).head(5)[["Name", "Artist", "PlayCount"]].to_dict(orient="records")

    # Top 5 artistes les plus joués (agrégation par PlayCount total)
    artist_grouped = df.groupby("Artist")["PlayCount"].sum().reset_index()
    top_artists = artist_grouped.sort_values(by="PlayCount", ascending=False).head(5).to_dict(orient="records")

    # Top 5 sons oubliés (gros PlayCount par le passé mais pas joués depuis > 1 an)
    now = pd.Timestamp.now()
    one_year_ago = now - pd.Timedelta(days=365)
    forgotten_df = df[(df["LastPlayed"].isna()) | (df["LastPlayed"] < one_year_ago)].sort_values(by="PlayCount", ascending=False)
    top_forgotten = forgotten_df.head(5)[["Name", "Artist", "PlayCount", "LastPlayed"]].to_dict(orient="records")

    return {
        "top_tracks": top_tracks,
        "top_artists": top_artists,
        "top_forgotten": top_forgotten
    }

def get_80_20_tracks(df: pd.DataFrame) -> pd.DataFrame:
    """Récupère la liste exacte des morceaux qui constituent les 80% des écoutes."""
    if df.empty:
        return pd.DataFrame()
    
    df_sorted = df.sort_values(by="PlayCount", ascending=False)
    total_plays = df_sorted["PlayCount"].sum()
    
    if total_plays == 0:
        return pd.DataFrame()
        
    df_sorted["CumulativePlays"] = df_sorted["PlayCount"].cumsum()
    threshold_80 = total_plays * 0.8
    
    return df_sorted[df_sorted["CumulativePlays"] <= threshold_80].drop(columns=["CumulativePlays"])

def get_extended_wrapped_stats(df: pd.DataFrame) -> dict:
    """Calcule les stats avancées pour le Wrapped étendu (Genres, BPM, Digging)."""
    stats = {}
    if df.empty:
        return stats
        
    # 1. Signature Musicale (Top 3 Genres)
    if "Genre" in df.columns:
        # On priorise les genres les plus joués
        if "PlayCount" in df.columns:
            genres = df.groupby("Genre")["PlayCount"].sum().sort_values(ascending=False)
        else:
            genres = df["Genre"].value_counts()
        
        top_genres = []
        total_plays = genres.sum() if genres.sum() > 0 else 1
        for g, count in genres.head(3).items():
            pct = int((count / total_plays) * 100)
            top_genres.append({"genre": g, "pct": pct, "count": count})
        stats["top_genres"] = top_genres
    else:
        stats["top_genres"] = []

    # 2. Le Grand Écart (BPM Min / Max sur les sons joués)
    stats["bpm_min"] = None
    stats["bpm_max"] = None
    if "BPM" in df.columns and "PlayCount" in df.columns:
        # On ne regarde que les sons qui ont été joués au moins 1 fois
        played_df = df[(df["PlayCount"] > 0) & (df["BPM"] > 0)]
        if not played_df.empty:
            min_row = played_df.loc[played_df["BPM"].idxmin()]
            max_row = played_df.loc[played_df["BPM"].idxmax()]
            stats["bpm_min"] = {"Name": min_row["Name"], "Artist": min_row["Artist"], "BPM": min_row["BPM"]}
            stats["bpm_max"] = {"Name": max_row["Name"], "Artist": max_row["Artist"], "BPM": max_row["BPM"]}

    # 3. Score de Digging (DateAdded)
    stats["new_tracks_count"] = 0
    stats["digging_score_pct"] = 0
    if "DateAdded" in df.columns:
        try:
            df["DateAdded"] = pd.to_datetime(df["DateAdded"], errors="coerce")
            one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=365)
            recent_tracks = df[df["DateAdded"] >= one_year_ago]
            stats["new_tracks_count"] = len(recent_tracks)
            stats["digging_score_pct"] = int((len(recent_tracks) / len(df)) * 100) if len(df) > 0 else 0
        except Exception:
            pass # Si Rekordbox n'a pas fourni de DateAdded exploitable

    return stats
if __name__ == "__main__":
    df = parse_rekordbox_xml()
    
    stats = compute_dj_stats(df)
    print("\n--- Statistiques Calculées ---")
    for k, v in stats.items():
        print(f"{k}: {v}")
        
    capsule = get_capsule_recommendations(df)
    print("\n--- Capsule Temporelle (Oubliés mais cultes) ---")
    print(capsule[["Name", "Artist", "PlayCount", "LastPlayed"]])