from rest_framework import serializers

class OrderItemSerializer(serializers.Serializer):
    item_id = serializers.CharField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(min_value=1)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False)
    is_veg = serializers.BooleanField(default=True)

class CreateOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField(max_length=500)
    phone = serializers.CharField(max_length=15)
    payment_method = serializers.ChoiceField(choices=['cod', 'online'], default='cod')
    special_instructions = serializers.CharField(required=False, allow_blank=True)

class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    order_number = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    customer_name = serializers.CharField(read_only=True)
    customer_email = serializers.CharField(read_only=True)
    customer_phone = serializers.CharField(read_only=True)
    delivery_address = serializers.CharField()
    items = OrderItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    delivery_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payment_method = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    estimated_delivery_time = serializers.DateTimeField(read_only=True)

class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=['pending', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'delivered', 'cancelled']
    )
