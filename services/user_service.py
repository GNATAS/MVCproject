from .database import Database

class UserService(Database):
    '''
    Provides user-related database operations.
    
    Methods
    -------
    get_user(username)
         Retrieves a user's information from the database by username.
         Returns a dictionary of user data if found, otherwise None.
    '''
    def get_user(self, username):
        self.cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
        row = self.cursor.fetchone()
        return dict(row) if row else None