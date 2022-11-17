from django.conf import settings
from django.db import models

__all__ = ["LikeDislikeManager"]


class LikeDislikeManager(models.Manager):
    def likes(self):
        return self.filter(vote=1)

    def dislikes(self):
        return self.get_queryset().filter(vote=-1)

    def rating(self):
        return self.get_queryset().aggregate(models.Sum('vote')).get('vote__sum') or 0

    def set_votes_or_create(
            self, user: settings.AUTH_USER_MODEL, vote: int, set_unset=True, **kwargs):
        votes = self.filter(author=user)
        if votes.exists():
            vote_model = votes.first()
            if set_unset and vote_model.vote == vote:
                vote_model.vote = self.model.UNSET
            else:
                vote_model.vote = vote

        else:
            vote_model = self.model(author=user, vote=vote, **kwargs)
        vote_model.save()
        return vote

    def last_vote(self, user: settings.AUTH_USER_MODEL):
        votes = self.filter(author=user)
        if votes.exists():
            return votes.first().vote
        else:
            return self.model.vote.default
