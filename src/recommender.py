"""
VibeFinder 1.0 — Music Recommender Simulation
Supports:
  - Advanced song features (popularity, release_decade, mood_tags)
  - Multiple scoring modes: balanced, genre_first, mood_first, energy_focused
  - Diversity penalty: no artist or genre dominates the top-k list
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import csv


# ─────────────────────────────────────────────────────────────
# Scoring mode weight configs  (Challenge 2)
# Each mode redistributes the weight budget across features.
# ─────────────────────────────────────────────────────────────
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre": 2.0,   # 40 % of max
        "mood": 1.0,    # 20 %
        "energy": 1.5,  # 30 %
        "acoustic": 0.5,# 10 %
        "popularity": 0.0, "decade": 0.0, "mood_tags": 0.0,
        "liveness": 0.0, "instrumentalness": 0.0,
    },
    "genre_first": {
        "genre": 4.0, "mood": 0.5, "energy": 0.75, "acoustic": 0.25,
        "popularity": 0.0, "decade": 0.0, "mood_tags": 0.0,
        "liveness": 0.0, "instrumentalness": 0.0,
    },
    "mood_first": {
        "genre": 0.5, "mood": 3.0, "energy": 1.0, "acoustic": 0.5,
        "popularity": 0.0, "decade": 0.0, "mood_tags": 0.0,
        "liveness": 0.0, "instrumentalness": 0.0,
    },
    "energy_focused": {
        "genre": 0.5, "mood": 0.5, "energy": 3.5, "acoustic": 0.5,
        "popularity": 0.0, "decade": 0.0, "mood_tags": 0.0,
        "liveness": 0.0, "instrumentalness": 0.0,
    },
    "advanced": {
        # Challenge 1 mode — uses all new features
        "genre": 1.5,
        "mood": 0.75,
        "energy": 1.0,
        "acoustic": 0.25,
        "popularity": 1.0,        # up to +1.0 for popular songs (if user wants popular=True)
        "decade": 0.75,           # up to +0.75 for decade match
        "mood_tags": 0.75,        # up to +0.75 for overlapping mood tags (capped at 0.75)
        "liveness": 0.5,          # up to +0.5 for live preference match
        "instrumentalness": 0.5,  # up to +0.5 for instrumental preference match
    },
}


# ─────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────
@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)
    liveness: float = 0.1          # 0=studio recording, 1=live performance
    instrumentalness: float = 0.1  # 0=lots of vocals, 1=fully instrumental


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Advanced fields (Challenge 1)
    preferred_decade: int = 0              # 0 = no preference
    preferred_mood_tags: List[str] = field(default_factory=list)
    prefer_popular: bool = False           # True = boost high-popularity songs
    prefers_live: bool = False             # True = reward live recordings
    prefers_instrumental: bool = False     # True = reward instrumental tracks


# ─────────────────────────────────────────────────────────────
# OOP Recommender (used by tests)
# ─────────────────────────────────────────────────────────────
class Recommender:
    """OOP recommendation engine with mode + diversity support."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song, mode: str = "balanced") -> float:
        """Compute a numeric score using the given scoring mode."""
        w = SCORING_MODES[mode]
        score = 0.0

        if song.genre.lower() == user.favorite_genre.lower():
            score += w["genre"]
        if song.mood.lower() == user.favorite_mood.lower():
            score += w["mood"]

        energy_gap = abs(user.target_energy - song.energy)
        score += (1.0 - energy_gap) * w["energy"]

        acoustic_pts = song.acousticness if user.likes_acoustic else (1.0 - song.acousticness)
        score += acoustic_pts * w["acoustic"]

        # Advanced features
        if w["popularity"] > 0 and user.prefer_popular:
            score += (song.popularity / 100.0) * w["popularity"]

        if w["decade"] > 0 and user.preferred_decade > 0:
            score += w["decade"] if song.release_decade == user.preferred_decade else 0.0

        if w["mood_tags"] > 0 and user.preferred_mood_tags:
            overlap = len(set(song.mood_tags) & set(user.preferred_mood_tags))
            tag_pts = min(overlap / max(len(user.preferred_mood_tags), 1), 1.0) * w["mood_tags"]
            score += tag_pts

        if w["liveness"] > 0:
            live_pts = song.liveness if user.prefers_live else (1.0 - song.liveness)
            score += live_pts * w["liveness"]

        if w["instrumentalness"] > 0:
            inst_pts = song.instrumentalness if user.prefers_instrumental else (1.0 - song.instrumentalness)
            score += inst_pts * w["instrumentalness"]

        return round(score, 3)

    def recommend(self, user: UserProfile, k: int = 5, mode: str = "balanced",
                  diverse: bool = False, max_per_artist: int = 1) -> List[Song]:
        """Return top-k Songs sorted by score, with optional diversity enforcement."""
        ranked = sorted(self.songs, key=lambda s: self._score(user, s, mode), reverse=True)
        if diverse:
            ranked = _apply_diversity(ranked, max_per_artist=max_per_artist)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song,
                               mode: str = "balanced") -> str:
        """Return a human-readable explanation of why a song was recommended."""
        w = SCORING_MODES[mode]
        parts = []

        if song.genre.lower() == user.favorite_genre.lower():
            parts.append(f"genre match '{song.genre}' (+{w['genre']})")
        if song.mood.lower() == user.favorite_mood.lower():
            parts.append(f"mood match '{song.mood}' (+{w['mood']})")

        energy_gap = abs(user.target_energy - song.energy)
        energy_pts = round((1.0 - energy_gap) * w["energy"], 2)
        parts.append(f"energy proximity (+{energy_pts})")

        acoustic_pts = round((song.acousticness if user.likes_acoustic else (1 - song.acousticness)) * w["acoustic"], 2)
        parts.append(f"acoustic preference (+{acoustic_pts})")

        if w["popularity"] > 0 and user.prefer_popular:
            pop_pts = round((song.popularity / 100.0) * w["popularity"], 2)
            parts.append(f"popularity {song.popularity}/100 (+{pop_pts})")

        if w["decade"] > 0 and user.preferred_decade > 0 and song.release_decade == user.preferred_decade:
            parts.append(f"decade match {song.release_decade} (+{w['decade']})")

        if w["mood_tags"] > 0 and user.preferred_mood_tags:
            overlap = set(song.mood_tags) & set(user.preferred_mood_tags)
            if overlap:
                tag_pts = round(min(len(overlap) / max(len(user.preferred_mood_tags), 1), 1.0) * w["mood_tags"], 2)
                parts.append(f"mood tags {overlap} (+{tag_pts})")

        if w["liveness"] > 0:
            live_pts = round((song.liveness if user.prefers_live else (1.0 - song.liveness)) * w["liveness"], 2)
            label = "live" if user.prefers_live else "studio"
            parts.append(f"{label} preference (+{live_pts})")

        if w["instrumentalness"] > 0:
            inst_pts = round((song.instrumentalness if user.prefers_instrumental else (1.0 - song.instrumentalness)) * w["instrumentalness"], 2)
            label = "instrumental" if user.prefers_instrumental else "vocal"
            parts.append(f"{label} preference (+{inst_pts})")

        return "; ".join(parts)


