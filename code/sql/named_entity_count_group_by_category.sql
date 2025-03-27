SELECT named_entity.category, COUNT(named_entity.id) AS "number_of_named_entities"
FROM named_entity
GROUP BY named_entity.category
ORDER BY number_of_named_entities DESC;