-- Original insert-only trigger, installed AFTER explicit demo lineage memberships.
-- Does not prevent deleting the last membership.
CREATE OR REPLACE FUNCTION enforce_person_lineage_participation() 
RETURNS TRIGGER AS $$ 
DECLARE
    lineage_id INT;
BEGIN
    -- Check if the person is already in the LineagePersonConnector table
    IF NOT EXISTS (
        SELECT 1 FROM LineagePersonConnector lpc WHERE lpc.PersonID = NEW.PersonID
    ) THEN
        -- Insert a new lineage and get the generated LineageID
        INSERT INTO Lineages (LineageName) VALUES (NEW.LastName) 
        RETURNING LineageID INTO lineage_id;

        -- Insert into LineagePersonConnector
        INSERT INTO LineagePersonConnector (LineageID, PersonID) 
        VALUES (lineage_id, NEW.PersonID);
    END IF;

    RETURN NEW; 
END; 
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_person_insert_enforce_lineage_participation 
AFTER INSERT ON Person 
FOR EACH ROW 
EXECUTE FUNCTION enforce_person_lineage_participation();
