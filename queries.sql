SELECT
    country_code,
    country_name,
    currency_code,
    vat_rate,
    region
FROM countries
WHERE is_active = 1;


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


