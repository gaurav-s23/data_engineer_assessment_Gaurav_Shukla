USE home_db;

-- property table (master)
CREATE TABLE IF NOT EXISTS `property` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `Property_Title` TEXT,
  `Address` TEXT,
  `Market` VARCHAR(255),
  `Flood` VARCHAR(255),
  `Street_Address` TEXT,
  `City` VARCHAR(255),
  `State` VARCHAR(50),
  `Zip` VARCHAR(50),
  `Property_Type` VARCHAR(100),
  `Highway` VARCHAR(100),
  `Train` VARCHAR(100),
  `Tax_Rate` DOUBLE,
  `SQFT_Basement` DOUBLE,
  `HTW` VARCHAR(200),
  `Pool` VARCHAR(50),
  `Commercial` VARCHAR(50),
  `Style` VARCHAR(255),
  `Stories` VARCHAR(50),
  `Beds` VARCHAR(50),
  `Baths` VARCHAR(50),
  `Year_Built` VARCHAR(50),
  `Lot_Size` VARCHAR(255),
  `Lot_Size_Units` VARCHAR(50),
  `Lot_Size_Acres` DOUBLE,
  `Gross_Operating_Income` DOUBLE,
  `Net_Operating_Income` DOUBLE,
  `NOI` DOUBLE,
  `Net_Yield` DOUBLE,
  `IRR` DOUBLE,
  `Latitude` DOUBLE,
  `Longitude` DOUBLE,
  `Subdivision` TEXT,
  `Taxes` BIGINT,
  `School_Average` DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Leads table (capital L)
CREATE TABLE IF NOT EXISTS `Leads` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `Reviewed_Status` VARCHAR(255),
  `Most_Recent_Status` VARCHAR(255),
  `Source` VARCHAR(255),
  `Occupancy` VARCHAR(255),
  `property_id` BIGINT,
  FOREIGN KEY (`property_id`) REFERENCES `property`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- leads table (lowercase)
CREATE TABLE IF NOT EXISTS `leads` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `Selling_Reason` TEXT,
  `Seller_Retained_Broker` TEXT,
  `Final_Reviewer` VARCHAR(255),
  `property_id` BIGINT,
  FOREIGN KEY (`property_id`) REFERENCES `property`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- HOA table
CREATE TABLE IF NOT EXISTS `HOA` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `HOA_Flag` VARCHAR(100),
  `HOA_Fee` DOUBLE,
  `HOA_Frequency` VARCHAR(100),
  `property_id` BIGINT,
  FOREIGN KEY (`property_id`) REFERENCES `property`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Valuation table (list -> multiple rows)
CREATE TABLE IF NOT EXISTS `Valuation` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `Redfin_Value` VARCHAR(255),
  `Zestimate` VARCHAR(255),
  `Valuation_Date` VARCHAR(255),
  `property_id` BIGINT,
  FOREIGN KEY (`property_id`) REFERENCES `property`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Rehab table (each element of rehab list becomes a row)
CREATE TABLE IF NOT EXISTS `Rehab` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `Underwriting_Rehab` DOUBLE,
  `Rehab_Calculation` DOUBLE,
  `Paint` VARCHAR(50),
  `Flooring_Flag` VARCHAR(50),
  `Foundation_Flag` VARCHAR(50),
  `Roof_Flag` VARCHAR(50),
  `HVAC_Flag` VARCHAR(50),
  `Kitchen_Flag` VARCHAR(50),
  `Bathroom_Flag` VARCHAR(50),
  `Appliances_Flag` VARCHAR(50),
  `Windows_Flag` VARCHAR(50),
  `Landscaping_Flag` VARCHAR(50),
  `Trashout_Flag` VARCHAR(50),
  `property_id` BIGINT,
  FOREIGN KEY (`property_id`) REFERENCES `property`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Taxes table (one column in config)
CREATE TABLE IF NOT EXISTS `Taxes` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `Taxes` BIGINT,
  `property_id` BIGINT,
  FOREIGN KEY (`property_id`) REFERENCES `property`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
