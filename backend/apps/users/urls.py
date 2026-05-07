from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, RoleViewSet, DepartmentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'departments', DepartmentViewSet)

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls