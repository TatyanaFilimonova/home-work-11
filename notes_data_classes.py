from abc import ABC, abstractmethod
from datetime import datetime
from datetime import date

import re
from .SQL_alchemy_classes import *
from sqlalchemy import or_, update, delete

from .LRU_cache import *


class Notebook(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_all_notes(self):
        pass

    @abstractmethod
    def get_notes(self, key):
        pass

    @abstractmethod
    def get_note_by_id(self, id):
        pass

    @abstractmethod
    def update_note(self, note, new_note):
        pass

    @abstractmethod
    def insert_note(self, note):
        pass

    @abstractmethod
    def delete_note(self, id):
        pass


class NotebookMongo(Notebook):

    def __init__(self, notes_db, counter_db):
        self.notes = []
        self.notes_db = notes_db
        self.counter_db = counter_db

    @LRU_cache(1)
    def get_all_notes(self):
        self.notes = []
        try:
            result = self.notes_db.find({}).sort('note_id')
            for res in result:
                self.notes.append(NoteMongo(res))
            return self.notes
        except Exception as e:
            raise e

    @LRU_cache(10)
    def get_notes(self, key):
        self.notes = []
        if key!="":
            rgx = re.compile(f'.*{key}.*', re.IGNORECASE)
            result = self.notes_db.find({'$or': [{'keywords': rgx}, {'text': rgx}]}).sort('note_id')
            for res in result:
                self.notes.append(NoteMongo(res))
            return self.notes
        else:
            return []

    @LRU_cache(10)
    def get_note_by_id(self, id):
        result = self.notes_db.find_one({'note_id': int(id)})
        if result is not None:
            return NoteMongo(result)
        else:
            return None

    @LRU_cache_invalidate('get_notes', 'get_all_notes', 'get_note_by_id')
    def update_note(self, id, request):
        try:
            kw = request.form.get('Keywords')
            if ',' in kw:
                kw = [k.strip() for k in kw.split(',')]
            elif " " in kw:
                kw = [k.strip() for k in kw.split(' ')]
            else:
                kw = [kw]
            self.notes_db.replace_one({'note_id': int(id)},
                                      {'note_id': int(id),
                                       'created_at': datetime.today(),
                                       'keywords': kw,
                                       'text': request.form.get('Text')
                                       }
                                      )
            return 0
        except Exception as e:
            return e

    @LRU_cache_invalidate('get_notes', 'get_all_notes')
    def insert_note(self, request):
        try:
            counter = self.counter_db.find_one({"counter_name": 'note_id'}, {'value': 1})['value']
            self.counter_db.replace_one(
                {"counter_name": 'note_id'},
                {"counter_name": 'note_id',
                 "value": counter + 1}
            )
            kw = request.form.get('Keywords')
            if ',' in kw:
                kw = [k.strip() for k in kw.split(',')]
            elif " " in kw:
                kw = [k.strip() for k in kw.split(' ')]
            else:
                kw = [kw, ]
            self.notes_db.insert_one({
                'note_id': (counter + 1),
                'keywords': kw,
                'text': request.form.get('Text'),
                'created_at': datetime.today(),
            })
            return 0
        except Exception as e:
            return e

    @LRU_cache_invalidate('get_notes', 'get_all_notes', 'get_note_by_id')
    def delete_note(self, id):
        try:
            self.notes_db.delete_one({'note_id': int(id)})
            return 0
        except Exception as e:
            return e


class NotebookPSQL(Notebook):

    def __init__(self, session=None):
        self.session = session

    @LRU_cache(1)
    def get_all_notes(self):
        self.notes = []
        result = self.session.query(
            Note_.note_id, Note_.keywords, Text.text, Note_.created_at
        ).join(Text).order_by(Note_.note_id).all()
        for r in result:
            self.notes.append(NotePSQL(r))
        return self.notes

    @LRU_cache(10)
    def get_notes(self, key):
        self.notes = []
        if key!="":
            result = self.session.query(
                Note_.note_id, Note_.keywords, Text.text, Note_.created_at
            ).join(Text).filter(
                or_(func.lower(Note_.keywords).like(func.lower(f"%{key}%")
                                                    ), func.lower(Text.text).like(func.lower(f"%{key}%")))
            ).order_by(Note_.note_id).all()
            for r in result:
                self.notes.append(NotePSQL(r))
            return self.notes
        else:
            return []
    @LRU_cache(10)
    def get_note_by_id(self, id):
        result = self.session.query(
            Note_.note_id, Note_.keywords, Text.text, Note_.created_at
        ).join(Text).filter(Note_.note_id == id)
        return NotePSQL(result[0])

    @LRU_cache_invalidate('get_notes', 'get_all_notes', 'get_note_by_id')
    def update_note(self, id, request):
        try:
            kw = request.form.get('Keywords')
            if ',' in kw:
                kw = [k.strip() for k in kw.split(',')]
            elif " " in kw:
                kw = [k.strip() for k in kw.split(' ')]
            else:
                kw = [kw, ]
            text = request.form.get('Text')
            self.session.execute(
                update(Note_, values={Note_.keywords: ",".join(kw)}
                       ).filter(Note_.note_id == id))
            self.session.execute(
                update(Text, values={Text.text: text}
                       ).filter(Text.note_id == id))
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            return e

    @LRU_cache_invalidate('get_notes', 'get_all_notes')
    def insert_note(self, request):
        try:
            kw = request.form.get('Keywords')
            if ',' in kw:
                kw = [k.strip() for k in kw.split(',')]
            elif " " in kw:
                kw = [k.strip() for k in kw.split(' ')]
            else:
                kw = [kw, ]
            text = request.form.get('Text')
            note = Note_(keywords=",".join(kw), created_at=date.today())
            self.session.add(note)
            self.session.commit()
            text = Text(note_id=note.note_id, text=text)
            self.session.add(text)
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            return e

    @LRU_cache_invalidate('get_notes', 'get_all_notes', 'get_note_by_id')
    def delete_note(self, id):
        try:
            stmt = delete(Note_).where(Note_.note_id == id)
            self.session.execute(stmt)
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            return e


class NoteAbstract(ABC):

    @abstractmethod
    def __init__(self):
        self.note_id = None
        self.text = None
        self.created_at = None
        self.keywords = None


class NoteMongo(NoteAbstract):

    def __init__(self, json):
        self.note_id = json['note_id']
        self.keywords = ','.join(json['keywords'])
        self.created_at = json['created_at']
        self.text = json['text']


class NotePSQL(NoteAbstract):

    def __init__(self, note):
        self.note_id = note.note_id
        self.created_at = note.created_at
        self.keywords = note.keywords
        self.text = note.text
