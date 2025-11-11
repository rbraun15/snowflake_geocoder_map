
-- assumption is the content of repository snowflake_geocoder has been run and is in place

use database demo_geocode;
use schema address_processing;
select * from source_addresses;


delete from source_addresses;
delete from geocoded_addresses;

INSERT INTO Source_Addresses (Name, Address_Source_ID, Department, Address, GeoCoded) VALUES     
    ('Greenville S1','S1', 'Sales', '616 Grey Fox Square Taylors SC 29687', 'No'),
    ('Greenville S5', 'S5', 'Student', '110 Ridge Rd Greenville, SC 29607', 'No'),
    ('Greenville S7', 'S7', 'Student', '321 Riverside Chase Greer, SC 29650', 'No'),
    ('Greenville S8', 'S8', 'Student', '212 W Broad Greenville, SC 29601', 'No');
    
    INSERT INTO Source_Addresses (Name, Address_Source_ID, Department, Address, GeoCoded) VALUES
    ('Miami Beach Property', 'A1', 'Sales', '4601 Collins Ave Miami Beach FL 33140', 'No'),
    ('Rochester Home', 'A2','Marketing', '114 Orland Rd Rochester NY 14622', 'No'),
    ('Greenville Residence','A3', 'Sales', '103 Autumn Rd Greenville SC 29650', 'No'),
    ('Clemson1', 'A4', 'Student', '217 W Main ST Central SC 29630', 'No'),
    ('Clemson2', 'A5', 'Student', '119 N Townville St Seneca SC 29678', 'No'),
    ('Clemson3', 'A6', 'Student', '356 Clemson St Clemson SC 29631', 'No');



 select * from source_addresses;   

CALL Process_Ungeocoded_Addresses_Batch(100);


select * from geocoded_addresses order by geocoded_timestamp desc;


select distinct address_source_id from geocoded_addresses;



CREATE OR REPLACE TABLE DONOR_DATA (
    RECORD_ID VARCHAR(3) PRIMARY KEY,
    NAME VARCHAR(100),
    DONATION_AMOUNT NUMBER(12, 2),
    DONATION_COUNT INTEGER,
    GRADUATION_DATE DATE,
    LAST_DONATION_DATE DATE,
    DEPARTMENT VARCHAR(50),
    DONOR_LEVEL VARCHAR(20)
);


INSERT INTO DONOR_DATA (RECORD_ID, NAME, DONATION_AMOUNT, DONATION_COUNT, GRADUATION_DATE, LAST_DONATION_DATE, DEPARTMENT, DONOR_LEVEL) VALUES
('S7', 'Alice Smith', 1500.00, 3, '2015-05-15', '2024-09-01', 'Engineering', 'Bronze'),
('S1', 'Bob Johnson', 50000.00, 1, '1998-12-20', '2025-01-10', 'Chemistry', 'Gold'),
('S5', 'Charlie Brown', 250.50, 5, '2020-05-01', '2024-10-25', 'Accounting', 'Silver'),
('A3', 'Diana Prince', 100000.00, 1, '1985-06-01', '2025-01-05', 'Chemistry', 'Platinum'),
('A6', 'Ethan Hunt', 500.00, 12, '2010-05-15', '2024-11-01', 'Engineering', 'Bronze'),
('A2', 'Fiona Glenn', 12000.00, 2, '1992-12-01', '2024-12-15', 'Accounting', 'Gold'),
('S8', 'George Kirk', 150.00, 8, '2022-05-20', '2024-07-22', 'Engineering', 'Bronze'),
('A4', 'Hannah Montana', 7500.00, 4, '2005-05-05', '2024-10-01', 'Chemistry', 'Silver'),
('A5', 'Isaac Newton', 30000.00, 3, '1975-06-01', '2024-11-11', 'Accounting', 'Platinum'),
('A1', 'Jane Doe', 100.00, 1, '2023-12-31', '2024-01-01', 'Engineering', 'Bronze');


ALTER TABLE geocoded_addresses ADD COLUMN
    H3_LEVEL_7 VARCHAR(20),
    H3_LEVEL_8 VARCHAR(20),
    H3_LEVEL_9 VARCHAR(20);



create view geocoded_donors_map_view as 

SELECT
    -- Donor Metadata (Source Table: D)
    d.RECORD_ID,
    d.NAME AS Donor_Name,
    d.DEPARTMENT AS Donor_Department,
    d.DONATION_AMOUNT,
    d.DONATION_COUNT,
    d.GRADUATION_DATE,
    d.LAST_DONATION_DATE,
    d.DONOR_LEVEL,

    -- Geocoding & Address Metadata (Geocoded Table: G)
    g.ADDRESS_SOURCE_ID,
    g.ADDRESS AS Original_Address_String,
    g.STREET,
    g.CITY,
    g.STATE,
    g.ZIP,
    g.LAT,
    g.LONG,
    g.H3_LEVEL_7,
    g.H3_LEVEL_8,
    g.H3_LEVEL_9,
    g.GEOCODED_TIMESTAMP

FROM
    DONOR_DATA d
LEFT JOIN
    GEOCODED_ADDRESSES g
    -- JOINING ON THE SPECIFIED KEY COLUMNS
    ON d.RECORD_ID = g.ADDRESS_SOURCE_ID;



    UPDATE DEMO_GEOCODE.ADDRESS_PROCESSING.Geocoded_Addresses
SET
    H3_LEVEL_7 = H3_LATLNG_TO_CELL_STRING(LAT, LONG, 7),
    H3_LEVEL_8 = H3_LATLNG_TO_CELL_STRING(LAT, LONG, 8),
    H3_LEVEL_9 = H3_LATLNG_TO_CELL_STRING(LAT, LONG, 9)
WHERE
    Lat IS NOT NULL AND Long IS NOT NULL
    AND H3_LEVEL_9 IS NULL;
