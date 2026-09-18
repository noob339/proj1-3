-- General tag listing recovered from the schema drafts; no family/person filter.
-- Original membership joins could multiply rows and are unnecessary here.
SELECT p.PersonID, d.DocumentID, dt.DocumentTagID, dt.DocumentTagDesc
FROM Person p
JOIN Documents d ON d.AssociatedPersonID = p.PersonID
JOIN DocumentTagMapping dtm ON dtm.DocumentID = d.DocumentID
JOIN DocumentTags dt ON dt.DocumentTagID = dtm.DocumentTagID
ORDER BY p.PersonID, d.DocumentID, dt.DocumentTagID;
