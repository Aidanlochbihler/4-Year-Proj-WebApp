import random
from django.core.management.base import BaseCommand
from datetime import datetime
from django.contrib.auth import get_user_model

from django.contrib.auth.models import Group, Permission
from pymongo import MongoClient
from django.contrib.contenttypes.models import ContentType

from core.database import trip_col

User = get_user_model()

class Command(BaseCommand):
	help = 'Populates the database with testing data'
	def handle(self, *args, **kwargs):
		# time = timezone.now().strftime('%X')
		# self.stdout.write("It's now %s" % time)
		trip_col.drop()

		User.objects.all().delete()
		user = User.objects.create_superuser('admin', 'admin@admin.admin', 'admin')
		Permission.objects.all().delete()
		Group.objects.all().delete()
		ct = ContentType.objects.get(app_label='auth', model='user')

		manager_group = Group.objects.create(name='user')
		can_edit_all = Permission.objects.create(codename='can_edit_all',
                                       name='Can edit all', content_type = ct)
		can_view_all = Permission.objects.create(codename='can_view_all',
                                       name='Can view all', content_type = ct)
		manager_group.permissions.add(can_edit_all, can_view_all)
		
		for i in range(2):
			user = User.objects.create_user(f'user{i}', f'user{i}@carleton.ca', '1234')
			manager_group.user_set.add(user)
			user.save()


		# Judge_group = Group.objects.create(name='basic')
		# can_edit_self_preferences = Permission.objects.create(codename='can_edit_self',
  #                                      name='Can edit self', content_type = ct) 
		# can_view_self_preferences = Permission.objects.create(codename='can_view_self',
  #                                      name='Can view self', content_type = ct) 
		# Judge_group.permissions.add(can_view_self_preferences, can_edit_self_preferences)

		# for i in range(10):
		# 	user = User.objects.create_user(f'user{i}', f'test{i}@carleton.ca', '1234')
		# 	Judge_group.user_set.add(user)
		# 	user.save()



		
		# {codename :"can_publish"}
		

			