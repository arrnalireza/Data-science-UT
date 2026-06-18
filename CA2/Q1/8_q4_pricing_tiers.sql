-- ============================================================
-- File: 8_q4_pricing_tiers.sql
-- Question:
--   Build a pricing tier dashboard by categorizing restaurants into
--   three tiers based on approx_cost_for_two:
--     Budget    : <= 500
--     Mid-Range : > 500 and < 1000
--     Premium   : >= 1000
--
--   Return city, tier, count, and average rating. Order by city
--   ascending and count descending.
--
-- Tables Used:
--   restaurants
--   locations
--   cities
--
-- Explanation:
--   The CASE expression creates the pricing tier. The query then
--   groups by city and tier to calculate the number of restaurants
--   and their average rating.
-- ============================================================


SELECT
    c.city_name,
    CASE
        WHEN r.approx_cost_for_two <= 500 THEN 'Budget'
        WHEN r.approx_cost_for_two > 500 AND r.approx_cost_for_two < 1000 THEN 'Mid-Range'
        WHEN r.approx_cost_for_two >= 1000 THEN 'Premium'
    END AS pricing_tier,
    COUNT(DISTINCT r.restaurant_id) AS restaurant_count,
    ROUND(AVG(r.rate), 2) AS avg_rating
FROM restaurants r
JOIN locations l ON r.location_id = l.location_id
JOIN cities c ON l.city_id = c.city_id
WHERE r.approx_cost_for_two IS NOT NULL
  AND r.rate IS NOT NULL
GROUP BY
    c.city_name,
    pricing_tier
ORDER BY
    c.city_name ASC,
    restaurant_count DESC;
