from django.core.management import BaseCommand

from common import testing


class Command(BaseCommand):
    help = 'Print confusion matrix after model is trained'
    
    def handle(self, *args, **options):
        testing.print_confusion_matrix()