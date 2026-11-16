"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from core.security.views import (
    SecurityAIDetectView,
    SecurityAttackRunView,
    SecurityBigDataSimulateView,
    SecurityDashboardView,
    SecurityDecryptView,
    SecurityEncryptView,
    SecurityStegoEmbedView,
    SecurityStegoExtractView,
)
from core.views import (
    LoginView,
    LogoutView,
    ProcessoViewset,
    RegisterView,
    SavedSearchViewSet,
    UserMeView,
)
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'processos', ProcessoViewset, basename='document')
router.register(r'saved-searches', SavedSearchViewSet, basename='saved-search')


auth_urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', UserMeView.as_view(), name='auth-me'),
]

security_urlpatterns = [
    path('security/encrypt/', SecurityEncryptView.as_view(), name='security-encrypt'),
    path('security/decrypt/', SecurityDecryptView.as_view(), name='security-decrypt'),
    path('security/steganography/embed/', SecurityStegoEmbedView.as_view(), name='security-stego-embed'),
    path('security/steganography/extract/', SecurityStegoExtractView.as_view(), name='security-stego-extract'),
    path('security/attacks/run/', SecurityAttackRunView.as_view(), name='security-attacks-run'),
    path('security/bigdata/simulate/', SecurityBigDataSimulateView.as_view(), name='security-bigdata-simulate'),
    path('security/ai/detect-anomalies/', SecurityAIDetectView.as_view(), name='security-ai-detect'),
    path('security/dashboard/', SecurityDashboardView.as_view(), name='security-dashboard'),
]


def health(request):
    return HttpResponse('OK', content_type='text/plain')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(auth_urlpatterns)),
    path('api/', include(security_urlpatterns)),
    path('api/', include(router.urls)),
]

urlpatterns += [
    path('health/', health),
    path('silk/', include('silk.urls', namespace='silk')),
]
