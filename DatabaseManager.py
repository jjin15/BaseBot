import sqlite3

DB_ERROR = 1

class DatabaseManager:
    def __init__(self, fn):
        self.conn = None
        self.cur = None
        try:
            self.connect(fn)
        except:
            pass

    def connect(self, fn):
        self.conn = sqlite3.connect(fn)
        self.cur = self.conn.cursor()

    """ Function will check whether or not a username exists in the database
        Returns DB_ERROR if there was an issue executing the query
        Returns False if user does not exist
        Returns name of user if user exists
    """
    def check_user_exists(self, uname):
        try:
            self.cur.execute("SELECT name FROM Users WHERE name=?", (str(uname),))
        except Exception as e:
            print("ERROR" + str(e))
            return DB_ERROR
        res = self.cur.fetchone()
        # user does not exist
        if res is None:
            return False
        return res[0]


    """ Adds a user to the database, with default 0 points
        Returns False if the user does not exist
        Returns True if operation successful
    """
    def add_user(self, uname, points=0):
        if self.check_user_exists(uname):
            return False
        try:
            data = (uname, points)
            self.cur.execute("INSERT into Users (name, points) VALUES (?,?)", data)
        except Exception as e:
            print ('exception in add_user: ' + str(e))
            return False
        self.conn.commit()
        return True

    """ Helper function that retrieves the number of points a certain user has
        returns False if the user does not exist
        returns the number of points (int) if user exists
    """
    def get_user_points(self, uname):
        if not self.check_user_exists(uname):
            return False
        try:
            data = (uname,)
            self.cur.execute("SELECT points FROM Users WHERE name=?", data)
            res = int(self.cur.fetchone()[0])
        except Exception as e:
            print("exception in get_user_points: " + str(e))
            return False
        return res

    """ Function to modify the number of points a user has
        Returns False if user does not exist
        returns True if operation successful
    """
    def change_user_points(self, uname, points):
        if not self.check_user_exists(uname):
            return False
        # need to pull current points
        res = self.get_user_points(uname)
        if not res:
            return False
        # update the new number of points
        new_res = res + points
        try:
            data = (new_res, uname)
            self.cur.execute("UPDATE Users SET points=? WHERE name=?", data)
        except Exception as e:
            print ('exception in change_user_points_update: ' + str(e))
            return False
        self.conn.commit()
        return True
