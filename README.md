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


The primary web page would be the family tree itself. It was implemented using the graphviz package. It’s a tree containing the nodes of all belonging to the family lineage with the user logged in at the center. It utilizes two complex queries involving multiple relationships where the first retrieves all the nodes of the graphs while the second retrieves all the edges of the graphs allowing us to build and render the family tree associated with the user. 

Another interesting web page is the layout of the person's details upon clicking on a node within the tree. It displays their info and allows you add documents and add other people related to the person as well. It involves multiple queries to multiple entities to be able to gather all this information. We made queries to retrieve the user's lineage, their relationships, their relationship types,  their personal details and their documents. Its interesting to bring this to life allowing us to interact with a majority of the relations in our tables in order to build a page that serves both as an informational resource for the user but also a way to add other people to their tree as well as add documents.  

We needed to add another entity for the relationship types in order to simplify the addition of a relative to said person. 

We used AI tools such as chatgpt to help us with the Jinja templates and html, as well as, debugging certain issues related to python syntax and additionally to troubleshoot our systemd service to automatically update and deploy our app as we work. 

