/* ============================================================
   StarScreen Cinemas - SQL Server schema + realistic test data
   SOFT605 Group Assignment deliverable #2 (schema.sql)

   How to run (each member, on their OWN local SQL Server):
     1. Open this file in SSMS and press Execute (F5), or:
        sqlcmd -S localhost\SQLEXPRESS -E -i database\schema.sql
     2. The script is RE-RUNNABLE: it drops and recreates everything.

   Table owners (write the INSERTs for your own feature's tables):
     M1  STAFF
     M2  MEMBERSHIP_TIER, CUSTOMER, MEMBERSHIP_HISTORY
     M3  MOVIE, SCREEN, SCREENING
     M4  SEAT, SCREENING_SEAT, PRICING, BOOKING, BOOKING_SEAT,
         PAYMENT, RECEIPT
     M5  coordinates this file + keeps it in sync with ERDiagram.mmd
   ============================================================ */

IF DB_ID('StarScreenCinema') IS NULL
    CREATE DATABASE StarScreenCinema;
GO

USE StarScreenCinema;
GO

/* ---- Drop in FK-dependency order so the script is re-runnable ---- */
DROP TABLE IF EXISTS RECEIPT;
DROP TABLE IF EXISTS PAYMENT;
DROP TABLE IF EXISTS BOOKING_SEAT;
DROP TABLE IF EXISTS BOOKING;
DROP TABLE IF EXISTS SCREENING_SEAT;
DROP TABLE IF EXISTS SCREENING;
DROP TABLE IF EXISTS SEAT;
DROP TABLE IF EXISTS SCREEN;
DROP TABLE IF EXISTS PRICING;
DROP TABLE IF EXISTS MOVIE;
DROP TABLE IF EXISTS MEMBERSHIP_HISTORY;
DROP TABLE IF EXISTS CUSTOMER;
DROP TABLE IF EXISTS MEMBERSHIP_TIER;
DROP TABLE IF EXISTS STAFF;
GO

/* ============================ TABLES ============================ */

CREATE TABLE STAFF (
    staff_id     VARCHAR(10)  NOT NULL PRIMARY KEY,
    username     VARCHAR(50)  NOT NULL UNIQUE,
    password     VARCHAR(50)  NOT NULL,
    full_name    VARCHAR(100) NOT NULL,
    role         VARCHAR(20)  NOT NULL
                 CHECK (role IN ('Cashier', 'Manager'))
);

CREATE TABLE MEMBERSHIP_TIER (
    tier_id           INT           NOT NULL PRIMARY KEY,
    tier_name         VARCHAR(20)   NOT NULL UNIQUE,
    discount_rate     DECIMAL(3,2)  NOT NULL,   -- 0.10 = 10% off
    points_per_dollar DECIMAL(3,1)  NOT NULL,
    upgrade_threshold INT           NULL        -- NULL = top tier / no upgrade
);

CREATE TABLE CUSTOMER (
    customer_id  VARCHAR(10)  NOT NULL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    phone        VARCHAR(20)  NULL,
    email        VARCHAR(100) NOT NULL,
    points       INT          NOT NULL DEFAULT 0,
    tier_id      INT          NOT NULL
                 FOREIGN KEY REFERENCES MEMBERSHIP_TIER(tier_id)
);

CREATE TABLE MEMBERSHIP_HISTORY (
    history_id   INT          NOT NULL IDENTITY(1,1) PRIMARY KEY,
    customer_id  VARCHAR(10)  NOT NULL
                 FOREIGN KEY REFERENCES CUSTOMER(customer_id),
    old_tier_id  INT          NOT NULL
                 FOREIGN KEY REFERENCES MEMBERSHIP_TIER(tier_id),
    new_tier_id  INT          NOT NULL
                 FOREIGN KEY REFERENCES MEMBERSHIP_TIER(tier_id),
    changed_at   DATETIME2    NOT NULL DEFAULT GETDATE()
);

CREATE TABLE MOVIE (
    movie_id     VARCHAR(10)  NOT NULL PRIMARY KEY,
    title        VARCHAR(100) NOT NULL,
    genre        VARCHAR(20)  NOT NULL
                 CHECK (genre IN ('Action','Drama','Horror','Kids','Romance','Thriller')),
    duration_min INT          NOT NULL CHECK (duration_min > 0),
    rating       VARCHAR(10)  NULL,
    is_active    BIT          NOT NULL DEFAULT 1
);

CREATE TABLE SCREEN (
    screen_id     VARCHAR(10) NOT NULL PRIMARY KEY,
    screen_number INT         NOT NULL UNIQUE,
    capacity      INT         NOT NULL
);

