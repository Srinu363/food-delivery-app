from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from mongo_client import get_collection
from bson import ObjectId
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create a new order from user's cart"""
    try:
        user = request.user
        data = request.data

        # Validate required fields
        required_fields = ['delivery_address', 'phone']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Get user's cart
        cart_collection = get_collection('carts')
        cart = cart_collection.find_one({'user_id': user.id})

        if not cart or not cart.get('items'):
            return Response({
                'success': False,
                'message': 'Cart is empty'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in cart['items'])
        delivery_fee = 0 if subtotal >= 500 else 50
        total_amount = subtotal + delivery_fee

        # Generate order number
        order_number = f"SF{random.randint(100000, 999999)}"

        # Get user profile for additional info
        user_profiles = get_collection('user_profiles')
        profile = user_profiles.find_one({'user_id': user.id})

        # Create order
        order_data = {
            'order_number': order_number,
            'user_id': user.id,
            'customer_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'customer_email': user.email,
            'customer_phone': data['phone'],
            'delivery_address': data['delivery_address'],
            'items': cart['items'],
            'subtotal': round(subtotal, 2),
            'delivery_fee': delivery_fee,
            'total_amount': round(total_amount, 2),
            'payment_method': data.get('payment_method', 'cod'),
            'payment_status': 'pending',
            'status': 'pending',
            'special_instructions': data.get('special_instructions', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'estimated_delivery_time': datetime.now() + timedelta(minutes=45)
        }

        # Save order
        orders_collection = get_collection('orders')
        result = orders_collection.insert_one(order_data)

        # Clear user's cart
        cart_collection.delete_one({'user_id': user.id})

        # Return order details
        order_data['id'] = str(result.inserted_id)

        return Response({
            'success': True,
            'message': 'Order placed successfully',
            'order': {
                'id': order_data['id'],
                'order_number': order_data['order_number'],
                'total_amount': order_data['total_amount'],
                'status': order_data['status'],
                'estimated_delivery_time': order_data['estimated_delivery_time'].isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return Response({
            'success': False,
            'message': 'Error placing order'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders(request):
    """Get current user's orders"""
    try:
        user_id = request.user.id
        orders_collection = get_collection('orders')

        orders = list(orders_collection.find({'user_id': user_id}).sort('created_at', -1))

        # Convert ObjectId to string and format dates
        for order in orders:
            order['id'] = str(order['_id'])
            del order['_id']
            if 'created_at' in order:
                order['created_at'] = order['created_at'].isoformat()
            if 'estimated_delivery_time' in order:
                order['estimated_delivery_time'] = order['estimated_delivery_time'].isoformat()

        return Response({
            'success': True,
            'orders': orders
        })
    except Exception as e:
        logger.error(f"Error getting user orders: {e}")
        return Response({
            'success': False,
            'message': 'Error fetching orders'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_detail(request, order_id):
    """Get detailed information about a specific order"""
    try:
        user_id = request.user.id
        orders_collection = get_collection('orders')

        # Find order and check ownership
        query = {'_id': ObjectId(order_id)}
        if not request.user.is_staff:
            query['user_id'] = user_id

        order = orders_collection.find_one(query)

        if not order:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Format response
        order['id'] = str(order['_id'])
        del order['_id']
        if 'created_at' in order:
            order['created_at'] = order['created_at'].isoformat()
        if 'estimated_delivery_time' in order:
            order['estimated_delivery_time'] = order['estimated_delivery_time'].isoformat()

        return Response({
            'success': True,
            'order': order
        })
    except Exception as e:
        logger.error(f"Error getting order detail: {e}")
        return Response({
            'success': False,
            'message': 'Error fetching order details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_orders(request):
    """Get all orders for admin dashboard"""
    try:
        orders_collection = get_collection('orders')

        # Get query parameters
        status_filter = request.GET.get('status')
        limit = int(request.GET.get('limit', 50))

        # Build query
        query = {}
        if status_filter:
            query['status'] = status_filter

        orders = list(orders_collection.find(query).sort('created_at', -1).limit(limit))

        # Format orders
        for order in orders:
            order['id'] = str(order['_id'])
            del order['_id']
            if 'created_at' in order:
                order['created_at'] = order['created_at'].isoformat()
            if 'estimated_delivery_time' in order:
                order['estimated_delivery_time'] = order['estimated_delivery_time'].isoformat()

        return Response({
            'success': True,
            'orders': orders,
            'count': len(orders)
        })
    except Exception as e:
        logger.error(f"Error getting all orders: {e}")
        return Response({
            'success': False,
            'message': 'Error fetching orders'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_order_status(request, order_id):
    """Update order status (admin only)"""
    try:
        data = request.data
        new_status = data.get('status')

        if not new_status:
            return Response({
                'success': False,
                'message': 'Status is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'message': 'Invalid status'
            }, status=status.HTTP_400_BAD_REQUEST)

        orders_collection = get_collection('orders')

        # Update order
        result = orders_collection.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': new_status,
                    'updated_at': datetime.now()
                }
            }
        )

        if result.matched_count == 0:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'message': f'Order status updated to {new_status}'
        })
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        return Response({
            'success': False,
            'message': 'Error updating order status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_dashboard_stats(request):
    """Get dashboard statistics for admin"""
    try:
        orders_collection = get_collection('orders')

        # Get today's date range
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Get statistics
        total_orders = orders_collection.count_documents({})
        today_orders = orders_collection.count_documents({
            'created_at': {'$gte': today_start, '$lt': today_end}
        })

        pending_orders = orders_collection.count_documents({'status': 'pending'})
        preparing_orders = orders_collection.count_documents({'status': {'$in': ['confirmed', 'preparing']}})

        # Calculate today's revenue
        today_revenue_pipeline = [
            {'$match': {
                'created_at': {'$gte': today_start, '$lt': today_end},
                'status': {'$ne': 'cancelled'}
            }},
            {'$group': {
                '_id': None,
                'total': {'$sum': '$total_amount'}
            }}
        ]

        today_revenue_result = list(orders_collection.aggregate(today_revenue_pipeline))
        today_revenue = today_revenue_result[0]['total'] if today_revenue_result else 0

        # Get recent orders
        recent_orders = list(orders_collection.find({}).sort('created_at', -1).limit(5))
        for order in recent_orders:
            order['id'] = str(order['_id'])
            del order['_id']
            if 'created_at' in order:
                order['created_at'] = order['created_at'].isoformat()

        return Response({
            'success': True,
            'stats': {
                'total_orders': total_orders,
                'today_orders': today_orders,
                'pending_orders': pending_orders,
                'preparing_orders': preparing_orders,
                'today_revenue': round(today_revenue, 2),
                'recent_orders': recent_orders
            }
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return Response({
            'success': False,
            'message': 'Error fetching dashboard statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
