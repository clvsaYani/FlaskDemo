from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import os
from datetime import datetime
from functools import wraps # Für den Login-Decorator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

@app.context_processor
def inject_now():
    """Macht die 'now'-Funktion im Template verfügbar, um das aktuelle Datum/Zeit zu erhalten."""
    return {'now': datetime.utcnow}

# ----- Hartkodierte Zugangsdaten (Nur für Demo!) -----
ADMIN_USERNAME = 'Admin'
ADMIN_PASSWORD = 'Admin'

posts = [
    {
        'id': 1,
        'title': 'Mein erster Blogbeitrag',
        'content': 'Willkommen zu meinem Demo-Blog! Flask macht Spaß.\n\nMan kann hier **Markdown** (oder einfach HTML) verwenden, wenn man es im Template entsprechend rendert.',
        'author': 'Admin',
        'date_posted': datetime.utcnow()
    },
    {
        'id': 2,
        'title': 'Ein weiterer Beitrag über CSS',
        'content': 'Modernes CSS kann mit Flexbox, Grid und benutzerdefinierten Eigenschaften (Variablen) sehr mächtig sein. Bootstrap hilft beim schnellen Start.',
        'author': 'Admin',
        'date_posted': datetime.utcnow()
    }
]
next_post_id = 3

# ----- Hilfsfunktionen / Decorators -----

def login_required(f):
    """Decorator, um sicherzustellen, dass der Benutzer eingeloggt ist."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Bitte logge dich ein, um diese Seite zu sehen.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ----- Routen (Seiten) -----

@app.route('/')
def index():
    """Startseite: Zeigt alle Blog-Posts, sortiert nach Datum (neueste zuerst)."""
    sorted_posts = sorted(posts, key=lambda p: p['date_posted'], reverse=True)
    return render_template('index.html', posts=sorted_posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """Zeigt einen einzelnen Blog-Post anhand seiner ID."""
    post = next((p for p in posts if p['id'] == post_id), None)
    if post is None:
        abort(404)
    return render_template('post_detail.html', post=post, title=post['title'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login-Seite."""
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Erfolgreich eingeloggt!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'danger')
            return render_template('login.html')

    return render_template('login.html', title="Login")

@app.route('/logout')
@login_required
def logout():
    """Ausloggen des Benutzers."""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Du wurdest erfolgreich ausgeloggt.', 'info')
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Seite zum Erstellen neuer Blog-Posts."""
    global next_post_id
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Titel und Inhalt dürfen nicht leer sein.', 'warning')
            return render_template('create_post.html', title="Neuer Beitrag", post_title=title, post_content=content)

        new_post = {
            'id': next_post_id,
            'title': title,
            'content': content,
            'author': session.get('username', 'Admin'),
            'date_posted': datetime.utcnow()
        }
        posts.append(new_post)
        next_post_id += 1
        flash('Neuer Beitrag erfolgreich erstellt!', 'success')
        return redirect(url_for('post_detail', post_id=new_post['id']))

    return render_template('create_post.html', title="Neuer Beitrag")

# ----- Fehlerbehandlung -----
@app.errorhandler(404)
def page_not_found(e):
    """Eigene 404-Fehlerseite."""
    return render_template('404.html', title="Seite nicht gefunden"), 404

# ----- App starten -----
if __name__ == '__main__':
    app.run(debug=True)