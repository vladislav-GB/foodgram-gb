import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов из CSV файла"

    def handle(self, *args, **options):
        path = os.path.abspath(
            os.path.join(settings.BASE_DIR, "../../data/ingredients.csv")
        )

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f"Файл не найден: {path}"))
            return

        added = 0
        skipped = 0

        try:
            with open(path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) != 2:
                        skipped += 1
                        continue
                    name, measurement = row[0].strip(), row[1].strip()
                    if not Ingredient.objects.filter(
                        name=name, measurement_unit=measurement
                    ).exists():
                        try:
                            Ingredient.objects.create(
                                name=name, measurement_unit=measurement
                            )
                            added += 1
                        except IntegrityError:
                            skipped += 1
                    else:
                        skipped += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Добавлено {added} ингредиентов. Пропущено: {skipped}"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Ошибка при загрузке ингредиентов: {str(e)}")
            )
