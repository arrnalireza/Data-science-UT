-- ============================================================
-- File: 3_load.sql
-- Purpose:
--   Loads and transforms data from the staging table into the
--   normalized relational schema.
--
-- Description:
--   This script inserts distinct cities, locations, restaurants,
--   listing types, cuisines, and restaurant types. It also populates
--   the many-to-many mapping tables.
--
-- Data Cleaning Notes:
--   - rate is converted from text to DECIMAL where possible.
--   - approx_cost_for_two is cleaned and converted to DECIMAL.
--   - duplicate values are handled using DISTINCT and INSERT IGNORE.
--   - many-to-many fields such as cuisines and restaurant types are
--     split into separate mapping tables.
--
-- Run Order:
--   Run this file after loading the CSV data into csv_file.
--
-- Important:
--   If LOAD DATA INFILE is used, update the CSV file path according
--   to the local machine before running.
-- ============================================================

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/zomato.csv'
INTO TABLE csv_file
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(url, address, name, online_order, book_table, rate, votes, phone,
 location, rest_type, dish_liked, cuisines, approx_cost_for_two,
 reviews_list, menu_item, listed_in_type, listed_in_city);


INSERT INTO cities (city_name)
SELECT DISTINCT TRIM(listed_in_city)
FROM csv_file
WHERE listed_in_city IS NOT NULL
  AND TRIM(listed_in_city) <> '';

INSERT INTO locations (location_name, city_id)
SELECT DISTINCT
    TRIM(c.location) AS location_name,
    ci.city_id
FROM csv_file c
JOIN cities ci
    ON TRIM(c.listed_in_city) = ci.city_name
WHERE c.location IS NOT NULL
  AND TRIM(c.location) <> '';

INSERT INTO restaurants (
    url, name, address, phone, location_id,
    online_order, book_table, rate, votes, approx_cost_for_two,
    dish_liked
)
SELECT
    c.url,
    TRIM(c.name),
    TRIM(c.address),
    TRIM(c.phone),
    l.location_id,
    TRIM(c.online_order),
    TRIM(c.book_table),
    CASE
        WHEN SUBSTRING_INDEX(TRIM(c.rate), '/', 1) REGEXP '^[0-9]+(\\.[0-9]+)?$'
        THEN CAST(SUBSTRING_INDEX(TRIM(c.rate), '/', 1) AS DECIMAL(4,2))
        ELSE NULL
    END AS rate,
    CASE
        WHEN TRIM(c.votes) REGEXP '^[0-9]+$'
        THEN CAST(TRIM(c.votes) AS UNSIGNED)
        ELSE NULL
    END AS votes,
    CASE
        WHEN REPLACE(TRIM(c.approx_cost_for_two), ',', '') REGEXP '^[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(TRIM(c.approx_cost_for_two), ',', '') AS DECIMAL(10,2))
        ELSE NULL
    END AS approx_cost_for_two,
    c.dish_liked
FROM csv_file c
JOIN cities ci
    ON TRIM(c.listed_in_city) = ci.city_name
JOIN locations l
    ON TRIM(c.location) = l.location_name
   AND l.city_id = ci.city_id;


INSERT INTO listing_types (listing_type_name)
SELECT DISTINCT TRIM(listed_in_type)
FROM csv_file
WHERE listed_in_type IS NOT NULL
  AND TRIM(listed_in_type) <> '';

INSERT INTO restaurant_listings (restaurant_id, listing_type_id)
SELECT DISTINCT
    r.restaurant_id,
    lt.listing_type_id
FROM restaurants r
JOIN csv_file c
    ON r.url = c.url
   AND r.name = TRIM(c.name)
JOIN listing_types lt
    ON TRIM(c.listed_in_type) = lt.listing_type_name;


INSERT IGNORE INTO cuisines (cuisine_name)
WITH RECURSIVE split_cuisines AS (
    SELECT
        TRIM(SUBSTRING_INDEX(cuisines, ',', 1)) AS cuisine_name,
        CASE
            WHEN cuisines LIKE '%,%' THEN SUBSTRING(cuisines, LOCATE(',', cuisines) + 1)
            ELSE NULL
        END AS remaining
    FROM csv_file
    WHERE cuisines IS NOT NULL
      AND TRIM(cuisines) <> ''

    UNION ALL

    SELECT
        TRIM(SUBSTRING_INDEX(remaining, ',', 1)) AS cuisine_name,
        CASE
            WHEN remaining LIKE '%,%' THEN SUBSTRING(remaining, LOCATE(',', remaining) + 1)
            ELSE NULL
        END AS remaining
    FROM split_cuisines
    WHERE remaining IS NOT NULL
      AND TRIM(remaining) <> ''
)
SELECT DISTINCT cuisine_name
FROM split_cuisines
WHERE cuisine_name IS NOT NULL
  AND cuisine_name <> '';

CREATE INDEX idx_cuisines_name 
ON cuisines (cuisine_name);

CREATE INDEX idx_restaurants_url_name 
ON restaurants (url(255), name(255));

DROP TABLE IF EXISTS temp_split_cuisines;

CREATE TABLE temp_split_cuisines (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    url TEXT,
    restaurant_name VARCHAR(500),
    cuisine_name VARCHAR(255)
) ENGINE = InnoDB;


INSERT INTO temp_split_cuisines (url, restaurant_name, cuisine_name)
WITH RECURSIVE split_cuisines AS (
    SELECT
        c.url,
        TRIM(c.name) AS restaurant_name,
        TRIM(SUBSTRING_INDEX(c.cuisines, ',', 1)) AS cuisine_name,
        CASE
            WHEN c.cuisines LIKE '%,%' 
                THEN SUBSTRING(c.cuisines, LOCATE(',', c.cuisines) + 1)
            ELSE NULL
        END AS remaining
    FROM csv_file c
    WHERE c.cuisines IS NOT NULL
      AND TRIM(c.cuisines) <> ''

    UNION ALL

    SELECT
        url,
        restaurant_name,
        TRIM(SUBSTRING_INDEX(remaining, ',', 1)) AS cuisine_name,
        CASE
            WHEN remaining LIKE '%,%' 
                THEN SUBSTRING(remaining, LOCATE(',', remaining) + 1)
            ELSE NULL
        END AS remaining
    FROM split_cuisines
    WHERE remaining IS NOT NULL
      AND TRIM(remaining) <> ''
)
SELECT DISTINCT
    url,
    restaurant_name,
    cuisine_name
FROM split_cuisines
WHERE cuisine_name IS NOT NULL
  AND cuisine_name <> '';


DROP PROCEDURE IF EXISTS load_restaurant_cuisines_batches;

DELIMITER //

CREATE PROCEDURE load_restaurant_cuisines_batches()
BEGIN
    DECLARE v_start BIGINT DEFAULT 1;
    DECLARE v_max BIGINT DEFAULT 0;
    DECLARE v_step BIGINT DEFAULT 20000;

    SELECT COALESCE(MAX(id), 0)
    INTO v_max
    FROM temp_split_cuisines;

    WHILE v_start <= v_max DO

        INSERT IGNORE INTO restaurant_cuisines (restaurant_id, cuisine_id)
        SELECT DISTINCT
            r.restaurant_id,
            cu.cuisine_id
        FROM temp_split_cuisines sc
        JOIN restaurants r
            ON r.url = sc.url
           AND r.name = sc.restaurant_name
        JOIN cuisines cu
            ON cu.cuisine_name = sc.cuisine_name
        WHERE sc.id >= v_start
          AND sc.id < v_start + v_step;

        SET v_start = v_start + v_step;

    END WHILE;
END //

DELIMITER ;
CALL load_restaurant_cuisines_batches();


INSERT IGNORE INTO restaurant_types (restaurant_type_name)
WITH RECURSIVE split_types AS (
    SELECT
        TRIM(SUBSTRING_INDEX(rest_type, ',', 1)) AS restaurant_type_name,
        CASE
            WHEN rest_type LIKE '%,%' 
                THEN SUBSTRING(rest_type, LOCATE(',', rest_type) + 1)
            ELSE NULL
        END AS remaining
    FROM csv_file
    WHERE rest_type IS NOT NULL
      AND TRIM(rest_type) <> ''

    UNION ALL

    SELECT
        TRIM(SUBSTRING_INDEX(remaining, ',', 1)) AS restaurant_type_name,
        CASE
            WHEN remaining LIKE '%,%' 
                THEN SUBSTRING(remaining, LOCATE(',', remaining) + 1)
            ELSE NULL
        END AS remaining
    FROM split_types
    WHERE remaining IS NOT NULL
      AND TRIM(remaining) <> ''
)
SELECT DISTINCT restaurant_type_name
FROM split_types
WHERE restaurant_type_name IS NOT NULL
  AND restaurant_type_name <> '';
  
  CREATE INDEX idx_restaurant_types_name
ON restaurant_types (restaurant_type_name);

DROP TABLE IF EXISTS temp_split_types;

CREATE TABLE temp_split_types (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    url TEXT,
    restaurant_name VARCHAR(500),
    restaurant_type_name VARCHAR(100)
) ENGINE = InnoDB;

INSERT INTO temp_split_types (url, restaurant_name, restaurant_type_name)
WITH RECURSIVE split_types AS (
    SELECT
        c.url,
        TRIM(c.name) AS restaurant_name,
        TRIM(SUBSTRING_INDEX(c.rest_type, ',', 1)) AS restaurant_type_name,
        CASE
            WHEN c.rest_type LIKE '%,%' 
                THEN SUBSTRING(c.rest_type, LOCATE(',', c.rest_type) + 1)
            ELSE NULL
        END AS remaining
    FROM csv_file c
    WHERE c.rest_type IS NOT NULL
      AND TRIM(c.rest_type) <> ''

    UNION ALL

    SELECT
        url,
        restaurant_name,
        TRIM(SUBSTRING_INDEX(remaining, ',', 1)) AS restaurant_type_name,
        CASE
            WHEN remaining LIKE '%,%' 
                THEN SUBSTRING(remaining, LOCATE(',', remaining) + 1)
            ELSE NULL
        END AS remaining
    FROM split_types
    WHERE remaining IS NOT NULL
      AND TRIM(remaining) <> ''
)
SELECT DISTINCT
    url,
    restaurant_name,
    restaurant_type_name
FROM split_types
WHERE restaurant_type_name IS NOT NULL
  AND restaurant_type_name <> '';

CREATE INDEX idx_temp_split_types_name
ON temp_split_types (restaurant_type_name);

CREATE INDEX idx_temp_split_types_url_name
ON temp_split_types (url(255), restaurant_name(255));


INSERT IGNORE INTO restaurant_type_map (restaurant_id, restaurant_type_id)
SELECT DISTINCT
    r.restaurant_id,
    rt.restaurant_type_id
FROM temp_split_types st
JOIN restaurants r
    ON r.url = st.url
   AND r.name = st.restaurant_name
JOIN restaurant_types rt
    ON rt.restaurant_type_name = st.restaurant_type_name;
