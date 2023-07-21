from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        problem = request.form.get('problem')
        testmode = 'testmode' in request.form

        # Log the form data to the console
        print(f"URL: {url}")
        print(f"Problem: {problem}")
        print(f"Test Mode Enabled: {testmode}")

        # Run the script
        subprocess.run(['python3', 'generate_marketing_tests.py', '--url', url, '--user_prompt', problem, '--test_mode', str(testmode)])

        # Read the log file
        with open('logfile.log', 'r') as f:
            logs = f.read()

        # Send the logs as part of the response
        return f'Form submitted! Here are the logs: \n {logs}'
    else:
        return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
