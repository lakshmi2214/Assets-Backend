from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from assets import views as asset_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('init-db/', asset_views.init_db, name='init_db'), # Helper to run migrations
    path('', include('assets.urls')),   # Server-side rendered pages
    path('api/v1/', include('assets.api.v1.urls')),  # REST API for frontend
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


