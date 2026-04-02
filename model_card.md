# Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder takes a user's taste profile (favorite genre, mood, target energy, acoustic preference) and returns the top 5 most relevant songs from a catalog, ranked by a weighted score. It tries to answer: *"Given what this user told me they like, which songs in my catalog are the closest match?"*

It does **not** try to predict what a user will like in the future, learn from behavior, or discover hidden patterns. It is a lookup system with math, not a learning system.

---

## 3. Intended Use and Non-Intended Use

**Designed for:** classroom exploration to demonstrate how content-based filtering works, how features become scores, and where bias shows up in simple recommendation logic.

**Not intended for:** replacing real music platforms, making decisions that affect users' listening habits at scale, commercial deployment, or any context where diversity and fairness of recommendations matter beyond a demonstration.

---

## 4. How the Model Works (Algorithm Summary)

Every song in the catalog has measurable attributes: genre (e.g. "pop", "lofi"), mood (e.g. "happy", "intense"), energy (a number from 0 to 1 representing how "loud and active" the song feels), and acousticness (how "unplugged" it sounds).

The user provides a taste profile: their favorite genre, favorite mood, a target energy level, and whether they prefer acoustic music.

The model compares **each song** to the user's profile and awards points:

- 2 points if the song's genre matches the user's favorite
- 1 point if the mood matches
- Up to 1.5 points based on how close the song's energy is to the user's target (closer = more points)
- Up to 0.5 points based on acoustic preference

Songs are then sorted highest-to-lowest by score and the top 5 are returned with a plain-language reason explaining each pick.

---

## 5. Data Used

- **Catalog size:** 20 songs (10 starter + 10 added)
- **Genres represented:** pop, lofi, rock, electronic, folk, jazz, ambient, synthwave, indie pop, alternative
- **Moods represented:** happy, chill, intense, moody, melancholic, relaxed, focused, energetic
- **Data source:** Fictional songs with manually assigned attributes — no real audio analysis
- **Limitations:** The catalog is tiny. Pop has 3 songs and rock has 2, so genre-match recommendations are immediately thin. Jazz, folk, and ambient have only 1 song each, meaning those users essentially get zero genre-match points for most results. The attributes are made up — real recommenders use audio fingerprinting and machine learning to derive energy and mood from the actual sound.

---

## 6. Strengths

- **Transparent:** Every recommendation includes an exact breakdown of why it was chosen. Users can see exactly which attributes drove the score.
- **Predictable:** The scoring is deterministic — the same profile always produces the same ranking, making it easy to test and debug.
- **Works well for clear profiles:** The "Chill Lofi" and "High-Energy Pop" profiles produced results that closely matched intuition — top picks had both genre and mood matches.
- **Handles multi-attribute nuance:** A pop song with the wrong energy (e.g. "Gym Hero" at 0.93 vs a target of 0.35) correctly scores lower than a lofi song that's closer in energy — the numeric features prevent pure genre matching from dominating completely.

---

## 7. Observed Behavior / Biases

1. **Genre dominance / filter bubble:** Genre is worth 40% of the maximum score. A mediocre song in the right genre will consistently outscore a great song in a slightly different genre. A lofi fan will almost never see a jazz song even if both are equally mellow — this is a classic filter bubble.

2. **Dataset imbalance:** Pop and lofi songs appear most in the catalog. Users who prefer those genres get high-scoring exact matches. A jazz fan gets a maximum genre-match score of only 2 songs — the rest of their top 5 is filled by proximity in energy/acoustic, pulling in folk and ambient songs they may not actually enjoy.

3. **Conflicting preferences produce genre-only winners:** The "Conflicted" profile (high energy + melancholic mood) found no exact mood matches in the catalog. The top result was a genre match with a mismatched mood — the system can't say "I couldn't find what you wanted." It always surfaces *something*.

4. **No diversity mechanism:** If two songs are nearly identical in score, the system just picks whichever comes first in the sorted list. There is no "don't recommend the same artist twice" rule.

5. **Assumes a single fixed user taste:** Real users have different moods at different times. A single static profile can't capture "I want chill music on weekday mornings but intense music at the gym."

---

## 8. Evaluation Process

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

## 9. Ideas for Improvement

1. **Add a diversity rule:** Prevent the same artist or sub-genre from appearing more than once in the top 5. This would make the "rock + intense" profile surface results beyond just Voltline tracks.
2. **Use more features:** Add valence (emotional positivity) and tempo_bpm range matching. A user who likes mid-tempo (90–110 BPM) indie pop should score differently from one who likes fast-tempo pop.
3. **Support hybrid filtering:** Let users "rate" songs (thumbs up/down) and use those votes to adjust weights dynamically — blending content-based scoring with simple collaborative signals.

---

## 10. Personal Reflection

**Biggest learning moment:** The weight-shift experiment. I expected halving the genre weight to produce more diverse results — but the top 5 songs were identical. The scores got closer together, but the ranking didn't change. That told me something more important than what I was testing: data gaps limit diversity more than algorithm design does. No weight configuration can recommend diverse rock songs when the catalog only has two rock songs. I had been thinking of bias as a scoring problem, but it's really a data problem first.

**How AI tools helped — and when I had to verify them:** AI was fast for boilerplate (CSV loading, dataclass definitions, tabulate formatting). But when I asked for help with the energy proximity formula, the first version it suggested used `song.energy > user.energy` as a threshold instead of `abs(user.energy - song.energy)` as a proximity measure — that would reward high-energy songs for high-energy users, not *similar-energy* songs. That's a fundamentally wrong approach that passes a quick glance but produces bad results. I caught it because I ran the system and the same song ranked first for every profile. The lesson: always test AI-generated math by asking "does the output match my intuition?"

**What surprised me about simple algorithms feeling like real recommendations:** When the pop fan got Sunrise City at #1 and Ocean Drive at #2, it genuinely felt like the system *knew* them. It didn't. It did three multiplications and two string comparisons. What makes it feel intelligent is that the features (genre, mood, energy) were chosen to match how humans actually describe music. The math isn't smart — the feature selection is. Real AI systems are the same: the model architecture matters less than whether the input data captures what humans actually care about.

**What I'd try next:** Add a match-quality signal — something like "strong match (4 of 4 features matched)" vs "best available (1 of 4 features matched)" — so the user knows whether to trust the recommendation. The system currently returns 5 results with equal confidence whether it found perfect matches or near-total misses. That gap between a 4.93 and a 1.91 score is informative, but only if the user knows what those numbers mean.
