#!/usr/bin/python3

# https://cgi.cse.unsw.edu.au/~z5129023/ass2/UNSWtalk.cgi/

import os,re,sys,time,random
from flask import Flask, render_template, session, request, redirect, url_for
from email.utils import parseaddr
import subprocess
if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")


students_dir = "dataset-medium";
# students_dir = "dataset-small";

app = Flask(__name__)


def send_email(to,subject,message):
    mutt = [
            'mutt',
            '-s',
            subject,
            '-e', 'set copy=no',
            '-e', 'set realname=UNSWtalk',
            '--', to
    ]
    subprocess.run(
            mutt,
            input = message.encode('utf-8'),
            stderr = subprocess.PIPE,
            stdout = subprocess.PIPE)


@app.route('/', methods=['GET','POST'])
def login():
    return render_template('login.html')



@app.route('/check_login', methods=['POST'])
def check_login():
    zid = request.form.get('zid', '')
    password = request.form.get('password', '')
    students = sorted(os.listdir(students_dir))
    if zid not in students:
        return render_template('login.html',error='Unknown zid')
    else:
        current_path = students_dir + '/' + zid + '/' + "student.txt"
        f = open(current_path,'r')
        data = f.readlines()
        f.close()
        for each_line in data:
            each_line = each_line.strip()
            each_list = each_line.split(': ')
            if each_list[0]=='password':
                read_password = each_list[1]
                break
        if read_password != password:
            return render_template('login.html',error='Wrong password')
    session['zid'] = zid
    return start()


@app.route('/logout', methods=['POST'])
def logout():
    if 'zid' in session:
        session.pop('zid')
    if 'friend_list' in session:
        session.pop('friend_list')
    return render_template('login.html')



@app.route('/start', methods=['GET','POST'])
def start():
    flag = 0
    is_friend_flag = 0
    if 'zid' not in session:
        return render_template('login.html')
    students = sorted(os.listdir(students_dir))
    student_to_show = session['zid']
    student_to_show = request.args.get('zid', student_to_show)
    if student_to_show!=session['zid']:
        flag = 1
        session['curr_page'] = student_to_show
    student_to_show = request.form.get('cometo', student_to_show)
    if student_to_show!=session['zid']:
        flag = 1
        session['curr_page'] = student_to_show
    details_filename = os.path.join(students_dir, student_to_show, "student.txt")
    image_filename = os.path.join(students_dir, student_to_show, "img.jpg")
    post_list = []
    post_content = []
    number_list = []
    all_data_files = sorted(os.listdir("{}/{}".format(students_dir,student_to_show)))
    for each in all_data_files:
        if re.match(r'\d+\.txt',each):
            each_number = each.split('.')
            number_list.append(int(each_number[0]))
    number_list=sorted(number_list)
    for each_number in number_list:
        each_file = str(each_number) + '.txt'
        post_list.append(each_file)

    for each_post in range(len(post_list)-1,-1,-1):
        each_post_path = students_dir + '/' + student_to_show + '/' + post_list[each_post]
        if sys.version[0] == '2':
            f = open(each_post_path,'r')
        else:
            f = open(each_post_path,'r', encoding='utf-8')
        data = f.readlines()
        for each_line in data:
            each_line_list = each_line.split(': ')
            if each_line_list[0]=='time':
                post_time = each_line_list[1]
                post_time = re.sub(r'T',' ',post_time)
                post_time = re.sub(r'\+\d{4}','',post_time)
            if each_line_list[0]=='message':
                message = each_line_list[1]
                message = re.sub(r'\\n','<br>',message)
        post_inf = student_to_show + "/" + str(each_post) + ".txt"
        post_content.append([post_time,message,post_inf])
        f.close()

    with open(details_filename) as f:
        details = f.readlines()
    full_name = ''
    zid = ''
    birthday = ''
    program = ''
    suburb = ''
    friend_list = []
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
        elif line_list[0]=="friends":
            line_list[1] = re.sub(r'[\(\)]','',line_list[1].strip())
            friend_list = line_list[1].split(', ')
    f.close()
    # friend list
    friend_details = []
    if friend_list!=['']:
        if student_to_show==session['zid']:
            session['friend_list'] = friend_list
        if 'friend_list' in session and student_to_show in session['friend_list']:
            is_friend_flag = 1
        for each_friend in friend_list:
            current_path = students_dir + "/" + each_friend + "/" + "student.txt"
            f = open(current_path,'r')
            friend_data = f.readlines()
            f.close()
            for each_data in friend_data:
                each_list = each_data.split(':')
                if each_list[0]=="full_name":
                    friend_name = each_list[1]
                    continue
            current_path = students_dir + "/" + each_friend + "/" + "img.jpg"
            try:
                f = open(current_path,'rb')
                curr_data = f.read()
                f.close()
                f = open("./static/"+each_friend+".jpg",'wb')
                f.write(curr_data)
                f.close()
                each_path = "./static/"+each_friend+".jpg"
            except:
                each_path = ''
            friend_details.append([friend_name,each_path,each_friend])
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
    current_path = students_dir + "/" + student_to_show + "/" + "profile_text.txt"
    try:
        f = open(current_path,'r')
        profile_content = f.read()
        f.close()
    except:
        profile_content = ''
    return render_template('start.html', flag=flag,
                            is_friend_flag = is_friend_flag,
                            full_name=full_name,
                            zid = zid,
                            birthday = birthday,
                            program = program,
                            suburb = suburb,
                            img_path=img_path,
                            post_list=post_content,
                            friend_list=friend_details,
                            profile_content=profile_content)



