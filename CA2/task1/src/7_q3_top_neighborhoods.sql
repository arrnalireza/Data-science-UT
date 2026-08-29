-- ============================================================
-- File: 7_q3_top_neighborhoods.sql
-- Question:
--   Find location neighborhoods that have an average restaurant
--   rating strictly greater than 4.2 and have at least 50 restaurants
--   in that specific location.
--
-- Tables Used:
--   restaurants
--   locations
--   cities
--
-- Explanation:
--   Restaurants are grouped by neighborhood/location. The HAVING
--   clause is used because the conditions are based on aggregate
--   values: average rating and restaurant count.
--
-- Note:
--   This query returns no rows, it means no location satisfies
--   both conditions at the same time.
-- ============================================================

SELECT
    l.location_name,
    c.city_name,
    COUNT(DISTINCT r.restaurant_id) AS restaurant_count,
    ROUND(AVG(r.rate), 2) AS avg_rating
FROM restaurants r
JOIN locations l
    ON r.location_id = l.location_id
JOIN cities c
    ON l.city_id = c.city_id
WHERE r.rate IS NOT NULL
GROUP BY
    l.location_id,
    l.location_name,
    c.city_name
HAVING AVG(r.rate) > 4.2
   AND COUNT(DISTINCT r.restaurant_id) >= 50
ORDER BY
    avg_rating DESC,
    restaurant_count DESC;
