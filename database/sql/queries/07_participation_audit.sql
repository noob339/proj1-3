-- NEW audit: any returned row violates the intended lineage participation rule.
SELECT p.PersonID, p.FirstName, p.LastName
FROM Person p
WHERE NOT EXISTS (
    SELECT 1 FROM LineagePersonConnector lpc WHERE lpc.PersonID = p.PersonID
)
ORDER BY p.PersonID;
