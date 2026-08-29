-- ============================================================
-- File: 6_q2_online_order_pricing.sql
-- Question:
--   Does allowing online orders affect pricing?
--   Calculate the average approx_cost_for_two and total votes grouped
--   by online_order status, broken down by listed_in(city).
--
-- Tables Used:
--   restaurants
--   locations
--   cities
--
-- Explanation:
--   The restaurants table does not directly store city_id. Instead,
--   each restaurant references a location, and each location references
--   a city. Therefore, the join path is:
--     restaurants -> locations -> cities
--
--   The query groups results by city and online_order status.
-- ============================================================

SELECT
    c.city_name,
    r.online_order,
    COUNT(DISTINCT r.restaurant_id) AS total_restaurants,
    ROUND(AVG(r.approx_cost_for_two), 2) AS avg_approx_cost_for_two,
    SUM(COALESCE(r.votes, 0)) AS total_votes
FROM restaurants r
JOIN locations l ON r.location_id = l.location_id
JOIN cities c ON l.city_id = c.city_id
WHERE r.online_order IN ('Yes', 'No')
  AND r.approx_cost_for_two IS NOT NULL
GROUP BY
    c.city_name,
    r.online_order
ORDER BY
    c.city_name ASC,
    r.online_order ASC;
