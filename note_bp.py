# local packages
from . import global_var
from .contact_bp import *

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template, request, session, url_for
)

note_bp = Blueprint('note', __name__, url_prefix='/note')


@note_bp.route('/find_notes', methods=['GET', 'POST'])
def find_notes():
    results = []
    if request.method == 'POST':
        keywords = clean_search_str(
                   request.form.get('Keywords'))
        for k in [kw.strip() for kw in keywords.split(",")]:
            for res in global_var.note_book.get_notes(k):
                if res not in results:
                    results.append(res)
        return render_template('note/find_notes_found.html', result=results)
    else:
        return render_template('note/find_notes_search.html')

         
@note_bp.route('/show_all_notes', methods=['GET', 'POST'])
def show_all_notes():
    if request.method == 'POST':
        return redirect('/bot-command')
    else:
        result = global_var.note_book.get_all_notes()
        return render_template('note/all_notes.html', result=result)


@note_bp.route('/add_note', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        res = global_var.note_book.insert_note(request)
        if res == 0:
            return render_template('note/add_note_OK.html')
        else:
            return html_error(res)
    else:
        return render_template('note/add_note.html')


@note_bp.route('/edit_note', methods=['GET', 'POST'])
def edit_note():
    results = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [kw.strip() for kw in keywords.split(",")]:
            for res in global_var.note_book.get_notes(k):
                if res not in results:
                    results.append(res)
        return render_template('note/find_notes_found.html', result=results)
    else:
        return render_template('note/find_notes_search.html')

        
@note_bp.route('/save_note/<id>', methods=['GET', 'POST'])
def save_note(id):
    if request.method == 'POST':
        res = global_var.note_book.update_note(id, request)
        if res == 0:
            return render_template('note/edit_notes_OK.html')
        else:
            return html_error(res)
    else:
        result = global_var.note_book.get_note_by_id(id)
        return render_template(
                  'note/edit_notes_save.html',
                  res=result)
                              

@note_bp.route('/delete_note', methods=['GET', 'POST'])
def delete_note():
    results = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [kw.strip() for kw in keywords.split(",")]:
            for res in global_var.note_book.get_notes(k):
                if res not in results:
                    results.append(res)
        return render_template(
                  'note/delete_notes_found.html',
                  result=results)
    else:
        return render_template(
                  'note/delete_notes_search.html') 
        

@note_bp.route('/delete_note/<id>', methods=['GET', 'POST'])
def note_delete_(id):
    res = global_var.note_book.delete_note(id)
    if res == 0:
        return render_template('note/delete_notes_OK.html', id=id)
    else:
        return html_error(res)
