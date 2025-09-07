from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from mongo_client import get_collection
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    """Get all active categories"""
    try:
        categories_collection = get_collection('categories')
        categories = list(categories_collection.find({'is_active': True}).sort('sort_order', 1))

        # Convert ObjectId to string
        for category in categories:
            category['id'] = str(category['_id'])
            del category['_id']

        return Response({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return Response({
            'success': False,
            'message': 'Error fetching categories'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_menu_items(request):
    """Get menu items with optional filtering"""
    try:
        items_collection = get_collection('menu_items')

        # Get query parameters
        category = request.GET.get('category')
        search = request.GET.get('search')
        is_veg = request.GET.get('is_veg')

        # Build query
        query = {'is_available': True}

        if category:
            query['category'] = category

        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]

        if is_veg is not None:
            query['is_veg'] = is_veg.lower() == 'true'

        items = list(items_collection.find(query).sort('name', 1))

        # Convert ObjectId to string
        for item in items:
            item['id'] = str(item['_id'])
            del item['_id']

        return Response({
            'success': True,
            'items': items,
            'count': len(items)
        })
    except Exception as e:
        logger.error(f"Error getting menu items: {e}")
        return Response({
            'success': False,
            'message': 'Error fetching menu items'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_menu_item(request, item_id):
    """Get single menu item by ID"""
    try:
        items_collection = get_collection('menu_items')
        item = items_collection.find_one({'_id': ObjectId(item_id)})

        if item:
            item['id'] = str(item['_id'])
            del item['_id']
            return Response({
                'success': True,
                'item': item
            })
        else:
            return Response({
                'success': False,
                'message': 'Item not found'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting menu item: {e}")
        return Response({
            'success': False,
            'message': 'Invalid item ID or server error'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add item to user's cart"""
    try:
        user_id = request.user.id
        data = request.data

        # Validate required fields
        if not data.get('item_id') or not data.get('quantity'):
            return Response({
                'success': False,
                'message': 'Item ID and quantity are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_collection = get_collection('carts')
        items_collection = get_collection('menu_items')

        # Get item details
        try:
            item = items_collection.find_one({'_id': ObjectId(data['item_id'])})
            if not item or not item.get('is_available'):
                return Response({
                    'success': False,
                    'message': 'Item not found or not available'
                }, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({
                'success': False,
                'message': 'Invalid item ID'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create cart item
        cart_item = {
            'item_id': data['item_id'],
            'name': item['name'],
            'price': float(item['price']),
            'quantity': int(data['quantity']),
            'special_instructions': data.get('special_instructions', ''),
            'image_url': item.get('image_url', ''),
            'is_veg': item.get('is_veg', True),
            'added_at': datetime.now()
        }

        # Check if user has existing cart
        cart = cart_collection.find_one({'user_id': user_id})

        if cart:
            # Check if item already exists in cart
            existing_item_index = -1
            for i, cart_item_existing in enumerate(cart.get('items', [])):
                if cart_item_existing['item_id'] == data['item_id']:
                    existing_item_index = i
                    break

            if existing_item_index >= 0:
                # Update quantity
                cart['items'][existing_item_index]['quantity'] += int(data['quantity'])
                cart['items'][existing_item_index]['special_instructions'] = data.get('special_instructions', '')
            else:
                # Add new item
                cart['items'].append(cart_item)

            cart['updated_at'] = datetime.now()
            cart_collection.replace_one({'user_id': user_id}, cart)
        else:
            # Create new cart
            new_cart = {
                'user_id': user_id,
                'items': [cart_item],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            cart_collection.insert_one(new_cart)

        return Response({
            'success': True,
            'message': 'Item added to cart successfully'
        })
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return Response({
            'success': False,
            'message': 'Error adding item to cart'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """Get user's cart"""
    try:
        user_id = request.user.id
        cart_collection = get_collection('carts')

        cart = cart_collection.find_one({'user_id': user_id})

        if cart:
            # Calculate totals
            total_amount = 0
            total_items = 0

            for item in cart.get('items', []):
                total_amount += item['price'] * item['quantity']
                total_items += item['quantity']

            # Calculate delivery fee (free above 500)
            delivery_fee = 0 if total_amount >= 500 else 50

            return Response({
                'success': True,
                'cart': {
                    'items': cart.get('items', []),
                    'total_items': total_items,
                    'subtotal': round(total_amount, 2),
                    'delivery_fee': delivery_fee,
                    'total_amount': round(total_amount + delivery_fee, 2),
                    'free_delivery_threshold': 500
                }
            })
        else:
            return Response({
                'success': True,
                'cart': {
                    'items': [],
                    'total_items': 0,
                    'subtotal': 0,
                    'delivery_fee': 0,
                    'total_amount': 0,
                    'free_delivery_threshold': 500
                }
            })
    except Exception as e:
        logger.error(f"Error getting cart: {e}")
        return Response({
            'success': False,
            'message': 'Error fetching cart'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        user_id = request.user.id
        cart_collection = get_collection('carts')

        cart = cart_collection.find_one({'user_id': user_id})

        if cart:
            cart['items'] = [item for item in cart.get('items', []) if item['item_id'] != item_id]
            cart['updated_at'] = datetime.now()
            cart_collection.replace_one({'user_id': user_id}, cart)

            return Response({
                'success': True,
                'message': 'Item removed from cart'
            })

        return Response({
            'success': False,
            'message': 'Cart not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        return Response({
            'success': False,
            'message': 'Error removing item from cart'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """Update cart item quantity and instructions"""
    try:
        user_id = request.user.id
        data = request.data
        cart_collection = get_collection('carts')

        cart = cart_collection.find_one({'user_id': user_id})

        if cart:
            for item in cart.get('items', []):
                if item['item_id'] == item_id:
                    item['quantity'] = int(data.get('quantity', item['quantity']))
                    item['special_instructions'] = data.get('special_instructions', item.get('special_instructions', ''))
                    break

            cart['updated_at'] = datetime.now()
            cart_collection.replace_one({'user_id': user_id}, cart)

            return Response({
                'success': True,
                'message': 'Cart item updated'
            })

        return Response({
            'success': False,
            'message': 'Cart not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating cart item: {e}")
        return Response({
            'success': False,
            'message': 'Error updating cart item'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear user's cart"""
    try:
        user_id = request.user.id
        cart_collection = get_collection('carts')

        cart_collection.delete_one({'user_id': user_id})

        return Response({
            'success': True,
            'message': 'Cart cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        return Response({
            'success': False,
            'message': 'Error clearing cart'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