CREATE TABLE SEAT (
    seat_id     VARCHAR(10) NOT NULL PRIMARY KEY,
    screen_id   VARCHAR(10) NOT NULL
                FOREIGN KEY REFERENCES SCREEN(screen_id),
    seat_number VARCHAR(5)  NOT NULL,   -- e.g. 'A5' (row letter + seat no.)
    seat_type   VARCHAR(10) NOT NULL
                CHECK (seat_type IN ('Standard', 'Premium')),
    CONSTRAINT UQ_seat_per_screen UNIQUE (screen_id, seat_number)
);

CREATE TABLE PRICING (
    pricing_id     VARCHAR(10)  NOT NULL PRIMARY KEY,
    screening_type VARCHAR(20)  NOT NULL,
    seat_type      VARCHAR(10)  NOT NULL,
    base_price     DECIMAL(6,2) NOT NULL,
    CONSTRAINT UQ_pricing UNIQUE (screening_type, seat_type)
);

CREATE TABLE SCREENING (
    screening_id   VARCHAR(10) NOT NULL PRIMARY KEY,
    movie_id       VARCHAR(10) NOT NULL
                   FOREIGN KEY REFERENCES MOVIE(movie_id),
    screen_id      VARCHAR(10) NOT NULL
                   FOREIGN KEY REFERENCES SCREEN(screen_id),
    screening_date DATE        NOT NULL,
    screening_time VARCHAR(10) NOT NULL,   -- e.g. '7:00 PM' (matches the app)
    screening_type VARCHAR(20) NOT NULL
                   CHECK (screening_type IN ('Standard', 'IMAX', 'Kids'))
);

CREATE TABLE SCREENING_SEAT (
    screening_seat_id VARCHAR(20) NOT NULL PRIMARY KEY,  -- e.g. 'SC-01-A5'
    screening_id      VARCHAR(10) NOT NULL
                      FOREIGN KEY REFERENCES SCREENING(screening_id),
    seat_id           VARCHAR(10) NOT NULL
                      FOREIGN KEY REFERENCES SEAT(seat_id),
    is_booked         BIT         NOT NULL DEFAULT 0,
    CONSTRAINT UQ_screening_seat UNIQUE (screening_id, seat_id)
);

CREATE TABLE BOOKING (
    booking_id      VARCHAR(10)  NOT NULL PRIMARY KEY,
    customer_id     VARCHAR(10)  NULL      -- NULL = guest walk-in
                    FOREIGN KEY REFERENCES CUSTOMER(customer_id),
    staff_id        VARCHAR(10)  NOT NULL
                    FOREIGN KEY REFERENCES STAFF(staff_id),
    booking_date    DATETIME2    NOT NULL DEFAULT GETDATE(),
    subtotal        DECIMAL(8,2) NOT NULL,
    discount_amount DECIMAL(8,2) NOT NULL DEFAULT 0,
    gst_amount      DECIMAL(8,2) NOT NULL,
    final_amount    DECIMAL(8,2) NOT NULL,
    points_earned   INT          NOT NULL DEFAULT 0
);

CREATE TABLE BOOKING_SEAT (
    booking_seat_id   VARCHAR(20) NOT NULL PRIMARY KEY,  -- e.g. 'BK-1001-1'
    booking_id        VARCHAR(10) NOT NULL
                      FOREIGN KEY REFERENCES BOOKING(booking_id),
    screening_seat_id VARCHAR(20) NOT NULL UNIQUE        -- prevents double booking
                      FOREIGN KEY REFERENCES SCREENING_SEAT(screening_seat_id)
);

CREATE TABLE PAYMENT (
    payment_id     VARCHAR(10)  NOT NULL PRIMARY KEY,
    booking_id     VARCHAR(10)  NOT NULL UNIQUE
                   FOREIGN KEY REFERENCES BOOKING(booking_id),
    payment_method VARCHAR(10)  NOT NULL
                   CHECK (payment_method IN ('Cash', 'Card', 'Voucher')),
    amount         DECIMAL(8,2) NOT NULL,
    payment_date   DATETIME2    NOT NULL DEFAULT GETDATE()
);

CREATE TABLE RECEIPT (
    receipt_id VARCHAR(15) NOT NULL PRIMARY KEY,
    booking_id VARCHAR(10) NOT NULL UNIQUE
               FOREIGN KEY REFERENCES BOOKING(booking_id),
    issued_at  DATETIME2   NOT NULL DEFAULT GETDATE()
);
GO

/* ========================== TEST DATA ==========================
   Realistic data covering the assignment's demo requirements:
   - customers from EVERY membership tier
   - movies across all six genres
   - completed bookings that demonstrate the discount, GST,
     loyalty-point, and auto-upgrade logic (see BK-1003: the booking
     that pushed Lisa from Silver to Gold, logged in the history).
   ================================================================ */

