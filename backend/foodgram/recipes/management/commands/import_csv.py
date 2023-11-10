import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = "Import ingredients from CSV file"

    def handle(self, *args, **options):
        csv_ingredients_file_path = os.path.join(
            settings.BASE_DIR, "data", "ingredients.csv"
        )
        csv_tags_file_path = os.path.join(
            settings.BASE_DIR, "data", "tags.csv"
        )
        try:
            with open(
                    csv_ingredients_file_path, "r", encoding="utf-8"
            ) as csv_file:
                csv_reader = csv.reader(csv_file)
                for name, measurement_unit in csv_reader:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name, measurement_unit=measurement_unit
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Ингредиент"
                                f" {ingredient.name} добавлен в базу."
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Ингредиент"
                                f" {ingredient.name} уже есть в базе."
                            )
                        )
        except FileNotFoundError:
            raise CommandError(
                "Файл ingredients не найден по указанному пути."
            )
        try:
            with open(csv_tags_file_path, "r", encoding="utf-8") as ing_file:
                reader = csv.reader(ing_file, delimiter=',')
                for name, slug, color in reader:
                    tag, created = Tag.objects.get_or_create(
                        name=name,
                        slug=slug,
                        color=color,
                    )
                    if not created:
                        self.stdout.write(self.style.WARNING(
                            f"Тег {tag.name} уже есть в базе. Обновлено."))
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Тег {tag.name} добавлен в базу.")
                        )
        except FileNotFoundError:
            raise CommandError(
                "Файл tags не найден по указанному пути."
            )
