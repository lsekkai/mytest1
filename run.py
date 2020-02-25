from datetime import datetime

from sqlalchemy_utils import database_exists
from flask import Flask, render_template, url_for, request, session
from models import db, Translation

app = Flask(__name__, template_folder="app/templates/",
                      static_folder="app/templates/")
DB_URI = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
db.init_app(app)
if not database_exists(DB_URI):
    with app.app_context():
        db.create_all()
        tr1 = Translation(src="text1")
        tr2 = Translation(src="text2")
        tr3 = Translation(src="text3")
        for tr in (tr1, tr2, tr3):
            db.session.add(tr)
        db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/traduction', methods=['GET', 'POST'])
def traduction():
    id_traduction = request.args.get('id_traduction')
    if request.method == 'POST':
        traduction = Translation.query.filter(Translation.id == id_traduction).first()
        traduction.trg= request.form['phrase-traduit']
        traduction.translated=True
        traduction.translatedOn = datetime.utcnow
        traduction.translatedBy = session.get("user", default="Djamel")
        traduction.issue = request.form['issue']

         # li ce commentaire stp
         # il ma dit meme si la phrase ne peut pas etre traduite il a coché sur issue
        # et l'utilisateur fait entrer du text on garde le text et le checkbox et a True

        db.session.commit()

    not_translated = Translation.query.filter(Translation.translated == False).all()
    return render_template('traductions.html', traductions=not_translated)

@app.route('/score')
def score():
    return render_template('score.html')


if __name__ == '__main__':
    app.run(debug=True,port=8080)