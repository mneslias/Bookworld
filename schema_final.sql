-- ---
-- Globals
-- ---

-- SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
-- SET FOREIGN_KEY_CHECKS=0;

-- ---
-- Table 'sales_raw'
-- 
-- ---

DROP TABLE IF EXISTS `sales_raw`;
		
CREATE TABLE `sales_raw` (
  `order_id` CHAR NULL AUTO_INCREMENT DEFAULT NULL,
  `order_date` DATETIME NULL DEFAULT NULL,
  `book_id` CHAR NULL DEFAULT NULL,
  `country_code` CHAR NULL DEFAULT NULL,
  `channel_code` CHAR NULL DEFAULT NULL,
  `quantity` DECIMAL NULL DEFAULT NULL,
  `discount_rate` INTEGER NULL DEFAULT NULL,
  `book_name` CHAR NULL DEFAULT NULL,
  `prix_en_livres` INTEGER NULL DEFAULT NULL,
  `prix_en_euros` INTEGER NULL DEFAULT NULL,
  `total_revenue_livres` INTEGER NULL DEFAULT NULL,
  `total_revenue_euros` INTEGER NULL DEFAULT NULL,
  `acquisition_cost_gbp` INTEGER NULL DEFAULT NULL,
  `acquisition_cost_eur` INTEGER NULL DEFAULT NULL,
  `net_revenue_gbp` INTEGER NULL DEFAULT NULL,
  `net_revenue_eu` INTEGER NULL DEFAULT NULL,
  PRIMARY KEY (`order_id`, `country_code`, `channel_code`)
);

-- ---
-- Table 'channels_category'
-- 
-- ---

DROP TABLE IF EXISTS `channels_category`;
		
CREATE TABLE `channels_category` (
  `category_name` CHAR NULL AUTO_INCREMENT DEFAULT NULL,
  `margin_rate` INTEGER NULL DEFAULT NULL,
  `strategic_flag` INTEGER NULL DEFAULT NULL,
  `channel_code` CHAR NULL DEFAULT NULL,
  `channel_name` CHAR NULL DEFAULT NULL,
  `acquisition_cost_gbp` INTEGER NULL DEFAULT NULL,
  `channel_group` CHAR NULL DEFAULT NULL,
  `acquisition_cost_eur` INTEGER NULL DEFAULT NULL,
  PRIMARY KEY (`channel_code`)
);

-- ---
-- Table 'countries_actifs'
-- 
-- ---

DROP TABLE IF EXISTS `countries_actifs`;
		
CREATE TABLE `countries_actifs` (
  `country_code` CHAR NULL AUTO_INCREMENT DEFAULT NULL,
  `country_name` CHAR NULL DEFAULT NULL,
  `currency_code` CHAR NULL DEFAULT NULL,
  `vat_rate` INTEGER NULL DEFAULT NULL,
  `region` CHAR NULL DEFAULT NULL,
  PRIMARY KEY (`country_code`)
);

-- ---
-- Table 'sales_by_country'
-- 
-- ---

DROP TABLE IF EXISTS `sales_by_country`;
		
CREATE TABLE `sales_by_country` (
  `country_code` CHAR NULL AUTO_INCREMENT DEFAULT NULL,
  `country_name` CHAR NULL DEFAULT NULL,
  `total_orders` INTEGER NULL DEFAULT NULL,
  `total_quantity` INTEGER NULL DEFAULT NULL,
  `total_revenue_gbp` INTEGER NULL DEFAULT NULL,
  `total_revenue_eur` INTEGER NULL DEFAULT NULL,
  PRIMARY KEY (`country_code`)
);

-- ---
-- Foreign Keys 
-- ---

ALTER TABLE `sales_raw` ADD FOREIGN KEY (country_code) REFERENCES `countries_actifs` (`country_code`);
ALTER TABLE `sales_raw` ADD FOREIGN KEY (country_code) REFERENCES `sales_by_country` (`country_code`);
ALTER TABLE `channels_category` ADD FOREIGN KEY (channel_code) REFERENCES `sales_raw` (`channel_code`);
ALTER TABLE `countries_actifs` ADD FOREIGN KEY (country_code) REFERENCES `sales_by_country` (`country_code`);

-- ---
-- Table Properties
-- ---

-- ALTER TABLE `sales_raw` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `channels_category` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `countries_actifs` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `sales_by_country` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ---
-- Test Data
-- ---

-- INSERT INTO `sales_raw` (`order_id`,`order_date`,`book_id`,`country_code`,`channel_code`,`quantity`,`discount_rate`,`book_name`,`prix_en_livres`,`prix_en_euros`,`total_revenue_livres`,`total_revenue_euros`,`acquisition_cost_gbp`,`acquisition_cost_eur`,`net_revenue_gbp`,`net_revenue_eu`) VALUES
-- ('','','','','','','','','','','','','','','','');
-- INSERT INTO `channels_category` (`category_name`,`margin_rate`,`strategic_flag`,`channel_code`,`channel_name`,`acquisition_cost_gbp`,`channel_group`,`acquisition_cost_eur`) VALUES
-- ('','','','','','','','');
-- INSERT INTO `countries_actifs` (`country_code`,`country_name`,`currency_code`,`vat_rate`,`region`) VALUES
-- ('','','','','');
-- INSERT INTO `sales_by_country` (`country_code`,`country_name`,`total_orders`,`total_quantity`,`total_revenue_gbp`,`total_revenue_eur`) VALUES
-- ('','','','','','');