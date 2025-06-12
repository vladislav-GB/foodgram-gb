import os
import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from django.conf import settings


class Command(BaseCommand):
    help = "Загрузка ингредиентов из CSV файла"

    def handle(self, *args, **options):
        project_root = os.path.dirname(os.path.dirname(settings.BASE_DIR))
        path = os.path.join(project_root, "data", "ingredients.csv")

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f"Файл не найден: {path}"))
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                ingredients = [
                    Ingredient(
                        name=row[0].strip(),
                        measurement=row[1].strip(),
                    )
                    for row in reader
                    if len(row) == 2
                ]
                Ingredient.objects.bulk_create(ingredients)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Успешно загружено {len(ingredients)} ингредиентов!"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Ошибка при загрузке ингредиентов: {str(e)}")
            )
