from io import SEEK_CUR
from flask.globals import session ###
from flask import Flask, render_template, url_for, request, flash, redirect, session
from forms import ForgotPasswordForm, RegistrationForm, LoginForm, PasswordResetForm
from flask_mysqldb import MySQL
import emails as e
import datetime
import random
#from yaml
import mysql.connector
from flask_session import Session

app = Flask(__name__) # instatiating the flask module to this variable so python knows where to look for 

'''
try:
    con = mysql.connector.connect(host='localhost', user='root',passwd='raccoon_()_123')
    if con.is_connected():
        cur = con.cursor()
        cur.execute("use projectapp")
    else:
        print("some error")
     
except mysql.connector.Error as e:
    print(e)
 '''
#Configuring MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'raccoon_()_123'
app.config['MYSQL_DB'] = 'projectapp'
app.config['SECRET_KEY'] = 'c5b001929f7e9cba838cd7a922db0dec'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"       #stores in the hard drive (stored under a /flask_session folder in your config directory)

'''
mysql> create table Users(UserID int auto_increment, username varchar(50), email varchar(120), password varchar(30),primary key(UserID));
Query OK, 0 rows affected (1.59 sec)

mysql> desc users;
+----------+--------------+------+-----+---------+----------------+
| Field    | Type         | Null | Key | Default | Extra          |
+----------+--------------+------+-----+---------+----------------+
| UserID   | int          | NO   | PRI | NULL    | auto_increment |
| username | varchar(50)  | YES  |     | NULL    |                |
| email    | varchar(120) | YES  |     | NULL    |                |
| password | varchar(30)  | YES  |     | NULL    |                |
+----------+--------------+------+-----+---------+----------------+
4 rows in set (0.13 sec)
'''
Session(app)
mysql = MySQL(app)




# Routes

@app.route("/", methods=['GET','POST']) #default page that opens
#the home page- where the todolist will show up
def home():
    if not session.get("email"):
        return redirect("/login")
    cur = mysql.connection.cursor()
    cur.execute("select username from users where userid={}".format(session['userid']))
    name=cur.fetchone()[0]
    quote=e.quotes
    cur.execute("select count(*) from tasks where userid={} and completed=1".format(session['userid']))
    done=cur.fetchall()[0][0]*360
    cur.execute("select count(*) from tasks where userid={}".format(session['userid']))
    try:
        done/=cur.fetchall()[0][0]
    except:
        done="Complete more tasks to access this data"
    perfectdays=0
    cur.execute("select distinct deadline from tasks where userid={}".format(session['userid']))
    deadlines=[i[0] for i in cur.fetchall()]
    for deadline in deadlines:
        cur.execute("select dateofcompletion<=deadline from tasks where userid={} and deadline={}".format(session['userid'], deadline))
        lst=[i[0] for i in cur.fetchall()]
        if deadline not in lst:
            perfectdays+=1
    today=datetime.datetime.now()
    cur.execute("select count(*) from tasks where userid={} and completed=1 and week(dateofcompletion,0)={}".format(session['userid'], today.strftime("%U").lstrip("0")))
    thisweek=cur.fetchall()[0][0]
    cur.execute("select count(*) from tasks where userid={} and completed=1 and month(dateofcompletion)={}".format(session['userid'], today.strftime("%m").lstrip("0")))
    thismonth=cur.fetchall()[0][0]
    cur.execute("select subject from tasks where userid={} and completed=1".format(session['userid']))
    result=[i[0] for i in cur.fetchall()]
    subjects={sub:result.count(sub) for sub in ["Maths", "Physics", "Chemistry", "Computer Science"]}
    submax=max(subjects.values())
    cur = mysql.connection.cursor()
    cur.execute("select count(*) from usersub1 where userid={} and datedone is not null group by month(datedone)".format(session['userid']))
    lst=[i[0] for i in cur.fetchall()]
    if len(lst):
        sum1=0
        for i in lst:
            sum1+=i
        average=sum1/len(lst)
    else:
        average=0
    cur.execute("select task from tasks where userid={} and completed=1 order by dateofcompletion desc".format(session['userid']))
    tasks=[i[0] for i in cur.fetchall()][:5]
    isdone=bool(tasks)
    d={}
    for sub in ["chemistry","physics","math","cs"]:
        cur.execute("select chaptername from chapters, usersub1 where chapters.chnum=usersub1.chnum and userid={} and done=0 and sub='{}'".format(session['userid'], sub))
        result=[i[0] for i in cur.fetchall()]
        d[sub]=result
    email=session["email"]
    return render_template('home.html', title="Dashboard",quote=random.choice(quote),done=str(done)+"deg",d=d,recent=tasks,isdone=isdone,thisweek=thisweek,thismonth=thismonth,perfectdays=perfectdays,subjects=subjects,submax=submax,name=name,average=average, email=email)

