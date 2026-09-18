-- Corrected: source claimed to fetch documents but selected tags and had no filter.
-- LEFT JOIN retains untagged documents; one row per document/tag pair.
SELECT d.DocumentID, d.LinkToDoc, d.DocumentDesc, d.OccurrenceDate,
       d.AssociatedPersonID, dt.DocumentTagID, dt.DocumentTagDesc
FROM Documents d
LEFT JOIN DocumentTagMapping dtm ON dtm.DocumentID = d.DocumentID
LEFT JOIN DocumentTags dt ON dt.DocumentTagID = dtm.DocumentTagID
WHERE d.AssociatedPersonID = 6
ORDER BY d.DocumentID, dt.DocumentTagID;
