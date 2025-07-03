import functools
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# create a blueprint and register it using the factory
bp = Blueprint('auth', __name__, url_prefix='/auth')

# first view: register
# /auth/register

# when flask receives a request to /auth/register, it will call this function
# and use the return value as the response.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # if there is post, start validating input
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # if no input provided, show an error message
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # if input, then execute sql query for creating
        # or validating user
        if error is None:
            try:
                # the input values or tuple values are replaced with ? placeholders
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    # password should not be stores in database directly
                    # so use the generated hash password for security
                    (username, generate_password_hash(password)),
                )

                # to save the changes, call the commit() fx
                db.commit()

            # occurs when username already exists in db
            except db.IntegrityError:
                error = f"User {username} is already registerd."

            # after storing the user redirect to the login page  
            else:
                return redirect(url_for("auth.login"))

        # if validation fails, show error
        flash(error)

    # render the form template for inputs
    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # queries user first and stores it for later use
        # fetchnone returns one row from query.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect Username.'
        
        # hashes the submitted password in the same way as the stored hash 
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()

            # stores data across requests.
            # when validation succeeds, the user's id is stored in a new session
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('/login.html')

# bp.before_app_request() registers a function that runs before the view function, 
# no matter what URL is requested.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    # check if user exists in session
    if user_id is None:
        g.user = None
    else:
        # get user data form the database
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# logout
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# require authentication in other views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view