-- Visualiation 1: Scatter Plot of the relationship between proportion of black residents in a district and the number of complaints per capita

-- Custom SQL query 1: Creates a query that shows the proportion of black residents per police district
SELECT CAST(black AS float) / CAST(total AS float) AS proportion_black, a.area_id
FROM (
      -- The total population per district
      SELECT SUM(count) AS total, area_id
      FROM data_racepopulation
      GROUP BY area_id
      ) tp
JOIN (
      -- The total black population per district
      SELECT count AS black, area_id
      FROM data_racepopulation
      WHERE race = 'Black'
      ) tb ON tp.area_id = tb.area_id
WHERE a.area_id >= 1527
ORDER BY a.area_id

-- Custom SQL Query 2: Creates a query that shows the number of allegations per 100,000 residents per police district
SELECT (CAST(apa.num_allegations AS float) / CAST(total_pop AS float)) * 100000 AS allegations_per_capita, pd_id
FROM (
      -- Finds what area each allegation belongs to by finding which police district contains the point associated with the allegation
      SELECT COUNT(da.crid) AS num_allegations, pd.id AS pd_id
      FROM data_allegation da
      JOIN (
            SELECT id, polygon
            FROM data_area
            WHERE area_type = 'police-districts'
            ) pd
      ON st_contains (pd.polygon, da.point)
      GROUP BY pd.id) apa
JOIN (
      -- Total population per district
      SELECT SUM(count) as total_pop, area_id
      FROM data_racepopulation
      WHERE area_id > 1500
      GROUP BY area_id
      ) tp
ON tp.area_id = apa.pd_id
ORDER BY pd_id


-- Visualization 2: Grouped histogram showing breakdown of proportion of complaints submitted by black vs non-black residents for each type of complaint
SELECT
       da.allegation_name, black, white, hispanic,
       (black + white + hispanic) as total_allegations,
       COALESCE(black / NULLIF(CAST((black + white + hispanic) as float), 0),0) as black_proportion,
       COALESCE(white / NULLIF(CAST((black + white + hispanic) as float), 0),0) as white_proportion,
       COALESCE(hispanic / NULLIF(CAST((black + white + hispanic) as float), 0),0) as hispanic_proportion
FROM
    (SELECT most_common_category_id,
        SUM(case when race = 'Black' then 1 else 0 end) black,
        SUM(case when race = 'White' then 1 else 0 end) white,
        SUM(case when race = 'Hispanic' then 1 else 0 end) hispanic
    FROM data_allegation da
        JOIN data_complainant dc on da.crid = dc.allegation_id
    group by most_common_category_id) allegations_abr_race
JOIN data_allegationcategory da on most_common_category_id = da.id
GROUP BY da.allegation_name, black, white, hispanic;
