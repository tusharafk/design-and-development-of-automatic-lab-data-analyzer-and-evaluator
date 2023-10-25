# design-and-development-of-automatic-lab-data-analyzer-and-evaluator
Step 1 — Installing Flask
In this step, you’ll activate your Python environment and install Flask using the pip package installer.

If you haven’t already activated your programming environment, make sure you’re in your project directory (flask_blog) and use the following command to activate the environment:

source env/bin/activate
Once your programming environment is activated, your prompt will now have an env prefix that may look as follows:
(env)sshy@localhost:$
To install Flask, run the following command:pip install flask
Once the installation is complete, run the following command to confirm the installation:python -c "import flask; print(flask.__version__)"

Step 2 — Creating a Base Application
Now that you have your programming environment set up, you’ll start using Flask. In this step, you’ll make a small web application inside a Python file and run it to start the server, which will display some information on the browser.

In your flask_blog directory, open a file named hello.py for editing, use nano or your favorite text editor:

nano hello.py


This hello.py file will serve as a minimal example of how to handle HTTP requests. Inside it, you’ll import the Flask object, and create a function that returns an HTTP response. Write the following code inside hello.py:

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

In the preceding code block, you first import the Flask object from the flask package. You then use it to create your Flask application instance with the name app. You pass the special variable __name__ that holds the name of the current Python module. It’s used to tell the instance where it’s located—you need this because Flask sets up some paths behind the scenes.

Once you create the app instance, you use it to handle incoming web requests and send responses to the user. @app.route is a decorator that turns a regular Python function into a Flask view function, which converts the function’s return value into an HTTP response to be displayed by an HTTP client, such as a web browser. You pass the value '/' to @app.route() to signify that this function will respond to web requests for the URL /, which is the main URL.

The hello() view function returns the string 'Hello, World!' as a response.

Save and close the file.

To run your web application, you’ll first tell Flask where to find the application (the hello.py file in your case) with the FLASK_APP environment variable:

export FLASK_APP=hello

Then run it in development mode with the FLASK_ENV environment variable:

export FLASK_ENV=development
Lastly, run the application using the flask run command:

flask run

Step 3 — Using HTML templates
create a html for frontend and put them in template folder
and for css files put them in static folder

Step 4 — Setting up the Database
You’ll use a SQLite database file to store your data because the sqlite3 module, which we will use to interact with the database, is readily available in the standard Python library. For more information about SQLite, 


-----------------------------------------checkout this for information----------------------------
https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3#step-4-setting-up-the-database
