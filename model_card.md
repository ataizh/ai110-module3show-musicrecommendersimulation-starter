# Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests the top 5 songs from a small 20-song catalog based on a user's preferred genre, mood, energy level, and acoustic preference. It is designed for **classroom exploration only** — to demonstrate how content-based filtering works and where its limitations show up. It is not intended for real users or production music apps.

**Not intended for:** replacing real music platforms, making decisions that affect users' listening habits at scale, or any context where diversity and fairness of recommendations matter beyond a demonstration.

---

## 3. How the Model Works

Every song in the catalog has measurable attributes: genre (e.g. "pop", "lofi"), mood (e.g. "happy", "intense"), energy (a number from 0 to 1 representing how "loud and active" the song feels), and acousticness (how "unplugged" it sounds).

The user provides a taste profile: their favorite genre, favorite mood, a target energy level, and whether they prefer acoustic music.

The model compares **each song** to the user's profile and awards points:

- 2 points if the song's genre matches the user's favorite
- 1 point if the mood matches
- Up to 1.5 points based on how close the song's energy is to the user's target (closer = more points)
- Up to 0.5 points based on acoustic preference

Songs are then sorted highest-to-lowest by score and the top 5 are returned with a plain-language reason explaining each pick.

---

## 4. Data

- **Catalog size:** 20 songs (10 starter + 10 added)
- **Genres represented:** pop, lofi, rock, electronic, folk, jazz, ambient, synthwave, indie pop, alternative
- **Moods represented:** happy, chill, intense, moody, melancholic, relaxed, focused, energetic
- **Data source:** Fictional songs with manually assigned attributes — no real audio analysis
- **Limitations:** The catalog is tiny. Pop has 3 songs and rock has 2, so genre-match recommendations are immediately thin. Jazz, folk, and ambient have only 1 song each, meaning those users essentially get zero genre-match points for most results. The attributes are made up — real recommenders use audio fingerprinting and machine learning to derive energy and mood from the actual sound.

---

## 5. Strengths

- **Transparent:** Every recommendation includes an exact breakdown of why it was chosen. Users can see exactly which attributes drove the score.
- **Predictable:** The scoring is deterministic — the same profile always produces the same ranking, making it easy to test and debug.
- **Works well for clear profiles:** The "Chill Lofi" and "High-Energy Pop" profiles produced results that closely matched intuition — top picks had both genre and mood matches.
- **Handles multi-attribute nuance:** A pop song with the wrong energy (e.g. "Gym Hero" at 0.93 vs a target of 0.35) correctly scores lower than a lofi song that's closer in energy — the numeric features prevent pure genre matching from dominating completely.

---

## 6. Limitations and Bias

1. **Genre dominance / filter bubble:** Genre is worth 40% of the maximum score. A mediocre song in the right genre will consistently outscore a great song in a slightly different genre. A lofi fan will almost never see a jazz song even if both are equally mellow — this is a classic filter bubble.

2. **Dataset imbalance:** Pop and lofi songs appear most in the catalog. Users who prefer those genres get high-scoring exact matches. A jazz fan gets a maximum genre-match score of only 2 songs — the rest of their top 5 is filled by proximity in energy/acoustic, pulling in folk and ambient songs they may not actually enjoy.

3. **Conflicting preferences produce genre-only winners:** The "Conflicted" profile (high energy + melancholic mood) found no exact mood matches in the catalog. The top result was a genre match with a mismatched mood — the system can't say "I couldn't find what you wanted." It always surfaces *something*.

4. **No diversity mechanism:** If two songs are nearly identical in score, the system just picks whichever comes first in the sorted list. There is no "don't recommend the same artist twice" rule.

5. **Assumes a single fixed user taste:** Real users have different moods at different times. A single static profile can't capture "I want chill music on weekday mornings but intense music at the gym."

---

## 7. Evaluation

**Profiles tested:**

| Profile | Expected top result | Actual top result | Match? |
|---|---|---|---|
| High-Energy Pop Fan | pop + happy + high energy | Sunrise City (pop/happy/0.82) | ✅ Yes |
| Chill Lofi Listener | lofi + chill + low energy | Library Rain (lofi/chill/0.35) | ✅ Yes |
| Deep Intense Rock Fan | rock + intense + high energy | Storm Runner tied Iron Curtain | ✅ Yes |
| Conflicted (alt + melancholic + 0.88 energy) | unclear | Gravity Drop (alt/intense — wrong mood) | ⚠️ Partial |

**Experiment — weight shift (genre 2.0 → 1.0):**
When genre weight was halved, the "Chill Lofi" profile's #3 and #4 picks changed from other lofi songs to "Spacewalk Thoughts" (ambient/chill) — a reasonable cross-genre suggestion. This showed that reducing genre weight increases diversity but makes the genre-match signal weaker.

**Surprise finding:** The "Deep Intense Rock Fan" profile scored identically (4.93) for two songs (Storm Runner and Iron Curtain). The tiebreaker was just list order. A real system would need a secondary ranking rule.

---

## 8. Future Work

1. **Add a diversity rule:** Prevent the same artist or sub-genre from appearing more than once in the top 5. This would make the "rock + intense" profile surface results beyond just Voltline tracks.
2. **Use more features:** Add valence (emotional positivity) and tempo_bpm range matching. A user who likes mid-tempo (90–110 BPM) indie pop should score differently from one who likes fast-tempo pop.
3. **Support hybrid filtering:** Let users "rate" songs (thumbs up/down) and use those votes to adjust weights dynamically — blending content-based scoring with simple collaborative signals.

---

## 9. Personal Reflection

Building VibeFinder made it concrete just how much "simple math" can mimic the feeling of intelligence. When the pop fan's top result was exactly the right song, it felt like the system understood them — but it was just three multiplications and a comparison. That gap between "feels smart" and "is actually smart" is easy to miss as a user.

The most surprising moment was the conflicted profile: high energy + melancholic mood. No song in the catalog had that combination, but the system confidently returned a result anyway with a score of 3.83 — it never says "I don't know." Real AI systems have this same problem at scale: they always produce an answer, which can be misleading when the answer is actually wrong.

Using AI tools during this project sped up boilerplate significantly (CSV loading, dataclass structure), but I had to double-check the scoring logic because an early suggestion returned the same song for every profile — the energy proximity formula was accidentally always returning the maximum. That taught me that AI suggestions for math-heavy logic need careful manual verification, not just a quick glance.

If I extended this project, I would add a "confidence" output: something like "3 of 5 attributes matched — moderate confidence," so the user knows when the recommendation is a strong match vs a best-available fallback.
