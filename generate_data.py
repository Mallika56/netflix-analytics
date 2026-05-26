"""
Generate a realistic, intentionally-messy Netflix-style dataset.
Mirrors the shape of the well-known Kaggle 'netflix_titles' dataset so that
all cleaning challenges (nulls, multi-genre strings, mixed duration units,
inconsistent dates) are present for genuine practice.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N = 3000  # number of titles

# ---- Vocabulary ----
genres_pool = [
    "Dramas", "Comedies", "Documentaries", "International Movies",
    "International TV Shows", "Action & Adventure", "Children & Family Movies",
    "Stand-Up Comedy", "Horror Movies", "Thrillers", "Romantic Movies",
    "Crime TV Shows", "Kids' TV", "Reality TV", "TV Dramas", "TV Comedies",
    "Sci-Fi & Fantasy", "Anime Series", "British TV Shows", "Independent Movies",
    "Music & Musicals", "Sports Movies", "Classic Movies", "Cult Movies",
]
countries = [
    "United States", "India", "United Kingdom", "Canada", "France", "Japan",
    "South Korea", "Spain", "Germany", "Mexico", "Australia", "Brazil",
    "Nigeria", "Egypt", "Turkey", None,  # None to inject missing countries
]
country_weights = np.array(
    [40, 14, 8, 5, 4, 4, 5, 3, 2, 3, 2, 2, 2, 1, 1, 4], dtype=float
)
country_weights /= country_weights.sum()

movie_ratings = ["G", "PG", "PG-13", "R", "NC-17", "NR", "TV-MA", "TV-14", "TV-PG"]
tv_ratings = ["TV-Y", "TV-Y7", "TV-G", "TV-PG", "TV-14", "TV-MA"]

first_names = ["Alex", "Maria", "John", "Priya", "Wei", "Sofia", "Ahmed", "Yuki",
               "Liam", "Olu", "Hana", "Diego", "Emma", "Raj", "Nina", "Tom"]
last_names = ["Smith", "Garcia", "Kim", "Patel", "Chen", "Lopez", "Khan", "Tanaka",
              "Brown", "Adeyemi", "Sato", "Silva", "Jones", "Sharma", "Novak", "Lee"]

def rand_person():
    return f"{rng.choice(first_names)} {rng.choice(last_names)}"

def rand_cast():
    k = rng.integers(2, 6)
    return ", ".join(rand_person() for _ in range(k))

def rand_genres(is_movie):
    # Netflix packs 1-3 genres into one comma-separated string
    k = rng.integers(1, 4)
    pool = [g for g in genres_pool if ("TV" not in g) == is_movie] or genres_pool
    chosen = rng.choice(pool, size=min(k, len(pool)), replace=False)
    return ", ".join(chosen)

rows = []
for i in range(N):
    is_movie = rng.random() < 0.68  # Netflix skews toward movies in raw counts
    ttype = "Movie" if is_movie else "TV Show"

    release_year = int(rng.integers(1945, 2022))
    # date_added is usually >= release_year; Netflix added most content 2015-2021
    add_year = int(np.clip(release_year + rng.integers(0, 8), 2008, 2021))
    add_month = int(rng.integers(1, 13))
    add_day = int(rng.integers(1, 28))

    # Inject DATE MESSINESS: mixed formats + some missing
    r = rng.random()
    if r < 0.06:
        date_added = None
    elif r < 0.5:
        # "September 9, 2019" style (the real dataset's dominant format)
        date_added = pd.Timestamp(add_year, add_month, add_day).strftime("%B %d, %Y")
    elif r < 0.8:
        date_added = f"{add_year}-{add_month:02d}-{add_day:02d}"  # ISO
    else:
        date_added = f"{add_month}/{add_day}/{add_year}"  # US slash

    # Duration: minutes for movies, "N Seasons" for shows (mixed unit messiness)
    if is_movie:
        duration = f"{int(rng.integers(40, 200))} min"
    else:
        s = int(rng.integers(1, 11))
        duration = f"{s} Season" + ("s" if s > 1 else "")

    rating = (rng.choice(movie_ratings) if is_movie else rng.choice(tv_ratings))
    # Inject a few missing/garbled ratings
    if rng.random() < 0.03:
        rating = None

    country = rng.choice(countries, p=country_weights)

    director = rand_person() if (is_movie and rng.random() > 0.25) else None
    cast = rand_cast() if rng.random() > 0.08 else None

    rows.append({
        "show_id": f"s{i+1}",
        "type": ttype,
        "title": f"Sample Title {i+1}",
        "director": director,
        "cast": cast,
        "country": country,
        "date_added": date_added,
        "release_year": release_year,
        "rating": rating,
        "duration": duration,
        "listed_in": rand_genres(is_movie),
        "description": "A sample description for demonstration purposes.",
    })

df = pd.DataFrame(rows)

# Inject a handful of exact duplicate rows (real data has these)
dupes = df.sample(15, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

df.to_csv("/home/claude/netflix_titles.csv", index=False)
print(f"Rows: {len(df)}")
print(f"Nulls per column:\n{df.isnull().sum()}")
print(f"\nSample:\n{df.head(3).to_string()}")
