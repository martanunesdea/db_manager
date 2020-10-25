from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('bookings', __name__, url_prefix='/bookings')

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT b.id, date_booking, author_id, username'
        ' FROM bookings b JOIN user u ON b.author_id = u.id'
        ' ORDER BY b.id DESC'
    ).fetchall()
    return render_template('bookings/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date_booking']
        date_booking = pd.to_datetime(date, format='%d-%m-%Y', errors='coerce')
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO bookings (title, author_id, date_booking)'
                ' VALUES (?, ?, ?)',
                (title, g.user['id'], date_booking)
            )
            db.commit()
            return redirect(url_for('bookings.index'))

    return render_template('bookings/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT b.id, title, date_booking, author_id, username'
        ' FROM bookings b JOIN user u ON b.author_id = u.id'
        ' WHERE b.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Booking id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        date_booking = request.form['date_booking']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE bookings SET title = ?, date_booking = ?'
                ' WHERE id = ?',
                (title, date_booking, id)
            )
            db.commit()
            return redirect(url_for('bookings.index'))

    return render_template('bookings/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM bookings WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('bookings.index'))