import calendar
import os
from sys import platform
import numpy as np
import cv2
import keras
from keras.models import Model,load_model
from flask import Flask, render_template, url_for, request, redirect, session, flash, Response, make_response
from datetime import datetime, timedelta
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import random
import hashlib
import shutil
from sqlalchemy import func, ForeignKey, extract, desc


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def verify_login(email, password):
    query = User.query.filter(User.email == email, User.password == password)
    result = query.first()
    if result:
        return True
    else:
        return False


# el method de btala3 3dad el tests bta3et al user by id w ht3ml return l list feha al tests
def get_tests_results():
    if session.get('user'):
        query = Test.query.filter(Test.user_id == session.get('user'))\
            .order_by(desc(Test.id))
        results = query.all()
        return results
    return []


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#


app = Flask(__name__)

# configuration of mail (Password Recovey)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'FlaskappGP@gmail.com'
app.config['MAIL_PASSWORD'] = 'flaskapp123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users_Data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(days=.5)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # bio = db.Column(db.Text)

    def __init__(self, name, password, email, phone):
        self.name = name
        self.password = password
        self.email = email
        self.phone = phone


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    patient_name = db.Column(db.String(50), nullable=False)
    patient_gender = db.Column(db.Integer, nullable=False)
    patient_age = db.Column(db.Integer, nullable=False)
    patient_phone = db.Column(db.String(50), nullable=False)

    result = db.Column(db.Text, nullable=False)
    note = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey(User.id))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship('User', foreign_keys='Test.user_id')



class ForgetKeys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey(User.id))
    key = db.Column(db.Text, nullable=False)
    date_expired = db.Column(db.DateTime, default=(datetime.utcnow() + timedelta(minutes=10)))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship('User', foreign_keys='ForgetKeys.user_id')


@app.context_processor
def inject_now():
    return {
        'now': datetime.utcnow(),
        'user': User.query.filter_by(id=session.get('user')).first()
    }


# Root Route

@app.route('/')
def dashboard():
    
    if session.get('user'):
        
        total_tests = Test.query.count()

        tests_month = db.session.query(Test) \
            .filter(extract('month', Test.date_created) == datetime.today().month).count()

        tests = Test.query.filter_by(user_id=session.get('user')).all()
        monthly_tests = list(filter(lambda x: (x.date_created.date().month == datetime.today().date().month), tests))
        today_tests = list(filter(lambda x: (x.date_created.date() == datetime.today().date()), tests))

        total_by_month = db.session.query(func.count(Test.id).label('id'),
                                          extract('month', Test.date_created)). \
            filter(Test.user_id != session.get('user')). \
            group_by(extract('month', Test.date_created)).all()

        user_by_month = db.session.query(func.count(Test.id).label('id'),
                                         extract('month', Test.date_created)). \
            filter_by(user_id=session.get('user')). \
            group_by(extract('month', Test.date_created)).all()

        chart_labels_total = [calendar.month_name[label[1]] for label in total_by_month]
        chart_data_total = [label[0] for label in total_by_month]

        chart_labels_user = [calendar.month_name[label[1]] for label in user_by_month]
        chart_data_user = [label[0] for label in user_by_month]

        return render_template('dashboard.html',
                               total_tests=total_tests,
                               tests_month=tests_month,
                               tests=tests,
                               monthly_tests=monthly_tests,
                               today_tests=today_tests,
                               chart_labels_total=chart_labels_total,
                               chart_data_total=chart_data_total,
                               chart_labels_user=chart_labels_user,
                               chart_data_user=chart_data_user)
    else:
        return render_template('login.html')


# Authorization Routes

