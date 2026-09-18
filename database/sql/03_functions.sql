-- Replacement for enum_lins + enum_lins_r; same public return signature.
-- Traverses shared lineage membership, NOT Relations. UNION stops cycles.
-- Intentional change: computes the whole component, without the old depth-8 cap.
CREATE OR REPLACE FUNCTION enum_lins(p_personId INTEGER)
RETURNS TABLE (LineageID INTEGER)
LANGUAGE sql STABLE AS $$
    WITH RECURSIVE reached(LineageID) AS (
        SELECT lpc.LineageID
        FROM LineagePersonConnector lpc WHERE lpc.PersonID = p_personId
        UNION
        SELECT other.LineageID
        FROM reached r
        JOIN LineagePersonConnector member ON member.LineageID = r.LineageID
        JOIN LineagePersonConnector other ON other.PersonID = member.PersonID
    )
    SELECT r.LineageID FROM reached r;
$$;
