from flask import Flask, render_template,request,flash,redirect,url_for,session
import sqlite3
from datetime import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
import re
import math

import sqlite3

app = Flask(__name__)
app.secret_key="123"

conn=sqlite3.connect("database.db")
conn=sqlite3.connect('database.db',check_same_thread=False)
c = conn.cursor()

conn.commit()

@app.route('/student_experiments/<string:student_id>')
def student_experiments(student_id):
    
    # Fetch experiment data for the selected student from the database
    c.execute("SELECT DISTINCT ExperimentID, ExperimentDate FROM experiments WHERE StudentID=? ORDER BY ExperimentDate DESC", (student_id,))
    experiment_data = c.fetchall()

    # Get the experiment details for each ExperimentID
    experiment_details = []
    for data in experiment_data:
        experiment_id = data['ExperimentID']
        experiment_date = data['ExperimentDate']

        # Check if observation exists in the "observations" table
        c.execute("SELECT 1 FROM observations WHERE StudentID=? AND ExperimentID=? AND observation_date=?", (student_id, experiment_id, experiment_date))
        
        observation_exists = c.fetchone()
        
        if observation_exists:
            observation_link = url_for('observation', student_id=student_id, experiment_id=experiment_id, experiment_date=experiment_date)
           
        else:
            # Check if observation exists in the "observation2" table
            c.execute("SELECT 1 FROM observation2 WHERE StudentID=? AND ExperimentID=? AND observation_date=?", (student_id, experiment_id, experiment_date))
            
            observation2_exists = c.fetchone()
        # Add this after querying for observations
            
    
            if observation2_exists:
                observation_link = url_for('observation2', student_id=student_id, experiment_id=experiment_id, experiment_date=experiment_date)
            else:
                observation_link = None
                if observation_single_canv:
                    observation_link = url_for('observation_single_canv', student_id=student_id, experiment_id=experiment_id, experiment_date=experiment_date)
                else:
                    observation_link = None
                
        
        experiment_info = {
            'ExperimentID': experiment_id,
            'ExperimentDate': experiment_date,
            'ObservationLink': observation_link,
        }
        experiment_details.append(experiment_info)

    return render_template('student_experiments.html', experiments=experiment_details, student_id=student_id)


@app.route('/observation_single_canv/<string:student_id>/<int:experiment_id>/<string:experiment_date>')
def observation_single_canv(student_id, experiment_id, experiment_date):
    print("Student ID:", student_id)
    print("Experiment ID:", experiment_id)
    print("Experiment Date:", experiment_date)
    
    # Fetch student observations from the database for single_canv experiment
    c.execute("SELECT Length, Width, Thickness, Weight, Deflection FROM single_canv WHERE StudentID=? AND ExperimentID=? AND observation_date = ?",
              (student_id, experiment_id, experiment_date))
    observations = c.fetchall()
    print("Fetched Observations:", observations) 

    # Close the database connection
    calculated_values = [calculate_value_single_canv(observation) for observation in observations]
    total_lengths = [values[0] for values in calculated_values]
    result_single_canv = [values[1] for values in calculated_values]

    # Render the observation template for single_canv experiment
    return render_template('observation3.html', observations=observations, student_id=student_id, total_lengths=total_lengths, result_single_canv=result_single_canv)


def calculate_value_single_canv(observation):
    # Perform the calculation based on the observation data for single_canv experiment
    total_lengths = observation[0] * observation[1] * observation[2]
    result_single_canv = observation[3] / (observation[4] * total_lengths)
    return total_lengths, result_single_canv



