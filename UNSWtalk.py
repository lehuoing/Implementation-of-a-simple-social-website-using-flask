#!/usr/bin/python3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os,re
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
    post_list = []
    all_data_files = sorted(os.listdir("{}/{}".format(students_dir,student_to_show)))
    for each in all_data_files:
        if re.match(r'\d+\.txt',each):
            post_list.append(each)
    post_list = sorted(post_list)
    with open(details_filename) as f:
        details = f.readlines()
    full_name = ''
    zid = ''
    birthday = ''
    program = ''
    suburb = ''
    for line in details:
        line_list = line.split(':')
        if line_list[0]=="full_name":
            full_name = line_list[1]
        elif line_list[0]=="zid":
            zid = line_list[1]
        elif line_list[0]=="birthday":
            birthday = line_list[1]
        elif line_list[0]=="program":
            program = line_list[1]
        elif line_list[0]=="home_suburb":
            suburb = line_list[1]
    f.close()
    img_path="./static/"+student_to_show+".jpg"
    try:
        f = open(image_filename,'rb')
        image_data = f.read()
        f.close()
        f = open("./static/"+student_to_show+".jpg",'wb')
        f.write(image_data)
        f.close()
    except:
        img_path = ''
    session['n'] = n + 1
    return render_template('start.html', full_name=full_name,
                            zid = zid,
                            birthday = birthday,
                            program = program,
                            suburb = suburb,
                            img_path=img_path)

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
