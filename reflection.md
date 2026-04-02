# Reflection: Profile Comparisons

This file compares what happened when I ran VibeFinder 1.0 against four different user profiles and explains *why* the outputs make sense (or don't).

---

## High-Energy Pop Fan vs. Chill Lofi Listener

**Pop Fan prefs:** genre=pop, mood=happy, energy=0.85, likes_acoustic=False  
**Lofi Fan prefs:** genre=lofi, mood=chill, energy=0.35, likes_acoustic=True

**What changed:** Every single song in the top 5 was different. The pop fan got Sunrise City and Ocean Drive; the lofi fan got Library Rain and Midnight Coding. The two profiles share zero overlap in their top results.

**Why it makes sense:** Genre and energy are pulling in completely opposite directions. Pop fan has high energy (0.85) and hates acoustic sound; lofi fan has low energy (0.35) and loves acoustic sound. These are the two biggest scoring factors after genre, so they naturally sort the catalog into two completely separate clusters. This is the system working correctly — it's genuinely capturing the difference between "I want a banger" and "I want something quiet to study to."

**Interesting observation:** The lofi fan's #5 pick was Spacewalk Thoughts (ambient/chill), not a lofi song. This happened because we ran out of chill lofi tracks and the system fell back to the nearest energy+mood match. It's a good example of graceful degradation when the catalog is too small.

---

## Chill Lofi Listener vs. Deep Intense Rock Fan

**Lofi Fan prefs:** genre=lofi, mood=chill, energy=0.35, likes_acoustic=True  
**Rock Fan prefs:** genre=rock, mood=intense, energy=0.90, likes_acoustic=False

**What changed:** Again, completely different top 5s. Rock fan got Storm Runner and Iron Curtain (both rock/intense); lofi fan got Library Rain and Midnight Coding.

**Why it makes sense:** These two profiles are about as far apart as possible on every axis — genre, mood, energy (0.35 vs 0.90), and acoustic preference (True vs False). The system correctly treats them as polar opposites. If you imagine a 2D map with "energy" on one axis and "acoustic" on the other, these two users are in opposite corners. The scoring logic amplifies that distance into very different recommendation lists.

**Interesting observation:** The rock fan's #3, #4, and #5 picks are all from other genres (pop, electronic, alternative) because the catalog only has 2 rock songs. Once those two are used up, mood becomes the next strongest signal — and all three fallback songs share the "intense" mood. This shows how genre scarcity in a small dataset forces the system to lean harder on secondary features.

---

## Deep Intense Rock Fan vs. Conflicted Profile (high energy + melancholic)

**Rock Fan prefs:** genre=rock, mood=intense, energy=0.90, likes_acoustic=False  
**Conflicted prefs:** genre=alternative, mood=melancholic, energy=0.88, likes_acoustic=False

**What changed:** The top 2 results swapped. Rock fan: Storm Runner + Iron Curtain. Conflicted: Gravity Drop + Broken Signal. From #3 onward both profiles pull from the same high-energy non-acoustic pool (Iron Curtain, Neon Jungle, Storm Runner), but in different order.

**Why it makes sense:** The two profiles have nearly identical energy preferences (0.88 vs 0.90), so energy proximity points are almost the same for every song. The difference is entirely in genre and mood. Rock fan gets 2 exact genre matches and 2 mood matches right away; the conflicted profile gets 2 genre matches but zero mood matches (no "melancholic + high energy" songs exist in the catalog). The conflicted profile scores lower overall because the mood match point is never awarded.

**Why it's a problem:** The conflicted user is not actually served well. Their top result is Gravity Drop (alternative/intense) — wrong mood. The system gave them the genre they asked for but couldn't honor the mood. A real recommendation system should say "we couldn't find a perfect match" rather than silently substituting. This is a significant limitation of always returning k results regardless of match quality.

---

## High-Energy Pop Fan vs. Conflicted Profile

**Pop Fan prefs:** genre=pop, mood=happy, energy=0.85, likes_acoustic=False  
**Conflicted prefs:** genre=alternative, mood=melancholic, energy=0.88, likes_acoustic=False

**What changed:** The pop fan got two strong full-matches (genre + mood + energy). The conflicted profile got only genre matches with no mood matches at all.

**Why it makes sense:** "Pop + happy" is well-represented in the catalog (3 songs). "Alternative + melancholic + high energy" has zero exact matches. The pop fan's score ceiling is 5.0; the conflicted user's realistic ceiling is about 4.0 (genre match + energy proximity + acoustic, but never the mood point). This shows that the system is biased toward users whose preferences align with the most common genres in the catalog — a real fairness concern if this were a production app.

**Takeaway for real systems:** When you build a dataset, the genres and moods you include determine whose tastes the system can serve well. A catalog that skews toward pop will always over-serve pop fans. This is how real-world recommendation systems can unintentionally reinforce mainstream tastes and under-serve listeners with niche preferences.
