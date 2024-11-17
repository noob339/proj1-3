
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
import sqlalchemy
from sqlalchemy.pool import NullPool
from flask import Flask, request, session, render_template, g, redirect, Response, abort, flash, url_for
from jinja2 import Environment, FileSystemLoader
from graphviz import Graph, Digraph
# Jinja2 Environment
env = Environment(loader=FileSystemLoader("templates"))

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = os.urandom(24)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://user:password@104.196.222.236/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@104.196.222.236/proj1part2"
#
DATABASEURI = "postgresql://es4140:whocares123@104.196.222.236/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = sqlalchemy.create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

# The string needs to be wrapped around text()

conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);"""))
#conn.execute(text("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""))

# To make the queries run, we need to add this commit line

conn.commit() 
@app.before_request
def auth():
    # List of routes to exclude from the middleware check
    excluded_routes = ['index', 'login', 'register']

    # Check if the route is excluded
    if request.endpoint in excluded_routes:
        return  # Skip the check for these routes
    print(request.endpoint)
    # Check if the session variable "user" is set
    if 'UserID' not in session:
        return render_template('index.html')


def get_associated_person_id(user_id, conn):
    """
    Retrieve the associated person_id for a given user_id.

    Args:
        user_id (int): The user ID to find the associated person_id for.
        conn (sqlalchemy.engine.Connection): The database connection.

    Returns:
        int: The associated person_id if found, or None otherwise.
    """
    try:
        # Query to find person_id where AssociatedUserID matches the user_id
        query = sqlalchemy.text("""
            SELECT personid
            FROM person
            WHERE AssociatedUserID = :user_id
        """)

        # Execute the query
        result = conn.execute(query, {"user_id": user_id}).fetchone()
        person_id = result[0]
        print(result)
        # Return the person_id if a result is found
        if result:
            return person_id  # Adjust access if result is tuple or dict

    except Exception as e:
        # Log or handle the error
        print(f"Database error: {str(e)}")

    # Return None if no result or an error occurred
    return None

@app.route('/family_tree')
def render_tree():
    with engine.connect() as conn:
        # 6 default is for debugging auth middleware 
        user_id = session.get("UserID", 6)
        person_id = get_associated_person_id(user_id, conn)
        # Fetch nodes
        nodes_query = sqlalchemy.text("""
        SELECT p.personid, p.firstname, p.lastname, p.associateduserid, l.lineagename 
        FROM enum_lins(:person_id) el
        JOIN LineagePersonConnector AS lpc ON lpc.LineageID = el.LineageID
        JOIN Person AS p ON p.PersonID = lpc.PersonID
        JOIN Lineages AS l ON l.LineageID = lpc.LineageID;
        """)
        nodes = conn.execute(nodes_query, {"person_id": person_id}).fetchall()

        # Fetch edges
        edges_query = sqlalchemy.text("""
        SELECT people.personid, r.directrelationship AS relatedtopersonid,
               rt.RelationshipTypeID, rt.RelationshipTypeDesc 
        FROM (SELECT p.*, l.lineagename 
              FROM enum_lins(:person_id) el
              JOIN LineagePersonConnector AS lpc ON lpc.LineageID = el.LineageID
              JOIN Person AS p ON p.PersonID = lpc.PersonID
              JOIN Lineages AS l ON l.LineageID = lpc.LineageID) people
        JOIN Relations AS r ON r.personid = people.personid
        JOIN RelationshipTypes rt ON r.DirectRelationshipTypeID = rt.RelationshipTypeID;
        """)
        edges = conn.execute(edges_query, {"person_id": person_id}).fetchall()

    # Create the graph
    graph = Graph(format="svg")
    #graph.attr(rankdir="LR")  # Left to right orientation

    # Add nodes
    for personid, firstname, lastname, associateduserid, lineagename in nodes:
        graph.node(
            str(personid),
            label=f"{firstname} {lastname}\n(Lineage: {lineagename})",
            tooltip=f"UserID: {associateduserid}",
            href=f"/person/{personid}"
        )
    seen_edges = set()
    # Add edges
    for personid, relatedtopersonid, relationship_type_id, relationship_desc in edges:
        if (relatedtopersonid, personid) in seen_edges or (personid, relatedtopersonid) in seen_edges:
           continue
        seen_edges.add((personid, relatedtopersonid))
        graph.edge(
            str(personid),
            str(relatedtopersonid),
            label=relationship_desc,
            tooltip=f"Type ID: {relationship_type_id}"
        )

    # Render the graph to SVG
    svg = graph.pipe(format="svg").decode("utf-8")
    return render_template("family_tree.html", graph_svg=svg)

def add_documentation(conn, personid, doc_desc, doc_link, doc_date, tags_csv):
    """
    Handles adding new documentation to the database, including tags and mappings, within a single transaction.
    """
    # Begin a transaction
    with conn.begin() as transaction:
        user_id = session.get("UserID", 6)
        try:
            user_id = session.get("UserID", None)
            # Insert the document into the Documents table
            insert_doc_query = sqlalchemy.text("""
            INSERT INTO Documents (AssociatedPersonID, DocumentDesc, LinkToDoc, OccurrenceDate, addedbyuserid)
            VALUES (:personid, :doc_desc, :doc_link, :doc_date, :user_id)
            RETURNING DocumentID;
            """)
            result = conn.execute(
                insert_doc_query,
                {"personid": personid, "doc_desc": doc_desc, "doc_link": doc_link, "doc_date": doc_date, "user_id": user_id},
            )
            document_id = result.fetchone()[0]

            # Parse the CSV of tags
            tags = [tag.strip() for tag in tags_csv.split(",") if tag.strip()]

            # Fetch existing tags from the DocumentTags table
            existing_tags_query = sqlalchemy.text("""
            SELECT DocumentTagID, DocumentTagDesc FROM DocumentTags WHERE DocumentTagDesc = ANY(:tags);
            """)
            existing_tags = conn.execute(existing_tags_query, {"tags": tags}).fetchall()

            existing_tag_map = {row[1]: row[0] for row in existing_tags}
            new_tags = [tag for tag in tags if tag not in existing_tag_map]

            # Insert missing tags into the DocumentTags table
            if new_tags:
                insert_tags_query = sqlalchemy.text("""
                INSERT INTO DocumentTags (DocumentTagDesc, addedbyuserid) VALUES (:tag, :user_id) RETURNING DocumentTagID, DocumentTagDesc;
                """)
                for tag in new_tags:
                    result = conn.execute(insert_tags_query, {"tag": tag, "user_id": user_id})
                    tag_row = result.fetchone()
                    print(tag_row)
                    existing_tag_map[tag_row[1]] = tag_row[0]

            # Map tags to the document in the DocumentTagMapping table
            insert_mapping_query = sqlalchemy.text("""
            INSERT INTO DocumentTagMapping (DocumentID, DocumentTagID) VALUES (:document_id, :tag_id);
            """)
            for tag_id in existing_tag_map.values():
                conn.execute(insert_mapping_query, {"document_id": document_id, "tag_id": tag_id, "user_id": user_id})
            
            return redirect(f"/person/{personid}")
        except Exception as e:
            # If an error occurs, roll back the transaction
            transaction.rollback()
            raise e  # Re-raise the exception for further handling



@app.route("/person/<int:personid>", methods=["GET", "POST"])
def person_details(personid):
    if request.method == "POST":
        # Handle the POST request in a separate function
        doc_desc = request.form["doc_desc"]
        doc_link = request.form["doc_link"]
        doc_date = request.form["doc_date"]
        tags_csv = request.form["tags"]

        with engine.connect() as conn:
            return add_documentation(conn, personid, doc_desc, doc_link, doc_date, tags_csv)

        # Redirect to refresh the page with the updated data
        

    # Fetch person details, relationships, and documentation
    with engine.connect() as conn:
        # Fetch person details
        person_query = sqlalchemy.text("""
        SELECT p.personid, p.firstname, p.lastname, p.associateduserid, l.lineagename 
        FROM Person AS p
        JOIN LineagePersonConnector AS lpc ON p.PersonID = lpc.PersonID
        JOIN Lineages AS l ON l.LineageID = lpc.LineageID
        WHERE p.personid = :personid;
        """)
        person_result = conn.execute(person_query, {"personid": personid}).fetchone()

        # If person not found, return 404
        if not person_result:
            return f"Person with ID {personid} not found", 404

        # Fetch relationships
        relationships_query = sqlalchemy.text("""
        SELECT Person.PersonID AS RelatedToPersonID, Person.FirstName, Person.LastName, rt.RelationshipTypeDesc 
        FROM Relations AS r
        JOIN RelationshipTypes AS rt ON r.DirectRelationshipTypeID = rt.RelationshipTypeID
        JOIN Person ON Person.PersonID = r.directrelationship
        WHERE r.personid = :personid;
        """)
        relationships = conn.execute(relationships_query, {"personid": personid}).fetchall()

        # Fetch documentation
        documentation_query = sqlalchemy.text("""
        SELECT d.DocumentID, d.DocumentDesc, d.LinkToDoc, d.OccurrenceDate, 
               STRING_AGG(dt.DocumentTagDesc, ',') AS tags
        FROM Documents AS d
        JOIN DocumentTagMapping dtm ON dtm.DocumentID = d.DocumentID
        JOIN DocumentTags dt ON dt.DocumentTagID = dtm.DocumentTagID
        WHERE d.AssociatedPersonID = :personid
        GROUP BY d.DocumentID, d.DocumentDesc, d.LinkToDoc, d.OccurrenceDate;
        """)
        documentation = conn.execute(documentation_query, {"personid": personid}).fetchall()

    # Render the template
    return render_template(
        "person_details.html",
        person={
            "personid": person_result.personid,
            "firstname": person_result.firstname,
            "lastname": person_result.lastname,
            "associateduserid": person_result.associateduserid,
            "lineagename": person_result.lineagename,
        },
        relationships=[
            {"related_to": RelatedToPersonID, "relationship_desc": RelationshipTypeDesc, "FirstName": FirstName, "LastName": LastName}
            for RelatedToPersonID, FirstName, LastName, RelationshipTypeDesc in relationships
        ],
        documentation=[
            {
                "doc_id": DocumentID,
                "desc":   DocumentDesc,
                "link":   LinkToDoc,
                "date":   OccurrenceDate,
                "tags":   tags,
            }
            for DocumentID,
                DocumentDesc,
                LinkToDoc,
                OccurrenceDate,
                tags, in documentation
        ],
    )


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

@app.route('/')
def index():

  return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email')  # Optional email input
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                query = sqlalchemy.text("""
                    INSERT INTO "users" ("username", "email", "password")
                    VALUES (:username, :email, :password)
                """)
                g.conn.execute(
                    query,
                    {
                        "username": username,
                        "email": email,
                        "password": password,
                    }
                )
                g.conn.commit()
                flash("Registration successful!")
                return redirect(url_for('register'))
            except Exception as e:
                # Capture the exact error for debugging
                error = f"Database error: {str(e)}"
                print(error)  # Log it for debugging
                flash(error)

    return render_template('registration.html')





@app.route('/login', methods=('GET', 'POST'))
def login():
    # If the request is not POST, immediately render the login page
    if request.method != 'POST':
        return render_template('login.html')

    # Process POST request
    username = request.form.get('username')
    password = request.form.get('password')

    # Validate input
    if not username:
        flash('Username is required.')
        return render_template('login.html')

    if not password:
        flash('Password is required.')
        return render_template('login.html')

    try:
        # Query the database for the user
        query = sqlalchemy.text("""
            SELECT userid, username, password FROM users WHERE "username" = :username
        """)
        user = g.conn.execute(query, {"username": username}).fetchone()
        g.conn.commit()

        # Check if user exists
        if user is None:
            flash('Incorrect username.')
            return render_template('login.html')

        userid, db_username, db_password = user

        # Validate password (no hashing for now)
        if db_password != password:
            flash('Incorrect password.')
            return render_template('login.html')

        # Successful login
        session.clear()
        session['UserID'] = userid  # Set session user ID
        flash("Login successful!")
        return redirect(url_for('render_tree'))

    except Exception as e:
        error = f"Database error: {str(e)}"
        print(error)  # Log the error for debugging
        flash(error)
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