@app.route('/result', methods=['GET','POST'])
def result():
    if 'zid' not in session:
        return render_template('login.html')
    search_item = request.form.get('search_item','')
    current_result = []
    if re.match(r'^z\d+$',search_item):
        current_path = students_dir + "/" + search_item + "/" + "student.txt"
        try:
            f = open(current_path,'r')
            result_data = f.readlines()
            f.close()
            for each_data in result_data:
                each_data = each_data.strip()
                each_list = each_data.split(': ')
                if each_list[0]=="full_name":
                    result_name = each_list[1]
                elif each_list[0]=="zid":
                    result_zid = each_list[1]
        except:
            return render_template('result.html')
        current_path = students_dir + "/" + search_item+ "/" + "img.jpg"
        try:
            f = open(current_path,'rb')
            curr_data = f.read()
            f.close()
            f = open("./static/"+search_item+".jpg",'wb')
            f.write(curr_data)
            f.close()
            result_path = "./static/"+search_item+".jpg"
        except:
            result_path = ''
        current_result.append([result_name,result_zid,result_path])
    elif search_item=='':
        return render_template('result.html')
    else:
        students = sorted(os.listdir(students_dir))
        for each_stu in students:
            current_path = students_dir + "/" + each_stu + "/" + "student.txt"
            f = open(current_path,'r')
            result_data = f.readlines()
            f.close()
            for each_data in result_data:
                each_data = each_data.strip()
                each_list = each_data.split(': ')
                if each_list[0]=="full_name":
                    result_name = each_list[1]
                elif each_list[0]=="zid":
                    result_zid = each_list[1]
            if re.search(search_item,result_name,flags=re.IGNORECASE):
                current_path = students_dir + "/" + result_zid + "/" + "img.jpg"
                try:
                    f = open(current_path,'rb')
                    curr_data = f.read()
                    f.close()
                    f = open("./static/"+result_zid+".jpg",'wb')
                    f.write(curr_data)
                    f.close()
                    result_path = "./static/"+result_zid+".jpg"
                except:
                    result_path = ''
                current_result.append([result_name,result_zid,result_path])
    return render_template('result.html', current_result=current_result)


