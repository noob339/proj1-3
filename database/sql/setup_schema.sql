\set ON_ERROR_STOP on
-- Same schema and lookup data, without demo people/documents.
BEGIN;
SET LOCAL search_path = public;
\ir 01_schema.sql
\ir 02_reference_data.sql
\ir 03_functions.sql
\ir 05_triggers.sql
COMMIT;