#study.html
@app.route("/study")
def study():
    cur = mysql.connection.cursor()
    d={}
    for sub in ["math","physics","cs","chemistry"]:
        cur.execute("select count(*) from usersub1, chapters where usersub1.chnum=chapters.chnum and done=1 and userid={} and sub='{}' and term=1".format(session['userid'], sub))
        done=cur.fetchall()[0][0]
        cur.execute("select count(*) from chapters where term=1")
        total=cur.fetchall()[0][0]
        term1=done*100/total
        cur.execute("select count(*) from usersub1, chapters where usersub1.chnum=chapters.chnum and done=1 and userid={} and sub='{}' and term=2".format(session['userid'], sub))
        done=cur.fetchall()[0][0]
        cur.execute("select count(*) from chapters where term=2")
        total=cur.fetchall()[0][0]
        term2=done*100/total
        d[sub]=(term1, term2)
    return render_template("study.html",d=d)


@app.route("/updatechap/<sub>", methods=['GET','POST'])
def update_chapter(sub):
    cur = mysql.connection.cursor()
    if sub in ["math","phy","chem","cs"]:
        d={"math":"math","phy":"physics","chem":"chemistry","cs":"cs"}
        
        cur.execute("select usersub1.chnum, chaptername from usersub1,chapters where usersub1.chnum=chapters.chnum and done=0 and userid={} and sub='{}'".format(session['userid'], d[sub]))
        chaps={i[0]:i[1] for i in cur.fetchall()}
        #return str(chaps)
        if request.method == 'POST':
            data=request.form
            chdone=tuple(int(i) for i in data.keys())
            if len(chdone)==1:
                cur.execute(f"update usersub1 set done=1 where chnum={chdone[0]}")
                today=datetime.date.today()
                formatted_date=today.strftime("%Y-%m-%d")
                cur.execute(f"update usersub1 set datedone=str_to_date('{formatted_date}','%Y-%m-%d') where chnum={chdone[0]}")
                mysql.connection.commit()
                return redirect("/study")
            elif len(chdone)>1:
                cur.execute(f"update usersub1 set done=1 where chnum in {chdone}")
                today=datetime.date.today()
                formatted_date=today.strftime("%Y-%m-%d")
                cur.execute(f"update usersub1 set datedone=str_to_date('{formatted_date}','%Y-%m-%d') where chnum in {chdone}")
                mysql.connection.commit()
                return redirect("/study")
        return render_template("updatechap.html",chaps=chaps)


@app.route("/logout")
def logout():
    session['login'] = False
    session.pop('loggedin', None)
    session.pop("email",None)
    session.pop("userid",None)
    session.pop("password",None)
    session.pop("username",None)
    #flash('You have been logged out!', 'success')
    return redirect(url_for('login'))


@app.route("/calendar", methods=["GET","POST"])
def calendar():
    return render_template("calendar.html")

