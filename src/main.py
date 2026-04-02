"""
VibeFinder 1.0 — CLI demo
Demonstrates all four optional challenges:
  Challenge 1: Advanced features (popularity, decade, mood_tags)
  Challenge 2: Scoring modes (balanced / genre_first / mood_first / energy_focused / advanced)
  Challenge 3: Diversity penalty (max 1 song per artist, max 2 per genre)
  Challenge 4: Tabulate-formatted output table

Run with:  python -m src.main
"""

import os
from tabulate import tabulate
from src.recommender import load_songs, recommend_songs, SCORING_MODES

SONGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


# ── Challenge 4: Tabulate table printer ──────────────────────
def print_table(label: str, user_prefs: dict, songs: list,
                mode: str = "balanced", diverse: bool = False,
                max_per_artist: int = 1, k: int = 5) -> None:
    """Print recommendations as a formatted table using tabulate."""
    diverse_label = f"  [diverse, max {max_per_artist}/artist]" if diverse else ""
    print(f"\n{'-'*72}")
    print(f"  Profile : {label}   |   Mode: {mode.upper()}{diverse_label}")
    print(f"  Prefs   : {user_prefs}")
    print(f"{'-'*72}")

    results = recommend_songs(user_prefs, songs, k=k, mode=mode,
                              diverse=diverse, max_per_artist=max_per_artist)

    rows = []
    for rank, (song, score, explanation) in enumerate(results, start=1):
        # Truncate long explanation for table width
        short_why = explanation if len(explanation) <= 70 else explanation[:67] + "..."
        rows.append([
            rank,
            song["title"],
            song["artist"],
            f"{song['genre']} / {song['mood']}",
            f"{score:.2f}",
            short_why,
        ])

    print(tabulate(
        rows,
        headers=["#", "Title", "Artist", "Genre / Mood", "Score", "Why"],
        tablefmt="outline",
        maxcolwidths=[None, 20, 14, 18, None, 45],
    ))
    print()


def run_experiment(songs: list) -> None:
    """
    Step 3 experiment: compare balanced vs genre-halved weights for the rock fan.
    Shows whether halving genre weight makes results more diverse or just different.
    """
    rock_fan = {"genre": "rock", "mood": "intense", "energy": 0.90, "likes_acoustic": False}

    print("\n" + "="*72)
    print("  EXPERIMENT — Weight Shift: genre 2.0 vs genre 1.0 (rock fan)")
    print("  Hypothesis: halving genre weight should increase cross-genre variety")
    print("="*72)
    print_table("Rock Fan  [BALANCED — genre=2.0]",   rock_fan, songs, mode="balanced")
    print_table("Rock Fan  [MOOD_FIRST mode — genre weight=0.5, mood weight=3.0]",
                rock_fan, songs, mode="mood_first")

    print("  FINDING: In 'balanced' mode, top 2 are rock/intense (genre match).")
    print("  In 'mood_first' mode (genre weight=0.5), genre match is almost irrelevant.")
    print("  Top results shift to any intense song regardless of genre.")
    print("  -> More diverse genre-wise, but less predictable for a dedicated rock fan.")
    print()


def main() -> None:
    songs = load_songs(SONGS_PATH)
    print(f"Loaded songs: {len(songs)}")

    run_experiment(songs)

    # ── Base profiles ──────────────────────────────────────────
    pop_fan     = {"genre": "pop",         "mood": "happy",       "energy": 0.85, "likes_acoustic": False}
    lofi_fan    = {"genre": "lofi",        "mood": "chill",       "energy": 0.35, "likes_acoustic": True}
    rock_fan    = {"genre": "rock",        "mood": "intense",     "energy": 0.90, "likes_acoustic": False}
    conflicted  = {"genre": "alternative", "mood": "melancholic", "energy": 0.88, "likes_acoustic": False}

    # ── Challenge 1: Advanced profile with new features ────────
    advanced_fan = {
        "genre": "electronic",
        "mood": "energetic",
        "energy": 0.92,
        "likes_acoustic": False,
        "prefer_popular": True,          # boosts high-popularity songs
        "preferred_decade": 2020,        # rewards 2020s tracks
        "preferred_mood_tags": ["euphoric", "driving", "energetic"],
    }

    # ===========================================================
    # CHALLENGE 2: Same profile, four different scoring modes
    # ===========================================================
    print("\n" + "="*72)
    print("  CHALLENGE 2 — SCORING MODES (same pop/happy profile, 4 modes)")
    print("="*72)
    for mode in ["balanced", "genre_first", "mood_first", "energy_focused"]:
        print_table("High-Energy Pop Fan", pop_fan, songs, mode=mode)

    # ===========================================================
    # CHALLENGE 3: Diversity penalty comparison
    # ===========================================================
    print("\n" + "="*72)
    print("  CHALLENGE 3 — DIVERSITY (rock fan: without vs with diversity)")
    print("="*72)
    print_table("Rock Fan — NO diversity", rock_fan, songs, mode="balanced", diverse=False)
    print_table("Rock Fan — WITH diversity (max 1/artist)", rock_fan, songs, mode="balanced", diverse=True, max_per_artist=1)

    # ===========================================================
    # CHALLENGE 1: Advanced mode with new features
    # ===========================================================
    print("\n" + "="*72)
    print("  CHALLENGE 1 — ADVANCED FEATURES (popularity + decade + mood_tags)")
    print("="*72)
    print_table("Electronic / Euphoric 2020s Fan", advanced_fan, songs, mode="advanced")

    # ===========================================================
    # All 4 base profiles in balanced mode (for reference)
    # ===========================================================
    print("\n" + "="*72)
    print("  ALL PROFILES — BALANCED MODE with diversity")
    print("="*72)
    print_table("High-Energy Pop Fan",          pop_fan,    songs, diverse=True)
    print_table("Chill Lofi Listener",           lofi_fan,   songs, diverse=True)
    print_table("Deep Intense Rock Fan",         rock_fan,   songs, diverse=True)
    print_table("Conflicted (hi-energy+melancholic)", conflicted, songs, diverse=True)


if __name__ == "__main__":
    main()
