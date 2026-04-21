from django.apps import AppConfig


class PayappConfig(AppConfig):
    name = 'payapp'

    def ready(self):
        from django.contrib.auth.models import User

        if not User.objects.filter(username='admin1').exists():
            User.objects.create_user(
                username='admin1',
                password='admin1',
                is_staff=True,
                is_superuser=True
            )
