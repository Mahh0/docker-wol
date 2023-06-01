from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from ping3 import ping
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hosts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'  # Clé secrète pour la session

db = SQLAlchemy(app)


class Host(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(30), unique=True, nullable=False)
    ip = db.Column(db.String(20), unique=True, nullable=False)
    mac = db.Column(db.String(17), nullable=False)

    def __repr__(self):
        return f'<Host {self.ip}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


@app.route('/')
def index():
    hosts = Host.query.all()
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html', hosts=hosts, check_host_status=check_host_status, session=session)
    else:
        return render_template('index.html', hosts=hosts, check_host_status=check_host_status)


@app.route('/add', methods=['POST'])
def add_host():
    nom = request.form['nom']
    ip = request.form['ip']
    mac = request.form['mac']
    host = Host(nom=nom, ip=ip, mac=mac)
    db.session.add(host)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:host_id>', methods=['POST'])
def delete_host(host_id):
    host = Host.query.get_or_404(host_id)
    db.session.delete(host)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/wol/<ip>')
def wake_on_lan(ip):
    mac = Host.query.filter_by(ip=ip).first().mac
    subprocess.run(['wakeonlan', mac])
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return render_template('logout.html')


@app.template_filter('status_class')
def status_class(pingable):
    if pingable:
        return 'status-green'
    else:
        return 'status-red'


def check_host_status(ip):
    result = ping(ip)
    if result is not None:
        return True
    return False


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User(username='admin', password='admin')
            db.session.add(user)
            db.session.commit()
    app.run(host='0.0.0.0', port=80, debug=True)