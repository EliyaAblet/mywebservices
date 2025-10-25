# dogapp/views.py

# dogapp/views.py

# ---------- Standard / DRF imports ----------
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Dog
from .serializers import DogSerializer
from .permissions import IsOwner


# ---------- Optional SOAP (Spyne) imports ----------
SPYNE_AVAILABLE = True
try:
    # Try to import Spyne and its Django integration.
    from spyne import Application, rpc, ServiceBase, Integer, Unicode
    from spyne.protocol.soap import Soap11
    from spyne.server.django import DjangoApplication
except Exception:
    SPYNE_AVAILABLE = False


# ---------- REST Endpoints ----------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def rest_get_dog(request, dog_id: int):
    """
    Simple REST function view that returns a single Dog if the requester is the owner.
    """
    try:
        dog = Dog.objects.get(pk=dog_id)
        if dog.owner != request.user:
            return JsonResponse(
                {"error": "You do not have permission to access this dog."}, status=403
            )
        serializer = DogSerializer(dog)
        return JsonResponse(serializer.data, safe=False)
    except Dog.DoesNotExist:
        return JsonResponse({"error": "Dog not found"}, status=404)


class DogDetailAPIView(generics.RetrieveAPIView):
    """
    API view to retrieve a dog object, only if the user is the owner.
    """
    queryset = Dog.objects.all()
    serializer_class = DogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]


# ---------- SOAP helpers & service (only if Spyne is available) ----------
def _auth_from_environ(environ):
    """
    Extract Basic Auth from a WSGI environ-like dict (as used by Spyne's transport.req).
    Returns (user, error_tuple or None). error_tuple = (status, message, headers_dict)
    """
    auth_header = environ.get("HTTP_AUTHORIZATION")
    if not auth_header:
        return None, (401, "Unauthorized", {"WWW-Authenticate": 'Basic realm="DogService"'})

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "basic":
        return None, (401, "Unauthorized", {"WWW-Authenticate": 'Basic realm="DogService"'})

    import base64
    try:
        username, password = base64.b64decode(parts[1]).decode("utf-8").split(":", 1)
    except Exception:
        return None, (401, "Unauthorized", {"WWW-Authenticate": 'Basic realm="DogService"'})

    user = authenticate(username=username, password=password)
    if user is not None and getattr(user, "is_authenticated", False):
        return user, None

    return None, (401, "Unauthorized", {"WWW-Authenticate": 'Basic realm="DogService"'})


if SPYNE_AVAILABLE:
    class DogService(ServiceBase):
        @rpc(Integer, _returns=Unicode)
        def get_dog(ctx, dog_id):
            # ctx.transport.req is a WSGI environ-style dict
            environ = getattr(ctx.transport, "req", {}) or {}
            user, error = _auth_from_environ(environ)

            if user is None:
                status_code, message, headers = error
                ctx.transport.resp_code = status_code
                for k, v in headers.items():
                    ctx.transport.resp_headers[k] = v
                return message

            try:
                dog = Dog.objects.get(pk=dog_id)
                if dog.owner != user:
                    return "You do not have permission to view this dog."
                return f"Dog: {dog.name}, Age: {dog.age}, Breed: {dog.breed}"
            except Dog.DoesNotExist:
                return "Dog not found."

    soap_app = Application(
        [DogService],
        "dogapp.soap",
        in_protocol=Soap11(validator="lxml"),
        out_protocol=Soap11(),
    )
    dog_service = csrf_exempt(DjangoApplication(soap_app))

else:
    # Fallback stub so imports in urls.py won't crash the site.
    @csrf_exempt
    def dog_service(request, *args, **kwargs):
        return HttpResponse(
            "SOAP endpoint temporarily disabled (Spyne unavailable).",
            status=503,
            content_type="text/plain",
        )

