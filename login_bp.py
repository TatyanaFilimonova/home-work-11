from . import global_var
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

login_bp = Blueprint('login', __name__, url_prefix='/login')


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login(request)
    else:
        return render_template('login/log.html')


@login_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['User_name']
        login = request.form['Login']
        password = request.form['Password']
        error = None
        if not username:
            error = 'Username is required.'
        elif not username:
            error = 'Login is required.'
        elif not password:
            error = 'Password is required.'
        if error is None:
            global_var.users_db.insert_user(username, login, generate_password_hash(password))
            return redirect(url_for("login.login"))
        flash(error)
    return render_template('login/register.html')


def do_the_login(request):
    login = request.form['Login']
    password = request.form['Password']
    user = global_var.users_db.get_user(login)
    error = None
    if user is None:
        error = 'Incorrect login'
    elif not check_password_hash(user.password, password):
        error = 'Incorrect password.'
    if error is None:
        session['user_id'] = str(user.id)
        session['user'] = user.user_name
        return redirect(url_for('init.bot'))
    else:
        flash(error)
        return render_template('login/log.html')


@login_bp.route('/logout')
def logout():
    session.clear()
    session['user'] = None
    return redirect(url_for('login.login'))
