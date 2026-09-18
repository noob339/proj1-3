-- NEW helper query: inspect family-tree edges (enum_lins does not read these).
SELECT r.PersonID, p.FirstName AS SourceFirstName, p.LastName AS SourceLastName,
       r.DirectRelationship AS TargetPersonID,
       target.FirstName AS TargetFirstName, target.LastName AS TargetLastName,
       rt.RelationshipTypeDesc
FROM Relations r
JOIN Person p ON p.PersonID = r.PersonID
JOIN Person target ON target.PersonID = r.DirectRelationship
JOIN RelationshipTypes rt ON rt.RelationshipTypeID = r.DirectRelationshipTypeID
WHERE r.PersonID = 6
ORDER BY r.DirectRelationship;