/* ---- Staff [M1] ---- */
INSERT INTO STAFF (staff_id, username, password, full_name, role) VALUES
('ST-01', 'cashier', 'cashier123', 'Alex Kim',      'Cashier'),
('ST-02', 'manager', 'manager123', 'John Reynolds', 'Manager');

/* ---- Membership tiers [M2] (rates mirror models/customer.py) ---- */
INSERT INTO MEMBERSHIP_TIER (tier_id, tier_name, discount_rate, points_per_dollar, upgrade_threshold) VALUES
(0, 'Guest',   0.00, 0.0, NULL),
(1, 'Regular', 0.10, 1.0, 500),
(2, 'Silver',  0.20, 1.5, 1000),
(3, 'Gold',    0.30, 2.0, NULL);

/* ---- Customers [M2] - one from each registered tier ----
   Points shown are AFTER the seed bookings below. */
INSERT INTO CUSTOMER (customer_id, name, phone, email, points, tier_id) VALUES
('CU-0001', 'Sarah Johnson',   '0412 345 678', 'sarah.j@email.com',  661, 2),  -- Silver
('CU-0002', 'Michael Chen',    '0423 456 789', 'm.chen@email.com',  1547, 3),  -- Gold
('CU-0003', 'Emma Williams',   '0434 567 890', 'emma.w@email.com',   211, 1),  -- Regular
('CU-0004', 'James Rodriguez', '0445 678 901', 'j.rod@email.com',     56, 1),  -- Regular
('CU-0005', 'Lisa Thompson',   '0456 789 012', 'lisa.t@email.com',  1010, 3);  -- upgraded to Gold by BK-1003

/* ---- Movies [M3] - all six genres from the brief ---- */
INSERT INTO MOVIE (movie_id, title, genre, duration_min, rating, is_active) VALUES
('MV-01', 'Dune: Part Three',  'Action',   155, 'PG-13', 1),
('MV-02', 'Midnight in Paris', 'Romance',  114, 'PG',    1),
('MV-03', 'Quantum Breach',    'Thriller', 125, 'MA15+', 1),
('MV-04', 'The Haunting Hour', 'Horror',   108, 'R16',   1),
('MV-05', 'Dragon''s Fury',    'Kids',     105, 'G',     1),
('MV-06', 'Ocean''s Story',    'Drama',    118, 'PG',    0);   -- deactivated

/* ---- Screens [M3] - 3 screens, 50 seats each ---- */
INSERT INTO SCREEN (screen_id, screen_number, capacity) VALUES
('SCR-1', 1, 50), ('SCR-2', 2, 50), ('SCR-3', 3, 50);

/* ---- Seats [M4] - rows A-E x seats 1-10 per screen;
        rows A and B are Premium (generated set-based) ---- */
;WITH seat_rows(r) AS (SELECT v FROM (VALUES ('A'),('B'),('C'),('D'),('E')) t(v)),
      seat_cols(n) AS (SELECT v FROM (VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10)) t(v))
INSERT INTO SEAT (seat_id, screen_id, seat_number, seat_type)
SELECT CONCAT('S', sc.screen_number, '-', sr.r, sc2.n),
       sc.screen_id,
       CONCAT(sr.r, sc2.n),
       CASE WHEN sr.r IN ('A', 'B') THEN 'Premium' ELSE 'Standard' END
FROM SCREEN sc
CROSS JOIN seat_rows sr
CROSS JOIN seat_cols sc2;

/* ---- Pricing [M4] - screening type x seat type ---- */
INSERT INTO PRICING (pricing_id, screening_type, seat_type, base_price) VALUES
('PR-01', 'Standard', 'Standard', 15.00),
('PR-02', 'Standard', 'Premium',  22.00),
('PR-03', 'IMAX',     'Standard', 22.00),
('PR-04', 'IMAX',     'Premium',  30.00),
('PR-05', 'Kids',     'Standard', 10.00),
('PR-06', 'Kids',     'Premium',  14.00);

/* ---- Screenings [M3] - dated TODAY so the daily reports show data ---- */
INSERT INTO SCREENING (screening_id, movie_id, screen_id, screening_date, screening_time, screening_type) VALUES
('SC-01', 'MV-01', 'SCR-1', CAST(GETDATE() AS DATE), '10:00 AM', 'IMAX'),
('SC-02', 'MV-01', 'SCR-1', CAST(GETDATE() AS DATE), '7:00 PM',  'IMAX'),
('SC-03', 'MV-02', 'SCR-2', CAST(GETDATE() AS DATE), '2:00 PM',  'Standard'),
('SC-04', 'MV-03', 'SCR-2', CAST(GETDATE() AS DATE), '8:30 PM',  'Standard'),
('SC-05', 'MV-04', 'SCR-3', CAST(GETDATE() AS DATE), '9:00 PM',  'Standard'),
('SC-06', 'MV-05', 'SCR-3', CAST(GETDATE() AS DATE), '11:00 AM', 'Kids');

