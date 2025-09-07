from rest_framework import serializers

class CategorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    image_url = serializers.URLField()
    is_active = serializers.BooleanField(default=True)
    sort_order = serializers.IntegerField(default=0)

class MenuItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image_url = serializers.URLField()
    category = serializers.CharField(max_length=100)
    is_available = serializers.BooleanField(default=True)
    is_veg = serializers.BooleanField(default=True)
    preparation_time = serializers.IntegerField(default=20)  # in minutes
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    ingredients = serializers.CharField(required=False)

class CartItemSerializer(serializers.Serializer):
    item_id = serializers.CharField()
    name = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantity = serializers.IntegerField(min_value=1, max_value=10)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(read_only=True)
