from rest_framework.permissions import BasePermission
from events.models import Event

class IsOwner(BasePermission):
    message = "You must be the owner of this event."

    def has_permission(self, request, view):
        obj = Event.objects.get(id=view.kwargs['event_id'])
        if obj.owner == request.user:
            return True
        else:
            return False

class CanBook(BasePermission):
    message = "Not enough available seats"

    def has_permission(self, request, view):
        obj = Event.objects.get(id=view.kwargs['event_id'])
        if obj.get_seats_left() >= int(request.data['tickets']):
            return True
        else:
            return False

class IsValidNumber(BasePermission):
    message = "Not a valid tickets number"

    def has_permission(self, request, view):
        if int(request.data['tickets']) > 0:
            return True
        else:
            return False