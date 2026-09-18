-- Later README query, simplified to DISTINCT and consistent English parsing.
SELECT DISTINCT d.DocumentID, d.LinkToDoc, d.DocumentDesc, d.OccurrenceDate,
       d.AddedByUserID, d.AssociatedPersonID, d.CreationDate
FROM enum_lins(6) el
JOIN LineagePersonConnector lpc ON lpc.LineageID = el.LineageID
JOIN Documents d ON d.AssociatedPersonID = lpc.PersonID
JOIN DocumentTagMapping dtm ON dtm.DocumentID = d.DocumentID
JOIN DocumentTags dt ON dt.DocumentTagID = dtm.DocumentTagID
WHERE to_tsvector('english', dt.DocumentTagDesc)
          @@ plainto_tsquery('english', 'medical')
  AND to_tsvector('english', d.DocumentDesc)
          @@ plainto_tsquery('english', 'eyes')
ORDER BY d.DocumentID;
