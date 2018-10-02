from django.core.management import BaseCommand

from common import testing


class Command(BaseCommand):
    help = 'Train the classifier model from the training data in the database'

    def handle(self, *args, **options):
        testing.test_output_svm()
