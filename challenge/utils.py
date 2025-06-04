from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from challenge.redis_client import publish_event

def send_email(data: dict) -> bool:
    template, email_txt = "inbound_parser.html", "inbound_parser.txt"
    html_content = render_to_string(template, data)
    plain_content = render_to_string(email_txt, data)
    msg = EmailMultiAlternatives(
        data["subject"],
        plain_content,
        settings.SENDER_EMAIL,
        [settings.EMAIL_HOST_USER],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def inbound_notify(data: dict):
    publish_event("notification", {"event":"inbound_notify", "data": data})
     