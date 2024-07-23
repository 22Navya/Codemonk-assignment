from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ParagraphViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'paragraphs', ParagraphViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
