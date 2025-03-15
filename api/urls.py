from django.urls import path
from .views import create_user
from .views import authenticate_user
from .views import create_reading
from .views import get_readings
from .views import get_user_profile

urlpatterns = [
    path("create-user/", create_user, name="create_user"),
    path("authenticate-user/",authenticate_user,name="authenticate_user"),
    path("create-reading/",create_reading,name="create_reading"),
    path("readings/",get_readings,name="get_readings"),
    path("user-profile/<int:user_id>/",get_user_profile,name="get_user_profile"),


]
