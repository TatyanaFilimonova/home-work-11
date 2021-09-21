# local packages
from .neural_code import *
from .LRU_cache import *
from .db_mongo import contact_db, counter_db, note_db, user_db, db
from .db_postgres import pgsession
from .users_data_classes import *
from .note_bp import *
from .notes_data_classes import *
from . import global_var

# global packages
from flask import redirect, url_for, session, render_template
from flask import request
import warnings

warnings.filterwarnings('ignore')
init_bp = Blueprint('init', __name__, url_prefix='')
command_history = {"command": "response"}

# routes section


# Choose session for db is initialized and user  is logined
def before_request():
    if 'db' not in session or global_var.contact_book is None:
        if request.endpoint != 'init.db_select':
            return redirect(url_for('init.db_select'))
        else:
            return None
    else:
        if ('user' not in session or session['user'] is None
           ) and request.endpoint not in ['login.login', 'login.register']:
            return redirect(url_for('login.login'))
        else:
            return None


@init_bp.route('/hello_', methods=['GET', 'POST'])
def hello_():
    return redirect('/bot-command')


@init_bp.route('/help_', methods=['GET', 'POST'])
def help_():
    return render_template(
        'help/help.html',
        exec_command=exec_command)


@init_bp.route('/')
def index():
    return redirect(url_for('init.bot'))


@init_bp.route('/DB_select', methods=['GET', 'POST'])
def db_select():
    if request.method == 'POST':
        option = request.form['db']
        flush_cache()
        session['user'] = None
        session['db'] = None
        if option == 'mongodb':
            global_var.contact_book = ContactbookMongo(contact_db, counter_db)
            global_var.note_book = NotebookMongo(note_db, counter_db)
            global_var.users_db = AppUserMongo(user_db)
        else:
            global_var.contact_book = ContactbookPSQL(pgsession)
            global_var.note_book = NotebookPSQL(pgsession)
            global_var.users_db = AppUserPSQL(pgsession)
            session['db'] = 'choosed'
        return redirect(url_for('init.bot'))
    else:
        return render_template('select_db.html')


@init_bp.route('/bot-command', methods=['GET', 'POST'])
def bot():
    if request.method == 'POST':
        command = request.form.get('BOT command')
        user_intense = listener(command)
        command_history[command] = user_intense[0][0]
        return redirect(url_for(exec_command[user_intense[1]][0]))
    else:
        return render_template(
            'bot_page.html', command_history=command_history)


# end of routes section


exec_command = {
    "hello": ['init.hello_', "hello:              Greetings", 0],
    "add contact": ['contact.add_contact', "add contact:        Add a new contact", 2],
    "edit contact": ['contact.edit_contact', "edit contact:       Edit the contact detail", 2],
    "find contact": ['contact.find_contact', "find contact:       Find the records by phone or name", 1],
    "find notes": ['note.find_notes', "find notes:         Find the notes by text or keywords", 1],
    "show all contacts": ['contact.show_all_contacts',
                          "show all contacts:  Print all the records of adress book, page by page", 0],
    "show all notes": ['note.show_all_notes',
                       "show all_notes:     Print all the records of adress book, page by page", 0],
    "help": ['init.help_', "help:               Print a list of the available commands", 0],
    "add note": ['note.add_note', "add note:           Add new text note ", 0],
    "edit note": ['note.edit_note', "edit note:          Edit existing text note ", 0],
    "delete contact": ['contact.delete_contact', "delete contact:     Delete contact", 2],
    "delete note": ['note.delete_note', "delete note:        Delete text note", 2],
    "next birthday": ['contact.next_birthday',
                      "next birthday:      Let you the contats with birthdays in specified period", 2],
    "logout": ['login.logout', 'user logout: change active user'],
    "choose data engine": ['init.db_select', 'Change current database engine']
}


@LRU_cache(max_len=10)
def listener(message):
    return_list, intents = predict_class(message)
    if not return_list:
        return get_response([{'intent': 'help'}], intents)
    res = get_response(return_list, intents)
    return res


def close_db():
    """Closes db  connection"""
    pgsession.close()
    db.close()
    session.clear()
    print("Databases are closed")


def init_app(app):
    app.teardown_appcontext(close_db)
