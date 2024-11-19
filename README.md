# Django-MiniProject2

## Student Management System
This project is a comprehensive student management system built with Django and Django Rest Framework, allowing for role-based access for students, teachers, and admins.


## Ensure you have the following installed:
- Django
- Redis 
- Celery

## To Start Celery Workers and Beat:
celery -A studentmanagementsystem worker -l info

celery -A studentmanagementsystem beat -l info

## To Start Redis
Redis is required for Celery to function correctly. To start Redis, use the following command (on Linux/Unix systems):

/usr/bin/redis-server

## To Start Unit Test
python manage.py test
