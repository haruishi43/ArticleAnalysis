from django.core.management import BaseCommand

import os
from common import scraper


class Command(BaseCommand):
    help = 'Deletes the training data stored in database'
    
    def handle(self, *args, **options):
        scraper.delete_data()
        os.remove('common/model.p')
