from django.core.management.base import BaseCommand
from ...services import MeetService

class Command(BaseCommand):
    def handle(self, *args, **options):
        MeetService().send_star_emails_from_commandline()
