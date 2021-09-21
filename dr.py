from SQL_alchemy_classes import *
#from db_postgres import *
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, or_, update, any_
from sqlalchemy.orm import sessionmaker

def get_dr(period=180):
    days = [(datetime.now() + timedelta(days=i)).strftime('%m-%d') for i in range(1, period + 1)]

    result = session.query(
            Contact.contact_id,
            Contact.name,
            Contact.birthday,
            func.substr(func.to_char(Contact.birthday, 'YYYY.mm.dd'), 6, 10).label('celebrate')
                       ).filter(
                               func.substr(func.to_char(Contact.birthday, 'YYYY-mm-dd'), 6, 10
                                          ).like(any_(days))).all()
    for r in result:
        print(r)

if __name__ == '__main__':
    engine = create_engine("postgresql+psycopg2://postgres:1234@localhost/contact_book")
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.bind = engine
    get_dr()
    engine.dispose()    
