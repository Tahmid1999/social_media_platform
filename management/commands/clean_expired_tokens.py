# I am writing  this  to automatically  cleaned  expired  tokens by corn jobs from  the  database  every  24  hours.

from django.core.management.base import BaseCommand
from django.utils import timezone
from user.models import User  

class Command(BaseCommand):
    help = 'Clean up expired tokens in the logged_in_tokens array'

    def handle(self, *args, **options):
        sixteen_days_ago = timezone.now() - timezone.timedelta(days=16)

        users_with_expired_tokens = User.objects.filter(
            logged_in_tokens__created_datetime__lt=sixteen_days_ago
        )

        for user in users_with_expired_tokens:
            user.logged_in_tokens = [
                token for token in user.logged_in_tokens
                if token['created_datetime'] >= sixteen_days_ago.isoformat()
            ]
            user.save()
        self.stdout.write(self.style.SUCCESS('Expired tokens cleaned up.'))