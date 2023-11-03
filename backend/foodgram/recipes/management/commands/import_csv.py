import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from CSV file'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(
            settings.BASE_DIR, "data", "ingredients.csv"
        )

        with open(csv_file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                name, measurement_unit = row
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Ингредиент {ingredient.name} добавлен в базу.'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Ингредиент {ingredient.name} уже есть в базе.'
                        )
                    )
