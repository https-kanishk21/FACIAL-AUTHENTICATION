import os
import cv2
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace 'your_secret_key' with a strong random string.

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    name = request.form['name']
    email = request.form['email']

    # Capture the user's face
    capture_face(name)

    # Perform face recognition
    if authenticate_face(name):
        session['authenticated'] = True
        session['name'] = name
        session['email'] = email
        return redirect('/welcome')
    else:
        session['authenticated'] = False
        return redirect('/')

@app.route('/welcome')
def welcome():
    authenticated = session.get('authenticated', False)
    if authenticated:
        name = session['name']
        email = session['email']
        return render_template('welcome.html', name=name, email=email)
    else:
        return redirect('/')

@app.route('/a')
def a():
    name = request.args.get('name', None)
    email = request.args.get('email', None)
    session['my_var'] = name
    session['my_value'] = email
    return redirect(url_for('b'))

@app.route('/b')
def b():
    name = session.get('my_var', None)
    email = session.get('my_value', None)
    return f"Name: {name}, Email: {email}"

def capture_face(name):
    # Create a folder to store the captured faces
    if not os.path.exists('faces'):
        os.makedirs('faces')

    # Initialize the webcam
    capture = cv2.VideoCapture(0)

    # Set the video width and height
    capture.set(3, 640)
    capture.set(4, 480)

    # Use the Haar cascade to detect faces
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = capture.read()

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Display the frame
        cv2.imshow('Capture', frame)

        # Capture and save the face when 's' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('s'):
            face = gray[y:y + h, x:x + w]
            cv2.imwrite('faces/{}.jpg'.format(name), face)
            break

    # Release the capture and destroy the windows
    capture.release()
    cv2.destroyAllWindows()

def authenticate_face(name):
    # Load the saved face image
    saved_face = cv2.imread('faces/{}.jpg'.format(name), cv2.IMREAD_GRAYSCALE)

    # Initialize the webcam for face recognition
    capture = cv2.VideoCapture(0)

    # Set the video width and height
    capture.set(3, 640)
    capture.set(4, 480)

    # Use the Haar cascade to detect faces
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = capture.read()

        # Convert the frame to grayscale for face recognition
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Perform face recognition on each detected face
        for (x, y, w, h) in faces:
            face = gray[y:y + h, x:x + w]

            # Compare the detected face with the saved face
            result = cv2.matchTemplate(face, saved_face, cv2.TM_CCOEFF_NORMED)
            similarity = result[0][0]

            # Set a threshold for face recognition
            threshold = 0.8

            if similarity > threshold:
                # Face recognized
                capture.release()
                cv2.destroyAllWindows()
                return True

        # Display the frame
        cv2.imshow('Authenticate', frame)

        # Break the loop when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and destroy the windows
    capture.release()
    cv2.destroyAllWindows()

    # Face not recognized
    return False

if __name__ == '__main__':
    app.run()