-- assert that all place.id_richelieu values are unique.
SELECT (
   	SELECT COUNT(place.id) FROM PLACE
) = (
 	SELECT COUNT(q.id_richelieu) 
	FROM ( SELECT DISTINCT place.id_richelieu FROM place ) AS q 
);


-- ne categories mapped to number of ne's in this category
SELECT 
	named_entity.category, 
	COUNT(named_entity.id_uuid) AS count_result
FROM named_entity
GROUP BY named_entity.category
ORDER BY count_result DESC;

-- theme categories mapped to number of themes in this category
SELECT 
	theme.category, 
	COUNT(theme.id_uuid) AS count_result
FROM theme
GROUP BY theme.category
ORDER BY count_result DESC;

-- theme mapped to number of iconographies for this theme
SELECT 
	theme.id_uuid, 
	theme.entry_name, 
    COUNT(r_iconography_theme.id) AS "count_result"
FROM theme
JOIN r_iconography_theme ON r_iconography_theme.id_theme = theme.id
GROUP BY theme.id_uuid, theme.entry_name, r_iconography_theme.id_theme
ORDER BY count_result DESC;

-- ne mapped to number of iconographies for this named_entity
SELECT 
	named_entity.id_uuid, 
	named_entity.entry_name, 
    COUNT(r_iconography_named_entity.id) AS "count_result"
FROM named_entity
JOIN r_iconography_named_entity 
	ON r_iconography_named_entity.id_named_entity = named_entity.id
GROUP BY 
	named_entity.id_uuid, 
	named_entity.entry_name, 
	r_iconography_named_entity.id_named_entity
ORDER BY count_result DESC;

-- places mapped to number of iconographies
SELECT 
	place.id_uuid, 
	place.id_richelieu, 
    COUNT(r_iconography_place.id) AS "count_result"
FROM place 
JOIN r_iconography_place ON r_iconography_place.id_place = place.id
GROUP BY place.id_uuid, place.id_richelieu, r_iconography_place.id_place
ORDER BY count_result DESC;


-- iconography mapped to number of places
SELECT 
	iconography.id, 
	COUNT(r_iconography_place.id) AS count_result
FROM iconography
JOIN r_iconography_place ON iconography.id = r_iconography_place.id_iconography
GROUP BY iconography.id
ORDER BY count_result DESC;

-- iconography mapped to number of named entities
SELECT 
	iconography.id, 
	COUNT(r_iconography_named_entity.id) AS count_result
FROM iconography
JOIN r_iconography_named_entity 
	ON iconography.id = r_iconography_named_entity.id_iconography
GROUP BY iconography.id
ORDER BY count_result DESC;


-- iconography mapped to number of themes
SELECT 
	iconography.id, 
	COUNT(r_iconography_theme.id) AS count_result
FROM iconography
JOIN r_iconography_theme 
	ON iconography.id = r_iconography_theme.id_iconography
GROUP BY iconography.id
ORDER BY count_result DESC;

