# 🍕 Srinu Foods - Complete Restaurant Ordering System

A full-stack web application for restaurant ordering similar to Domino's online system, built with Django backend, MongoDB database, and modern frontend.

## ✨ Features

### 🔐 User Authentication
- User registration and login with JWT tokens
- Password encryption and validation
- User profile management with MongoDB storage
- Role-based access (Customer/Admin)

### 🍽️ Menu Management
- Dynamic menu with categories
- Search and filter functionality (category, vegetarian)
- Real-time availability status
- Detailed item information (price, rating, prep time, ingredients)

### 🛒 Shopping Cart
- Add items to cart with quantity selection
- Update quantities and remove items
- Special instructions for items
- Cart persistence across sessions

### 📦 Order Management
- Order placement with delivery details
- Order tracking with multiple statuses
- Order history for customers
- Real-time order updates

### 👨‍🍳 Admin Dashboard
- Live dashboard with statistics
- Order management interface
- Status updates for orders
- Customer information view

### 📱 Responsive Design
- Mobile-first responsive design
- Modern UI/UX similar to popular food delivery apps
- Toast notifications and loading states
- Modal-based interactions

## 🛠️ Tech Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API development
- **MongoDB** - Database for restaurant data
- **SQLite** - Database for Django authentication
- **PyMongo** - MongoDB driver
- **JWT** - Authentication tokens

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with custom properties
- **Vanilla JavaScript** - Interactive functionality
- **Font Awesome** - Icons
- **Responsive Design** - Mobile-friendly

## 🚀 Installation & Setup
![Home Page](https://github.com/Srinu363/food-delivery-app/blob/main/food_delivery/images/Screenshot%202025-09-07%20094523.png)
![Our Menu](https://github.com/Srinu363/food-delivery-app/blob/main/food_delivery/images/Screenshot%202025-09-07%20094617.png)
![List Of Items](https://github.com/Srinu363/food-delivery-app/blob/main/food_delivery/images/Screenshot%202025-09-07%20094642.png)
![Login].(https://github.com/Srinu363/food-delivery-app/blob/main/food_delivery/images/Screenshot%202025-09-07%20094716.png)


### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running
- pip package manager

### Step-by-Step Setup

1. **Start MongoDB**
   ```bash
   # Start MongoDB service
   mongod

   # On macOS with Homebrew
   brew services start mongodb-community

   # On Ubuntu
   sudo systemctl start mongod
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Django Setup**
   ```bash
   # Run Django migrations for authentication
   python manage.py migrate

   # Create Django superuser (optional)
   python manage.py createsuperuser
   ```

4. **Setup MongoDB Data**
   ```bash
   python setup_data.py
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**
   - Main Website: http://localhost:8000
   - Admin Dashboard: http://localhost:8000/dashboard
   - Django Admin: http://localhost:8000/admin

## 🔑 Default Credentials

### Admin Access
- **Username:** admin
- **Password:** admin123
- **Access:** Full admin dashboard and Django admin

### Customer Accounts
- **Username:** customer | **Password:** customer123
- **Username:** john_doe | **Password:** customer123  
- **Username:** jane_smith | **Password:** customer123

## 📊 Database Structure

### Django (SQLite)
- User authentication and sessions
- Admin interface

### MongoDB Collections
- **categories** - Food categories with images
- **menu_items** - Menu items with full details
- **orders** - Customer orders with items and status
- **user_profiles** - Extended user information
- **carts** - Shopping carts for users

## 🌟 Key Features Explained

### Authentication Flow
1. User registers/logs in through frontend forms
2. JWT tokens issued for authenticated requests
3. User profile stored in MongoDB with additional fields
4. Role-based access control for admin features

### Ordering Process
1. Browse menu items by category or search
2. Add items to cart with quantities and special instructions
3. Review cart and proceed to checkout
4. Fill delivery details and place order
5. Order stored in MongoDB with unique order number
6. Admin can track and update order status

### Admin Dashboard
1. Real-time statistics (today's orders, revenue, pending orders)
2. Order management with status updates
3. Detailed order view with customer information
4. Quick actions for common status changes

## 🎨 Design Features

### Modern UI/UX
- Clean, modern design inspired by popular food delivery apps
- Consistent color scheme and typography
- Smooth animations and transitions
- Loading states and user feedback

### Responsive Design
- Mobile-first approach
- Flexible grid layouts
- Touch-friendly interface
- Optimized for all screen sizes

## 🔧 Configuration

### MongoDB Settings
```python
MONGODB_SETTINGS = {
    'HOST': 'mongodb://localhost:27017',
    'DB_NAME': 'srinu_foods_db'
}
```

### JWT Configuration
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

## 📝 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/update-profile/` - Update profile

### Menu
- `GET /api/menu/categories/` - Get all categories
- `GET /api/menu/items/` - Get menu items (with filters)
- `GET /api/menu/items/<id>/` - Get single item

### Cart
- `GET /api/menu/cart/` - Get user cart
- `POST /api/menu/cart/add/` - Add item to cart
- `PUT /api/menu/cart/update/<id>/` - Update cart item
- `DELETE /api/menu/cart/remove/<id>/` - Remove from cart

### Orders
- `POST /api/orders/create/` - Create new order
- `GET /api/orders/my-orders/` - Get user orders
- `GET /api/orders/<id>/` - Get order details

### Admin
- `GET /api/orders/admin/all/` - Get all orders
- `PUT /api/orders/admin/<id>/update-status/` - Update order status
- `GET /api/orders/admin/dashboard/stats/` - Dashboard statistics

## 🧪 Testing

### Manual Testing
1. Register new user account
2. Browse menu and add items to cart
3. Place an order with delivery details
4. Login as admin and manage orders
5. Test responsive design on different devices

### Sample Data
The setup script creates:
- 7 food categories
- 20+ menu items across all categories
- 3 customer accounts
- 8 sample orders with different statuses

## 🚀 Production Deployment

### Environment Variables
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
MONGODB_URI=mongodb://localhost:27017/srinu_foods_db
```

### Security Considerations
- Change default passwords
- Use environment variables for secrets
- Enable HTTPS in production
- Configure CORS properly
- Set up proper error handling

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**MongoDB Connection Error:**
```bash
# Check if MongoDB is running
ps aux | grep mongod

# Start MongoDB
mongod
```

**Port Already in Use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python manage.py runserver 8001
```

**Package Installation Issues:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Support

If you encounter any issues:
1. Check MongoDB is running
2. Verify all dependencies are installed
3. Run setup_data.py to populate database
4. Check Django migrations are applied

---

**Built with ❤️ for food lovers and Django developers!**

*Ready to serve delicious food online! 🍕*
