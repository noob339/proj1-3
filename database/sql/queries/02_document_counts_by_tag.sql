-- Count each document once per normalized category, even with shared lineages.
SELECT LOWER(dt.DocumentTagDesc) AS TagDesc,
       COUNT(DISTINCT d.DocumentID) AS no_tags
FROM enum_lins(6) el
JOIN LineagePersonConnector lpc ON lpc.LineageID = el.LineageID
JOIN Documents d ON d.AssociatedPersonID = lpc.PersonID
JOIN DocumentTagMapping dtm ON dtm.DocumentID = d.DocumentID
JOIN DocumentTags dt ON dt.DocumentTagID = dtm.DocumentTagID
GROUP BY LOWER(dt.DocumentTagDesc)
ORDER BY TagDesc;
