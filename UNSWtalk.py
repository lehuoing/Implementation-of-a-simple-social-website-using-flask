#!/usr/bin/python3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os
from flask import Flask, render_template, session

# students_dir = "dataset-medium";
students_dir = "dataset-small";

app = Flask(__name__)

#Show unformatted details for student "n".
# Increment  n and store it in the session cookie

@app.route('/', methods=['GET','POST'])
@app.route('/start', methods=['GET','POST'])
def start():
    n = session.get('n', 0)
    students = sorted(os.listdir(students_dir))
    student_to_show = students[n % len(students)]
    details_filename = os.path.join(students_dir, student_to_show, "student.txt")
    image_filename = os.path.join(students_dir, student_to_show, "img.jpg")
    with open(details_filename) as f:
        details = f.read()
    f.close()
    f = open(image_filename,'rb')
    image_data = f.read()
    f.close()
    f = open("./static/"+student_to_show+".jpg",'wb')
    f.writelines(image_data)
    f.close()
    session['n'] = n + 1
    return render_template('start.html', student_details=details,img_path="./static/"+student_to_show+".jpg")

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
