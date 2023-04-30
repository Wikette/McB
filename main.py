from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    photo = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)

            return redirect(url_for('profile'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        user = current_user
        user.nom = request.form['nom'].upper()
        user.prenom = request.form['prenom'].upper()

        # Traiter l'image
        img_data = base64.b64decode(request.form['photo'].split(',')[1])
        img = Image.open(io.BytesIO(img_data)).convert('RGBA')
        img = img.resize((210, 210), Image.ANTIALIAS)

        # Appliquer le border-radius de 50%
        mask = Image.new('L', (210, 210), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 210, 210), fill=255)
        img.putalpha(mask)

        # Sauvegarder l'image en mémoire
        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        user.photo = base64.b64encode(output.getvalue()).decode()
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('profile.html')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        user = current_user

        # Charger et traiter l'image utilisateur
        img_data = base64.b64decode(user.photo)
                img = Image.open(io.BytesIO(img_data)).convert('RGBA')

        # Charger l'image template
        base_image = Image.open("static/template.png")
        base_image.paste(img, (95, 760), img)

        # Ajouter du texte
        draw = ImageDraw.Draw(base_image)
        font = ImageFont.truetype("fonts/Between 3 W01 Heavy.ttf", 32)

        text_width, _ = draw.textsize(user.nom, font=font)
        draw.text((850 - text_width, 785), user.nom, font=font, fill="#31302F")

        text_width, _ = draw.textsize(user.prenom, font=font)
        draw.text((850 - text_width, 840), user.prenom, font=font, fill="#31302F")

        date_validite = datetime.datetime.now().strftime("%d %B %Y").upper()
        text_width, _ = draw.textsize(date_validite, font=font)
        draw.text((840 - text_width, 910), date_validite, font=font, fill="#FFFFFF")

        # Sauvegarder l'image en mémoire
        output = io.BytesIO()
        base_image.save(output, format='PNG')
        output.seek(0)

        # Créer une réponse avec le nom de fichier et envoyer l'image
        response = make_response(output.getvalue())
        response.headers.set('Content-Type', 'image/png')
        response.headers.set('Content-Disposition', 'attachment', filename='output.png')
        return response

    return render_template('index.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

