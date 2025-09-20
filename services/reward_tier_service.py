from .database import Database

class RewardTierService(Database):
    """
    Service class for handling operations related to reward tiers in the database.

    Methods
    -------
    get_reward_tiers(project_id)
        Retrieves all reward tiers associated with the specified project ID.

    Parameters
    ----------
    project_id : int
        The unique identifier of the project for which to fetch reward tiers.

    Returns
    -------
    list of dict
        A list of dictionaries, each representing a reward tier for the given project.
    """
    def get_reward_tiers(self, project_id):
        self.cursor.execute("SELECT * FROM RewardTiers WHERE project_id=?", (project_id,))
        return [dict(row) for row in self.cursor.fetchall()]