from django.core.management import BaseCommand

from common import scraper


class Command(BaseCommand):
    help = 'Gets training data from gunosy.com and saves it in the database'
    
    def handle(self, *args, **options):
        scraper.get_training_data()
