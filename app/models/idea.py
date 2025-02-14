class Idea:
    def __init__(self, title: str, description: str, votes: int = 0):
        self.title = title
        self.description = description
        self.votes = votes

    def upvote(self):
        self.votes += 1

    def downvote(self):
        self.votes -= 1

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "votes": self.votes
        }