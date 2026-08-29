-- ============================================================
-- File: 1_tables.sql
-- Purpose:
--   Creates the normalized relational schema for the food
--   delivery restaurant dataset.
--
-- Description:
--   This script creates the main database and final normalized
--   tables, including restaurants, cities, locations, cuisines,
--   restaurant types, and listing types.
--
-- Design Notes:
--   - cities and locations are separated to avoid repeated city
--     and neighborhood values.
--   - restaurants reference locations using location_id.
--   - cuisines, restaurant types, and listing types are modeled
--     using many-to-many relationship tables because one restaurant
--     can have multiple cuisines/types/listings.
--   - large raw text fields such as menu_item and reviews_list are
--     not stored in the final restaurants table because they are not
--     required for the SQL analysis queries.
--
-- Run Order:
--   Run this file first.
-- ============================================================


CREATE DATABASE IF NOT EXISTS food_delivery_db;
USE food_delivery_db;

DROP TABLE IF EXISTS restaurant_type_map;
DROP TABLE IF EXISTS restaurant_cuisines;
DROP TABLE IF EXISTS restaurant_listings;
DROP TABLE IF EXISTS restaurant_types;
DROP TABLE IF EXISTS cuisines;
DROP TABLE IF EXISTS listing_types;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS cities;

CREATE TABLE cities (
    city_id INT PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    location_name VARCHAR(100) NOT NULL,
    city_id INT NOT NULL,
    UNIQUE (location_name, city_id),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE TABLE restaurants (
    restaurant_id INT PRIMARY KEY AUTO_INCREMENT,
    url TEXT,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(100),
    location_id INT NOT NULL,
    online_order VARCHAR(3),
    book_table VARCHAR(3),
    rate DECIMAL(4,2),
    votes INT,
    approx_cost_for_two DECIMAL(10,2),
    dish_liked TEXT,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE listing_types (
    listing_type_id INT PRIMARY KEY AUTO_INCREMENT,
    listing_type_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE restaurant_listings (
    restaurant_id INT NOT NULL,
    listing_type_id INT NOT NULL,
    PRIMARY KEY (restaurant_id, listing_type_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (listing_type_id) REFERENCES listing_types(listing_type_id)
);

CREATE TABLE cuisines (
    cuisine_id INT PRIMARY KEY AUTO_INCREMENT,
    cuisine_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE restaurant_cuisines (
    restaurant_id INT NOT NULL,
    cuisine_id INT NOT NULL,
    PRIMARY KEY (restaurant_id, cuisine_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (cuisine_id) REFERENCES cuisines(cuisine_id)
);

CREATE TABLE restaurant_types (
    restaurant_type_id INT PRIMARY KEY AUTO_INCREMENT,
    restaurant_type_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE restaurant_type_map (
    restaurant_id INT NOT NULL,
    restaurant_type_id INT NOT NULL,
    PRIMARY KEY (restaurant_id, restaurant_type_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (restaurant_type_id) REFERENCES restaurant_types(restaurant_type_id)
);