@app.route("/calendar/<date>", methods=["GET","POST"])
def showtasks(date):
    month, day, year=[int(i) for i in date.split("-")]
    date2=datetime.date(year,month,day)
    today=datetime.date.today()
    shoulddisablebutton=(today<date2)
    formatted_date = date2.strftime('%Y-%m-%d')
    prettydate=date2.strftime("%A, %B %d, %Y")
    cur = mysql.connection.cursor()
    cur.execute("select task, subject from tasks where userid={} and deadline=str_to_date('{}','%Y-%m-%d')".format(session['userid'], formatted_date))
    tasks=cur.fetchall()
    return render_template("date.html",tasks=tasks,prettydate=prettydate,urldate=date,boolean=shoulddisablebutton)


@app.route("/login", methods=['GET','POST']) 
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("use projectapp")
        userDetails = request.form #details from whatever's entered in the form section of the registration page
        email = userDetails['email'] # the input under name 'email'
        password= userDetails['password']
        cur.execute("select userid,username,email,password,userid from users")
        a=cur.fetchall()
        #return str(a[3][2])+" "+email
        for i in a:
            if i[2]==email and i[3]==password:
                userid = i[0]
                username = i[1]
                session['login'] = True
                session['userid'] = int(userid)
                session['username'] = username
                session['password'] = password
                session["email"] = email #flask session code, remember login trial
                cur.close
                flash('You have been logged in!', 'success')
                cur = mysql.connection.cursor()
                #sq_alter = "ALTER TABLE TASKS ALTER COLUMN USERID SET DEFAULT {}".format(session['userid'])
                #cur.execute(sq_alter)
                mysql.connection.commit()
                cur.close()
                '''
                cur = mysql.connection.cursor()
                sq_alter = "ALTER TABLE TASKS ALTER COLUMN USERID SET DEFAULT {}".format(session['userid'])
                cur.execute(sq_alter)
                mysql.connection.commit()
                cur.close()
                '''
                return redirect(url_for('home')) # 'home' is the route NAME not the link (it's def home())
               
        #flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title="Login", form=form)



@app.route("/register", methods=['GET','POST']) #aka sign-up page- where a new user makes an account
# get request- display the form to the user     post request- store the details on to the db
def register():
    form = RegistrationForm()
    #if form.validate_on_submit():
        #flash(f'Account created for {form.username.data}!','success')
        #return redirect(url_for('home')) # 'home' is the route NAME not the link (it's def home())
    if request.method == 'POST': 
        #submit button was hit and now the data has to be stored onto db
        # Fetch form data
        cur = mysql.connection.cursor()
        userDetails = request.form #details from whatever's entered in the form section of the registration page
        username = userDetails['username'] # the input undered the input name 'username'
        email = userDetails['email']
        password= userDetails['password']
        cur.execute("use projectapp")
        cur.execute("select * from users")
        all=cur.fetchall()
        count=0
        for i in all:
            if email in i:
                count+=1
        if count==0:
            cur.execute("insert into users(username, email, password) values(%s,%s,%s)",(username,email,password))
            mysql.connection.commit()
            cur.execute(f"select userid from users where username='{username}'")
            uid=cur.fetchall()[0][0]
            cur.execute(f"insert into usersub1(userid,chnum) select {uid}, chnum from chapters")
        else:
            return redirect(url_for('register'))

        mysql.connection.commit()
        cur.close()

        cur = mysql.connection.cursor()
        cur.execute("select userid,username,email,password from users")
        a=cur.fetchall()
        for i in a:
            if i[2]==email and i[3]==password:
                userid = i[0]
                username = i[1]
                cur.close()
                #flash('Hello! {}'.format(username), 'success')
                cur = mysql.connection.cursor()
                sq_alter = "ALTER TABLE TASKS ALTER COLUMN USERID SET DEFAULT {}".format(userid)
                cur.execute(sq_alter)

                mysql.connection.commit()
                cur.close()
                #cur = mysql.connection.cursor()
                session['login'] = True
                session['userid'] = int(userid)
                session['username'] = username
                session['password'] = password
                session["email"] = email #flask session code, remember login trial

        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('home')) # 'home' is the route NAME not the link (it's def home())
    
    
    return render_template('register.html', title="Register", form=form)

