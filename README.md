The db is on es4140

The url: http://34.139.151.172:8111/

The user is able to register and log in

Upon logging in, the user will be able to view their family tree. They can click on a node within their family tree and that person's detail will be displayed. 

They are also able to add documents for said person

The user is able to see all of the tags within their family and the tags they specifically created. 

Users are able to add documentation and add people to their family trees as well. 

The primary web page would be the family tree itself. It was implemented using the graphviz package. It’s a tree containing the nodes of all belonging to the family lineage with the user logged in at the center. 

Another interesting web page is the layout of the person's details upon clicking on a node within the tree. It displays their info, allows you add documents and add other people related to the person as well. 

We needed to add another entity for the relationship types in order to simplify the addition of a relative to said person. 

We used AI tools such as chatgpt to help us with the Jinja templates and html, as well as, debugging certain issues related to python syntax and additionally to troubleshoot our systemd service to automatically update and deploy our app as we work. 

