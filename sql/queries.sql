-- Netflix Content Analytics — SQL queries
-- Run via DuckDB against the cleaned `df` (title-level) and `df_genres` (exploded) frames.
-- Q1-Q3 are worked examples; add Q4-Q9 here as you write them in the notebook.

-- Q1: Movies vs. TV Shows
SELECT type, COUNT(*) AS title_count
FROM df
GROUP BY type
ORDER BY title_count DESC;

-- Q2: Top 10 genres overall
SELECT genre, COUNT(*) AS title_count
FROM df_genres
GROUP BY genre
ORDER BY title_count DESC
LIMIT 10;

-- Q3: Genre trend over time (selected genres)
SELECT year_added, genre, COUNT(*) AS titles
FROM df_genres
WHERE genre IN ('Dramas', 'Comedies', 'Documentaries')
  AND year_added IS NOT NULL
GROUP BY year_added, genre
ORDER BY year_added, genre;

-- Q8 (reference): top genre per year via window function
WITH yearly AS (
    SELECT year_added, genre, COUNT(*) AS n
    FROM df_genres
    WHERE year_added IS NOT NULL
    GROUP BY year_added, genre
)
SELECT year_added, genre, n
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY year_added ORDER BY n DESC) AS rk
    FROM yearly
)
WHERE rk = 1
ORDER BY year_added;
