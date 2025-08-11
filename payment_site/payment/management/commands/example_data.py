from decimal import Decimal

from django.core.management.base import BaseCommand
from ...models import Items, Orders, Discounts, Tax


class Command(BaseCommand):
    help = 'Создание примеров для работы с приложением'

    def handle(self, *args, **options):
        item1, _ = Items.objects.get_or_create(
            name="Звезды в телеграм в количестве 1000 штук",
            defaults={
                'description': 'Покупка 2500 звезд на аккаунт телеграм',
                'price': 1649,
                'currency': 'rub'
            }
        )

        item2, _ = Items.objects.get_or_create(
            name="Подписка на Spotify",
            defaults={
                'description': 'Подписка на сервис Spotify для прослушивания иностранной музыки',
                'price': 5.49,
                'currency': 'usd'
            }
        )
        item3, _ = Items.objects.get_or_create(
            name="Электронная книга 'Мастер и Маргарита' М. А. Булгаков",
            defaults={
                'description': 'Покупка книги в электронном варианте Мастер и Маргарита автора М. А. Булгакова',
                'price': 300,
                'currency': 'rub'
            }
        )

        item4, _ = Items.objects.get_or_create(
            name="Покупка аккаунта Steam",
            defaults={
                'description': 'Покупка аккаунта Steam с играми: Team Fortress 2, Dota 2, Crossout, Deceit, Russian Fishing, CS2, PUBG',
                'price': 29.05,
                'currency': 'usd'
            }
        )

        discount1, _ = Discounts.objects.get_or_create(
            name='SUMMERSALE',
            defaults={
                'percent_off': 15,
                'duration': 'repeating',
            }
        )

        discount2, _ = Discounts.objects.get_or_create(
            name='ALL5IN',
            defaults={
                'percent_off': 5,
                'duration': 'repeating',
            }
        )

        tax, _ = Tax.objects.get_or_create(
            name='НДС',
            defaults={
                'percent': 10
            }
        )

        order1, created = Orders.objects.get_or_create(
            total_price = Decimal('1656.65'),
            discount=discount1,
        )

        if created:
            order1.item.set([item1, item3])
            order1.save()

        order2, created = Orders.objects.get_or_create(
            total_price = Decimal('34.54'),
            discount=discount2,
        )

        if created:
            order2.item.set([item2, item4])
            order2.tax.set([tax])
            order2.save()