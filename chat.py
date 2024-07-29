from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

app = Flask(__name__)

# Generate and set the secret key
app.secret_key = secrets.token_hex(32)  # or use the generated string directly

socketio = SocketIO(app)

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'abbdulrazza@gmail.com'
EMAIL_HOST_PASSWORD = 'ufhk jari qbnl fehy'
EMAIL_RECIPIENT = 'abdul.r@latitudetechnolabs.org'

# Define options based on the selected service
service_options = ['Java', 'Python', 'Php']
app_dev_options = ['Kotlin', 'React Native', 'Rust']
testing_options = ['Manual Testing', 'Automation Testing']
hire_option = ['python developer', 'java developer', 'php developer']

@app.route('/')
def index():
    session.clear()  # Clear session data on new connection
    return render_template('index.html')

@socketio.on('user_message')
def handle_user_message(message):
    if 'selected_services' not in session:
        session['selected_services'] = []

    if message == 'start':
        response = {
            'question': 'Hello, I am here to assist you :) ',
            # 'options': ['QA Testing', 'Web Development', 'App Development', 'Hire developer']
        }
    elif message == 'Hire developer':
        session['selected_services'] = ['Hire developer']
        response = {
            'question': 'You selected Hire. Please choose a language:',
            'options': ['python developer','java developer','php developer']
        }
    elif message in ['python developer','java developer','php developer']:
        session['selected_services'].append(message)
        response = {
            'question': f'You selected {message}. Please select a framework:',
            'options': ['Django', 'Flask'] if message == 'python developer' else ['Spring'] if message == 'java developer' else ['Laravel']
        }
    elif message in ['Django', 'Flask', 'Spring', 'Laravel']:
        session['selected_services'].append(message)
        response = {
            'question': f'You selected {message}. Please choose your experience level:',
            'options': ['1 year', '2 years', '3+ years']
        }

    elif message in ['1 year', '2 years', '3+ years']:
        session['selected_services'].append(message)
        response = {
            'question': f'You selected {message}. Please provide your details:',
            'showForm': True,
            'selectedServices': session['selected_services']
        }
    elif message in service_options:
        session['selected_services'] = ['Web Development', message]
        response = {
            'question': f'You selected {message}. Please provide your details:',
            'showForm': True,
            'selectedServices': message
        }
    elif message == 'App Development':
        response = {
            'question': 'You selected App Development. Please select a technology:',
            'options': app_dev_options
        }
    elif message == 'QA Testing':
        response = {
            'question': 'You selected QA Testing. Please select a technology:',
            'options': testing_options
        }
    elif message in testing_options:
        session['selected_services'] = ['QA Testing', message]
        response = {
            'question': f'You selected {message}. Please provide your details:',
            'showForm': True,
            'selectedServices': session['selected_services']
        }
    elif message == 'Web Development':
        response = {
            'question': 'You selected Web Development. Please select a technology:',
            'options': service_options
        }
    elif message in app_dev_options:
        session['selected_services'] = ['App Development', message]
        response = {
            'question': f'You selected {message}. Please provide your details:',
            'showForm': True,
            'selectedServices': session['selected_services']
        }
    else:
        response = {
            'question': 'Hello   Please select an option:',
            'options': ['QA Testing', 'Web Development', 'App Development', 'Hire developer']
        }

    session.modified = True  # Mark session as modified to ensure changes are saved
    emit('bot_response', response)
@socketio.on('form_submission')
def handle_form_submission(data):
    name = data.get('name')
    email = data.get('email')
    mobile = data.get('mobile')
    selected_services = data.get('selected_services', [])

    # Construct the email content
    subject = 'User Details and Selected Services'
    body = f'''
    Name: {name}
    Email: {email}
    Mobile: {mobile}

    Selected Services: {selected_services}
    '''
    
    try:
        # Construct the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email using smtplib
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        emit('form_response', {'status': 'success', 'message': 'Thank you for response.Hr will get bact to you shortly !'})
    except Exception as e:
        error_message = str(e)
        emit('form_response', {'status': 'error', 'message': error_message})
        print("Exception occurred:", error_message)

if __name__ == '__main__':
    socketio.run(app, debug=True,port=3000)
