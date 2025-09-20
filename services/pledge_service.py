from datetime import datetime
from .database import Database
from .project_service import ProjectService  

class PledgeService(Database):
    """
    Service class for handling pledge-related operations in the crowdfunding platform.
    Methods
    -------
    add_pledge(user_id, project_id, amount, reward_tier_id):
        Attempts to add a pledge for a user to a project with an optional reward tier.
        Validates project existence, deadline, reward tier constraints, and updates relevant tables.
        Returns a tuple (status, message) indicating success or rejection and reason.
    add_rejected_pledge(user_id, project_id, amount, reward_tier_id, reason):
        Records a rejected pledge attempt in the database with the provided reason.
    get_stats(user_id):
        Retrieves the count of successful and rejected pledges for the specified user.
        Returns a tuple (success_count, rejected_count).
    """
    def add_pledge(self, user_id, project_id, amount, reward_tier_id):
        now = datetime.now()
        # Instantiate ProjectService to get project details
        project_service = ProjectService()
        project = project_service.get_project(project_id)
        project_service.close()
        if not project:
            return 'rejected', 'Project not found'
        deadline_date = datetime.strptime(project['deadline'], '%Y-%m-%d').date()
        if deadline_date < now.date():
            return 'rejected', 'Deadline passed'

        if reward_tier_id:
            self.cursor.execute("SELECT min_amount, quota_remaining FROM RewardTiers WHERE id=?", (reward_tier_id,))
            tier = self.cursor.fetchone()
            if tier is None:
                return 'rejected', 'Invalid tier'
            if amount < tier['min_amount']:
                return 'rejected', 'Amount too low for tier'
            if tier['quota_remaining'] <= 0:
                return 'rejected', 'Quota full'

        # Success: update
        self.cursor.execute("INSERT INTO Pledges (user_id, project_id, timestamp, amount, reward_tier_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, project_id, now, amount, reward_tier_id, 'success'))
        self.cursor.execute("UPDATE Projects SET current_funded = current_funded + ? WHERE id=?", (amount, project_id))
        if reward_tier_id:
            self.cursor.execute("UPDATE RewardTiers SET quota_remaining = quota_remaining - 1 WHERE id=?", (reward_tier_id,))
        self.conn.commit()
        return 'success', ''

    def add_rejected_pledge(self, user_id, project_id, amount, reward_tier_id, reason):
        now = datetime.now()
        self.cursor.execute("INSERT INTO Pledges (user_id, project_id, timestamp, amount, reward_tier_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, project_id, now, amount, reward_tier_id, 'rejected'))
        self.conn.commit()

    def get_stats(self, user_id):
        self.cursor.execute("SELECT status, COUNT(*) as count FROM Pledges WHERE user_id = ? GROUP BY status", (user_id,))
        stats = {row['status']: row['count'] for row in self.cursor.fetchall()}
        return stats.get('success', 0), stats.get('rejected', 0)