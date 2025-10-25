from django.contrib import admin
from django.urls import path
# dog_service is currently a fallback view returning 503 if Spyne isn't loaded.
from dogapp.views import dog_service, DogDetailAPIView
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # SOAP endpoint
   # path('soap/dogservice/', dog_service),

    # REST endpoint (secured with DRF + JWT/Session + centralized IsOwner permission)
    path('rest/dog/<int:pk>/', DogDetailAPIView.as_view(), name='rest_get_dog'),

    # Session-based login/logout
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # GraphQL endpoint (secured with JWT middleware in schema.py)
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

