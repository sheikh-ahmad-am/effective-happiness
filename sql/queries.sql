-- =====================================================================
-- World Happiness Analytics — SQL verification queries (MySQL 8 compatible)
-- Dataset: data/happiness.csv (159 countries x 6 years, 2019-2024)
-- Table: happiness(country, region, year, ladder_score, log_gdp_per_capita,
--                   social_support, healthy_life_expectancy, freedom,
--                   generosity, corruption_perception)
-- Every query below is a SELECT that reproduces a headline number from
-- the README "Results" section (real run 2026-10-01).
-- =====================================================================

-- SETUP (run once in MySQL Workbench; then run the queries below):
--   1. CREATE DATABASE IF NOT EXISTS happiness_analytics;
--      USE happiness_analytics;
--   2. CREATE TABLE happiness (
--          country VARCHAR(60),
--          region VARCHAR(40),
--          year INT,
--          ladder_score DECIMAL(5,3),
--          log_gdp_per_capita DECIMAL(6,3),
--          social_support DECIMAL(5,3),
--          healthy_life_expectancy DECIMAL(5,1),
--          freedom DECIMAL(5,3),
--          generosity DECIMAL(5,3),
--          corruption_perception DECIMAL(5,3)
--      );
--   3. LOAD DATA INFILE '/path/to/happiness.csv'
--      INTO TABLE happiness
--      FIELDS TERMINATED BY ',' IGNORE 1 LINES;

-- ---------------------------------------------------------------------
-- Q1. Global average ladder score, latest year.
-- What it answers: the world's average happiness score in 2024.
-- README link: headline global average 5.318 across 159 countries.
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS countries,
       ROUND(AVG(ladder_score), 3) AS global_avg_ladder_2024
FROM happiness
WHERE year = 2024;

-- ---------------------------------------------------------------------
-- Q2. Top 10 happiest countries, latest year.
-- What it answers: which countries top the happiness ranking.
-- README link: Finland 7.854 first, Belgium 7.850 second.
-- ---------------------------------------------------------------------
SELECT country, region, ladder_score
FROM happiness
WHERE year = 2024
ORDER BY ladder_score DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- Q3. Bottom 5 countries, latest year.
-- What it answers: which countries sit at the bottom of the ranking.
-- README link: Afghanistan 2.294 last, South Sudan 2.930 second-last.
-- ---------------------------------------------------------------------
SELECT country, region, ladder_score
FROM happiness
WHERE year = 2024
ORDER BY ladder_score ASC
LIMIT 5;

-- ---------------------------------------------------------------------
-- Q4. Average ladder score by region, latest year.
-- What it answers: which world regions are happiest.
-- README link: Western Europe 7.037 (best), Sub-Saharan Africa 4.175 (worst).
-- ---------------------------------------------------------------------
SELECT region,
       COUNT(*) AS countries,
       ROUND(AVG(ladder_score), 3) AS avg_ladder
FROM happiness
WHERE year = 2024
GROUP BY region
ORDER BY avg_ladder DESC;

-- ---------------------------------------------------------------------
-- Q5. Average ladder by GDP quartile, latest year (MySQL 8 NTILE).
-- What it answers: does national wealth track happiness.
-- README link: Q1 (poorest) 4.035 -> Q4 (richest) 6.604.
-- ---------------------------------------------------------------------
SELECT gdp_quartile,
       COUNT(*) AS countries,
       ROUND(AVG(ladder_score), 3) AS avg_ladder
FROM (
    SELECT ladder_score,
           NTILE(4) OVER (ORDER BY log_gdp_per_capita) AS gdp_quartile
    FROM happiness
    WHERE year = 2024
) q
GROUP BY gdp_quartile
ORDER BY gdp_quartile;

-- ---------------------------------------------------------------------
-- Q6. Biggest climber and faller, 2019 -> 2024.
-- What it answers: which countries moved most over the six-year panel.
-- README link: Serbia +0.909 (climber), Cyprus -0.961 (faller).
-- (Run once with DESC for the climber, once with ASC for the faller.)
-- ---------------------------------------------------------------------
SELECT country,
       region,
       ROUND(MAX(CASE WHEN year = 2024 THEN ladder_score END)
           - MAX(CASE WHEN year = 2019 THEN ladder_score END), 3)
           AS ladder_change_2019_2024
FROM happiness
GROUP BY country, region
ORDER BY ladder_change_2019_2024 DESC
LIMIT 1;

-- ---------------------------------------------------------------------
-- Q7. Year-over-year global happiness trend.
-- What it answers: is the world getting happier.
-- README link: 2019 5.285 -> 2024 5.318 (nearly flat, +0.033).
-- ---------------------------------------------------------------------
SELECT year,
       ROUND(AVG(ladder_score), 3) AS global_avg_ladder
FROM happiness
GROUP BY year
ORDER BY year;
