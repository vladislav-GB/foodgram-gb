import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из CSV файла'

    def handle(self, *args, **options):
        with open('data/ingredients.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            ingredients = [
                Ingredient(
                    name=row[0],
                    measurement=row[1],
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients)
            self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены!'))