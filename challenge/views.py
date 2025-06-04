from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape

from challenge.utils import inbound_notify, send_email
from challenge.redis_client import subscribe


def home(request):
    return render(request, 'home.html')

@csrf_exempt
def submit_message(request):
    if request.method == "POST":
        msg = request.POST.get("message")
        email = request.POST.get("email")
        name = request. POST.get("fullname")
        data = {"subject": msg, "email": email, "name": name}
        send_email(data=data)
        return HttpResponse(f"""
            <div class="success-message">✅ Thank you {escape(name)}! Your message has been sent.</div>
        """)
    return HttpResponse("")

def inbound_webhook(request):
    if request.method == "POST":
        data = request.POST.values()
        inbound_notify(data)
        return HttpResponse("Message received successfully.")

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
