import json
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape

from challenge.utils import inbound_notify, send_email
from challenge.redis_client import subscribe
from django_q.tasks import async_task


def home(request):
    return render(request, 'home.html')

@csrf_exempt
def submit_message(request):
    
    if request.method == "POST":
        
        method = request.POST
        
        msg, email, name, subject = method.get("message"), method.get("email"), method.get("fullname"), method.get("subject")

        async_task(send_email, {"subject": subject, "email": email, "name": name, "message": msg})
        
        return HttpResponse(f"""<div class="success-message">✅ Thank you {escape(name)}! Your message has been sent.</div>""")
    else:
        return HttpResponse("")

@csrf_exempt
def inbound_webhook(request):
    
    if request.method == "POST":
        payload = json.loads(request.body)
        data = {
            "subject": payload.get("Subject"),
            "date": payload.get("Date"),
            "text_body": payload.get("TextBody"),
            "ip": request.META.get('REMOTE_ADDR'),
        }
        async_task(inbound_notify, data)
        return HttpResponse("Message received successfully.")
    else:
        return HttpResponse("Invalid request method.", status=405)

def sse_view(request):
    def event_stream():
        pubsub = subscribe("notification")
        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    # Decode the message data from bytes to string
                    yield f"data: {message['data'].decode()}\n\n"
        except GeneratorExit:
            pubsub.close()

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