# Route for individual student observation page
@app.route('/observation/<string:student_id>/<int:experiment_id>/<string:experiment_date>')
def observation(student_id,experiment_id,experiment_date):
    print("Student ID:", student_id)
    print("Experiment ID:", experiment_id)
    print("Experiment Date:", experiment_date)
    # Fetch student observations from the database
    c.execute("SELECT Distance, Observation1, Observation2, Observation3, Observation4, Observation5 FROM observations WHERE StudentID=? AND ExperimentID=? AND observation_date = ?", (student_id, experiment_id, experiment_date))
    observations = c.fetchall()
    print("Fetched Observations:", observations) 
    # Close the database connection
    calculated_values = [calculate_value(observation) for observation in observations]
    total_observation = [values[0] for values in calculated_values]
    result1 = [values[1] for values in calculated_values]
    
    # Generate the graph
    X = np.array(total_observation)
    Y = np.array(result1)
    A = np.vstack([X, np.ones(len(X))]).T
    m, l = np.linalg.lstsq(A, Y, rcond=None)[0]

    _, ax = plt.subplots()
    ax.set_xlabel('Result2')
    ax.set_ylabel('Result1')

    _ = plt.plot(X, Y, '.', label='Experimental data', markersize=10)
    _ = plt.plot(X, m * X + l, 'r', label='Fitted line')
    _ = plt.legend()
    
    for x_val, y_val, y_fit in zip(X, Y, m * X + l):
        plt.plot([x_val, x_val], [y_val, y_fit], 'k--', linewidth=0.5)
    
    # Create the "graphs" directory if it doesn't exist
    graphs_directory = os.path.join('static', 'graphs')
    os.makedirs(graphs_directory, exist_ok=True)
    formatted_experiment_date = re.sub(r'[^\w\s-]', '_', experiment_date)
    # Save the figure as a PNG file
    graph_filename = f'{student_id}_{experiment_id}_{formatted_experiment_date}.png'
    graph_path = os.path.join('static', 'graphs', graph_filename)
    plt.savefig(graph_path)
    plt.close()

    # Render the observation template with student observations
    return render_template('observation.html', observations=observations,student_id=student_id, total_observation=total_observation, result1=result1,graph_filename=graph_filename)

def calculate_value(observation):
    
    # Perform the calculation based on the observation data
    total_observation = round(math.degrees(math.atan(observation[3]/observation[0])),4)
    result1 =round(5.08e-5*(math.sin(math.radians(total_observation))/observation[1])* 1e9)
    return total_observation,result1


# Route for individual student observation page
@app.route('/observation2/<string:student_id>/<int:experiment_id>/<string:experiment_date>')
def observation2(student_id,experiment_id,experiment_date):

    # Fetch student observations from the database
    c.execute("SELECT Distance,Observation1,Observation2,Observation3,Observation4 FROM observation2 WHERE StudentID = ? AND ExperimentID=? AND  observation_date = ?", (student_id,experiment_id,experiment_date))
    observations2 = c.fetchall()

    # Close the database connection
    calculated_values = [calculate_value(observation) for observation in observations2]
    total_observation = [values[0] for values in calculated_values]
    result1 = [values[1] for values in calculated_values]
    # Generate the graph
    X = np.array(total_observation)
    Y = np.array(result1)
    A = np.vstack([X, np.ones(len(X))]).T
    m, l = np.linalg.lstsq(A, Y, rcond=None)[0]

    _, ax = plt.subplots()
    ax.set_xlabel('Result2')
    ax.set_ylabel('Result1')

    _ = plt.plot(X, Y, '.', label='Experimental data', markersize=10)
    _ = plt.plot(X, m * X + l, 'r', label='Fitted line')
    _ = plt.legend()
    
    for x_val, y_val, y_fit in zip(X, Y, m * X + l):
        plt.plot([x_val, x_val], [y_val, y_fit], 'k--', linewidth=0.5)
    
    # Create the "graphs" directory if it doesn't exist
    graphs_directory = os.path.join('static', 'graphs')
    os.makedirs(graphs_directory, exist_ok=True)
    formatted_experiment_date = re.sub(r'[^\w\s-]', '_', experiment_date)
    # Save the figure as a PNG file
    graph_filename = f'{student_id}_{experiment_id}_{formatted_experiment_date}.png'
    graph_path = os.path.join('static', 'graphs', graph_filename)
    plt.savefig(graph_path)
    plt.close()

    # Render the observation template with student observations
    return render_template('observation2.html', observations2=observations2,student_id=student_id, total_observation=total_observation, result1=result1,graph_filename=graph_filename)