@app.route('/posts', methods=['POST'])
def posts():
    if 'zid' not in session:
        return render_template('login.html')
    friend_list = []
    name_id_dir = {}
    message_dir = {}
    post_time_list = []
    result_list = []
    student_to_show = session['zid']
    current_path = students_dir + "/" + student_to_show + "/" + "student.txt"
    f = open(current_path,'r')
    friend_data = f.readlines()
    f.close()
    for each_data in friend_data:
        each_data = each_data.strip()
        line_list = each_data.split(': ')
        if line_list[0]=='friends':
            line_list[1] = re.sub(r'[\(\)]','',line_list[1].strip())
            friend_list = line_list[1].split(', ')
    if friend_list==['']:
        return render_template('friend_posts.html')
    for each_friend in friend_list:
        current_path = students_dir + "/" + each_friend + "/" + "student.txt"
        f = open(current_path,'r')
        friend_data = f.readlines()
        f.close()
        for each_data in friend_data:
            each_data = each_data.strip()
            line_list = each_data.split(': ')
            if line_list[0]=='full_name':
                name_id_dir[each_friend]=line_list[1]
                continue
        all_data_files = sorted(os.listdir("{}/{}".format(students_dir,each_friend)))
        for each in all_data_files:
            if re.match(r'\d+\.txt',each):
                each_path = students_dir + "/" + each_friend + "/" + each
                if sys.version[0] == '2':
                    f = open(each_path,'r')
                else:
                    f = open(each_path,'r', encoding='utf-8')
                data = f.readlines()
                f.close()
                for each_line in data:
                    each_line = each_line.strip()
                    each_line_list = each_line.split(': ')
                    if each_line_list[0]=='time':
                        post_time = each_line_list[1]
                        post_time = re.sub(r'T',' ',post_time)
                        post_time = re.sub(r'\+\d{4}','',post_time)
                    if each_line_list[0]=='message':
                        message = each_line_list[1]
                        message = re.sub(r'\\n','<br>',message)
                post_inf = each_friend + "/" + str(each)
                message_dir[post_time] = [post_time,name_id_dir[each_friend],each_friend,message,post_inf]
                post_time_list.append(post_time)
    post_time_list = sorted(post_time_list)
    post_time_list.reverse()
    for each_time in post_time_list:
        result_list.append(message_dir[each_time])
    return render_template('friend_posts.html',result_list = result_list)







@app.route('/make_post', methods=['POST'])
def make_post():
    return render_template('make_post.html')


@app.route('/save_post', methods=['POST'])
def save_post():
    student_to_show = session['zid']
    all_data_files = sorted(os.listdir("{}/{}".format(students_dir,student_to_show)))
    number_list = []
    message = request.form.get('post_content','')
    message = re.sub(r'\n','\\\\n',message)
    for each in all_data_files:
        if re.match(r'\d+\.txt',each):
            each_number = each.split('.')
            number_list.append(int(each_number[0]))
    number_list=sorted(number_list)
    if number_list!=[]:
        new_number = number_list[-1] + 1
    else:
        new_number = 0
    new_filename = str(new_number) + ".txt"
    curr_time = time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.localtime())
    current_path = "{}/{}/{}".format(students_dir,student_to_show,new_filename)
    f = open(current_path,'w')
    f.write("from: {}\n".format(student_to_show))
    f.write("message: {}\n".format(message))
    f.write("time: {}\n".format(curr_time))
    f.close()
    return render_template('make_post.html')




@app.route('/post_result', methods=['POST'])
def post_result():
    friend_list = []
    name_id_dir = {}
    message_dir = {}
    post_time_list = []
    result_list = []
    student_to_show = session['zid']
    need_search = request.form.get('search_item','')
    current_path = students_dir + "/" + student_to_show + "/" + "student.txt"
    f = open(current_path,'r')
    friend_data = f.readlines()
    f.close()
    for each_data in friend_data:
        each_data = each_data.strip()
        line_list = each_data.split(': ')
        if line_list[0]=='friends':
            line_list[1] = re.sub(r'[\(\)]','',line_list[1].strip())
            friend_list = line_list[1].split(', ')
    for each_friend in friend_list:
        current_path = students_dir + "/" + each_friend + "/" + "student.txt"
        f = open(current_path,'r')
        friend_data = f.readlines()
        f.close()
        for each_data in friend_data:
            each_data = each_data.strip()
            line_list = each_data.split(': ')
            if line_list[0]=='full_name':
                name_id_dir[each_friend]=line_list[1]
                continue
        all_data_files = sorted(os.listdir("{}/{}".format(students_dir,each_friend)))
        for each in all_data_files:
            if re.match(r'\d+\.txt',each):
                each_path = students_dir + "/" + each_friend + "/" + each
                if sys.version[0] == '2':
                    f = open(each_path,'r')
                else:
                    f = open(each_path,'r', encoding='utf-8')
                data = f.readlines()
                for each_line in data:
                    each_line = each_line.strip()
                    each_line_list = each_line.split(': ')
                    if each_line_list[0]=='time':
                        post_time = each_line_list[1]
                        post_time = re.sub(r'T',' ',post_time)
                        post_time = re.sub(r'\+\d{4}','',post_time)
                    if each_line_list[0]=='message':
                        message = each_line_list[1]
                        message = re.sub(r'\\n','<br>',message)
                if re.search(need_search,message,flags=re.IGNORECASE):
                    message_dir[post_time] = [post_time,name_id_dir[each_friend],each_friend,message]
                    post_time_list.append(post_time)
                f.close()
    post_time_list = sorted(post_time_list)
    post_time_list.reverse()
    for each_time in post_time_list:
        result_list.append(message_dir[each_time])
    if need_search == '':
        return render_template('post_result.html')
    return render_template('post_result.html',result_list=result_list,keywords=need_search)


