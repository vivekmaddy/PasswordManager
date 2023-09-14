from django_cron import CronJobBase, Schedule
from datetime import datetime


from .models import Passwords
# class ExpirePasswordCron(CronJobBase):
#     RUN_EVERY_MINS = 1  

#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'organisation.cron.ExpirePasswordCron'  # A unique code for your cron job

#     def do(self):
#         now = datetime.now()
#         passwords = Passwords.objects.filter(expired=False, duration_to__lte=now)
#         if passwords:
#             passwords.update(expired=True)


from background_task import background
from django.contrib.auth.models import User

@background()
def expire_passwords():
    now = datetime.now()
    passwords = Passwords.objects.filter(expired=False, duration_to__lte=now)
    if passwords:
        passwords.update(expired=True)