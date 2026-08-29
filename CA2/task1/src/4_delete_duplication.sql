-- ============================================================
-- File: 4_delete_duplication.sql
-- Purpose:
--   Removes duplicate restaurant records after loading.
--
-- Description:
--   Some restaurants may appear multiple times in the source dataset.
--   This script keeps one restaurant record for each unique
--   combination of url and name, then removes duplicate restaurant
--   rows after preserving/merging their mapping-table relationships.
--
-- Design Notes:
--   - The restaurant with the smallest restaurant_id is kept.
--   - duplicate_restaurant_map is used to map duplicate IDs to the
--     restaurant_id that should be kept.
--   - Mapping tables are merged before deleting duplicate restaurant
--     rows.
--
-- Run Order:
--   Run this file after 3_load.sql.
--
-- Verification:
--   After running, the duplicate check query at the end should return
--   no rows.
-- ============================================================



CREATE TABLE restaurants_backup_before_dedup AS
SELECT * FROM restaurants;

CREATE TABLE restaurant_cuisines_backup_before_dedup AS
SELECT * FROM restaurant_cuisines;

CREATE TABLE restaurant_type_map_backup_before_dedup AS
SELECT * FROM restaurant_type_map;

CREATE TABLE restaurant_listings_backup_before_dedup AS
SELECT * FROM restaurant_listings;

DROP TABLE IF EXISTS duplicate_restaurant_map;

CREATE TABLE duplicate_restaurant_map AS
SELECT
    r.restaurant_id AS duplicate_restaurant_id,
    keepers.keep_restaurant_id
FROM restaurants r
JOIN (
    SELECT
        url,
        name,
        MIN(restaurant_id) AS keep_restaurant_id
    FROM restaurants
    GROUP BY url, name
    HAVING COUNT(*) > 1
) keepers
    ON r.url = keepers.url
   AND r.name = keepers.name
WHERE r.restaurant_id <> keepers.keep_restaurant_id;

INSERT IGNORE INTO restaurant_cuisines (restaurant_id, cuisine_id)
SELECT DISTINCT
    drm.keep_restaurant_id,
    rc.cuisine_id
FROM restaurant_cuisines rc
JOIN duplicate_restaurant_map drm
    ON rc.restaurant_id = drm.duplicate_restaurant_id;
DELETE rc
FROM restaurant_cuisines rc
JOIN duplicate_restaurant_map drm
    ON rc.restaurant_id = drm.duplicate_restaurant_id;

INSERT IGNORE INTO restaurant_type_map (restaurant_id, restaurant_type_id)
SELECT DISTINCT
    drm.keep_restaurant_id,
    rtm.restaurant_type_id
FROM restaurant_type_map rtm
JOIN duplicate_restaurant_map drm
    ON rtm.restaurant_id = drm.duplicate_restaurant_id;

DELETE rtm
FROM restaurant_type_map rtm
JOIN duplicate_restaurant_map drm
    ON rtm.restaurant_id = drm.duplicate_restaurant_id;

INSERT IGNORE INTO restaurant_listings (restaurant_id, listing_type_id)
SELECT DISTINCT
    drm.keep_restaurant_id,
    rl.listing_type_id
FROM restaurant_listings rl
JOIN duplicate_restaurant_map drm
    ON rl.restaurant_id = drm.duplicate_restaurant_id;

DELETE rl
FROM restaurant_listings rl
JOIN duplicate_restaurant_map drm
    ON rl.restaurant_id = drm.duplicate_restaurant_id;
    
DELETE r
FROM restaurants r
JOIN duplicate_restaurant_map drm
    ON r.restaurant_id = drm.duplicate_restaurant_id;