@app.route('/edit_information', methods=['POST'])
def edit_information():
    if 'zid' not in session:
        return render_template('login.html')
    student_to_show = session['zid']
    details_filename = os.path.join(students_dir, student_to_show, "student.txt")
    with open(details_filename) as f:
        details = f.readlines()
    full_name = ''
    birthday = ''
    program = ''
    suburb = ''
    for line in details:
        line_list = line.split(': ')
        if line_list[0]=="full_name":
            full_name = line_list[1]
        elif line_list[0]=="birthday":
            birthday = line_list[1]
        elif line_list[0]=="program":
            program = line_list[1]
        elif line_list[0]=="home_suburb":
            suburb = line_list[1]
    f.close()
    current_path = students_dir + "/" + student_to_show + "/" + "profile_text.txt"
    try:
        f = open(current_path,'r')
        profile_content = f.read()
        f.close()
    except:
        profile_content = ''
    return render_template('edit_information.html',full_name=full_name,
                            birthday=birthday,program=program,suburb=suburb,profile_content=profile_content)


@app.route('/save_changeinfor', methods=['POST'])
def save_changeinfor():
    if 'zid' not in session:
        return render_template('login.html')
    student_to_show = session['zid']
    details_filename = os.path.join(students_dir, student_to_show, "student.txt")
    full_name = request.form.get('full_name','')
    birthday = request.form.get('birthday','')
    program = request.form.get('program','')
    suburb = request.form.get('suburb','')
    profile_content = request.form.get('profile_content','')
    f = open(details_filename,'r')
    data = f.readlines()
    f.close()
    need_w_data = ""
    for each in data:
        if re.search(r'full_name',each):
            each = "full_name: " + full_name + "\n"
        elif re.search(r'birthday',each):
            each = "birthday: " + birthday + "\n"
        elif re.search(r'program',each):
            each = "program: " + program + "\n"
        elif re.search(r'suburb',each):
            each = "home_suburb: " + suburb + "\n"
        need_w_data = need_w_data + each
    f = open(details_filename,'w')
    f.write(need_w_data)
    f.close()
    profile_file = request.files['file']
    if profile_file:
        img_data = profile_file.read()
        if img_data!=''.encode('utf-8'):
            current_path = os.path.join(students_dir, student_to_show, "img.jpg")
            f = open(current_path,'wb')
            f.write(img_data)
            f.close()
    current_path = students_dir + "/" + student_to_show + "/" + "profile_text.txt"
    f = open(current_path,'w')
    f.write(profile_content)
    f.close()
    return redirect(url_for('start'))


@app.route('/add_friend', methods=['POST'])
def add_friend():
    if 'zid' not in session:
        return render_template('login.html')
    student_to_show = session['zid']
    need_add = session['curr_page']
    details_filename = os.path.join(students_dir, student_to_show, "student.txt")
    f = open(details_filename,'r')
    data = f.readlines()
    f.close()
    need_w_data = ""
    for each in data:
        if re.search(r'friends',each):
            each = re.sub(r'\)',', {})'.format(need_add),each)
            each = re.sub(r'\(, ','(',each)
        need_w_data = need_w_data + each
    f = open(details_filename,'w')
    f.write(need_w_data)
    f.close()
    return redirect(url_for('start'))



@app.route('/delete_friend', methods=['POST'])
def delete_friend():
    if 'zid' not in session:
        return render_template('login.html')
    student_to_show = session['zid']
    need_d = session['curr_page']
    details_filename = os.path.join(students_dir, student_to_show, "student.txt")
    f = open(details_filename,'r')
    data = f.readlines()
    f.close()
    need_w_data = ""
    for each in data:
        if re.search(r'friends',each):
            each = re.sub(r', {}'.format(need_d),'',each)
            each = re.sub(r'\({}, '.format(need_d),'(',each)
            each = re.sub(r'\({}\)'.format(need_d),'()',each)
        need_w_data = need_w_data + each
    f = open(details_filename,'w')
    f.write(need_w_data)
    f.close()
    return redirect(url_for('start'))


