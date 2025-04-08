#pylint:skip-file

import json
import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import folium
from folium.features import DivIcon
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'NastiaTop2006'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150))
    surname = db.Column(db.String(150))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))


with app.app_context():
    db.create_all()

@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    
    if post and post.user_id == session['user_id']:
        db.session.delete(post)
        db.session.commit()
        flash('Допис успішно видалено!', category='success')
    else:
        flash('У вас немає прав для видалення цього допису', category='error')
    
    return redirect(url_for('index'))

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        flash('Ви повинні увіти, щоб додавати дописи', category='error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']
        
        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        flash('Допис успішно додано!', category='success')
        return redirect(url_for('index'))

    return render_template('add_post.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Вхід успішний', category='success')
            return redirect(url_for('index'))
        else:
            flash('Неправильні дані, спробуйте знову', category='error')

    if 'user_id' in session:
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        surname = request.form['surname']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Ім'я користувача вже існує, придумайте нове", category='error')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(username=username, password=hashed_password, name = name, surname = surname)
        db.session.add(new_user)
        db.session.commit()
        flash('Аккаунт створений успішно', category='success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out!', category='success')
    return redirect(url_for('login'))

def load_battles():
    file_path = os.path.join(app.static_folder, 'battles.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print("Opened")
            return json.load(f)
    except FileNotFoundError:
        print('Not found')
        return []


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('main_page.html', posts=posts)

@app.route('/wikipedia')
def wikipedia():
    return render_template('wikipedia.html')

@app.route('/map', methods=['GET', 'POST'])
def map_view():
    m = folium.Map(location=[49.5, 31.5], zoom_start=6)

    battles = load_battles()

    selected_start_year = request.form.get('start_year')
    selected_end_year = request.form.get('end_year')
    selected_period = request.form.get('period')

    if selected_start_year and selected_end_year:
        battles = [battle for battle in battles if int(selected_start_year) <= battle['year'] <= int(selected_end_year)]
    elif selected_start_year:
        battles = [battle for battle in battles if battle['year'] >= int(selected_start_year)]
    elif selected_end_year:
        battles = [battle for battle in battles if battle['year'] <= int(selected_end_year)]

    if selected_period:
        battles = [battle for battle in battles if battle.get('period') == selected_period]

    for battle in battles:
        if battle.get('latitude') and battle.get('longitude'):
            popup_html = f"""
            <div style="font-size: 16px;">
                <strong style="font-size: 1.1rem;">{battle['name']}</strong><br>
                Рік: {battle['year']}<br>
                {battle['info']}
            </div>
            """
            
            tooltip_html = f'<span style="font-size: 16px;">{battle["name"]}</span>'
            
            folium.Marker(
                location=[battle['latitude'], battle['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=tooltip_html
            ).add_to(m)

    map_html = m._repr_html_()

    return render_template('map.html', map_html=map_html, selected_start_year=selected_start_year, selected_end_year=selected_end_year, selected_period=selected_period)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/wiki_ww1')
def wiki_ww1():
    return render_template('wiki_ww1.html')

@app.route('/wiki_ww2')
def wiki_ww2():
    return render_template('wiki_ww2.html')

@app.route('/wiki_ussr')
def wiki_ussr():
    return render_template('wiki_ussr.html')

@app.route('/wiki_1991')
def wiki_1991():
    return render_template('wiki_1991.html')

@app.route('/wiki_2014')
def wiki_2014():
    return render_template('wiki_2014.html')

@app.route('/wiki_2022')
def wiki_2022():
    return render_template('wiki_2022.html')

if __name__ == '__main__':
    app.run(debug=True)
