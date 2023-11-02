import csv
import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
application = get_wsgi_application()

from recipes.models import Ingredient

csv_file_path = os.path.join(settings.BASE_DIR, "data", "ingredients.csv")

with open(csv_file_path, "r", encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        name, measurement_unit = row
        ingredient, created = Ingredient.objects.get_or_create(
            name=name, measurement_unit=measurement_unit
        )
        if created:
            print(f"Ингредиент {ingredient.name} добавлен в базу данных.")
        else:
            print(
                f"Ингредиент {ingredient.name} уже существует в базе данных."
            )