@app.route('/post_comment', methods=['GET','POST'])
def post_comment():
    name_zid_dir = {}
    students = sorted(os.listdir(students_dir))
    for each_stu in students:
        current_path = students_dir + "/" + each_stu + "/" + "student.txt"
        f = open(current_path,'r')
        stu_data = f.readlines()
        f.close()
        for each_data in stu_data:
            each_data = each_data.strip()
            each_list = each_data.split(': ')
            if each_list[0]=="full_name":
                name_zid_dir[each_stu] = each_list[1]
                continue
    post_id = request.args.get('postid', '')
    current_post = students_dir + "/" + post_id
    if sys.version[0] == '2':
        f = open(current_post,'r')
    else:
        f = open(current_post,'r', encoding='utf-8')
    data = f.readlines()
    f.close()
    for each_line in data:
        each_line = each_line.strip()
        each_line_list = each_line.split(': ')
        if each_line_list[0]=='time':
            post_time = each_line_list[1]
            post_time = re.sub(r'T',' ',post_time)
            post_time = re.sub(r'\+\d{4}','',post_time)
        if each_line_list[0]=='message':
            message = each_line_list[1]
            message = re.sub(r'\\n','<br>',message)
        if each_line_list[0]=='from':
            post_from = each_line_list[1]
    curr_post_content = [name_zid_dir[post_from],post_time,message,post_from]
    postid_list = post_id.split('/')
    all_data_files = sorted(os.listdir("{}/{}".format(students_dir,postid_list[0])))
    post_file_name = postid_list[1].split('.')[0]
    comment_dir = {}
    comment_timelist = []
    result_list = []
    for each in all_data_files:
        if re.match(r'{}\-.+\.txt'.format(post_file_name),each):
            current_path = students_dir + "/" + postid_list[0] + "/" + each
            if sys.version[0] == '2':
                f = open(current_path,'r')
            else:
                f = open(current_path,'r', encoding='utf-8')
            data = f.readlines()
            f.close()
            for each_line in data:
                each_line = each_line.strip()
                each_line_list = each_line.split(': ')
                if each_line_list[0]=='time':
                    post_time = each_line_list[1]
                    post_time = re.sub(r'T',' ',post_time)
                    post_time = re.sub(r'\+\d{4}','',post_time)
                if each_line_list[0]=='message':
                    message = each_line_list[1]
                    message = re.sub(r'\\n','<br>',message)
                    m = re.search(r'z\d{7}',message)
                    if m:
                        contains_id_list = re.findall(r'z\d{7}',message)
                        for contains_id in contains_id_list:
                            change_content = "<a href=\"start?zid={}\">{}</a>".format(contains_id,name_zid_dir[contains_id])
                            message = re.sub(contains_id,change_content,message)
                if each_line_list[0]=='from':
                    comment_from = each_line_list[1]
            comment_timelist.append(post_time)
            comment_dir[post_time] = [name_zid_dir[comment_from],post_time,message,comment_from]
    comment_timelist = sorted(comment_timelist)
    comment_timelist.reverse()
    for each_time in comment_timelist:
        result_list.append(comment_dir[each_time])
    return render_template('comments.html',curr_post=curr_post_content,result_list=result_list)


@app.route('/signup', methods=['GET','POST'])
def signup():
    return render_template('signup.html')

@app.route('/confirm_email', methods=['POST'])
def confirm_email():
    zid = request.form.get('zid','')
    email_addr = request.form.get('email','')
    if not re.match(r'^z\d{7}$',zid):
        return render_template('signup.html',error="Invaild zid")
    elif os.path.exists(students_dir + '/' + zid):
        return render_template('signup.html',error="Account exists")
    if not re.match(r'^.+@.+\..+$',email_addr):
        return render_template('signup.html',error="Invaild email address")

    new_path = students_dir + "/" + zid
    os.mkdir(new_path)
    new_path = students_dir + "/" + zid + "/" + "student.txt"
    f = open(new_path,'w')
    f.write("zid: {}\n".format(zid))
    f.write("email: {}\n".format(email_addr))
    f.write("friends: ()\n")
    f.close()
    new_path = students_dir + "/" + zid + "/" + "confirm_number.txt"
    f = open(new_path,'w')
    curr_cnumber = str(random.randint(1000,9999))
    f.write(curr_cnumber)
    f.close()
    # send email
    send_email(email_addr,'New account creation','Your confirm number is {}.'.format(curr_cnumber))

    session['new_zid'] = zid
    return render_template('new_information.html',error="Confirm email has been sent!")


