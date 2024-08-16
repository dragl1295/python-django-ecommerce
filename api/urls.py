from django.urls import include, path
from .views import CartItemViewSet, OrderViewSet, ReviewViewSet, UserViewSet,ProductViewSet
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'rooms',RoomView)
# router.register(r'messages',MessageView)
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')


urlpatterns = [
   path('register/', views.RegisterView.as_view(), name='register'),
   path('login/', views.LoginView.as_view(), name='login'),
   path('', include(router.urls)),
]

