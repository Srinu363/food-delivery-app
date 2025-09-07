#!/usr/bin/env python
"""
Srinu Foods - MongoDB Data Setup Script
This script populates the MongoDB database with initial data
"""

import os
import sys
import django
from datetime import datetime
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srinu_foods.settings')
django.setup()

from django.contrib.auth.models import User
from mongo_client import get_collection

def create_admin_user():
    """Create admin user for the system"""
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@srinufoods.com',
            'first_name': 'Srinu',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True
        }
    )

    if created or not admin_user.check_password('admin123'):
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.username}")
    else:
        print(f"✅ Admin user already exists: {admin_user.username}")

    # Create user profile in MongoDB
    user_profiles = get_collection('user_profiles')
    if not user_profiles.find_one({'user_id': admin_user.id}):
        user_profiles.insert_one({
            'user_id': admin_user.id,
            'phone': '+91-9876543210',
            'address': '123 Admin Street, Food City, FC 12345',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
        print("✅ Created admin profile in MongoDB")

def create_customer_users():
    """Create sample customer users"""
    customers = [
        {
            'username': 'customer',
            'email': 'customer@example.com',
            'first_name': 'Regular',
            'last_name': 'Customer',
            'phone': '+91-9876543211',
            'address': '456 Customer Lane, Food City, FC 12346'
        },
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+91-9876543212',
            'address': '789 Doe Street, Food City, FC 12347'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '+91-9876543213',
            'address': '321 Smith Avenue, Food City, FC 12348'
        }
    ]

    user_profiles = get_collection('user_profiles')

    for customer_data in customers:
        phone = customer_data.pop('phone')
        address = customer_data.pop('address')

        customer, created = User.objects.get_or_create(
            username=customer_data['username'],
            defaults=customer_data
        )

        if created or not customer.check_password('customer123'):
            customer.set_password('customer123')
            customer.save()
            print(f"✅ Created customer user: {customer.username}")

        # Create profile in MongoDB
        if not user_profiles.find_one({'user_id': customer.id}):
            user_profiles.insert_one({
                'user_id': customer.id,
                'phone': phone,
                'address': address,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })

def create_categories():
    """Create food categories"""
    categories_data = [
        {
            'name': 'Appetizers',
            'description': 'Start your meal with our delicious appetizers',
            'image_url': 'https://images.unsplash.com/photo-1551782450-17144efb9c50?w=400&h=300&fit=crop',
            'is_active': True,
            'sort_order': 1
        },
        {
            'name': 'Main Course',
            'description': 'Hearty and satisfying main dishes',
            'image_url': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
            'is_active': True,
            'sort_order': 2
        },
        {
            'name': 'Biryanis',
            'description': 'Aromatic and flavorful rice dishes',
            'image_url': 'https://images.unsplash.com/photo-1563379091774-c86b4d57fb16?w=400&h=300&fit=crop',
            'is_active': True,
            'sort_order': 3
        },
        {
            'name': 'South Indian',
            'description': 'Traditional South Indian delicacies',
            'image_url': 'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400&h=300&fit=crop',
            'is_active': True,
            'sort_order': 4
        },
        {
            'name': 'Chinese',
            'description': 'Indo-Chinese fusion dishes',
            'image_url': 'https://images.unsplash.com/photo-1526318896980-cf86fd85717d?w=400&h=300&fit=crop',
            'is_active': True,
            'sort_order': 5
        },
        {
            'name': 'Beverages',
            'description': 'Refreshing drinks and beverages',
            'image_url': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop',
            'is_active': True,
            'sort_order': 6
        },
        {
            'name': 'Desserts',
            'description': 'Sweet treats to end your meal',
            'image_url': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop',
            'is_active': True,
            'sort_order': 7
        }
    ]

    categories = get_collection('categories')
    categories.delete_many({})  # Clear existing categories

    for category in categories_data:
        category['created_at'] = datetime.now()
        category['updated_at'] = datetime.now()

    result = categories.insert_many(categories_data)
    print(f"✅ Created {len(result.inserted_ids)} categories")

def create_menu_items():
    """Create menu items"""
    menu_items_data = [
        # Appetizers
        {
            'name': 'Paneer Tikka',
            'description': 'Marinated cottage cheese grilled to perfection with bell peppers and onions',
            'price': 180.00,
            'image_url': 'https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&h=300&fit=crop',
            'category': 'Appetizers',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 15,
            'rating': 4.8,
            'ingredients': 'Paneer, Bell Peppers, Onions, Yogurt, Spices'
        },
        {
            'name': 'Chicken Tikka',
            'description': 'Tender chicken pieces marinated in yogurt and spices, grilled in tandoor',
            'price': 220.00,
            'image_url': 'https://images.unsplash.com/photo-1610057099431-d73a1c9d2f2f?w=400&h=300&fit=crop',
            'category': 'Appetizers',
            'is_available': True,
            'is_veg': False,
            'preparation_time': 20,
            'rating': 4.9,
            'ingredients': 'Chicken, Yogurt, Ginger-Garlic, Spices'
        },
        {
            'name': 'Vegetable Samosa',
            'description': 'Crispy pastry filled with spiced potatoes and vegetables',
            'price': 80.00,
            'image_url': 'https://images.unsplash.com/photo-1601050690117-94f5f6fa7e15?w=400&h=300&fit=crop',
            'category': 'Appetizers',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 10,
            'rating': 4.5,
            'ingredients': 'Potatoes, Peas, Pastry, Spices'
        },

        # Main Course
        {
            'name': 'Butter Chicken',
            'description': 'Creamy tomato-based chicken curry with aromatic spices',
            'price': 320.00,
            'image_url': 'https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=400&h=300&fit=crop',
            'category': 'Main Course',
            'is_available': True,
            'is_veg': False,
            'preparation_time': 25,
            'rating': 4.9,
            'ingredients': 'Chicken, Tomatoes, Cream, Butter, Spices'
        },
        {
            'name': 'Paneer Butter Masala',
            'description': 'Rich cottage cheese curry in creamy tomato gravy',
            'price': 280.00,
            'image_url': 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&h=300&fit=crop',
            'category': 'Main Course',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 20,
            'rating': 4.7,
            'ingredients': 'Paneer, Tomatoes, Cream, Cashews, Spices'
        },
        {
            'name': 'Dal Tadka',
            'description': 'Yellow lentils tempered with cumin, garlic and spices',
            'price': 150.00,
            'image_url': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop',
            'category': 'Main Course',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 15,
            'rating': 4.6,
            'ingredients': 'Yellow Dal, Cumin, Garlic, Ginger, Spices'
        },

        # Biryanis
        {
            'name': 'Chicken Biryani',
            'description': 'Aromatic basmati rice with tender chicken and traditional spices',
            'price': 350.00,
            'image_url': 'https://images.unsplash.com/photo-1563379091774-c86b4d57fb16?w=400&h=300&fit=crop',
            'category': 'Biryanis',
            'is_available': True,
            'is_veg': False,
            'preparation_time': 45,
            'rating': 4.9,
            'ingredients': 'Basmati Rice, Chicken, Yogurt, Fried Onions, Saffron, Spices'
        },
        {
            'name': 'Mutton Biryani',
            'description': 'Rich and flavorful biryani with tender mutton pieces',
            'price': 420.00,
            'image_url': 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400&h=300&fit=crop',
            'category': 'Biryanis',
            'is_available': True,
            'is_veg': False,
            'preparation_time': 60,
            'rating': 4.8,
            'ingredients': 'Basmati Rice, Mutton, Yogurt, Fried Onions, Saffron, Spices'
        },
        {
            'name': 'Vegetable Biryani',
            'description': 'Fragrant basmati rice with mixed vegetables and aromatic spices',
            'price': 250.00,
            'image_url': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=400&h=300&fit=crop',
            'category': 'Biryanis',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 35,
            'rating': 4.5,
            'ingredients': 'Basmati Rice, Mixed Vegetables, Fried Onions, Saffron, Spices'
        },

        # South Indian
        {
            'name': 'Masala Dosa',
            'description': 'Crispy rice and lentil crepe filled with spiced potato filling',
            'price': 120.00,
            'image_url': 'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400&h=300&fit=crop',
            'category': 'South Indian',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 20,
            'rating': 4.8,
            'ingredients': 'Rice, Lentils, Potatoes, Onions, Spices'
        },
        {
            'name': 'Idli Sambar',
            'description': 'Steamed rice cakes served with lentil curry and coconut chutney',
            'price': 90.00,
            'image_url': 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400&h=300&fit=crop',
            'category': 'South Indian',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 15,
            'rating': 4.6,
            'ingredients': 'Rice, Lentils, Coconut, Spices'
        },
        {
            'name': 'Uttapam',
            'description': 'Thick pancake topped with vegetables and served with chutneys',
            'price': 110.00,
            'image_url': 'https://images.unsplash.com/photo-1630383249896-424e482df921?w=400&h=300&fit=crop',
            'category': 'South Indian',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 18,
            'rating': 4.4,
            'ingredients': 'Rice, Lentils, Vegetables, Spices'
        },

        # Chinese
        {
            'name': 'Chicken Fried Rice',
            'description': 'Wok-fried rice with tender chicken pieces and fresh vegetables',
            'price': 200.00,
            'image_url': 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop',
            'category': 'Chinese',
            'is_available': True,
            'is_veg': False,
            'preparation_time': 18,
            'rating': 4.4,
            'ingredients': 'Rice, Chicken, Vegetables, Soy Sauce, Spices'
        },
        {
            'name': 'Veg Hakka Noodles',
            'description': 'Stir-fried noodles with fresh vegetables and Indo-Chinese sauces',
            'price': 180.00,
            'image_url': 'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400&h=300&fit=crop',
            'category': 'Chinese',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 15,
            'rating': 4.3,
            'ingredients': 'Noodles, Vegetables, Soy Sauce, Garlic, Spices'
        },
        {
            'name': 'Chilli Chicken',
            'description': 'Spicy Indo-Chinese chicken with bell peppers and onions',
            'price': 240.00,
            'image_url': 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400&h=300&fit=crop',
            'category': 'Chinese',
            'is_available': True,
            'is_veg': False,
            'preparation_time': 22,
            'rating': 4.6,
            'ingredients': 'Chicken, Bell Peppers, Onions, Soy Sauce, Chilli Sauce'
        },

        # Beverages
        {
            'name': 'Mango Lassi',
            'description': 'Refreshing yogurt-based mango drink',
            'price': 80.00,
            'image_url': 'https://images.unsplash.com/photo-1571091655789-405eb7a3a3a8?w=400&h=300&fit=crop',
            'category': 'Beverages',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 5,
            'rating': 4.5,
            'ingredients': 'Mango, Yogurt, Sugar, Cardamom'
        },
        {
            'name': 'Fresh Lime Water',
            'description': 'Refreshing lime water with fresh mint leaves',
            'price': 50.00,
            'image_url': 'https://images.unsplash.com/photo-1583064313642-a7c149480c7e?w=400&h=300&fit=crop',
            'category': 'Beverages',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 3,
            'rating': 4.2,
            'ingredients': 'Lime, Water, Sugar, Mint, Salt'
        },
        {
            'name': 'Masala Chai',
            'description': 'Traditional Indian spiced tea',
            'price': 30.00,
            'image_url': 'https://images.unsplash.com/photo-1597318181864-67930d969e1d?w=400&h=300&fit=crop',
            'category': 'Beverages',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 5,
            'rating': 4.7,
            'ingredients': 'Tea, Milk, Spices, Sugar'
        },

        # Desserts
        {
            'name': 'Gulab Jamun',
            'description': 'Soft milk dumplings in rose-flavored sugar syrup',
            'price': 90.00,
            'image_url': 'https://images.unsplash.com/photo-1571219349904-d80d6ec84ea9?w=400&h=300&fit=crop',
            'category': 'Desserts',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 8,
            'rating': 4.8,
            'ingredients': 'Milk Powder, Flour, Sugar, Rose Water'
        },
        {
            'name': 'Ras Malai',
            'description': 'Soft cheese dumplings in sweetened, thickened milk',
            'price': 110.00,
            'image_url': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=300&fit=crop',
            'category': 'Desserts',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 10,
            'rating': 4.6,
            'ingredients': 'Cottage Cheese, Milk, Sugar, Cardamom, Pistachios'
        },
        {
            'name': 'Ice Cream',
            'description': 'Assorted flavors of creamy ice cream',
            'price': 70.00,
            'image_url': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop',
            'category': 'Desserts',
            'is_available': True,
            'is_veg': True,
            'preparation_time': 2,
            'rating': 4.3,
            'ingredients': 'Milk, Cream, Sugar, Various Flavors'
        }
    ]

    menu_items = get_collection('menu_items')
    menu_items.delete_many({})  # Clear existing items

    for item in menu_items_data:
        item['created_at'] = datetime.now()
        item['updated_at'] = datetime.now()

    result = menu_items.insert_many(menu_items_data)
    print(f"✅ Created {len(result.inserted_ids)} menu items")

def create_sample_orders():
    """Create sample orders for demonstration"""
    users = User.objects.all()
    if not users:
        print("⚠️ No users found, skipping sample orders")
        return

    menu_items = get_collection('menu_items')
    all_items = list(menu_items.find())

    if not all_items:
        print("⚠️ No menu items found, skipping sample orders")
        return

    orders_data = []
    statuses = ['pending', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'delivered']

    for i in range(8):
        user = random.choice(users)
        selected_items = random.sample(all_items, random.randint(1, 4))

        order_items = []
        subtotal = 0

        for item in selected_items:
            quantity = random.randint(1, 3)
            item_subtotal = float(item['price']) * quantity
            subtotal += item_subtotal

            order_items.append({
                'item_id': str(item['_id']),
                'name': item['name'],
                'price': float(item['price']),
                'quantity': quantity,
                'special_instructions': random.choice(['', 'Less spicy', 'Extra sauce', 'No onions']),
                'image_url': item.get('image_url', ''),
                'is_veg': item.get('is_veg', True)
            })

        delivery_fee = 0 if subtotal >= 500 else 50
        total_amount = subtotal + delivery_fee

        order = {
            'order_number': f'SF{random.randint(100000, 999999)}',
            'user_id': user.id,
            'customer_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'customer_email': user.email,
            'customer_phone': f'+91-{random.randint(7000000000, 9999999999)}',
            'delivery_address': f'{random.randint(1, 999)} {random.choice(["MG Road", "Brigade Road", "Commercial Street", "Koramangala", "Indiranagar"])}, Bangalore, Karnataka - {random.randint(560001, 560100)}',
            'items': order_items,
            'subtotal': round(subtotal, 2),
            'delivery_fee': delivery_fee,
            'total_amount': round(total_amount, 2),
            'payment_method': random.choice(['cod', 'online']),
            'payment_status': random.choice(['pending', 'completed']),
            'status': random.choice(statuses),
            'special_instructions': random.choice(['', 'Ring the doorbell', 'Leave at gate', 'Call before delivery']),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'estimated_delivery_time': datetime.now()
        }

        orders_data.append(order)

    orders = get_collection('orders')
    orders.delete_many({})  # Clear existing orders

    result = orders.insert_many(orders_data)
    print(f"✅ Created {len(result.inserted_ids)} sample orders")

def main():
    """Main setup function"""
    print("🍕 Setting up Srinu Foods MongoDB Database")
    print("=" * 50)

    try:
        print("\n👥 Setting up users...")
        create_admin_user()
        create_customer_users()

        print("\n📋 Setting up food categories...")
        create_categories()

        print("\n🍽️ Setting up menu items...")
        create_menu_items()

        print("\n📦 Creating sample orders...")
        create_sample_orders()

        print("\n" + "=" * 50)
        print("🎉 Database setup completed successfully!")
        print("=" * 50)

        print("\n🔑 Login Credentials:")
        print("   👨‍🍳 Admin: admin / admin123")
        print("   👤 Customer: customer / customer123")
        print("   👤 John Doe: john_doe / customer123")
        print("   👤 Jane Smith: jane_smith / customer123")

        print("\n🌐 Access the application:")
        print("   🏠 Main Website: http://localhost:8000")
        print("   👨‍🍳 Admin Dashboard: http://localhost:8000/dashboard")
        print("   ⚙️  Django Admin: http://localhost:8000/admin")

        print("\n🗄️ MongoDB Collections Created:")

        # Show collection stats
        collections = ['categories', 'menu_items', 'orders', 'user_profiles']
        for collection_name in collections:
            collection = get_collection(collection_name)
            count = collection.count_documents({})
            print(f"   📄 {collection_name}: {count} documents")

        print("\n🚀 Your restaurant is ready to serve customers!")

    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
