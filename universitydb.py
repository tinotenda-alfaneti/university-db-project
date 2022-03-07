#the module wass used for rendering html files on the web, redirecting through the pages/addresses
from flask import Flask,render_template,request, flash, redirect, url_for
#the module was used module if for linking flask with sql.
from flask_sqlalchemy import SQLAlchemy
#the module is used to manage logins and logouts so that once a user clicks logout, they won't be able to access that page before login in again
from flask_login import UserMixin, login_user, login_required, logout_user, LoginManager
#this was used to encrypt/hash the password for admin so that even where it is saved in the database it will not be read
from werkzeug.security import generate_password_hash, check_password_hash



#setting up flask app and database objects
webapp = Flask(__name__)
webapp.config["SECRET_KEY"] = "group 5" #to be able to use sessions
webapp.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///university.db" #setting location of database.It is created if it doesnot exist
db= SQLAlchemy(webapp)
db.init_app(webapp) #initializing the flask app


#Creating table class for Students
class Students(db.Model):
    student_id = db.Column(db.Integer,primary_key=True)
    student_name = db.Column(db.String(500))
    student_number = db.Column(db.Integer)
    #constructor for the table class
    def __init__(self, student_name, student_number):
        self.student_name = student_name 
        self.student_number = student_number

#Creating table class for Departments
class Departments(db.Model):
    Dpmt_id = db.Column(db.Integer,primary_key=True)
    department_number = db.Column(db.Integer)
    department_name = db.Column(db.String(500))
    #constructor for the table class
    def __init__(self,department_name, department_number):
        self.department_name = department_name
        self.department_number = department_number

#Creating table class for Instructors
class Instructors(db.Model):
    Instructor_id = db.Column(db.Integer,primary_key=True)
    dept_id = db.Column(db.Integer, db.ForeignKey("departments.Dpmt_id"))
    instructor_name = db.Column(db.String(100))
    #constructor for the table class
    def __init__(self, instructor_name, dept_id):
        self.instructor_name = instructor_name
        self.dept_id = dept_id
        
