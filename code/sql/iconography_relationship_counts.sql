-- count number of relationships to the iconography table.
-- we exclude the `filename` and `admin` tables since they're purely technical
WITH c_r_iconography_institution AS (
	SELECT 
		'r_iconography_institution'::text AS qualifier,
	    COUNT (r_institution.id) AS cnt
	FROM r_institution
	WHERE r_institution.id_iconography IS NOT NULL
), c_r_iconography_place AS (
	SELECT 
		'r_iconography_place'::text AS qualifier,
	    COUNT (r_iconography_place.id) AS cnt
	FROM r_iconography_place
), c_r_iconography_named_entity AS (
	SELECT 
		'r_iconography_named_entity'::text AS qualifier,
	    COUNT (r_iconography_named_entity.id) AS cnt
	FROM r_iconography_named_entity
), c_r_iconography_theme AS (
	SELECT 
		'r_iconography_theme'::text AS qualifier,
	    COUNT (r_iconography_theme.id) AS cnt
	FROM r_iconography_theme
), c_r_all AS (
	SELECT * FROM c_r_iconography_institution
	UNION (SELECT * FROM c_r_iconography_place)
	UNION (SELECT * FROM c_r_iconography_theme)
	UNION (SELECT * FROM c_r_iconography_named_entity)
), c_r_all_sum AS (
	SELECT 
		'c_r_all_sum (sum of all relationships above'::text AS qualifier,
		SUM(c_r_all.cnt) AS cnt
	FROM c_r_all
)

SELECT * FROM c_r_all_sum
UNION (SELECT * FROM c_r_all)
ORDER BY cnt DESC
;