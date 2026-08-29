-- ============================================================
-- File: 5_q1_delivery_cost.sql
-- Question:
--   Find the total number of restaurants and the average approximate
--   cost for two people, filtering only for restaurants that offer
--   "Delivery" using listed_in(type).
--
-- Tables Used:
--   restaurants
--   restaurant_listings
--   listing_types
--
-- Explanation:
--   Restaurants are joined with listing_types through the junction
--   table restaurant_listings. The query filters only restaurants
--   where listing_type_name = 'Delivery', then calculates the count
--   and average cost.
-- ===========================================================

SELECT
    COUNT(DISTINCT r.restaurant_id) AS total_restaurants,
    ROUND(AVG(r.approx_cost_for_two), 2) AS avg_approx_cost_for_two
FROM restaurants r
JOIN restaurant_listings rl
    ON r.restaurant_id = rl.restaurant_id
JOIN listing_types lt
    ON rl.listing_type_id = lt.listing_type_id
WHERE lt.listing_type_name = 'Delivery'
  AND r.approx_cost_for_two IS NOT NULL;



