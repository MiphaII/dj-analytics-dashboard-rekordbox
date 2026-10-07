import os
import xml.etree.ElementTree as ET
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_XML_PATH = os.path.join(BASE_DIR, "data", "sample.xml")

def generate_mock_xml(filepath=DEFAULT_XML_PATH):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    root = ET.Element("DJ_PLAYLISTS", Version="1.0.0")
    collection = ET.SubElement(root, "COLLECTION", Entries="6")
    
    # Ajout de la Tonality (Camelot Wheel) et d'un set simulé
    mock_tracks = [
        {"TrackID": "1", "Name": "Acid Rain", "Artist": "Perc", "BPM": "132.00", "PlayCount": "45", "LastPlayed": "2026-05-12", "Genre": "Techno", "Tonality": "8A"},
        {"TrackID": "2", "Name": "Groove Tool", "Artist": "PAWSA", "BPM": "128.00", "PlayCount": "2", "LastPlayed": "2024-01-10", "Genre": "Tech House", "Tonality": "9A"},
        {"TrackID": "3", "Name": "Sub Zero", "Artist": "Ben Klock", "BPM": "135.00", "PlayCount": "89", "LastPlayed": "2026-09-01", "Genre": "Raw Techno", "Tonality": "8A"},
        {"TrackID": "4", "Name": "Forgotten Minimal", "Artist": "Ricardo Villalobos", "BPM": "124.00", "PlayCount": "1", "LastPlayed": "2023-11-05", "Genre": "Minimal", "Tonality": "11B"},
        {"TrackID": "5", "Name": "Banger 2026", "Artist": "Amelie Lens", "BPM": "138.00", "PlayCount": "112", "LastPlayed": "2026-10-01", "Genre": "Hard Techno", "Tonality": "7A"},
        {"TrackID": "6", "Name": "Closing Track", "Artist": "Bicep", "BPM": "126.00", "PlayCount": "60", "LastPlayed": "2026-10-02", "Genre": "Electronica", "Tonality": "10B"}
    ]
    
    for t in mock_tracks:
        ET.SubElement(collection, "TRACK", **t)
        
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)

def parse_rekordbox_xml(filepath=DEFAULT_XML_PATH):
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        generate_mock_xml(filepath)
    try:
        tree = ET.parse(filepath)
    except ET.ParseError:
        generate_mock_xml(filepath)
        tree = ET.parse(filepath)
        
    root = tree.getroot()
    tracks_data = []
    collection = root.find("COLLECTION")
    if collection is not None:
        for track in collection.findall("TRACK"):
            tracks_data.append(track.attrib)
            
    if not tracks_data:
        return pd.DataFrame()
        
    df = pd.DataFrame(tracks_data)
    
    if "BPM" in df.columns:
        df["BPM"] = pd.to_numeric(df["BPM"], errors="coerce")
    if "PlayCount" in df.columns:
        df["PlayCount"] = pd.to_numeric(df["PlayCount"], errors="coerce").fillna(0).astype(int)
    if "LastPlayed" in df.columns:
        df["LastPlayed"] = pd.to_datetime(df["LastPlayed"], errors="coerce")
        
    return df