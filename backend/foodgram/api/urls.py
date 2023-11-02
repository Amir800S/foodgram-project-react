from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = "api"

router = DefaultRouter()

router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"users", CustomUserViewSet, basename="users")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
