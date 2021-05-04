from app.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(
            email__endswith='smilewestada.com',
        )
        for user in users:
            user.delete()
        self.stdout.write("Complete.")
        return
