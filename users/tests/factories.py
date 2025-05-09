import factory
from django.contrib.auth.models import User
from users.models import UserProfile

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    keycloak_id = factory.Sequence(lambda n: f'keycloak-{n}')
    mfa_enabled = False
    phone_number = factory.Sequence(lambda n: f'+1555000{n:04d}') 