def calculate_value(observation):
    
    # Perform the calculation based on the observation data
    total_observation = round(math.degrees(math.atan(observation[3]/observation[0])),4)
    result1 =round(5.08e-5*(math.sin(math.radians(total_observation))/observation[1])* 1e9)
    return total_observation,result1




@app.route('/')
def index():
    return render_template('login.html')

@app.route('/indexpage')
def indexpage():
     # Check if the StudentID is in the session
    if "StudentID" in session:
        # Get the StudentID from the session
        student_id = session["StudentID"]
        c.execute("SELECT Name FROM AIML WHERE usn=?", (student_id,))
        student_name = c.fetchone()

        # Check if student name exists in the database
        if student_name:
            student_name = student_name[0]
        else:
            # Handle the case when student name is not found in the database
            student_name = "N/A"
        # You can use the student_id to fetch student-specific data from the database or perform any other actions

        return render_template("index.html", student_id=student_id,student_name=student_name)
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database to check if the entered credentials are valid
        c.execute("SELECT * FROM AIML WHERE ID=? AND gmail=?", (password, username))
        result = c.fetchone()

        if result:
            # Check if the student has already changed their password
            student_id = result[0]
            session['StudentID'] = student_id
            password = result[2]
            if password:
                # Redirect to the dashboard upon successful login
                session['StudentID'] = student_id
                return redirect('/indexpage')
            else:
                # Student needs to change password
                return redirect(url_for('change_password', username=username))
        else:
            # If credentials don't match, display an error message
            return render_template('login.html', error='Invalid username or password')

    return redirect('/')



@app.route('/customer',methods=["GET","POST"])
def customer():
    return render_template("customer.html")