@app.route('/new_information', methods=['POST'])
def new_information():
    if 'new_zid' not in session:
        return render_template('login.html')

    confirm_number_path = students_dir + "/" + session['new_zid'] + "/" + "confirm_number.txt"
    f = open(confirm_number_path,'r')
    real_cnumber = f.read()
    f.close()
    confirm_number = request.form.get('confirm_number','')
    password = request.form.get('password','')
    confirm_password = request.form.get('confirm_password','')
    if confirm_number!=real_cnumber:
        return render_template('new_information.html',error="Wrong confirm number!")
    if password=='':
        return render_template('new_information.html',error="Password cannot be empty!")
    if confirm_password!=password:
        return render_template('new_information.html',error="Twice inputs password are different!")
    full_name = request.form.get('full_name','')
    birthday = request.form.get('birthday','')
    program = request.form.get('program','')
    suburb = request.form.get('suburb','')
    current_zid = session['new_zid']
    current_path = students_dir + "/" + current_zid + "/" + "student.txt"
    f = open(current_path,'a')
    if full_name!='':
        f.write("full_name: {}\n".format(full_name))
    if birthday!='':
        f.write("birthday: {}\n".format(birthday))
    if program!='':
        f.write("program: {}\n".format(program))
    if suburb!='':
        f.write("home_suburb: {}\n".format(suburb))
    f.write("password: {}\n".format(password))
    f.close()
    profile_file = request.files['file']
    if profile_file:
        img_data = profile_file.read()
        if img_data!=''.encode('utf-8'):
            current_path = os.path.join(students_dir, current_zid, "img.jpg")
            f = open(current_path,'wb')
            f.write(img_data)
            f.close()
    session.pop('new_zid')
    return render_template('login.html',error="New account created. Please login.")


@app.route('/password_recovery', methods=['GET','POST'])
def password_recovery():
    return render_template('password_recovery.html')

@app.route('/set_newpassword', methods=['POST'])
def set_newpassword():
    email = request.form.get('email','')
    if email=='':
        return render_template('password_recovery.html',error="Please input email")
    all_students = sorted(os.listdir(students_dir))
    need_recover = ''
    for each_stu in all_students:
        current_path = students_dir + "/" + each_stu + "/" + "student.txt"
        f = open(current_path,'r')
        data = f.read()
        f.close()
        if re.search(r'email: {}'.format(email),data):
            need_recover = each_stu
            break
    if need_recover=='':
        return render_template('password_recovery.html',error="Account does not exist")
    else:
        session['need_recover'] = need_recover
        new_path = students_dir + "/" + need_recover + "/" + "confirm_number.txt"
        f = open(new_path,'w')
        curr_cnumber = str(random.randint(1000,9999))
        f.write(curr_cnumber)
        f.close()

    # send email
    send_email(email,'Password recovery','Your confirm number is {}.'.format(curr_cnumber))
    return render_template('set_newpassword.html',error="Confirm email has been sent.")

@app.route('/save_password', methods=['POST'])
def save_password():
    if 'need_recover' not in session:
        return render_template('login.html')
    zid = session['need_recover']

    confirm_number_path = students_dir + "/" + zid + "/" + "confirm_number.txt"
    f = open(confirm_number_path,'r')
    real_cnumber = f.read()
    f.close()
    confirm_number = request.form.get('confirm_number','')
    password = request.form.get('password','')
    confirm_password = request.form.get('confirm_password','')
    if confirm_number!=real_cnumber:
        return render_template('set_newpassword.html',error="Wrong confirm number!")
    if password=='':
        return render_template('set_newpassword.html',error="Password cannot be empty!")
    if confirm_password!=password:
        return render_template('set_newpassword.html',error="Twice inputs password are different!")

    current_path = students_dir + "/" + zid + "/" + "student.txt"

    f = open(current_path,'r')
    data = f.readlines()
    f.close()
    need_w_data = ""
    for each in data:
        if re.search(r'password',each):
            each = "password: " + password + "\n"
        need_w_data = need_w_data + each
    f = open(current_path,'w')
    f.write(need_w_data)
    f.close()
    return render_template('login.html',error="Password recovered. Please login.")





if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
