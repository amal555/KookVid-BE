from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve as static_serve
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/recipes/', include('recipes.urls')),
    path('api/users/', include('users.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Serve index.html at root "/"
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    # Serve React assets (JS/CSS) from /assets/
    re_path(r'^assets/(?P<path>.*)$', static_serve, {
        'document_root': r"C:\Users\Lenovo 500\Documents\CookU\dish-master-hub\dist\assets",
    }),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)