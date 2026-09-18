\set ON_ERROR_STOP on
-- Run after setup_demo.sql in a disposable DB. All test changes roll back.
-- Sequence increments are not rolled back, so do not depend on next IDs afterward.
BEGIN;
DO $$
DECLARE pid INTEGER; lid INTEGER; n INTEGER; ids INTEGER[];
BEGIN
    IF (SELECT COUNT(*) FROM Users) <> 23 OR
       (SELECT COUNT(*) FROM Person) <> 28 OR
       (SELECT COUNT(*) FROM Documents) <> 48 OR
       (SELECT COUNT(*) FROM DocumentTags) <> 7 OR
       (SELECT COUNT(*) FROM Relations) <> 29 OR
       (SELECT COUNT(*) FROM Lineages) <> 13 OR
       (SELECT COUNT(*) FROM LineagePersonConnector) <> 28 OR
       (SELECT COUNT(*) FROM DocumentTagMapping) <> 48 OR
       (SELECT COUNT(*) FROM RelationshipTypes) <> 9 THEN
        RAISE EXCEPTION 'Unexpected demo row counts';
    END IF;
    IF EXISTS (SELECT 1 FROM Users WHERE Password IS NOT NULL) THEN
        RAISE EXCEPTION 'Demo passwords must be NULL';
    END IF;
    IF EXISTS (SELECT 1 FROM Person p WHERE NOT EXISTS (
        SELECT 1 FROM LineagePersonConnector lpc WHERE lpc.PersonID = p.PersonID
    )) THEN RAISE EXCEPTION 'Orphan lineage membership'; END IF;
    SELECT array_agg(LineageID ORDER BY LineageID) INTO ids FROM enum_lins(6);
    IF ids IS DISTINCT FROM ARRAY[5] THEN RAISE EXCEPTION 'Wayne lineage mismatch'; END IF;
    -- Repeated calls formerly depended on temporary table lifecycle.
    PERFORM * FROM enum_lins(6);
    IF EXISTS (SELECT 1 FROM enum_lins(-1)) THEN RAISE EXCEPTION 'Unknown person'; END IF;
    -- Cross-lineage bridge and a cycle; six unique people, not multiplied rows.
    INSERT INTO LineagePersonConnector VALUES (6,10), (11,5);
    SELECT array_agg(LineageID ORDER BY LineageID) INTO ids FROM enum_lins(6);
    IF ids IS DISTINCT FROM ARRAY[5,10] THEN RAISE EXCEPTION 'Bridge/cycle failure'; END IF;
    SELECT COUNT(DISTINCT p.PersonID) INTO n FROM enum_lins(6) e
      JOIN LineagePersonConnector c ON c.LineageID=e.LineageID
      JOIN Person p ON p.PersonID=c.PersonID;
    IF n <> 6 THEN RAISE EXCEPTION 'Duplicate or missing family people'; END IF;
    SELECT COUNT(DISTINCT d.DocumentID) INTO n FROM enum_lins(6) e
      JOIN LineagePersonConnector c ON c.LineageID=e.LineageID
      JOIN Documents d ON d.AssociatedPersonID=c.PersonID
      JOIN DocumentTagMapping m ON m.DocumentID=d.DocumentID
      JOIN DocumentTags t ON t.DocumentTagID=m.DocumentTagID
      WHERE to_tsvector('english',t.DocumentTagDesc) @@ plainto_tsquery('english','medical')
        AND to_tsvector('english',d.DocumentDesc) @@ plainto_tsquery('english','eyes');
    IF n <> 2 THEN RAISE EXCEPTION 'Medical search mismatch'; END IF;
    INSERT INTO Person (FirstName,LastName) VALUES ('Trigger','Example') RETURNING PersonID INTO pid;
    SELECT COUNT(*) INTO n FROM LineagePersonConnector WHERE PersonID=pid;
    IF n <> 1 THEN RAISE EXCEPTION 'Trigger did not create membership'; END IF;
    SELECT l.LineageID INTO lid FROM Lineages l JOIN LineagePersonConnector c USING(LineageID)
      WHERE c.PersonID=pid AND l.LineageName='Example';
    IF lid IS NULL THEN RAISE EXCEPTION 'Trigger lineage name mismatch'; END IF;
    -- Document the original trigger's limitation rather than claim full enforcement.
    DELETE FROM LineagePersonConnector WHERE PersonID=pid;
    IF EXISTS (SELECT 1 FROM LineagePersonConnector WHERE PersonID=pid) THEN
      RAISE EXCEPTION 'Unexpected deletion behavior';
    END IF;
    -- Assert actual FK enforcement.
    BEGIN
      INSERT INTO DocumentTagMapping VALUES (999999,999999,DEFAULT,DEFAULT);
      RAISE EXCEPTION 'Foreign key accepted invalid IDs';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    RAISE NOTICE 'All smoke checks passed';
END;
$$;
ROLLBACK;
