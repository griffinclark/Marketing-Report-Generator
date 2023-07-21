from flask import Flask, render_template, request
import subprocess
import uuid
import os

app = Flask(__name__)

# Create an initial, default log file
default_logfile = 'error.log'
open(default_logfile, 'w').close()

# This list will store all the unique log file names
logfiles = [default_logfile]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        problem = request.form.get('problem')
        testmode = 'testmode' in request.form

        # Log the form data to the console
        logfile = "logs/"+f"logfile_{url.replace('/', '$')}_{problem.replace(' ', '%20')}_{uuid.uuid4()}.log"
        print(logfile)
        # Create the logfile
        open(logfile, 'w').close()

        # Add the unique log file name to the list
        logfiles.append(logfile)

        # Run the script in the background without waiting for it to finish
        subprocess.Popen(['python3', 'generate_marketing_test.py', '--url', url, '--user_prompt', problem, '--test_mode', str(testmode), '--log_file', logfile])

        return render_template('loading.html')  # loading.html should include the JavaScript to update the logs

    else:
        return render_template('form.html')

@app.route('/logs', methods=['GET'])
def logs():
    # Read the most recent log file
    with open(logfiles[-1], 'r') as f:
        logs = f.read()

    return logs

if __name__ == '__main__':
    port = 5001
    # result = os.popen(f'lsof -i :{port}').read().split('\n')
    # if len(result) > 1:  # If the port is occupied
    #     pid = result[1].split()[1]  # Get the PID of the process occupying the port
    #     os.system(f'kill -9 {pid}')  # Terminate the process
    app.run(port=port, debug=True)
