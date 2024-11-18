The db is on es4140

The url: http://34.139.151.172:8111/

# User Stories

## User Registration Epic

1. **As a user,** I want to be able to register an account with my basic information (name, email, password) to associate my family tree with. endpoint: /register
2. **Upon registration,** I want to receive an email to verify my account belongs to me. not implemented

## Family Tree Creation and Maintenance Epic

1. **As a user,** I want to be able to log in to see and edit my family tree. endpoint: /family_tree
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
   - It is interesting to interact with mauch of our schema.

- We needed to add another entity for the relationship types to the ERD because it was already present in our database, and allows us to flexibly populate drop down selectors for specifying relationship types, and add new relationship types easily. 

# Use of external tooling

- We used AI tools such as chatgpt to help us with the Jinja templates and html, as well as, debugging certain issues related to python syntax and additionally to troubleshoot our systemd service to automatically update and deploy our app as we work. 

- We also used graphviz to help generate family trees dynamically from the database
- Flask as a web server
- Jinja for html templating
- psycopg2 to act as an interface for sqlalchemy to work with a postgresl database engine
- sqlalchemy to connect to the database
- click to setup flask web server options ie port, IPs to accept incoming connections from, set the web server to run multithreaded etc
