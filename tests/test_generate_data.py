import pandas as pd
import pytest

from generate_data import GENRES_POOL, generate_titles


EXPECTED_COLUMNS = {
    "show_id", "type", "title", "director", "cast", "country", "date_added",
    "release_year", "rating", "duration", "listed_in", "description",
}


@pytest.fixture()
def small_df() -> pd.DataFrame:
    return generate_titles(n=300, seed=42)


def test_has_expected_columns(small_df):
    assert EXPECTED_COLUMNS.issubset(small_df.columns)


def test_row_count_includes_injected_duplicates(small_df):
    # generate_titles(n=300, ...) appends 15 duplicate rows on top of n.
    assert len(small_df) == 315


def test_type_is_movie_or_tv_show(small_df):
    assert set(small_df["type"].unique()) <= {"Movie", "TV Show"}


def test_duration_unit_matches_type(small_df):
    movies = small_df[small_df["type"] == "Movie"]
    shows = small_df[small_df["type"] == "TV Show"]
    assert movies["duration"].str.endswith("min").all()
    assert shows["duration"].str.contains(r"^\d+ Seasons?$", regex=True).all()


def test_genres_are_from_the_known_pool(small_df):
    seen = {g.strip() for row in small_df["listed_in"] for g in row.split(",")}
    assert seen.issubset(set(GENRES_POOL))


def test_messiness_is_injected(small_df):
    # Nulls (country/director/cast/rating) and duplicate rows are both
    # deliberately injected -- the dataset should show each kind.
    assert small_df.isnull().any().any()
    assert small_df.duplicated().any()


def test_generation_is_deterministic_for_a_given_seed():
    first = generate_titles(n=100, seed=42)
    second = generate_titles(n=100, seed=42)
    pd.testing.assert_frame_equal(first, second)


def test_different_seeds_produce_different_data():
    first = generate_titles(n=100, seed=1)
    second = generate_titles(n=100, seed=2)
    assert not first["listed_in"].equals(second["listed_in"])