/* ---- Screening seats [M4] - one row per seat per screening
        (generated set-based; all start free) ---- */
INSERT INTO SCREENING_SEAT (screening_seat_id, screening_id, seat_id, is_booked)
SELECT CONCAT(scr.screening_id, '-', st.seat_number),
       scr.screening_id,
       st.seat_id,
       0
FROM SCREENING scr
JOIN SEAT st ON st.screen_id = scr.screen_id;

/* ---- Completed bookings [M4] --------------------------------------
   Price math: subtotal -> minus tier discount -> plus 15% GST.

   BK-1001 Michael (Gold 30%, 2 pt/$):  IMAX Premium A4+A5 = 60.00
           -18.00 disc -> 42.00 -> +6.30 GST -> 48.30, +97 pts
   BK-1002 Sarah (Silver 20%, 1.5 pt/$): Std C3+C4 = 30.00
           -6.00 -> 24.00 -> +3.60 -> 27.60, +41 pts (Cash)
   BK-1003 Lisa (Silver 20%): Std Premium B6 = 22.00
           -4.40 -> 17.60 -> +2.64 -> 20.24, +30 pts
           ==> 980 + 30 = 1,010 points: AUTO-UPGRADE Silver -> Gold
   BK-1004 Emma (Regular 10%, 1 pt/$): Kids D2+D3+D4 = 30.00
           -3.00 -> 27.00 -> +4.05 -> 31.05, +31 pts
   BK-1005 James (Regular 10%): Std E7 = 15.00
           -1.50 -> 13.50 -> +2.03 -> 15.53, +16 pts
   ------------------------------------------------------------------- */
INSERT INTO BOOKING (booking_id, customer_id, staff_id, booking_date, subtotal, discount_amount, gst_amount, final_amount, points_earned) VALUES
('BK-1001', 'CU-0002', 'ST-01', GETDATE(), 60.00, 18.00, 6.30, 48.30, 97),
('BK-1002', 'CU-0001', 'ST-01', GETDATE(), 30.00,  6.00, 3.60, 27.60, 41),
('BK-1003', 'CU-0005', 'ST-01', GETDATE(), 22.00,  4.40, 2.64, 20.24, 30),
('BK-1004', 'CU-0003', 'ST-02', GETDATE(), 30.00,  3.00, 4.05, 31.05, 31),
('BK-1005', 'CU-0004', 'ST-01', GETDATE(), 15.00,  1.50, 2.03, 15.53, 16);

INSERT INTO BOOKING_SEAT (booking_seat_id, booking_id, screening_seat_id) VALUES
('BK-1001-1', 'BK-1001', 'SC-02-A4'),
('BK-1001-2', 'BK-1001', 'SC-02-A5'),
('BK-1002-1', 'BK-1002', 'SC-03-C3'),
('BK-1002-2', 'BK-1002', 'SC-03-C4'),
('BK-1003-1', 'BK-1003', 'SC-04-B6'),
('BK-1004-1', 'BK-1004', 'SC-06-D2'),
('BK-1004-2', 'BK-1004', 'SC-06-D3'),
('BK-1004-3', 'BK-1004', 'SC-06-D4'),
('BK-1005-1', 'BK-1005', 'SC-05-E7');

/* Mark every seat that has a BOOKING_SEAT row as taken */
UPDATE ss SET ss.is_booked = 1
FROM SCREENING_SEAT ss
JOIN BOOKING_SEAT bs ON bs.screening_seat_id = ss.screening_seat_id;

INSERT INTO PAYMENT (payment_id, booking_id, payment_method, amount, payment_date) VALUES
('PAY-1001', 'BK-1001', 'Card', 48.30, GETDATE()),
('PAY-1002', 'BK-1002', 'Cash', 27.60, GETDATE()),
('PAY-1003', 'BK-1003', 'Card', 20.24, GETDATE()),
('PAY-1004', 'BK-1004', 'Card', 31.05, GETDATE()),
('PAY-1005', 'BK-1005', 'Card', 15.53, GETDATE());

INSERT INTO RECEIPT (receipt_id, booking_id, issued_at) VALUES
('RC-BK-1001', 'BK-1001', GETDATE()),
('RC-BK-1002', 'BK-1002', GETDATE()),
('RC-BK-1003', 'BK-1003', GETDATE()),
('RC-BK-1004', 'BK-1004', GETDATE()),
('RC-BK-1005', 'BK-1005', GETDATE());

/* ---- Membership history [M2] - BK-1003 pushed Lisa Silver -> Gold ---- */
INSERT INTO MEMBERSHIP_HISTORY (customer_id, old_tier_id, new_tier_id, changed_at) VALUES
('CU-0005', 2, 3, GETDATE());
GO

PRINT 'StarScreenCinema schema and test data created successfully.';
GO
