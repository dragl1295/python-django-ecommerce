from rest_framework import generics,status,viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied

from .models import Cart, CartItem, Order, OrderItem, Product
from .serializers import CartItemSerializer, CustomTokenObtainPairSerializer, OrderSerializer, ProductSerializer, UserSerializer
from rest_framework.response import Response
from .permissions import IsAdminOrSelf, IsSeller


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'date_of_birth': user.date_of_birth,
                    'is_seller': user.is_seller
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            refresh = serializer.validated_data['refresh']
            access = serializer.validated_data['access']
            return Response({
                'refresh': str(refresh),
                'access': str(access),
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'date_of_birth': user.date_of_birth,
                    'is_seller': user.is_seller
                }
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return User.objects.filter(id=self.request.user.id)    
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsSeller]

    def get_queryset(self):
        return Product.objects.all()

    def perform_create(self, serializer):
        # Set the user to the current user when creating a new product
        
         user = self.request.user
         print(f"Creating product for user: {user}")
         if user.is_seller or user.is_superuser:
            serializer.save(user=user)
         else:
             # Raise an error if the user does not meet the criteria
            raise PermissionDenied("You must be a seller or superuser to create a product.")

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(Cart, user=self.request.user)
        serializer.save(cart=cart)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(f"updating product for user: {self.request.user}")

        return Order.objects.filter(user=self.request.user)


