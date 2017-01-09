import MySQLdb

def connection():
    conn = MySQLdb. connect( host = "localhost",
                            user = "root",
                            passwd = "better think about it",
                            db = "pocketTanks")
    c = conn. cursor()

    return c, conn
