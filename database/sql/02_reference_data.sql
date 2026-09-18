-- Lookup rows, NOT a PostgreSQL ENUM. IDs retained from the source.
INSERT INTO RelationshipTypes (RelationshipTypeID, RelationshipTypeDesc) VALUES
(1,'Mother'), (2,'Father'), (3,'Brother'), (4,'Sister'), (5,'Sibling'),
(6,'Daughter'), (7,'Son'), (8,'Child'), (9,'Spouse');
SELECT setval(pg_get_serial_sequence('relationshiptypes','relationshiptypeid'),9,true);
