from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('core.urls')),
    path("accounts/", include("accounts.urls")),
    path('pokedex/', include('pokemon.urls')),
    path('favorites/', include('favorites.urls')),
    path('teams/', include('teams.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)