from django.urls import path
from .views import create_user
from .views import authenticate_user
from .views import create_reading
from .views import get_readings
from .views import get_user_profile
from .views import api_home
from .views import upload_profile_picture
from .views import view_readings
from .views import reading_detail
from .views import upvote_reading
from .views import submit_comment
from .views import toggle_favorite
from .views import get_comments
from .views import check_favorite_status
from .views import get_favorites
from .views import get_newreadings

urlpatterns = [
    path('', api_home, name='api_home'),  # ✅ Add a default API route
    path("create-user/", create_user, name="create_user"),
    path("authenticate-user/",authenticate_user,name="authenticate_user"),
    path("create-reading/",create_reading,name="create_reading"),
    path("readings/",get_readings,name="get_readings"),
    path("user-profile/<int:user_id>/",get_user_profile,name="get_user_profile"),
    path("upload-profile-picture/<int:user_id>/", upload_profile_picture, name="upload_profile_picture"),
    path("viewreadings/",view_readings, name="view_readings"),
    path("viewreadings/<int:id>/", reading_detail, name="reading_detail"),
    path("upvote/<int:id>/", upvote_reading, name="upvote_reading"),
    path("comment/<int:reading_id>/", submit_comment, name="submit_comment"),
    path("comments/<int:reading_id>/", get_comments, name="get_comments"),
    path("favorite/<int:reading_id>/", toggle_favorite, name="toggle_favorite"),
    path("favorite/<int:reading_id>/status/", check_favorite_status, name="check_favorite_status"),
    path("favorites/", get_favorites, name="get_favorites"),
    path("newreadings/", get_newreadings, name="get_newreadings"),


]