# ─────────────────────────────────────────────────────────────
# Diversity helper  (Challenge 3)
# ─────────────────────────────────────────────────────────────
def _apply_diversity(ranked_songs, max_per_artist: int = 1, max_per_genre: int = 2):
    """
    Filter a pre-sorted list so no artist appears more than max_per_artist times
    and no genre appears more than max_per_genre times.
    Songs that would violate the cap are moved to the end.
    """
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    accepted = []
    deferred = []

    for item in ranked_songs:
        # item can be a Song dataclass, a dict, or a (song_dict, score, reason) tuple
        if isinstance(item, tuple):
            song = item[0]
            artist = song.artist if hasattr(song, "artist") else song["artist"]
            genre = song.genre if hasattr(song, "genre") else song["genre"]
        elif hasattr(item, "artist"):
            artist, genre = item.artist, item.genre
        else:
            artist, genre = item["artist"], item["genre"]

        a_ok = artist_counts.get(artist, 0) < max_per_artist
        g_ok = genre_counts.get(genre, 0) < max_per_genre

        if a_ok and g_ok:
            accepted.append(item)
            artist_counts[artist] = artist_counts.get(artist, 0) + 1
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        else:
            deferred.append(item)

    return accepted + deferred


# ─────────────────────────────────────────────────────────────
# Functional API  (used by src/main.py)
# ─────────────────────────────────────────────────────────────
def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with numeric fields cast."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            row["popularity"] = int(row.get("popularity", 50))
            row["release_decade"] = int(row.get("release_decade", 2020))
            raw_tags = row.get("mood_tags", "")
            row["mood_tags"] = [t.strip() for t in raw_tags.split(",") if t.strip()]
            row["liveness"] = float(row.get("liveness", 0.1))
            row["instrumentalness"] = float(row.get("instrumentalness", 0.1))
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced") -> Tuple[float, str]:
    """
    Score a single song dict against user preference dict using the given mode.

    Returns (total_score, reason_string).
    """
    w = SCORING_MODES[mode]
    score = 0.0
    parts = []

    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        score += w["genre"]
        parts.append(f"genre match '{song['genre']}' (+{w['genre']})")

    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        score += w["mood"]
        parts.append(f"mood match '{song['mood']}' (+{w['mood']})")

    energy_gap = abs(user_prefs.get("energy", 0.5) - song["energy"])
    energy_pts = round((1.0 - energy_gap) * w["energy"], 2)
    score += energy_pts
    parts.append(f"energy proximity (+{energy_pts})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acoustic_pts = round((song["acousticness"] if likes_acoustic else (1 - song["acousticness"])) * w["acoustic"], 2)
    score += acoustic_pts
    parts.append(f"acoustic preference (+{acoustic_pts})")

    # Advanced features (Challenge 1)
    if w["popularity"] > 0 and user_prefs.get("prefer_popular", False):
        pop_pts = round((song["popularity"] / 100.0) * w["popularity"], 2)
        score += pop_pts
        parts.append(f"popularity {song['popularity']}/100 (+{pop_pts})")

    if w["decade"] > 0 and user_prefs.get("preferred_decade", 0) > 0:
        if song["release_decade"] == user_prefs["preferred_decade"]:
            score += w["decade"]
            parts.append(f"decade match {song['release_decade']} (+{w['decade']})")

    if w["mood_tags"] > 0:
        user_tags = set(user_prefs.get("preferred_mood_tags", []))
        song_tags = set(song["mood_tags"])
        overlap = user_tags & song_tags
        if overlap:
            tag_pts = round(min(len(overlap) / max(len(user_tags), 1), 1.0) * w["mood_tags"], 2)
            score += tag_pts
            parts.append(f"mood tags {overlap} (+{tag_pts})")

    if w["liveness"] > 0:
        prefers_live = user_prefs.get("prefers_live", False)
        live_pts = round((song["liveness"] if prefers_live else (1.0 - song["liveness"])) * w["liveness"], 2)
        score += live_pts
        label = "live" if prefers_live else "studio"
        parts.append(f"{label} preference (+{live_pts})")

    if w["instrumentalness"] > 0:
        prefers_inst = user_prefs.get("prefers_instrumental", False)
        inst_pts = round((song["instrumentalness"] if prefers_inst else (1.0 - song["instrumentalness"])) * w["instrumentalness"], 2)
        score += inst_pts
        label = "instrumental" if prefers_inst else "vocal"
        parts.append(f"{label} preference (+{inst_pts})")

    return round(score, 3), "; ".join(parts)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: str = "balanced", diverse: bool = False,
                    max_per_artist: int = 1) -> List[Tuple[Dict, float, str]]:
    """
    Score every song and return the top-k as (song, score, explanation) tuples.
    Pass diverse=True to enforce artist/genre variety in results.
    """
    scored = [(song, *score_song(user_prefs, song, mode)) for song in songs]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    if diverse:
        ranked = _apply_diversity(
            ranked,
            max_per_artist=max_per_artist,
            max_per_genre=2,
        )

    return ranked[:k]
