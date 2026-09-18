\set ON_ERROR_STOP on
-- Execute via psql against an EMPTY disposable database. All-or-nothing setup.
BEGIN;
SET LOCAL search_path = public;
\ir 01_schema.sql
\ir 02_reference_data.sql
\ir 03_functions.sql
\ir 04_dummy_data.sql
\ir 05_triggers.sql
COMMIT;
