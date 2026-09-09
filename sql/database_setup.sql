-- =====================================================================
-- Hotel Booking Cancellation & Revenue Intelligence Analytics
-- File: database_setup.sql
-- Purpose: Create the MySQL database and table for the cleaned,
--          feature-engineered hotel booking dataset.
-- Engine: MySQL 8.0+ (uses window-function-compatible syntax elsewhere)
-- =====================================================================

DROP DATABASE IF EXISTS hotel_booking_analytics;
CREATE DATABASE hotel_booking_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hotel_booking_analytics;

-- ---------------------------------------------------------------------
-- Table: bookings
-- Source: data/processed/hotel_bookings_cleaned.csv
-- Grain: one row per hotel booking record
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS bookings;

CREATE TABLE bookings (
    booking_id                        INT AUTO_INCREMENT PRIMARY KEY,
    hotel                             VARCHAR(20)     NOT NULL,
    is_canceled                       TINYINT(1)      NOT NULL,
    lead_time                         INT             NOT NULL,
    arrival_date_year                 INT             NOT NULL,
    arrival_date_month                VARCHAR(15)     NOT NULL,
    arrival_date_week_number          INT             NOT NULL,
    arrival_date_day_of_month         INT             NOT NULL,
    stays_in_weekend_nights           INT             NOT NULL,
    stays_in_week_nights              INT             NOT NULL,
    adults                            INT             NOT NULL,
    children                          INT             NOT NULL,
    babies                            INT             NOT NULL,
    meal                              VARCHAR(15),
    country                           VARCHAR(10),
    market_segment                    VARCHAR(30),
    distribution_channel              VARCHAR(30),
    is_repeated_guest                 TINYINT(1),
    previous_cancellations            INT,
    previous_bookings_not_canceled    INT,
    reserved_room_type                VARCHAR(5),
    assigned_room_type                VARCHAR(5),
    booking_changes                   INT,
    deposit_type                      VARCHAR(20),
    agent                             INT NULL,
    company                           INT NULL,
    days_in_waiting_list              INT,
    customer_type                     VARCHAR(20),
    adr                                DECIMAL(10,2) NULL,
    required_car_parking_spaces       INT,
    total_of_special_requests         INT,
    reservation_status                VARCHAR(20),
    reservation_status_date           DATE NULL,
    has_agent                         TINYINT(1),
    has_company                       TINYINT(1),
    total_guests                      INT,
    total_stay_nights                 INT,
    lead_time_category                VARCHAR(40),
    arrival_month_num                 INT,
    arrival_date                      DATE NULL,
    season                            VARCHAR(10),
    arrival_quarter                   INT,
    is_returning_guest                TINYINT(1),
    has_prior_cancellation_history    TINYINT(1),
    potential_booking_revenue         DECIMAL(12,2) NULL,

    INDEX idx_hotel (hotel),
    INDEX idx_is_canceled (is_canceled),
    INDEX idx_market_segment (market_segment),
    INDEX idx_arrival_date (arrival_date),
    INDEX idx_deposit_type (deposit_type),
    INDEX idx_lead_time_category (lead_time_category)
);

-- ---------------------------------------------------------------------
-- Data import instructions
-- ---------------------------------------------------------------------
-- Option A: MySQL LOAD DATA (fastest, run from the MySQL client with
-- local_infile enabled and adjust the path to your local machine):
--
--   SET GLOBAL local_infile = 1;
--
--   LOAD DATA LOCAL INFILE '/path/to/data/processed/hotel_bookings_cleaned.csv'
--   INTO TABLE bookings
--   FIELDS TERMINATED BY ',' ENCLOSED BY '"'
--   LINES TERMINATED BY '\n'
--   IGNORE 1 ROWS
--   (hotel, is_canceled, lead_time, arrival_date_year, arrival_date_month,
--    arrival_date_week_number, arrival_date_day_of_month, stays_in_weekend_nights,
--    stays_in_week_nights, adults, children, babies, meal, country, market_segment,
--    distribution_channel, is_repeated_guest, previous_cancellations,
--    previous_bookings_not_canceled, reserved_room_type, assigned_room_type,
--    booking_changes, deposit_type, @agent, @company, days_in_waiting_list,
--    customer_type, @adr, required_car_parking_spaces, total_of_special_requests,
--    reservation_status, reservation_status_date, has_agent, has_company,
--    total_guests, total_stay_nights, lead_time_category, arrival_month_num,
--    arrival_date, season, arrival_quarter, is_returning_guest,
--    has_prior_cancellation_history, @potential_booking_revenue)
--   SET
--    agent = NULLIF(@agent, ''),
--    company = NULLIF(@company, ''),
--    adr = NULLIF(@adr, ''),
--    potential_booking_revenue = NULLIF(@potential_booking_revenue, '');
--
-- Option B: Use MySQL Workbench's "Table Data Import Wizard" and point it
-- at data/processed/hotel_bookings_cleaned.csv, matching the column order
-- above (booking_id is auto-generated and should not be imported).
--
-- Option C: Import programmatically from Python using SQLAlchemy + pandas:
--   import pandas as pd
--   from sqlalchemy import create_engine
--   engine = create_engine("mysql+pymysql://user:password@localhost/hotel_booking_analytics")
--   df = pd.read_csv("data/processed/hotel_bookings_cleaned.csv")
--   df.to_sql("bookings", engine, if_exists="append", index=False)
-- ---------------------------------------------------------------------

-- Quick sanity check queries after import
SELECT COUNT(*) AS total_rows FROM bookings;
SELECT hotel, COUNT(*) AS bookings FROM bookings GROUP BY hotel;
