
## application architecture 
- flask app uses blueprints to divide modules
- flask session to manage state variables
- application factory to bootup
- uvicorn to serve the application
- optional, peewee ORM for talking to the database, sqlite for data storage

### bp1 - auth
handles the login and token related operations - saves the token in session.
endpoints to login/logout and callback for google OAuth.

### bp2 - gmail
interaction with the gmail api to search or fetch emails.
endpoints to query emails for a query. uses the token from session to build gmail client. Returns all emails in a list.

### processing pipeline - generator
Pipeline to parse the html email based on regex. 
Example will make more sense [show example]. 
It returns a structured table for all emails as entries, including the epoch-timestamp extracted from the email meta.
built using yield to supercharge performance.


## structure & endpoints 
- create_app() in app.py inits the blueprints (and registers it's prefix)
- /google for google auth, fetching token for user & permissions etc.
- /api/v1/mailbox for gmail api related actions 
    - /match -> sends the query to gmail api- returns threads as it is
    - /fetch -> processess the matched threads to extract emails (each thread can have multiple emails).
                Emails are in the form base64 encoded html data.
    - /process -> takes the encoded emails, turns into html & parses the relevant info using regex. 
                 Ability to pass custom regex/use GPT to do this job. 
