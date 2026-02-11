# Тестовые клиенты: 2 физлица, 2 юрлица/ИП (любые имена и названия)

from django.core.management.base import BaseCommand

from contract_maker.models import Customer


class Command(BaseCommand):
    help = "Добавить тестовых клиентов: 2 физлица и 2 юрлица/ИП."

    def handle(self, *args, **options):
        created_count = 0

        # 2 физических лица
        c, created = Customer.objects.get_or_create(
            org_name="Петров Пётр Петрович",
            defaults={
                "client_type": Customer.CLIENT_TYPE_INDIVIDUAL,
                "address": "г. Минск, ул. Примерная, д. 1, кв. 1",
                "short_name": "П.П. Петров",
            },
        )
        if created:
            created_count += 1
            self.stdout.write(f"  + {c.org_name} (физлицо)")

        c, created = Customer.objects.get_or_create(
            org_name="Сидорова Анна Ивановна",
            defaults={
                "client_type": Customer.CLIENT_TYPE_INDIVIDUAL,
                "address": "г. Гомель, пр. Победы, д. 10, кв. 5",
                "short_name": "А.И. Сидорова",
            },
        )
        if created:
            created_count += 1
            self.stdout.write(f"  + {c.org_name} (физлицо)")

        # 2 юридических лица / ИП
        c, created = Customer.objects.get_or_create(
            org_name='ООО "Тестовая компания"',
            defaults={
                "client_type": Customer.CLIENT_TYPE_LEGAL,
                "rep_position": "директора",
                "rep_name": "Иванов Иван Иванович",
                "basis": "Устава",
                "short_name": "И.И. Иванов",
                "address": "г. Минск, ул. Бизнесовая, д. 5",
                "unp": "123456789",
                "okpo": "12345678",
                "iban": "BY00XXXX00000000000000000000",
            },
        )
        if created:
            created_count += 1
            self.stdout.write(f"  + {c.org_name} (юрлицо)")

        c, created = Customer.objects.get_or_create(
            org_name="ИП Козлов Сергей Николаевич",
            defaults={
                "client_type": Customer.CLIENT_TYPE_LEGAL,
                "rep_name": "Козлов Сергей Николаевич",
                "basis": "свидетельства о гос. регистрации",
                "short_name": "С.Н. Козлов",
                "address": "г. Минск, ул. Торговая, д. 3",
                "unp": "987654321",
                "okpo": "87654321",
                "iban": "BY11YYYY00000000000000000000",
            },
        )
        if created:
            created_count += 1
            self.stdout.write(f"  + {c.org_name} (ИП)")

        if created_count:
            self.stdout.write(self.style.SUCCESS(f"Добавлено клиентов: {created_count}"))
        else:
            self.stdout.write("Все тестовые клиенты уже есть в базе.")