#Creating table class for Courses       
class Courses(db.Model):
    course_id = db.Column(db.Integer,primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructors.Instructor_id"))
    course_name = db.Column(db.String(500))
    #constructor for the table class
    def __init__(self, instructor_id, course_name):
        self.instructor_id = instructor_id 
        self.course_name = course_name
        
#Creating table class for student_course       
class student_course(db.Model):
    sc_id = db.Column(db.Integer,primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.course_id"))
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"))
    #constructor for the table class
    def __init__(self, course_id, student_id):
        self.course_id =course_id 
        self.student_id=student_id
        
#Creating table class for Admin_user        
class Admin_user(db.Model, UserMixin): #UserMixin is inherited so that we may be able to hash our admin password
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(500))
    user_password = db.Column(db.String(150))
    #constructor for the table class
    def __init__(self, user_name, user_password):
        self.user_name = user_name 
        self.user_password = user_password
        
#setting up a login manager instance        
login_manager = LoginManager()
login_manager.login_view = "loginrequired"
login_manager.init_app(webapp)

@login_manager.user_loader
def load_user(id):
    return Admin_user.query.get(int(id))

#this is the page where people will be directed when trying to access a page for admins(adding/editing)
@webapp.route("/loginrequired")
def loginrequired():
    return render_template("loginrequired.html")      

#homepage
@webapp.route("/", methods=["GET","POST"])
def home():
    return render_template("homepage.html")

#students page
@webapp.route("/students", methods=["GET","POST"])
def student():
    students = Students.query.all()
    return render_template("student.html",students=students)

#login page
@webapp.route("/login", methods=["POST", "GET"])
def login():
    #data=request.form
    if request.method == "POST":
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        
        user = Admin_user.query.filter_by(user_name=user_name).first()
        if user:
            #comparing the hash of the entered password and the one in the admin_user table
            if check_password_hash(user.user_password, user_password):
                #showing/flashing a message on screen if true
                flash("Logged in successfully", category="success")
                #using the LoginManager the user will be logged in
                login_user(user, remember=False) 
                return redirect(url_for("admin_home"))
            else:
                flash("Incorrect password, Try Again", category="error")
        else:
            flash("You are not the Admin User", category="error")
    return render_template("login.html")

@webapp.route("/admin_home", methods=["GET","POST"])
#this is to make sure that you won't access this route/page with being logged in
@login_required
def admin_home():
    return render_template("admin_login.html")

@webapp.route("/studentedit", methods=["GET","POST"])
@login_required
def student_edit():
    student_name = request.form.get("student_name")
    student_number = request.form.get("student_number")
    new_student = Students(student_name, student_number)
    db.session.commit()
    students = Students.query.all()
    return render_template("studentedit.html",students=students)

@webapp.route("/studentedit/<int:student_id>", methods=["GET","POST"])
@login_required
def studentedit(student_id):
    student=Students.query.filter_by(student_id=student_id).first()
    if request.method =="POST":
        student_name = request.form.get("student_name")
        student_number = request.form.get("student_number")
        student.student_name = student_name
        student.student_number =student_number
        db.session.commit()
        students = Students.query.all()
        return render_template("studentedit.html",students=students)
    return render_template("editstudent.html",student=student)
    
@webapp.route("/addstudent", methods=["GET","POST"])
@login_required
def addstudent():
    students = Students.query.all()
    if request.method == "POST":
    
        student_name = request.form.get("student_name")
        student_number = request.form.get("student_number")   
        student = Students(student_name, student_number)
        db.session.add(student)
        db.session.commit()   
        students = Students.query.all()
        return redirect(url_for("student_edit"))
    return render_template("addstudent.html")

@webapp.route("/courses", methods=["GET","POST"])
def course():
    courses = Courses.query.all()
    if request.method == "POST":
        course_name = request.form.get("course_name")
        instructor_id = request.form.get("instructor_id")   
        course = Courses(course_name, instructor_id)
        db.session.add(course)
        db.session.commit()   
        courses = Courses.query.all()
        return render_template("course.html",courses=courses)
    return render_template("course.html",courses=courses)

@webapp.route("/clogin", methods=["POST", "GET"])
def course_login():
    #data=request.form
    if request.method == "POST":
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        user = Admin_user.query.filter_by(user_name=user_name).first()
        if user:
            if check_password_hash(user.user_password, user_password):
                flash("Logged in successfully", category="success")
                login_user(user, remember=False)
                return redirect(url_for("cadmin_home"))
            else:
                flash("Incorrect password, Try Again", category="error")
        else:
            flash("You are not the Admin User", category="error")
    return render_template("clogin.html")

@webapp.route("/cadmin_home", methods=["GET","POST"])
@login_required 
def cadmin_home():
    return render_template("admin_login_courses.html")

@webapp.route("/course_edit", methods=["GET","POST"])
@login_required 
def course_edit():
    course_name = request.form.get("course_name")
    instructor_id = request.form.get("instructor_id")
    new_course = Courses(course_name, instructor_id)
    db.session.commit()
    courses = Courses.query.all()
    return render_template("course_edit.html",courses=courses)

@webapp.route("/course_edit/<int:course_id>", methods=["GET","POST"])
@login_required 
def editcourse(course_id):
    course=Courses.query.filter_by(course_id=course_id).first()
    if request.method =="POST":
        course_name = request.form.get("course_name")
        instructor_id = request.form.get("instructor_id") 
        course.course_name = course_name
        course.instructor_id = instructor_id 
        db.session.commit()
        courses = Courses.query.all()
        return render_template("course_edit.html",courses=courses)
    return render_template("editcourse.html",course=course)

@webapp.route("/addcourse", methods=["GET","POST"])
@login_required 
def addcourse():
    courses = Courses.query.all()
    if request.method == "POST":
        course_name = request.form.get("course_name")
        instructor_id = request.form.get("instructor_id")   
        course = Courses(instructor_id, course_name)
        db.session.add(course)
        db.session.commit()   
        courses = Courses.query.all()
        return redirect(url_for("course_edit"))
    return render_template("addcourse.html")

@webapp.route("/departments", methods=["GET","POST"])
def department():
    departments = Departments.query.all()
    return render_template("department.html",departments=departments)

@webapp.route("/dlogin", methods=["POST", "GET"])
def dlogin():
    #data=request.form
    if request.method == "POST":
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        user = Admin_user.query.filter_by(user_name=user_name).first()
        if user:
            if check_password_hash(user.user_password, user_password):
                flash("Logged in successfully", category="success")
                login_user(user, remember=False)
                return redirect(url_for("dadmin_home"))
            else:
                flash("Incorrect password, Try Again", category="error")
        else:
            flash("You are not the Admin User", category="error")         
    return render_template("dlogin.html")

@webapp.route("/dadmin_home", methods=["GET","POST"])
@login_required 
def dadmin_home():
    return render_template("admin_login_dept.html")

@webapp.route("/departmentedit", methods=["GET","POST"])
@login_required 
def departmentedit():
    department_name = request.form.get("department_name")
    department_number = request.form.get("department_number")
    new_department = Departments(department_name, department_number)
    db.session.commit()
    departments = Departments.query.all()
    return render_template("departmentedit.html",departments=departments)

@webapp.route("/departmentedit/<int:Dpmt_id>", methods=["GET","POST"])
@login_required 
def edituser(Dpmt_id):
    department=Departments.query.filter_by(Dpmt_id=Dpmt_id).first()
    if request.method =="POST":
        department_name = request.form.get("department_name")
        department_number = request.form.get("department_number")
        department.department_name = department_name
        department.department_number =department_number
        db.session.commit()
        departments = Departments.query.all()
        return render_template("departmentedit.html",departments=departments)
    return render_template("editdepartment.html",department=department)

@webapp.route("/adddepartment", methods=["GET","POST"])
@login_required 
def adddepartment():
    departments = Departments.query.all()
    if request.method == "POST":
        department_name = request.form.get("department_name")
        department_number = request.form.get("department_number")
        department = Departments(department_name, department_number)
        db.session.add(department)
        db.session.commit()   
        departments = Departments.query.all()
        return redirect(url_for("departmentedit"))
    return render_template("adddepartment.html")


@webapp.route("/instructors", methods=["GET","POST"])
def instructor():
    instructors = Instructors.query.all()
    return render_template("instructors.html",instructors=instructors)

@webapp.route("/ilogin", methods=["POST", "GET"])
def ilogin():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        user = Admin_user.query.filter_by(user_name=user_name).first()
        if user:
            if check_password_hash(user.user_password, user_password):
                flash("Logged in successfully", category="success")
                login_user(user)
                return redirect(url_for("iadmin_home"))
            else:
                flash("Incorrect password, Try Again", category="error")
        else:
            flash("You are not the Admin User", category="error")
    return render_template("ilogin.html")

@webapp.route("/iadmin_home", methods=["GET","POST"])
@login_required 
def iadmin_home():
    return render_template("admin_login_inst.html")

@webapp.route("/instructorsedit", methods=["GET","POST"])
@login_required 
def instructoredit():
        instructor_name = request.form.get("instructor_name")
        dept_id = request.form.get("dept_id")   
        instructor = Instructors(instructor_name, dept_id)
        db.session.commit()   
        instructors = Instructors.query.all()
        return render_template("instructorsedit.html",instructors=instructors)


@webapp.route("/instructorsedit/<int:Instructor_id>", methods=["GET","POST"])
@login_required 
def iedituser(Instructor_id):
    instructor=Instructors.query.filter_by(Instructor_id=Instructor_id).first()
    if request.method =="POST":
        instructor_name = request.form.get("instructor_name")
        dept_id = request.form.get("dept_id")   
        instructor.instructor_name= instructor_name
        instructor.dept_id=dept_id
        db.session.commit()   
        instructors = Instructors.query.all()
        return render_template("instructorsedit.html",instructors=instructors)
    return render_template("editinstructor.html",instructor=instructor)

@webapp.route("/addinstructors", methods=["GET","POST"])
@login_required 
def addinstructor():
    instructors = Instructors.query.all()
    if request.method == "POST":
        instructor_name = request.form.get("instructor_name")
        dept_id = request.form.get("dept_id")   
        instructor = Instructors(instructor_name, dept_id)
        db.session.add(instructor)
        db.session.commit()   
        instructors = Instructors.query.all()
        return redirect(url_for("instructoredit"))
    return render_template("addinstructor.html")


@webapp.route("/studentcourse", methods=["GET","POST"])
def studentcourse():
    studentcourses = student_course.query.all()
    if request.method == "POST":
        course_id = request.form.get("course_id")
        student_id = request.form.get("student_id")   
        studentcourse = student_course(course_id, student_id)
        db.session.add(studentcourse)
        db.session.commit()   
        studentcourses = student_course.query.all()
        return render_template("studentcourse.html",studentcourses=studentcourses)
    return render_template("studentcourse.html",studentcourses=studentcourses)

@webapp.route("/sclogin", methods=["POST", "GET"])
def sclogin():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        user = Admin_user.query.filter_by(user_name=user_name).first()
        if user:
            if check_password_hash(user.user_password, user_password):
                flash("Logged in successfully", category="success")
                login_user(user, remember=False)
                return redirect(url_for("scadmin_home"))
            else:
                flash("Incorrect password, Try Again", category="error")
        else:
            flash("You are not the Admin User", category="error")  
    return render_template("sclogin.html")


@webapp.route("/scadmin_home", methods=["GET","POST"])
@login_required 
def scadmin_home():
    return render_template("admin_login_sc.html")

@webapp.route("/studentcourseedit", methods=["GET","POST"])
@login_required 
def studentcourseedit():
        course_id = request.form.get("course_id")
        student_id = request.form.get("student_id")   
        studentcourse.course_id = course_id
        studentcourse.student_id = student_id
        db.session.commit()   
        studentcourses = student_course.query.all()
        return render_template("studentcourseedit.html",studentcourses=studentcourses)

@webapp.route("/studentcourseedit/<int:sc_id>", methods=["GET","POST"])
@login_required 
def scedituser(sc_id):
    studentcourse = student_course.query.filter_by(sc_id=sc_id).first()
    if request.method =="POST":
        course_id = request.form.get("course_id")
        student_id = request.form.get("student_id")   
        studentcourse.course_id = course_id
        studentcourse.student_id = student_id
        db.session.commit()   
        studentcourses = student_course.query.all()
        return render_template("studentcourseedit.html",studentcourses=studentcourses)
    return render_template("editstudentcourse.html",studentcourse=studentcourse)

@webapp.route("/addstudentcourse", methods=["GET","POST"])
@login_required 
def addstudentcourse():
    studentcourse = student_course.query.all()
    if request.method == "POST":
        course_id = request.form.get("course_id")
        student_id = request.form.get("student_id")   
        studentcourse= student_course(course_id, student_id)
        db.session.add(studentcourse)
        db.session.commit()   
        studentcourses = student_course.query.all()
        return redirect(url_for("studentcourseedit"))
    return render_template("addstudentcourse.html")

@webapp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


#This was used to create the login details for the Admin User. We commented it out so that it won't appear on the webpage 
"""
@webapp.route("/signin", methods=["POST", "GET"])
def signin():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        user = Admin_user.query.filter_by(user_name=user_name).first()
        if user:
            flash("user_name already exist", category="error")
        
        if len(user_name) <4:
            flash("Username must greater be than 4", category="error")
        
        elif len(user_password)<3:
            flash("Password must be greater than 3", category="error")
        else:
            #generating a hashed password using the method sha256
            new_user = Admin_user(user_name=user_name, user_password=generate_password_hash(user_password, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home"))
            flash("Account created", category="success")
            
    return render_template("admin_creating.html")
"""
if __name__=="__main__":
    db.create_all()
    webapp.run()