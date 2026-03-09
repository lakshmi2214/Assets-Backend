from django.urls import path, include
from rest_framework.routers import DefaultRouter
from assets.viewsets import AssetViewSet, BookingViewSet, CategoryViewSet, SubCategoryViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from assets.api.v1.views import signup, verify_email

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subcategories', SubCategoryViewSet, basename='subcategory')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', signup, name='api-signup'),
    path('auth/verify-email/', verify_email, name='api-verify-email'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