@app.route('/auth/login/perform', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ba5od al data mn al user mn saf7et al html
        email = request.form['email']
        password = (hashlib.md5(request.form['password'].encode())).hexdigest()

        # hena h3ml verification l al email wl password mn al database w hrga3ha f var esmo verified
        query = User.query.filter(User.email == email, User.password == password)
        result = query.first()

        if result:
            # al id da hangebo mn al database
            # hena hgeb al data bta3et al user mn al database w a7otha fl session
            session.permanent = True

            # hgeeb al data bta3to aly hya al name w email w password w phone
            session["user"] = result.id

            # m4 m7tag a pass al data f parameter 3l4an al session da zaher ll app kolo
            return redirect(url_for("dashboard"))
        else:
            flash(" Wrong UserName or Password", "Login issue")
            return render_template("login.html", LoginFailure=True)
    else:
        return render_template('login.html')


@app.route('/auth/register/perform', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        # ba5od al data mn al user mn saf7et al html
        username = request.form['username']
        password = (hashlib.md5(request.form['password'].encode())).hexdigest()
        email = request.form['email']
        phone = request.form['phone']
        Type = request.form['selection']
        try:
            is_phone = carrier._is_mobile(number_type(phonenumbers.parse("+2" + phone)))
        except:
            flash(" invalid Phone Number ..", "info")
            return render_template('register.html', SignupFailure=True)

        # hena h3ml check ll email aly hwa da5loh 3l4an lw mowgood f3lan fl database atla3lo message t2ol eno mwgood f3lan
        check_email = User.query.filter(User.email == email).first()
        if check_email:
            # kda al email tl3 mwgood fl database
            flash(" This Email already exists ", "info")
            return render_template('register.html', SignupFailure=True)
        else:
            # kda al email m4 mwgood f hbda2 a3ml save ll data bta3to fl database
            add_new_user = User(username, password, email, phone)
            db.session.add(add_new_user)
            db.session.commit()
            db.session.refresh(add_new_user)
            session.permanent = True
            session["user"] = add_new_user.id
            return redirect(url_for("dashboard"))
    else:
        return render_template('register.html')


@app.route('/auth/register', methods=['GET', 'POST'])
def signup():
    if session.get('user'):
        return redirect(url_for('dashboard'))
    else:
        return render_template('register.html')


@app.route('/auth/login', methods=['GET', 'POST'])
def signin():
    if session.get('user'):
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')


@app.route('/auth/logout')
def logout():
    if session.get('user'):
        del session["user"]
    return redirect(url_for('signin'))


@app.route('/auth/profile')
def profile():
    if session.get('user'):
        user = User.query.filter(User.id == session.get('user')).first()
        return render_template('profile.html', user=user)
    return redirect(url_for('signin'))


@app.route('/auth/password/forget', methods=['GET', 'POST'])
def forget_password():
    return render_template('forget_password.html')


@app.route('/auth/password/send_code', methods=['GET', 'POST'])
def send_code():
    if request.method == 'POST':
        email = request.form['email']
        check_email = User.query.filter_by(email=email).first()

        if check_email:
            random_num = random.randint(10000, 99999)
            # Add Key to Database
            db.session.add(ForgetKeys(user_id=check_email.id, key=random_num))
            db.session.commit()

            session["email_recovery"] = email
            msg = Message(
                'Hello',
                sender='FlaskappGP@gmail.com',
                recipients=[email]
            )
            msg.body = '''
                                Hello Flask message sent from Flask-Mail

                                   To change your Password This is your Verification Code is : ''' + str(random_num)
            mail.send(msg)
            return render_template('code_verification.html')
        else:
            flash("Email Not Found")
            return render_template('forget_password.html', emailnotFound=True)
    else:
        return render_template('login.html')


@app.route('/auth/password/verify_code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        code = request.form['verification_code']

        user = User.query.filter_by(email=session["email_recovery"]).first()
        key_stored = ForgetKeys.query \
            .filter(ForgetKeys.user_id == user.id, ForgetKeys.date_expired > datetime.utcnow()) \
            .order_by(ForgetKeys.id.desc()) \
            .first()
        if key_stored:
            if code == str(key_stored.key):
                db.session.delete(key_stored)
                db.session.commit()
                return render_template('change_password.html')

        flash("Wrong Verification Code")
        return render_template('code_verification.html', Verificationerror=True)
    else:
        return render_template('login.html')


@app.route('/auth/password/change', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if session.get("email_recovery"):
            if password == password_confirm:
                user = User.query.filter_by(email=session["email_recovery"]).first()
                user.password = (hashlib.md5(password.encode())).hexdigest()
                db.session.commit()
                return render_template('change_password.html', success=True)
            else:
                flash("Two Passwords Are Not Identical")
                return render_template('change_password.html', PASSVerificationerror=True)
        else:
            flash("Some Thing Went Wrong")
            return render_template('change_password.html', PASSVerificationerror=True)
    else:
        return render_template('login.html')


@app.route('/auth/password/success', methods=['GET', 'POST'])
def recovery():
    return render_template('login.html')


@app.route('/auth/user/update', methods=['GET', 'POST'])
def update_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        if session.get("user"):
            user = User.query.filter_by(id=session.get("user")).first()
            user.name = name
            user.email = email
            user.phone = phone
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            flash("Some Thing Went Wrong")
            return redirect(url_for('signin'))
    else:
        return redirect(url_for('signin'))


# Pages Routes

#
@app.route('/tests/create')
def create_test():
    if session.get('user'):
        return render_template('create_test.html')
    return redirect(url_for('signin'))


#
@app.route('/tests/history')
def tests_history():
    if session.get('user'):
        
        user = User.query.filter(User.id == session.get('user')).first()
        return render_template('history.html', tests=get_tests_results())
    else:
        return redirect(url_for('signin'))


@app.route('/test/operation', methods=['GET', 'POST'])
def operation():
    if session.get('user'):
        if request.form.get('start_test') == 'Start Testing':
            if request.files["pic"] and request.files["pic"] != "":
                pics = request.files.getlist("pic")

                add_new_test = Test(name=request.form['name'],
                                    result='Very Good',
                                    user_id=session.get('user'),
                                    patient_name=request.form['patient_name'],
                                    patient_gender=request.form['patient_gender'],
                                    patient_age=request.form['patient_age'],
                                    patient_phone=request.form['patient_phone'],
                                    note=request.form['note'])
                db.session.add(add_new_test)
                db.session.commit()
                db.session.refresh(add_new_test)
                tid = add_new_test.id
              

                directory = os.path.join(app.config['UPLOAD_FOLDER'], 'tests', str(tid))
                for pic in pics:
                    filename = secure_filename(pic.filename)
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    pic.save(os.path.join(directory, filename))

                # **** HERE TEST CODE **** #
                # opt = detect.parse_opt(tid, directory)
                # result = detect.main(opt)
                vgg_model = load_model('chest_xray.h5')   
                
                    
                categories = ['COVID','NORMAL','PNEUMONIA']
                image_1 = directory + '/' + secure_filename(pic.filename)
                img_array = cv2.imread(image_1)
                img_array = cv2.resize(img_array,(224,224))/255.
                img = np.expand_dims(img_array, axis=0)
                y_pred = vgg_model.predict(img)
                yhat = np.argmax(y_pred)
                x = categories[yhat]
                test = Test.query.filter_by(id=tid).first()

                result_text = x

                test.result = (result_text) if len(result_text) > 0 else 'No diseases detected'
                db.session.commit()

                flash("Images have been uploaded successfully")
                return redirect(url_for('view_test', tid=tid))
            else:
                flash("There is no images to be tested")
                return render_template('create_test.html', error=True)

        else:
            return redirect(url_for('create_test'))
    else:
        return render_template('login.html')


@app.route('/test/view/<tid>', methods=['GET', 'POST'])
def view_test(tid):
    if session.get('user'):
        test = Test.query.filter(Test.id == tid, Test.user_id == session.get('user')).first()
        directory = os.path.join('static/uploads/tests', str(test.id))
        if os.path.exists(directory):
            images = [os.path.join(request.url_root, directory, f) for f in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, f))]
        else:
            images = []
        return render_template('view_test.html', test=test, images=images)
    flash("No Authorization to download test")
    return redirect(url_for('signin'))


@app.route('/test/delete/<tid>', methods=['GET', 'POST'])
def delete_test(tid):
    if session.get('user'):
        deleted = Test.query.filter(Test.id == tid, Test.user_id == session.get('user')).delete()
        directory = os.path.join('static/uploads/tests', str(tid))
        shutil.rmtree(directory)
        
        db.session.commit()
        return redirect(url_for("tests_history"))
    flash("No Authorization to delete test")
    return redirect(url_for('signin'))




if __name__ == "__main__":
    
    with app.app_context():    
        db.create_all()
    app.run(debug=True)
