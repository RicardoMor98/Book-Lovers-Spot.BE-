from django.contrib import admin
from django.urls import path, include
from .views import home  # ✅ Import home view

urlpatterns = [
    path('', home, name='home'),  # ✅ Add root URL route
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
