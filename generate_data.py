"""
Generate a realistic, intentionally-messy Netflix-style dataset.
Mirrors the shape of the well-known Kaggle 'netflix_titles' dataset so that
all cleaning challenges (nulls, multi-genre strings, mixed duration units,
inconsistent dates) are present for genuine practice.
"""
import numpy as np
import pandas as pd

N_DEFAULT = 3000

# ---- Vocabulary ----
GENRES_POOL = [
    "Dramas", "Comedies", "Documentaries", "International Movies",
    "International TV Shows", "Action & Adventure", "Children & Family Movies",
    "Stand-Up Comedy", "Horror Movies", "Thrillers", "Romantic Movies",
    "Crime TV Shows", "Kids' TV", "Reality TV", "TV Dramas", "TV Comedies",
    "Sci-Fi & Fantasy", "Anime Series", "British TV Shows", "Independent Movies",
    "Music & Musicals", "Sports Movies", "Classic Movies", "Cult Movies",
]
COUNTRIES = [
    "United States", "India", "United Kingdom", "Canada", "France", "Japan",
    "South Korea", "Spain", "Germany", "Mexico", "Australia", "Brazil",
    "Nigeria", "Egypt", "Turkey", None,  # None to inject missing countries
]
COUNTRY_WEIGHTS = np.array(
    [40, 14, 8, 5, 4, 4, 5, 3, 2, 3, 2, 2, 2, 1, 1, 4], dtype=float
)
COUNTRY_WEIGHTS /= COUNTRY_WEIGHTS.sum()

MOVIE_RATINGS = ["G", "PG", "PG-13", "R", "NC-17", "NR", "TV-MA", "TV-14", "TV-PG"]
TV_RATINGS = ["TV-Y", "TV-Y7", "TV-G", "TV-PG", "TV-14", "TV-MA"]

FIRST_NAMES = ["Alex", "Maria", "John", "Priya", "Wei", "Sofia", "Ahmed", "Yuki",
               "Liam", "Olu", "Hana", "Diego", "Emma", "Raj", "Nina", "Tom"]
LAST_NAMES = ["Smith", "Garcia", "Kim", "Patel", "Chen", "Lopez", "Khan", "Tanaka",
              "Brown", "Adeyemi", "Sato", "Silva", "Jones", "Sharma", "Novak", "Lee"]


def _rand_person(rng: np.random.Generator) -> str:
    """Return one random 'First Last' name."""
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def _rand_cast(rng: np.random.Generator) -> str:
    """Return a comma-separated cast list of 2-5 random names."""
    k = rng.integers(2, 6)
    return ", ".join(_rand_person(rng) for _ in range(k))


def _rand_genres(rng: np.random.Generator, is_movie: bool) -> str:
    """Return 1-3 comma-separated genres, matching Netflix's packed-string format."""
    k = rng.integers(1, 4)
    pool = [g for g in GENRES_POOL if ("TV" not in g) == is_movie] or GENRES_POOL
    chosen = rng.choice(pool, size=min(k, len(pool)), replace=False)
    return ", ".join(chosen)


def generate_titles(n: int = N_DEFAULT, seed: int = 42) -> pd.DataFrame:
    """Build a synthetic Netflix-titles dataset shaped like the real Kaggle one.

    Injects the same cleaning challenges as the real dataset: mixed
    date_added formats, mixed duration units (minutes vs. seasons),
    missing country/rating/director/cast values, and a handful of exact
    duplicate rows appended on top of `n`.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
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

        rating = (rng.choice(MOVIE_RATINGS) if is_movie else rng.choice(TV_RATINGS))
        # Inject a few missing/garbled ratings
        if rng.random() < 0.03:
            rating = None

        country = rng.choice(COUNTRIES, p=COUNTRY_WEIGHTS)

        director = _rand_person(rng) if (is_movie and rng.random() > 0.25) else None
        cast = _rand_cast(rng) if rng.random() > 0.08 else None

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
            "listed_in": _rand_genres(rng, is_movie),
            "description": "A sample description for demonstration purposes.",
        })

    df = pd.DataFrame(rows)

    # Inject a handful of exact duplicate rows (real data has these)
    dupes = df.sample(15, random_state=1)
    df = pd.concat([df, dupes], ignore_index=True)
    return df


if __name__ == "__main__":
    df = generate_titles()
    df.to_csv("data/netflix_titles_Sample.csv", index=False)
    print(f"Rows: {len(df)}")
    print(f"Nulls per column:\n{df.isnull().sum()}")
    print(f"\nSample:\n{df.head(3).to_string()}")