@app.route('/forgotpassword', methods=['GET','POST'])
def forgotpassword():
    error = None
    message = None
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("use projectapp")
        global email
        userDetails = request.form
        email = userDetails['email']
        cur.execute("select email,userid from users")
        registered_emails=cur.fetchall()
        for i in registered_emails:
            if i[0]==email:
                #return i[1]
                e.resetpassword(i[0])
                #return redirect(url_for('verification'))

    return render_template('forgotpassword.html',form=form, error=error, message = message)

@app.route('/resetpassword/<email>', methods=['GET','POST'])
def resetpassword(email):
    error = None
    message = None
    form = PasswordResetForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("use projectapp")
        userDetails = request.form
        email = userDetails['email']
        password = userDetails['new_password']
        cur.execute(f"update users set password=%s where email=%s",(password,email))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('home'))
        '''</div>
        <!-- div><button><a href="{{ url_for('resetpassword')}}">Reset Password</a></button></div -->
        </div>  '''
    return render_template('resetpassword.html',form=form, error=error, message = message, email=email)

'''
@app.route('/forgotpassword/verification',methods=['GET','POST'])
def verification():
    code=''
    for i in range(4):
        code+=str(random.randint(0,9))
    e.verification(email,code)
    code = str(code)
    #return code
    if request.method == 'POST':
        verification_details = request.form
        vcode = verification_details['vcode']
        return (code,vcode)
        if vcode == code:
            #return redirect(url_for('reset_password'))
            return "success"
        else:
            return "fail" 
    return render_template('verification.html',code=code)
'''

###MOHI'S CODE
'''
@app.route("/mytodo" , methods = ['GET' , 'POST']) #url to go to in order to display the to do list
def index():
    cur = mysql.connection.cursor()
    resultval = cur.execute("SELECT * FROM TASKS WHERE USERID = {}".format(session['userid']))   #returns number of rows #add where clause later
    if resultval>0:
        todo_list_a = cur.fetchall()
        cur.close()
        lstouter = []
        for item in todo_list_a:
                
            taskid = item[0]
            task = item[1]
            deadline = item[2]
            completed = item[3]
            dateofcompletion = item[4]
            subject = item[5]
            userid = item[6]
            chnum = item[7]
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM CHAPTERS")
            chaptersexisting = cur.fetchall() #a tuple of tuples(rows in table chapters)
            cur.close()
            lst_chnums = []
            for i in chaptersexisting:
                chapternum = int(i[0])
                lst_chnums.append(chapternum)

            if chnum in lst_chnums:
                cur = mysql.connection.cursor()
                cur.execute("SELECT CHAPTERNAME FROM CHAPTERS WHERE CHNUM = {}".format(chnum))
                chapternamefetch = cur.fetchall()
                chaptername = chapternamefetch[0][0]
                cur.close()
                lstinner = [taskid, task, deadline, completed, dateofcompletion, subject, userid, chaptername]
                lstouter.append(lstinner)
            else:
                flash("Please select an existing chapter", "danger")
                

            todo_list = lstouter
        #return str(lstouter)
        return render_template("todo.html" , todo_list = todo_list)
    else:
        cur.close()
        #return render_template('create to do list.html')
        return redirect("/mytodo/add")
        

@app.route("/mytodo/add" , methods = ['GET', 'POST'])
def add():
    if request.method == 'POST':
        #Fetching form data in form of dictionary

        todo_list = request.form 
        task = todo_list['task']
        deadline = todo_list['deadline']
        subject = todo_list['subject']
        try:
            chnum = int(todo_list['chnum'])
        except:
            flash("Please select a valid chapter code","danger")
            return redirect(url_for('index'))

        if subject == '':
            flash("Please select a subject","danger")
        else:
            checking = 0            #checking becomes 1 when chapter falls under subject, remains zero otherwise
            cur = mysql.connection.cursor()
            cur.execute("SELECT CHNUM, CHAPTERNAME FROM CHAPTERS")
            fetchedresult = cur.fetchall()  #tuple of tuples
            fetchedresult_list = []
            for a in fetchedresult:
                fetchedresult_innerlist = [a[0],a[1]]
                fetchedresult_list.append(fetchedresult_innerlist)
                #now fetchedresult_list is a list of each row as a list. innerlist[0] is chapternumber correspoding to chapter name innerlist[1]
            cur.close()
            if chnum >= 1:
                cur = mysql.connection.cursor()
                if chnum < 15:
                    #subject is physics
                    if subject == "Physics":
                        checking = 1
                    else:
                        flash("The chosen chapter does not belong to the selected subject. Try again.","danger")                    
                else:
                    if chnum < 31:
                        #subject is chemistry
                        if subject == "Chemistry":
                            checking = 1
                        else:
                            flash("The chosen chapter does not belong to the selected subject. Try again.","danger")
                    else:
                        if chnum < 44:
                            #subject is maths
                            if subject == "Math":
                                checking = 1
                            else:
                                flash("The chosen chapter does not belong to the selected subject. Try again.","danger")                            
                        else:
                            if chnum <= 58:
                                #subject is cs
                                if subject == "CS":
                                    checking = 1
                                else:
                                    flash("The chosen chapter does not belong to the selected subject. Try again.","danger")

                            else:
                                flash("Please enter a valid subject code", "danger")
            else:
                flash("Please enter select a valid subject code", "danger")

            if checking == 1:
                #checking if user has entered a date
                if deadline == '':
                    flash("Invalid Date","danger")
                else:
                    #checking if the date entered is on or after today
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT CURDATE()")
                    currentdate_tuple = cur.fetchone()
                    currentdate = str(currentdate_tuple[0])
                    cur.close()
                    if str(deadline) < currentdate:
                        flash("Invalid Date","danger")
                    else:
                        cur = mysql.connection.cursor()                        
                        cur.execute("INSERT INTO TASKS (task , deadline, subject, chnum, userid) VALUES (%s,%s,%s,%s,%s)", (task, deadline,subject,chnum,session['userid']))
                        e.reminder(task,session["email"], session['username'], deadline)
                        mysql.connection.commit()
                        cur.close()
                        return redirect(url_for('index'))                   
            else:
                #flash("The chosen chapter does not belong to the selected subject. Try again.","danger")
                pass
    return render_template('todo.html')
'''

