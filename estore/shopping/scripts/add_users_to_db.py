"""
HOW TO RUN THIS
 - python manage.py runscript add_users_to_db -v3
"""
from django.contrib.auth.hashers import make_password


def run():
    from django.contrib.auth.models import User

    user_metadata = {
        "first_name": "user",
        "last_name": "foobar",
        "is_staff": 0,
        "is_active": 1,
    }

    for i in range(1, 6):
        password = make_password("testpass123")
        username = f"user{i}"
        new_user = User.objects.create_user(
            username=username,
            password=password,
            email=f"{username}@example.com",
            **user_metadata
        )
        new_user.save()
