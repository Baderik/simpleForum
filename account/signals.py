from django.dispatch import Signal

__all__ = ["friend_request_accepted", "friend_request_rejected"]

friend_request_accepted = Signal()
friend_request_rejected = Signal()