@app.route("/mytodo" , methods = ['GET' , 'POST']) #url to go to in order to display the to do list
def index():
    cur = mysql.connection.cursor()
    resultval = cur.execute("SELECT * FROM TASKS WHERE USERID = {}".format(session['userid']))   #returns number of rows #add where clause later
    if resultval>0:
        todo_list_a = cur.fetchall()
        cur.close()
        lstouter = []
        for item in todo_list_a:
                
            taskid = item[0]
            task = item[1]
            deadline = item[2]
            completed = item[3]
            dateofcompletion = item[4]
            subject = item[5]
            userid = item[6]
            chnum = item[7]
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM CHAPTERS")
            chaptersexisting = cur.fetchall() #a tuple of tuples(rows in table chapters)
            cur.close()
            lst_chnums = []
            for i in chaptersexisting:
                chapternum = int(i[0])
                lst_chnums.append(chapternum)

            if chnum in lst_chnums:
                cur = mysql.connection.cursor()
                cur.execute("SELECT CHAPTERNAME FROM CHAPTERS WHERE CHNUM = {}".format(chnum))
                chapternamefetch = cur.fetchall()
                chaptername = chapternamefetch[0][0]
                cur.close()
                lstinner = [taskid, task, deadline, completed, dateofcompletion, subject, userid, chaptername]
                lstouter.append(lstinner)
            else:
                flash("Please select an existing chapter", "danger")
                

            todo_list = lstouter
        #return str(lstouter)
        return render_template("list.html" , todo_list = todo_list)
    else:
        cur.close()
        #return render_template('create to do list.html')
        return redirect("/mytodo/add")
        

