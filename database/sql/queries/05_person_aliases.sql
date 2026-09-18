-- Later README array demonstration. WITH ORDINALITY preserves alias order.
SELECT p.PersonID, p.FirstName, p.LastName,
       string_agg(a.alias, ', ' ORDER BY a.position) AS AliasesCommaSeparated
FROM Person p
LEFT JOIN LATERAL unnest(p.Aliases) WITH ORDINALITY AS a(alias, position) ON TRUE
WHERE p.PersonID = 6
GROUP BY p.PersonID, p.FirstName, p.LastName;
