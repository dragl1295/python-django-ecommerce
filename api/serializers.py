from rest_framework import serializers 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import Cart, CartItem, Order, OrderItem, Product, Review
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'address', 'date_of_birth', 'is_seller')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        # You can apply Django's default password validators or custom ones here
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value  
        
class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['user']  # Ensure 'user' is read-only

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user  # Automatically set the user
        return super().create(validated_data)
    
        
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token
        token['email'] = user.email
        token['is_seller'] = user.is_seller
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token    




class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']
        
    def validate(self, data):
        product = data['product']
        quantity = data['quantity']

        if quantity >= product.stock:
            raise serializers.ValidationError({
                "quantity": f"Requested quantity ({quantity}) exceeds available stock ({product.stock})."
            })

        return data     

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']
    
    

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'is_paid', 'created_at']
        read_only_fields = ['user', 'total_price', 'created_at']
        
    def validate(self, data):
        user = self.context['request'].user
        cart_items = CartItem.objects.filter(cart__user=user)

        for item in cart_items:
            if item.quantity > item.product.stock:
                raise serializers.ValidationError({
                    "product": f"Product '{item.product.name}' has insufficient stock. Available: {item.product.stock}, Requested: {item.quantity}."
                })

        return data    
    
    def create(self, validated_data):
        user = self.context['request'].user
        print(f"updating product for user: {user}")
        cart_items = CartItem.objects.filter(cart__user=user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(user=user, total_price=total_price, is_paid=False)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Reduce the stock of the product
            item.product.stock -= item.quantity
            item.product.save()

        # Clear the cart after creating the order
        cart_items.delete()

        return order
    
  