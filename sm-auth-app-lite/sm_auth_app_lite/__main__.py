
""" Use this file to run the server for development.
        wdir :
             cd small-auth-app
    
    In production, use `gunicorn` 
    1. using application factory and blueprints
        gunicorn looks for the 
        create_app() func in __init__ of sm_auth_app_lite folder.
        inside this function all blueprints are registered, config etc added
        run with : [BEING USED]
            .venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "sm_auth_app_lite:create_app()" 

    2. create the app in a app.py file, add whatever additional routes or sth
            .venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "sm_auth_app_lite.app:app" 
    """


from flask import jsonify
from  app import create_app
from common.session_manager import get_session_items
app = create_app() 

        
@app.route('/session',methods=['GET'])
def debug():
    # if not is_logged_in():pass
        # return redirect(url_for('login'))
    # Render the home page with a table or dashboard
    # else:
        return jsonify(get_session_items())
    # return redirect(url_for('login'))  


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0',port=5000,debug=True)
    # app.run(debug=True)

