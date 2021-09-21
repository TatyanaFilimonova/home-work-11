from abc import ABC, abstractmethod
from .SQL_alchemy_classes import *
from sqlalchemy import update, delete
from .LRU_cache import *


class ApplicationUser(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_user(self, login):
        pass

    @abstractmethod
    def insert_user(self, user):
        pass

    @abstractmethod
    def delete_user(self, user):
        pass
 
   
class AppUserMongo(ApplicationUser):

    def __init__(self, user_db):
        self.user_db = user_db

    def get_user(self, login):
        res = self.user_db.find_one({'login': login})
        if res is not None:
            user = Mongo_user(res)
            return user
        else:
            return res    

    @LRU_cache_invalidate('get_user') 
    def insert_user(self,  name_, login_, password_):
        try:
            res = self.get_user(login_) 
            if res == [] or res is None:
                self.user_db.insert_one({'user_name': name_,
                                         'login': login_,
                                         'password': password_
                                        })
                return None
            else:
                return f'User with login [{login_}] already exist'
        except Exception as e:
            return f"Some problem: {str(e)}"

    @LRU_cache_invalidate('get_user')
    def delete_user(self, login):
        try:
            self.user_db.delete_one({'login': login})
            return 0
        except Exception as e:
            return e


class AppUserPSQL(ApplicationUser):

    def __init__(self, session=None):
        self.session = session
        
    @LRU_cache(10)
    def get_user(self, login):
        res = self.session.query(
                    User_.id, User_.username, User_.login, User_.password
                    ).filter(User_.login == login).first()
        with open('insert.txt', 'a') as log:
            log.write(f"result of bd quering for existing user =  = {res}\n")
        if res is None:
            return res
        else:
            return Postgres_user(res)   

    @LRU_cache_invalidate('get_user')
    def insert_user(self, name_, login_, password_):
        res = self.get_user(login_)
        if res is None:
            try:
                user = User_(username=name_,
                             login=login_,
                             password=password_,
                             )
                self.session.add(user)
                self.session.commit()
                return None
            except Exception as e:
                return f'Could not append user list due to the proplem: {str(e)}'
            finally:
                self.session.rollback()
        else:
            return f'User with login [{login_}] already exist'

    @LRU_cache_invalidate('get_user')
    def delete_user(self, login_):
        try:
            stmt = delete(User_).where(User_.login == login_)
            self.session.execute(stmt)    
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            return e


class User_abstract(ABC):

    @abstractmethod
    def __init__(self):
        pass


class Mongo_user(User_abstract):

    def __init__(self, json):
        self.id = json['_id']
        self.user_name = json['user_name']
        self.login = json['login']
        self.password = json['password']
        

class Postgres_user(User_abstract):

    def __init__(self, result):
        self.id = result.id
        self.user_name = result.username
        self.login = result.login
        self.password = result.password
        
