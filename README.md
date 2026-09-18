# Family tree and digital archive

Course project by **Euripides Soto and Andrew Rubinstein**, Columbia COMS W4111.
The original Flask application is followed below by its historical feature notes.
The subsequent database cleanup is in `database/`; its source inventory, inferred
fixture repairs, and original recursion implementation are preserved there.

## Local setup

Requires Python 3.11+, PostgreSQL with `psql`/`createdb`, and the Graphviz `dot`
executable. Install Graphviz using your system package manager. From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
createdb db4111_demo
psql -X -v ON_ERROR_STOP=1 -d db4111_demo -f database/sql/setup_demo.sql
psql -X -v ON_ERROR_STOP=1 -d db4111_demo -f database/sql/queries/run_all.sql
psql -X -v ON_ERROR_STOP=1 -d db4111_demo -f database/tests/smoke.sql
export DATABASE_URL='postgresql+psycopg2:///db4111_demo'
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python webserver/server.py
```

Open http://127.0.0.1:8111 and register a new local account, then log in. Registration
stores a Werkzeug password hash and creates one person and one surname lineage.
All supplied fixture passwords remain NULL and cannot authenticate. Once logged
in, visit `/person/6` to explore Bruce Wayne's three documents and add people or
linked documents. Your tree initially shows your newly registered person.

The application defaults to the local `db4111_demo` database and explicitly uses
`public` as its search path. `.env.example` documents configuration; `.env` files
are not loaded automatically. Use shell exports and keep credentials out of git.
The old course database is not contacted. For another host/port, configure
`DATABASE_URL` and pass corresponding connection flags to `psql` and `createdb`.
For empty schema without fixtures, use `database/sql/setup_schema.sql` in a
separate new database. Never run demo setup against existing data. Existing
installations need a separately reviewed migration and backup; old plaintext
passwords are not accepted by the updated login.

## Integration decisions and limits

- Original unquoted identifiers fold to lowercase, matching the app's result keys.
  No ORM models or existing migration system were found.
- Only `enum_lins` is used by the app. The replacement traverses connected
  lineages without the old depth-eight limit, including inactive archive rows.
- This remains a shared course-demo archive: authenticated users can view and
  add to arbitrary people. Family connectivity is navigation, not authorization.
  `AssociatedUserID` remains an association, not ownership. When several people
  are associated, the lowest person ID is the deterministic tree starting point.
- Active accounts can log in; lineage and relationship selectors show active
  entries. Archive queries otherwise retain their historical lack of IsActive
  filtering. This is not a private multi-user service; no new privacy model,
  email verification, CSRF protection, upload storage, or external syncing is claimed.
- Registration relies on the insert trigger. Adding a relative replaces the new
  automatic surname lineage with the selected lineage in the same transaction,
  removing the unused automatic lineage. The trigger still does not prevent
  deleting a person's last membership.
- Relationship types describe the new target relative to the existing source.
  The app writes that directed edge only; it no longer creates an incorrect
  reciprocal with the same type. Reverse roles are not inferred. The original
  primary key still allows one type per ordered pair.
- Tag summaries count distinct documents so overlapping memberships do not
  inflate totals. User filtering continues to mean document author.

## Validation

SQL checks above require a freshly seeded demo database. Application regression
checks use one rollback-only transaction (sequences can still advance):

```sh
TEST_DATABASE_URL="$DATABASE_URL" .venv/bin/python -m unittest discover -s tests -v
```

See [integration validation](database/docs/INTEGRATION.md) for actual results.
`db4111-cleanup/` is the supplied handoff snapshot; `database/` is the integrated
location used by the app setup instructions. No historical database migration
or deployment was performed. Check course publication restrictions
before publishing course work.

## Original application notes

# User Stories

## User Registration Epic

1. **As a user,** I want to be able to register an account with my basic information (name, email, password) to associate my family tree with. endpoint: /register
2. **Upon registration,** I want to receive an email to verify my account belongs to me. not implemented

## Family Tree Creation and Maintenance Epic

1. **As a user,** I want to be able to log in to see and edit my family tree. endpoint: /login and /family_tree
2. **As a user,** I want to be able to update my information. not implemented fully, but you can update the associated person's info on endpoint /person
3. **As a user,** I want to be able to add new people I have relationships with:
   - a. When I add a new person, I want to be able to click on the person they have a direct relationship with and specify the relationship they have to this existing person. endpoint: /person
   - b. After I add this new person, I want to be able to input arbitrary information about them beyond their relationship to me and others I am related to. endpoint: /person
   - c. I want to be able to tag this arbitrary information as belonging to a certain class of data (e.g., medical info, military service, employment, gender, etc.). endpoint: /person
   - d. I want to be able to set an associated date related to this arbitrary information. endpoint: /person

## Additional Story Document Tag Review

1. I want to be able to see an aggregate of all the document tags associated with my close family members. endpoint: /user_tags
   - I want to be able to only show the tags I added when I check a box to apply this filter


## Detailed description of a few interesting features

- The primary web page is the family tree.
   - Implemented using the graphviz package.
   - The family tree shows many members of a family lineage, and connected lineages with the logged in user at the center.
   - It utilizes two queries involving multiple relationships where the first retrieves all the nodes of the graphs, and the second retrieves all the edges of the graphs allowing us to build and render the family tree associated with the user. 

- Another web page is the page to show details related to a person, which can be accessed by clicking on that person in the family tree. It displays their information allowing you add documents and add other people related to the person.
   - We made queries to retrieve the user's lineage, relationships, relationship types, personal details and documents.
   - This page serves both as an informational resource for the user, and a way to add other people to their tree, and add documents.  
   - It is interesting to interact with much of our schema.

- We needed to add another entity for the relationship types to the ERD because it was already present in our database, and allows us to flexibly populate drop down selectors for specifying relationship types, and add new relationship types easily. 

# Use of external tooling

- We also used graphviz to help generate family trees dynamically from the database
- Flask as a web server
- Jinja for html templating
- psycopg2 to act as an interface for sqlalchemy to work with a postgresql database engine
- sqlalchemy to connect to the database
- click to setup flask web server options ie port, IPs to accept incoming connections from, set the web server to run multithreaded etc
- We used AI tools such as chatgpt to help us with the Jinja templates and html, as well as, debugging certain issues related to python syntax and additionally to troubleshoot our systemd service to automatically update and deploy our app as we work. 
  - prompts include:
    - how do I pass data to jinja template
    - how do I set up a service on ubuntu with systemd
    - how do I check the logs of a service systemd is running
    - how can I setup a cron job that runs every n minutes
    - how do I access a value from a python tuple
    - how to I add a tuple to a set
    - what python libraries can be used to generate a clickable undirect graph
    - how can I use graphviz to generate a clickable svg for an undirected graph in memory and pass it to a jinja template
    - how can I get form data from a request in a flask endpoint
    - how can i define middleware that runs on a set of paths using flask
    - find me documentation with examples of using the session portion of flask
