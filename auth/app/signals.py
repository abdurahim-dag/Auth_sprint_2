import smtplib

from flask import current_app
from flask.signals import Namespace

from app.models import Messages
from app.utils import confirm_url_generate


my_signals = Namespace()
user_created = my_signals.signal('user-created')


@user_created.connect
def send_confirmation_email(user):
    """Сигнал отправляет на почту, для подтверждения email."""
    if not user.status:
        try:
            from_email = current_app.config['EMAIL_SENDER']
            host = current_app.config['EMAIL_HOST']
            port = int(current_app.config['EMAIL_PORT'])
            password = current_app.config['EMAIL_PASSWORD']
            to_email = user.email
            subject = Messages.subject
            url = confirm_url_generate(user.id)
            message = Messages.message % (user.nickname, url)
            with smtplib.SMTP(host, port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(from_email, password)  # Replace with your own email password
                smtp.sendmail(from_email, to_email, f'Subject: {subject}\n\n{message}')
        except:
            current_app.logger.error(f"Exception on send email for user {user.id}!")
