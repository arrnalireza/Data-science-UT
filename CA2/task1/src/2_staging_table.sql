-- ============================================================
-- File: 2_staging_table.sql
-- Purpose:
--   Creates the staging/raw table used to temporarily store the
--   original CSV data before normalization.
--
-- Description:
--   The staging table keeps the dataset in a structure close to
--   the original CSV file. Data is first loaded here, then cleaned
--   and inserted into the normalized relational tables.
--
-- Design Notes:
--   - TEXT/LONGTEXT columns are used for raw fields that may contain
--     long values, such as reviews_list or menu_item.
--   - The staging table is not the final analytical schema.
--   - Normalized tables are populated from this table in 3_load.sql.
--
-- Run Order:
--   Run this file after 1_tables.sql.
-- ============================================================


DROP TABLE IF EXISTS csv_file;

CREATE TABLE csv_file (
    url LONGTEXT,
    address LONGTEXT,
    name LONGTEXT,
    online_order LONGTEXT,
    book_table LONGTEXT,
    rate LONGTEXT,
    votes LONGTEXT,
    phone LONGTEXT,
    location LONGTEXT,
    rest_type LONGTEXT,
    dish_liked LONGTEXT,
    cuisines LONGTEXT,
    approx_cost_for_two LONGTEXT,
    reviews_list LONGTEXT,
    menu_item LONGTEXT,
    listed_in_type LONGTEXT,
    listed_in_city LONGTEXT
);

