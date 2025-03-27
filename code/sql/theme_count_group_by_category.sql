SELECT theme.category, COUNT(theme.id) AS "number_of_themes"
FROM theme
GROUP BY theme.category
ORDER BY number_of_themes DESC;