# small-auth-app-lite
tiny, minimum flask app with auth that should scale well for bigger projects

*docs to be filled out*
    - python version
    - project structure and directory structure
    - remove poetry
    - files to get: env :how to get? :env file   contents how to get? 
    - entry point for development
    - entry point for deployment

## startup (development)
- create virtualenv and activate it (or use poetry)
- install r.txt or pyproject.toml (poetry) 
- starting up for local development - 
    `cd sm_auth_app_lite`
    `python3 run.py`

- starting up for testing/deployment 
    - install gunicorn (if not already) and use:
        `.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "sm_auth_app_lite:create_app()" `
    This works well to make the server reliable.
    - open index at `localhost:5000/` (added a usage doc that should show up here)
    


## demo / testing 
 -  `localhost:5000/google/login` 
