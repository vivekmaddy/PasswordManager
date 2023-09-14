from django.core.mail import EmailMessage

def send_notification(to_email, subject, message):
    email = EmailMessage(subject, message, to=[to_email])
    email.send()