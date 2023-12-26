from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random
import string
from pprint import pprint

ENGINE = create_engine('sqlite:///./data.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=ENGINE)


def create_link_record(user_id, long_link, short_link, created_at):
    s = Session()
    s.execute(text(f'INSERT INTO links '
                   f'(user_id, long_link, short_link, created_at) '
                   f'VALUES ({user_id}, \"{long_link}\", \"{short_link}\", {created_at})')
              )
    s.commit()


def get_links(limit=10, offset=0):
    s = Session()
    rows = s.execute(text(f'SELECT id, short_link '
                          f'FROM links '
                          f'LIMIT {limit} '
                          f'OFFSET {offset}')
                     ).fetchall()
    s.commit()
    # pprint(rows)
    return rows


def get_clicks(limit=10, offset=0):
    s = Session()
    rows = s.execute(text(f'SELECT clicks, short_link '
                          f'FROM links '
                          f'LIMIT {limit} '
                          f'OFFSET {offset}')
                     ).fetchall()
    s.commit()
    return rows

def update_link_clicks(short_link, clicks):
    s = Session()
    s.execute(text(f'UPDATE links SET clicks={clicks} '
                   f'WHERE short_link=\"{short_link}\"')
              )
    s.commit()


def update_id_clicks(id, clicks):
    s = Session()
    s.execute(text(f'UPDATE links SET clicks={clicks} '
                   f'WHERE id={id}')
              )
    s.commit()


def get_top_links(user_id, created_after=0, limit=10):
    s = Session()
    rows = s.execute(text(f'SELECT DISTINCT short_link, clicks '
                          f'FROM links '
                          f'WHERE user_id = {user_id} AND created_at > {created_after} '
                          f'ORDER BY clicks DESC '
                          f'LIMIT {limit}')
                     ).fetchall()
    s.commit()
    return rows


def delete_records(id):
    s = Session()
    s.execute(text(f'DELETE FROM links WHERE id={id}'))
    s.commit()


# for j in range(0, 100):
#     user_id = random.randint(0, 100)
#     long_link = "".join([random.choice(string.ascii_letters) for i in range(20)])
#     short_link = "".join([random.choice(string.ascii_letters) for i in range(10)])
#     created_at = random.randint(700, 1000)
#     create_link_record(user_id, long_link, short_link, created_at)

# for j in range(400, 500):
#     delete_records(j)

