#!/usr/bin/python3

# https://cgi.cse.unsw.edu.au/~z5129023/ass2/UNSWtalk.cgi/

import os,re,sys,time
from flask import Flask, render_template, session, request
if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")


students_dir = "dataset-medium";
# students_dir = "dataset-small";

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def login():
    return render_template('login.html')



@app.route('/check_login', methods=['POST'])
def check_login():
    # zid = request.form.get('zid', '')
    # password = request.form.get('password', '')
    # students = sorted(os.listdir(students_dir))
    # if zid not in students:
    #     return render_template('login.html',error='Unknown zid')
    # else:
    #     current_path = students_dir + '/' + zid + '/' + "student.txt"
    #     f = open(current_path,'r')
    #     data = f.readlines()
    #     f.close()
    #     for each_line in data:
    #         each_line = each_line.strip()
    #         each_list = each_line.split(': ')
    #         if each_list[0]=='password':
    #             read_password = each_list[1]
    #             break
    #     if read_password != password:
    #         return render_template('login.html',error='Wrong password')
    zid = 'z5190009'
    session['zid'] = zid
    return start()


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('zid')
    return render_template('login.html')



@app.route('/start', methods=['GET','POST'])
def start():
    flag = 0
    if 'zid' not in session:
        return render_template('login.html')
    students = sorted(os.listdir(students_dir))
    student_to_show = session['zid']
    student_to_show = request.args.get('zid', student_to_show)
    if student_to_show!=session['zid']:
        flag = 1
    student_to_show = request.form.get('cometo', student_to_show)
    if student_to_show!=session['zid']:
        flag = 1
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
        post_content.append([post_time,message])
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
    return render_template('start.html', flag=flag,
                            full_name=full_name,
                            zid = zid,
                            birthday = birthday,
                            program = program,
                            suburb = suburb,
                            img_path=img_path,
                            post_list=post_content,
                            friend_list=friend_details)



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
                message_dir[post_time] = [post_time,name_id_dir[each_friend],each_friend,message]
                post_time_list.append(post_time)
                f.close()
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
    print(result_list)
    return render_template('post_result.html',result_list=result_list,keywords=need_search)




if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
