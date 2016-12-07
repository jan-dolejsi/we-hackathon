from flask import Blueprint, render_template, request, redirect, url_for

import capital


api = Blueprint('guestbook', __name__)

# api routes


@api.route('/', methods=['GET', 'POST'])
def main_page():
    book = guestbook.Greeting()
    results = book.fetch_greetings()
    if request.method == 'GET':
        return render_template('main.html', comment=None, results=results)
    elif request.method == 'POST':
        comment = request.form['comment']
        book.store_greeting(comment)
        return redirect(url_for('guestbook.main_page'))

