import sqlalchemy

db = ''
engine = sqlalchemy.create_engine(db)
connection = engine.connect()

connection.execute("""CREATE TABLE if not exists Users(
    idu integer primary key,
    full_name text not null,
    b_year integer,
    search_city text,
    gender integer);""")

connection.execute("""CREATE TABLE if not exists User_Candidate(
    idu integer references Users (idu),
    ids integer not null,
    full_name text not null,
    b_year integer not null,
    city text not null,
    gender integer not null,
    primary key (ids, idu));""")

