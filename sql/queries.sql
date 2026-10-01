-- =====================================================================
-- World Happiness Analytics — SQL verification queries (MySQL 8 compatible)
-- Dataset: data/happiness.csv — REAL World Happiness Report data,
--          2015-2025 (1,657 rows, 197 countries, 10 regions), refreshed
--          automatically by data/pull_data.py whenever new data lands.
-- Table: happiness(country, region, year, ladder_score, gdp,
--                   social_support, health, freedom, generosity, trust)
--   gdp / social_support / health / freedom / generosity / trust are the
--   WHR explanatory components (modelled contribution to the ladder);
--   trust = Trust (Government Corruption): higher = cleaner institutions.
-- Every query below is a SELECT that reproduces a headline number from
-- the README "Results" section (real run 2026-10-01).
-- Queries use MAX(year) / MIN(year) so they keep working as new yearly
-- data is pulled in — no hardcoded years to update.
-- =====================================================================

-- SETUP (run once in MySQL Workbench; then run the queries below):
--   1. CREATE DATABASE IF NOT EXISTS happiness_analytics;
--      USE happiness_analytics;
--   2. CREATE TABLE happiness (
--          country VARCHAR(60),
--          region VARCHAR(50),
--          year INT,
--          ladder_score DECIMAL(5,3),
--          gdp DECIMAL(5,3),
--          social_support DECIMAL(5,3),
--          health DECIMAL(5,3),
--          freedom DECIMAL(5,3),
--          generosity DECIMAL(5,3),
--          trust DECIMAL(5,3)
--      );
--   3. LOAD DATA INFILE '/path/to/happiness.csv'
--      INTO TABLE happiness
--      FIELDS TERMINATED BY ',' IGNORE 1 LINES;

-- ---------------------------------------------------------------------
-- Q1. Global average ladder score, latest year.
-- What it answers: the world's average happiness score right now.
-- README link: headline global average 5.578 across 147 countries (2025).
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS countries,
       ROUND(AVG(ladder_score), 3) AS global_avg_ladder
FROM happiness
WHERE year = (SELECT MAX(year) FROM happiness);

-- ---------------------------------------------------------------------
-- Q2. Top 10 happiest countries, latest year.
-- What it answers: which countries top the happiness ranking.
-- README link: Finland 7.736 first, Denmark 7.521 second (2025).
-- ---------------------------------------------------------------------
SELECT country, region, ladder_score
FROM happiness
WHERE year = (SELECT MAX(year) FROM happiness)
ORDER BY ladder_score DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- Q3. Bottom 5 countries, latest year.
-- What it answers: which countries sit at the bottom of the ranking.
-- README link: Afghanistan 1.364 last, Sierra Leone 2.998 second-last.
-- ---------------------------------------------------------------------
SELECT country, region, ladder_score
FROM happiness
WHERE year = (SELECT MAX(year) FROM happiness)
ORDER BY ladder_score ASC
LIMIT 5;

-- ---------------------------------------------------------------------
-- Q4. Average ladder score by region, latest year.
-- What it answers: which world regions are happiest.
-- README link: Australia and New Zealand 6.963 (best),
--              Southern Asia 3.929 (worst).
-- ---------------------------------------------------------------------
SELECT region,
       COUNT(*) AS countries,
       ROUND(AVG(ladder_score), 3) AS avg_ladder
FROM happiness
WHERE year = (SELECT MAX(year) FROM happiness)
GROUP BY region
ORDER BY avg_ladder DESC;

-- ---------------------------------------------------------------------
-- Q5. Average ladder by GDP-component quartile, latest year (NTILE).
-- What it answers: does national wealth track happiness.
-- README link: Q1 (poorest) 4.365 -> Q4 (richest) 6.757.
-- ---------------------------------------------------------------------
SELECT gdp_quartile,
       COUNT(*) AS countries,
       ROUND(AVG(ladder_score), 3) AS avg_ladder
FROM (
    SELECT ladder_score,
           NTILE(4) OVER (ORDER BY gdp) AS gdp_quartile
    FROM happiness
    WHERE year = (SELECT MAX(year) FROM happiness)
) q
GROUP BY gdp_quartile
ORDER BY gdp_quartile;

-- ---------------------------------------------------------------------
-- Q6. Biggest climber and faller, first -> latest year in the data.
-- What it answers: which countries moved most across the whole panel.
-- README link: Serbia +1.483 (climber), Afghanistan -2.211 (faller),
--              2015 -> 2025.
-- (Run once with DESC for the climber, once with ASC for the faller.)
-- ---------------------------------------------------------------------
SELECT country,
       region,
       ROUND(MAX(CASE WHEN year = (SELECT MAX(year) FROM happiness)
                      THEN ladder_score END)
           - MAX(CASE WHEN year = (SELECT MIN(year) FROM happiness)
                      THEN ladder_score END), 3)
           AS ladder_change
FROM happiness
GROUP BY country, region
HAVING MAX(CASE WHEN year = (SELECT MAX(year) FROM happiness)
                THEN ladder_score END) IS NOT NULL
   AND MAX(CASE WHEN year = (SELECT MIN(year) FROM happiness)
                THEN ladder_score END) IS NOT NULL
ORDER BY ladder_change DESC
LIMIT 1;

-- ---------------------------------------------------------------------
-- Q7. Year-over-year global happiness trend.
-- What it answers: is the world getting happier.
-- README link: 2015 5.376 -> 2025 5.578 (slowly up, +0.202).
-- ---------------------------------------------------------------------
SELECT year,
       ROUND(AVG(ladder_score), 3) AS global_avg_ladder
FROM happiness
GROUP BY year
ORDER BY year;
