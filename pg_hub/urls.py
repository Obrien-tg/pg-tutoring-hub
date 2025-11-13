"""
URL configuration for pg_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

urlpatterns = [
    # Configurable admin URL (default 'admin/') configured via settings.ADMIN_URL
    path(getattr(settings, "ADMIN_URL", "admin/"), admin.site.urls),
    # Lightweight health check endpoint
    path("healthz", lambda request: JsonResponse({"status": "ok"})),
    path("", include("core.urls")),
    path("users/", include("users.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("hub/", include("hub.urls")),
    path("chat/", include("chat.urls")),
    path("api/firebase/", include("users.firebase_urls")),
]

# API Documentation
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
