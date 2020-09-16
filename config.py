from passwords import database_connection

# main
SQLALCHEMY_DATABASE_URI_0 = database_connection
SQLALCHEMY_BINDS = {
    'avengers': SQLALCHEMY_DATABASE_URI_0,
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
