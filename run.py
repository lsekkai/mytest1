from datetime import datetime
from sqlalchemy import and_,or_
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists
from flask import Flask, render_template, request, session, url_for, jsonify, json, flash
from werkzeug.utils import redirect
import jsonpickle
from models import db, Translation, User

app = Flask(__name__, template_folder="templates/",
                      static_folder="templates/")
DB_URI = 'sqlite:///test.db'
#ENV = 'deploy'
#if ENV=='dev':

 #   DB_URI = 'sqlite:///test.db'
#else:
 #   DB_URI = 'postgres://sscsdpbdphavzu:514d5cafbcb6bc771cc5a5e47e441b064588e2e9a6c773852c453a37b0f5409b@ec2-54-247-79-178.eu-west-1.compute.amazonaws.com:5432/d30k5i5g0qluvo'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'
app.secret_key = 'blabla'
sess = Session()
db.init_app(app)
if not database_exists(DB_URI):
    with app.app_context():
        db.drop_all()
        db.create_all()
        for i in range(1, 1000):
            db.session.add(Translation(src=f"test {i}"))
        db.session.add(User(name="Djamel"))
        db.session.add(User(name="Yahya"))
        db.session.commit()


@app.route('/choise')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/traduction', methods=['GET', 'POST'])
def traduction():
    id_traduction = request.args.get('id_traduction')
    page_num = int(request.args.get('page_num'))
    username = session.get("user", default="Djamel")
    user = User.query.filter(User.name == username).first()
    user.average_score_user
    tops=user.Nmaxelements()

    if request.method == 'POST':
        traduction = Translation.query.filter(Translation.id == id_traduction).first()
        trg = request.form[f"translation{id_traduction}"]
        issue = request.form.get(f"issue{id_traduction}")
        if trg or issue:
            traduction.trg = trg
            traduction.translated = True
            traduction.translatedOn = datetime.utcnow()
            traduction.translatedBy = session.get("user", default="Djamel")
            traduction.issue = True if issue else False
        db.session.commit()
    not_translated = Translation.query.filter(Translation.translated == False).paginate(per_page=10,page=page_num)
    return render_template('traductions.html', traductions=not_translated,avrg=user.average_score_user,tops=tops)


@app.route('/score', methods=['GET', 'POST'])
def score():
    username = session.get("user", default="Yahya")
    page_num = int(request.args.get('page_num'))
    user = User.query.filter(User.name == username).first()
    user.average_score_user
    tops = user.Nmaxelements()
    if request.method == 'POST':
        id_traduction = request.args.get('id_traduction')
        traduction = Translation.query.filter(Translation.id == id_traduction).first()
        # Si c'est pas le meme user qui a traduit
        if username != traduction.translatedBy:
            traduction.verified = True
            traduction.quality = int(request.form['score'+id_traduction])
            traduction.verifiedOn = datetime.utcnow()
            traduction.verifiedBy = username
            traduction.com = request.form['com'+id_traduction]
            db.session.commit()
            user = User.query.filter(User.name==username).first()
            user.average_score_user

    not_scored = Translation.query.filter(and_(Translation.translated == True,
                                               Translation.verified == False,
                                               Translation.translatedBy != username,
                                               Translation.issue==False
                                               )).paginate(per_page=10,page=page_num)
    return render_template('score.html', traductions=not_scored,avrg=user.average_score_user,tops=tops)


@app.route('/reserch', methods=['GET', 'POST'])
def reserch():
    page = request.args.get('page')
    string = request.form['recherch']
    if request.method == 'POST' and string != '':
        if page == 'traduction':
            traduction = Translation.query.filter(and_(Translation.src.like('%' + string + '%'),
                                                       Translation.translated==False)).all()
            return render_template('traductions.html', traductions=traduction)
        elif page == 'score':
            traduction = Translation.query.filter(and_(or_(Translation.trg.like('%' + string + '%'),
                                                      Translation.src.like('%' + string + '%'))),
                                                  Translation.translated==True,
                                                  Translation.verified==False,
                                                  Translation.issue==False).all()
            return render_template('score.html', traductions=traduction)



@app.route('/', methods=['GET', 'POST'])
def login():
    sign = request.args.get('sign')
    if  request.method == 'POST':
        username = request.form['sign']
        user = User.query.filter(User.name == username).first()
        if sign=='in'  :
            if user!=None :
                session['user']=user.name
                flash('Thank you for login')
                return redirect(url_for('index'))
            else:
                flash('user unexistant')
                return render_template('login.html')

        if sign=='up' and user==None and username!='' and not username.isspace() :
            db.session.add(User(name=username))
            db.session.commit()
            session['user'] = username
            flash('Thank you for registering')
            return redirect(url_for('index'))
        else :
            flash('user exist')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user', None)
   return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True,port=8080)
