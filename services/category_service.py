from .database import Database

class CategoryService(Database):
    """
    Service class for handling category-related database operations.

    Inherits from:
        Database

    Methods:
        get_categories():
            Retrieves all categories from the 'Categories' table.

            Returns:
                list[dict]: A list of dictionaries, each representing a category record.
    """
    def get_categories(self):
        self.cursor.execute("SELECT * FROM Categories")
        return [dict(row) for row in self.cursor.fetchall()]