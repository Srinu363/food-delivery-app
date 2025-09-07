# Srinu Foods - Complete Restaurant Ordering System

A full-stack web application for restaurant ordering similar to Domino's online system.

## Features
- User registration and authentication
- Menu browsing with categories
- Shopping cart functionality
- Order placement and tracking
- Admin dashboard for order management
- Responsive design for mobile and desktop

## Tech Stack
- **Backend**: Django with REST Framework
- **Database**: MongoDB for restaurant data, SQLite for authentication
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Authentication**: JWT tokens

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB installed and running
- pip package manager

### Installation
1. Install MongoDB and start the service
   ```bash
   mongod
   ```

2. Install Python dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run Django migrations
   ```bash
   python manage.py migrate
   ```

4. Setup initial data
   ```bash
   python setup_data.py
   ```

5. Start the development server
   ```bash
   python manage.py runserver
   ```

6. Open your browser and visit `http://localhost:8000`

## Default Credentials
- **Admin**: admin / admin123
- **Customer**: customer / customer123

## API Endpoints
- `/api/auth/` - Authentication endpoints
- `/api/menu/` - Menu and cart management
- `/api/orders/` - Order management
- `/admin/` - Django admin panel

## Project Structure
- `accounts/` - User authentication app
- `menu/` - Menu items and cart management
- `orders/` - Order processing and tracking
- `static/` - CSS, JavaScript, and images
- `templates/` - HTML templates

Enjoy ordering from Srinu Foods! 🍕
