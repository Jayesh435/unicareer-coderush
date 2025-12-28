"""
Management command to create an admin user for UniCareer
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin user with proper permissions to access both Django admin and custom admin dashboard'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the admin user')
        parser.add_argument('email', type=str, help='Email for the admin user')
        parser.add_argument('password', type=str, help='Password for the admin user')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            # Create admin user with role='admin'
            # The save() method will automatically set is_staff=True and is_superuser=True
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='admin'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully created admin user: {username}\n'
                    f'Email: {email}\n'
                    f'Role: admin\n'
                    f'is_staff: {user.is_staff}\n'
                    f'is_superuser: {user.is_superuser}\n\n'
                    f'You can now access:\n'
                    f'- Django Admin: http://localhost:8000/admin/\n'
                    f'- Custom Admin Dashboard: http://localhost:8000/admin-dashboard/\n'
                )
            )
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(f'Error: User with username "{username}" already exists.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )
