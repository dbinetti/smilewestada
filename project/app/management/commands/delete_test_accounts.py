from django.core.management.base import BaseCommand
from django.db.models import Q

from app.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(
            Q(email__endswith='smilewestada.com') |
            Q(email__endswith='tfbnw.net')
        )
        for user in users:
            user.delete()
        self.stdout.write("Complete.")
        return
