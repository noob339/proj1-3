-- Original family UI query, with explicit fields. One row per person/lineage pair.
-- Replace 6 with a bound person ID in application code.
SELECT p.PersonID, p.FirstName, p.LastName, p.Aliases, l.LineageID, l.LineageName
FROM enum_lins(6) el
JOIN LineagePersonConnector lpc ON lpc.LineageID = el.LineageID
JOIN Person p ON p.PersonID = lpc.PersonID
JOIN Lineages l ON l.LineageID = lpc.LineageID
ORDER BY p.PersonID, l.LineageID;