@app.route("/mytodo/add" , methods = ['GET', 'POST'])
def add():
    if request.method == 'POST':
        #Fetching form data in form of dictionary

        todo_list = request.form 
        task = todo_list['task']
        deadline = todo_list['deadline']
        subject = todo_list['subject']
        try:
            chnum = int(todo_list['chnum'])
        except:
            flash("Please select a valid chapter code","danger")
            return redirect(url_for('index'))

        if subject == '':
            flash("Please select a subject","danger")
        else:
            checking = 0            #checking becomes 1 when chapter falls under subject, remains zero otherwise
            cur = mysql.connection.cursor()
            cur.execute("SELECT CHNUM, CHAPTERNAME FROM CHAPTERS")
            fetchedresult = cur.fetchall()  #tuple of tuples
            fetchedresult_list = []
            for a in fetchedresult:
                fetchedresult_innerlist = [a[0],a[1]]
                fetchedresult_list.append(fetchedresult_innerlist)
                #now fetchedresult_list is a list of each row as a list. innerlist[0] is chapternumber correspoding to chapter name innerlist[1]
            cur.close()
            if chnum >= 196:
                cur = mysql.connection.cursor()
                if chnum < 210:
                    #subject is physics
                    if subject == "Physics":
                        checking = 1
                    else:
                        flash("The chosen chapter does not belong to the selected subject. Try again.","danger")                    
                else:
                    if chnum < 226:
                        #subject is chemistry
                        if subject == "Chemistry":
                            checking = 1
                        else:
                            flash("The chosen chapter does not belong to the selected subject. Try again.","danger")
                    else:
                        if chnum < 239:
                            #subject is maths
                            if subject == "Math":
                                checking = 1
                            else:
                                flash("The chosen chapter does not belong to the selected subject. Try again.","danger")                            
                        else:
                            if chnum <= 253:
                                #subject is cs
                                if subject == "CS":
                                    checking = 1
                                else:
                                    flash("The chosen chapter does not belong to the selected subject. Try again.","danger")

                            else:
                                flash("Please enter a valid subject code", "danger")
            else:
                flash("Please enter select a valid subject code", "danger")

            if checking == 1:
                #checking if user has entered a date
                if deadline == '':
                    flash("Invalid Date","danger")
                else:
                    #checking if the date entered is on or after today
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT CURDATE()")
                    currentdate_tuple = cur.fetchone()
                    currentdate = str(currentdate_tuple[0])
                    cur.close()
                    if str(deadline) < currentdate:
                        flash("Invalid Date","danger")
                    else:
                        cur = mysql.connection.cursor()                        
                        cur.execute("INSERT INTO TASKS (task , deadline, subject, chnum) VALUES (%s,%s,%s,%s)", (task, deadline,subject,chnum))
                        mysql.connection.commit()
                        cur.close()
                        return redirect(url_for('index'))                   
            else:
                #flash("The chosen chapter does not belong to the selected subject. Try again.","danger")
                pass
    return render_template('todo.html')

@app.route("/mytodo/update/<int:todo_id>") 
def update(todo_id):
    #changing task status from not completed to completed and vice versa
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM TASKS WHERE TASK_ID = {}".format(todo_id))
    todo = cur.fetchone()
    cur_id = todo[0]
    cur_status = todo[3] #status refers to completed or not
    changed_status = int(not(cur_status))
    if changed_status == 0:
        date_compltion = "NULL"
    else:
        date_compltion = "CURDATE()"
    cur.close()

    cur = mysql.connection.cursor() #closing and creating another cursor for the sake of clarity
    sq_alter = "UPDATE TASKS SET COMPLETED = {0}, DATEOFCOMPLETION = {1} WHERE TASK_ID = {2}".format(changed_status, date_compltion, todo_id)
    cur.execute(sq_alter)
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("index"))

@app.route("/mytodo/delete/<int:todo_id>")
def delete(todo_id):
    #deleting a task from the database and display
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM TASKS WHERE TASK_ID = {}".format(todo_id))
    todo = cur.fetchone()
    cur_id = todo[0]
    sq_delete = "DELETE FROM TASKS WHERE TASK_ID = {}".format(cur_id)
    cur.execute(sq_delete)
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("index"))

if __name__=='__main__': # type "python Todolist.py" to get the web server start working
    app.run(debug=True)
