SELECT
    country_code,
    country_name,
    currency_code,
    vat_rate,
    region,
    is_active
FROM countries

UNION ALL

SELECT 'NL', 'Netherlands', 'EUR', 21.0, 'Europe', 1
WHERE 'NL' NOT IN (SELECT country_code FROM countries);


SELECT
    cr.category_name,
    cr.margin_rate,
    cr.strategic_flag,
    ch.channel_code,
    ch.channel_name,
    ch.acquisition_cost_gbp,
    ch.channel_group
FROM category_rules AS cr
LEFT JOIN channels AS ch
    ON cr.default_channel_code = ch.channel_code
WHERE cr.is_active = 1
  AND ch.is_active = 1;

SELECT DISTINCT
    channel_code,
    acquisition_cost_gbp
FROM channels
WHERE is_active = 1;
