from .database import Database

class ProjectService(Database):
    """
    ProjectService provides methods to interact with project data in the database.
    
    Methods
    -------
    get_projects(search='', category_id=None, sort='newest'):
         Retrieves a list of projects, optionally filtered by search term, category, and sorted by the specified criteria.
    
    get_project(project_id):
         Retrieves a single project's details by its unique identifier.
    """
    def get_projects(self, search='', category_id=None, sort='newest'):
        query = "SELECT p.*, c.name as category_name FROM Projects p JOIN Categories c ON p.category_id = c.id WHERE 1=1"
        params = []
        if search:
            query += " AND p.name LIKE ?"
            params.append(f"%{search}%")
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
        if sort == 'newest':
            query += " ORDER BY p.id DESC"  # Assume id increases over time
        elif sort == 'near_deadline':
            query += " ORDER BY p.deadline ASC"
        elif sort == 'most_funded':
            query += " ORDER BY p.current_funded DESC"
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_project(self, project_id):
        self.cursor.execute("SELECT p.*, c.name as category_name FROM Projects p JOIN Categories c ON p.category_id = c.id WHERE p.id=?", (project_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None