# Change Password route
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        username = request.form['username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        # Query the database to check if the entered credentials are valid
        
        c.execute("SELECT * FROM AIML WHERE ID=? AND gmail=?", (current_password, username))
        result = c.fetchone()

        if result:
                # Update the password in the database
                c.execute("UPDATE AIML SET ID=? WHERE gmail=?", (new_password, username))

                conn.commit()
                return redirect('/')
        else:
            return render_template('register.html', error='Invalid username or current password')

    return render_template('register.html', error='')


        
# Faculty Login
@app.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        c.row_factory = sqlite3.Row
        c.execute("SELECT * FROM facultys WHERE email = ? AND password = ?", (email, password))
        faculty = c.fetchone()
        
        if faculty:
            session['faculty_id'] = faculty['id']
            return redirect('/faculty/dashboard')
        else:
             return render_template('faculty_login.html', error='Invalid username or password')
    else:
        return render_template('faculty_login.html')
    

# Faculty Change Password
@app.route('/faculty/change_password', methods=['GET', 'POST'])
def faculty_change_password():
    if request.method == 'POST':
        email = request.form['email']
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        c.execute("SELECT * FROM facultys WHERE email = ? AND password = ?", (email, current_password))
        result = c.fetchone()

        if result:
            c.execute("UPDATE faculty SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            return redirect('/faculty/login')
        else:
            return render_template('faculty_register.html', error='Invalid email or current password')

    return render_template('faculty_register.html', error='')

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'faculty_id' in session:
        faculty_id = session['faculty_id']
        
        # Fetch unique batch IDs from faculty_batch table
        c.execute("SELECT DISTINCT batch_id FROM faculty_batch WHERE id = ?", (faculty_id,))
        batch_ids = c.fetchall()
        
        # Fetch students for each batch
        batch_students = {}
        for batch_id in batch_ids:
            c.execute("SELECT * FROM AIML WHERE batch = ?", (batch_id['batch_id'],))
            students = c.fetchall()
            batch_students[batch_id['batch_id']] = students
        
        return render_template('faculty_dashboard.html', batch_students=batch_students)
    else:
        return redirect('/faculty/login')
        

@app.route('/enter_observations', methods=['GET', 'POST'])
def enter_observations():

            if request.method == 'POST':
                StudentID = session['StudentID']
                print(StudentID)
                experiment_id=6
                name="laser"
                distance = request.form['distance']
                num_sets = int(request.form['num_sets'])  # Get the number of observation sets
                date=datetime.now()
                print(date)
                
                # Save multiple sets of observations
                for i in range(num_sets):
                    observation1 = request.form[f'observation1_{i+1}']
                    observation2 = request.form[f'observation2_{i+1}']
                    observation3 = request.form[f'observation3_{i+1}']
                    observation4 = request.form[f'observation4_{i+1}']
                    observation5 = request.form[f'observation5_{i+1}']

                    # Insert the observation set into the database
                    c.execute('''INSERT INTO observations (StudentID,ExperimentID,observation_date,Distance, Observation1, Observation2, Observation3, Observation4,Observation5)
                                VALUES (? ,?, ?, ?,?,?,?,?,?)''', (StudentID,experiment_id,date,distance, observation1, observation2, observation3, observation4,observation5))
                    conn.commit()

                c.execute('''INSERT INTO experiments (ExperimentID,StudentID,expname,ExperimentDate)
                                VALUES (? ,?, ?, ?)''', (experiment_id,StudentID,name,date))
                conn.commit()

            return render_template('customer.html')
        
    
# Create the trigger


@app.route('/enter_observation2', methods=['GET', 'POST'])
def enter_observations2():

            if request.method == 'POST':
                StudentID = session['StudentID']
                experiment_id = 5
                name="pendulum"
                sample=request.form['sample']
                distance = request.form['distance']
                num_sets = int(request.form['num_sets'])  # Get the number of observation sets
                date=datetime.now()
                
                # Save multiple sets of observations
                for i in range(num_sets):
                    observation1 = request.form[f'observation1_{i+1}']
                    observation2 = request.form[f'observation2_{i+1}']
                    observation3 = request.form[f'observation3_{i+1}']
                    observation4 = request.form[f'observation4_{i+1}']
                    

                    # Insert the observation set into the database
                    c.execute('''INSERT INTO observation2 (StudentID,ExperimentID,observation_date,sample,Distance, Observation1, Observation2, Observation3, Observation4)
                                VALUES (?,?,?,?, ?, ?, ?,?,?)''', (StudentID,experiment_id,date,sample,distance, observation1, observation2, observation3, observation4))
                    conn.commit()

                c.execute('''INSERT INTO experiments (ExperimentID,StudentID,expname,ExperimentDate)
                                VALUES (? ,?, ?, ?)''', (experiment_id,StudentID,name,date))
                conn.commit()

            return render_template('experiment2.html')
        

@app.route('/single_can', methods=['POST'])
def single_can():
    if request.method == 'POST':
        StudentID = session['StudentID']
        experiment_id = 1  # Update this with the correct experiment ID
        name = "Single Cantilever"
        num_sets = int(request.form['num_sets'])
        date = datetime.now()

        for i in range(num_sets):
            length = request.form[f'length_{i+1}']
            width = request.form[f'width_{i+1}']
            thickness = request.form[f'thickness_{i+1}']
            weight = request.form[f'weight_{i+1}']
            deflection = request.form[f'deflection_{i+1}']

            # Insert observation set into the database
            c.execute('''INSERT INTO single_canv (StudentID, ExperimentID, observation_date, Length, Width, Thickness, Weight, Deflection)
                        VALUES (?, ?, ?, ?, ?, ?, ?,?)''', (StudentID, experiment_id, date,length, width, thickness, weight, deflection))
            conn.commit()

        c.execute('''INSERT INTO experiments (ExperimentID, StudentID, expname, ExperimentDate)
                    VALUES (?, ?, ?, ?)''', (experiment_id, StudentID, name, date))
        conn.commit()

    return render_template('single_canv.html')

        


@app.route('/measure')
def measure():
    return render_template('customer.html')


@app.route('/measure2')
def measure2():
    return render_template('experiment2.html')

@app.route('/single_canv')
def single_canv():
    return render_template('single_canv.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)