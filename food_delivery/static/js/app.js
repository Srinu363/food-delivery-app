// Srinu Foods - Main Frontend Application

class SrinuFoodsApp {
    constructor() {
        this.currentUser = null;
        this.authToken = localStorage.getItem('authToken');
        this.categories = [];
        this.menuItems = [];
        this.cart = [];
        this.isLoading = false;

        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.checkAuthStatus();
        await this.loadCategories();
        await this.loadMenuItems();
        await this.updateCartDisplay();

        // Auto-refresh cart every 30 seconds if user is logged in
        if (this.authToken) {
            setInterval(() => this.loadCart(), 30000);
        }
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('loginBtn')?.addEventListener('click', () => this.showModal('loginModal'));
        document.getElementById('registerBtn')?.addEventListener('click', () => this.showModal('registerModal'));
        document.getElementById('cartBtn')?.addEventListener('click', () => this.showCartModal());

        // User dropdown
        document.getElementById('userDropdown')?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });

        document.addEventListener('click', () => this.closeDropdown());

        // User actions
        document.getElementById('myOrdersLink')?.addEventListener('click', () => this.showMyOrders());
        document.getElementById('logoutBtn')?.addEventListener('click', () => this.logout());

        // Forms
        document.getElementById('loginForm')?.addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('registerForm')?.addEventListener('submit', (e) => this.handleRegister(e));
        document.getElementById('orderForm')?.addEventListener('submit', (e) => this.handleOrder(e));

        // Search and filters
        document.getElementById('searchInput')?.addEventListener('input', (e) => this.handleSearch(e.target.value));
        document.getElementById('categoryFilter')?.addEventListener('change', (e) => this.filterByCategory(e.target.value));
        document.getElementById('vegFilter')?.addEventListener('change', (e) => this.filterVeg(e.target.checked));

        // Modal close buttons
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = btn.getAttribute('data-modal');
                this.hideModal(modalId);
            });
        });

        // Close modal on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }

    // Authentication Methods
    checkAuthStatus() {
        if (this.authToken) {
            this.loadUserProfile();
        }
    }

    async loadUserProfile() {
        try {
            const response = await this.apiCall('/api/auth/profile/', 'GET');
            if (response.success) {
                this.currentUser = response.user;
                this.updateAuthUI();
            } else {
                this.logout();
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            this.logout();
        }
    }

    updateAuthUI() {
        const authButtons = document.getElementById('authButtons');
        const userMenu = document.getElementById('userMenu');

        if (this.currentUser) {
            authButtons.style.display = 'none';
            userMenu.style.display = 'flex';
            document.getElementById('userName').textContent = 
                this.currentUser.first_name || this.currentUser.username;
        } else {
            authButtons.style.display = 'flex';
            userMenu.style.display = 'none';
        }
    }

    async handleLogin(e) {
        e.preventDefault();

        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        if (!username || !password) {
            this.showToast('Please fill in all fields', 'error');
            return;
        }

        try {
            this.showLoading();
            const response = await this.apiCall('/api/auth/login/', 'POST', {
                username,
                password
            });

            if (response.success) {
                this.authToken = response.tokens.access;
                localStorage.setItem('authToken', this.authToken);
                this.currentUser = response.user;
                this.updateAuthUI();
                this.hideModal('loginModal');
                this.showToast('Login successful!', 'success');

                // Load user cart
                await this.loadCart();
            } else {
                this.showToast(response.message || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showToast('Login failed. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async handleRegister(e) {
        e.preventDefault();

        const formData = {
            first_name: document.getElementById('registerFirstName').value,
            last_name: document.getElementById('registerLastName').value,
            username: document.getElementById('registerUsername').value,
            email: document.getElementById('registerEmail').value,
            phone: document.getElementById('registerPhone').value,
            address: document.getElementById('registerAddress').value,
            password: document.getElementById('registerPassword').value,
            confirm_password: document.getElementById('registerConfirmPassword').value
        };

        // Validation
        if (!formData.first_name || !formData.username || !formData.email || !formData.password) {
            this.showToast('Please fill in all required fields', 'error');
            return;
        }

        if (formData.password !== formData.confirm_password) {
            this.showToast('Passwords do not match', 'error');
            return;
        }

        if (formData.password.length < 6) {
            this.showToast('Password must be at least 6 characters', 'error');
            return;
        }

        try {
            this.showLoading();
            const response = await this.apiCall('/api/auth/register/', 'POST', formData);

            if (response.success) {
                this.authToken = response.tokens.access;
                localStorage.setItem('authToken', this.authToken);
                this.currentUser = response.user;
                this.updateAuthUI();
                this.hideModal('registerModal');
                this.showToast('Registration successful! Welcome to Srinu Foods!', 'success');
            } else {
                this.showToast(this.formatErrors(response.errors) || 'Registration failed', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showToast('Registration failed. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    logout() {
        this.authToken = null;
        this.currentUser = null;
        localStorage.removeItem('authToken');
        this.cart = [];
        this.updateAuthUI();
        this.updateCartDisplay();
        this.showToast('Logged out successfully', 'success');
    }

    // Menu Methods
    async loadCategories() {
        try {
            const response = await this.apiCall('/api/menu/categories/', 'GET');
            if (response.success) {
                this.categories = response.categories;
                this.renderCategories();
                this.populateCategoryFilter();
            }
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }

    async loadMenuItems(filters = {}) {
        try {
            let url = '/api/menu/items/';
            const params = new URLSearchParams();

            Object.keys(filters).forEach(key => {
                if (filters[key]) params.append(key, filters[key]);
            });

            if (params.toString()) {
                url += '?' + params.toString();
            }

            const response = await this.apiCall(url, 'GET');
            if (response.success) {
                this.menuItems = response.items;
                this.renderMenuItems();
            }
        } catch (error) {
            console.error('Error loading menu items:', error);
        }
    }

    renderCategories() {
        const container = document.getElementById('categoriesGrid');
        if (!container) return;

        container.innerHTML = this.categories.map(category => `
            <div class="category-card" onclick="app.filterByCategory('${category.name}')">
                <img src="${category.image_url}" alt="${category.name}" 
                     onerror="this.src='https://via.placeholder.com/80x80?text=${category.name}'">
                <h3>${category.name}</h3>
                <p>${category.description}</p>
            </div>
        `).join('');
    }

    renderMenuItems() {
        const container = document.getElementById('menuGrid');
        if (!container) return;

        if (this.menuItems.length === 0) {
            container.innerHTML = '<div class="no-items">No items found</div>';
            return;
        }

        container.innerHTML = this.menuItems.map(item => `
            <div class="menu-item">
                <img src="${item.image_url}" alt="${item.name}"
                     onerror="this.src='https://via.placeholder.com/300x200?text=${item.name}'">
                <div class="menu-item-content">
                    <div class="menu-item-header">
                        <h3>${item.name}</h3>
                        <div class="menu-item-price">₹${item.price}</div>
                    </div>
                    <p>${item.description}</p>
                    <div class="menu-item-footer">
                        <div class="rating">
                            <i class="fas fa-star"></i>
                            <span>${item.rating}</span>
                        </div>
                        <div class="prep-time">
                            <i class="fas fa-clock"></i>
                            <span>${item.preparation_time} mins</span>
                        </div>
                        <span class="${item.is_veg ? 'veg-badge' : 'non-veg-badge'}">
                            ${item.is_veg ? 'VEG' : 'NON-VEG'}
                        </span>
                    </div>
                    <button class="add-to-cart-btn" onclick="app.addToCart('${item.id}')">
                        <i class="fas fa-plus"></i> Add to Cart
                    </button>
                </div>
            </div>
        `).join('');
    }

    populateCategoryFilter() {
        const select = document.getElementById('categoryFilter');
        if (!select) return;

        const options = this.categories.map(cat => 
            `<option value="${cat.name}">${cat.name}</option>`
        ).join('');

        select.innerHTML = '<option value="">All Categories</option>' + options;
    }

    // Filter Methods
    handleSearch(query) {
        this.loadMenuItems({ search: query });
    }

    filterByCategory(category) {
        const filters = {};
        if (category) filters.category = category;
        this.loadMenuItems(filters);

        // Update filter select
        const select = document.getElementById('categoryFilter');
        if (select) select.value = category || '';

        // Scroll to menu
        this.scrollToSection('menu');
    }

    filterVeg(isVeg) {
        const filters = {};
        if (isVeg) filters.is_veg = 'true';
        this.loadMenuItems(filters);
    }

    // Cart Methods
    async addToCart(itemId, quantity = 1) {
        if (!this.authToken) {
            this.showToast('Please login to add items to cart', 'warning');
            this.showModal('loginModal');
            return;
        }

        try {
            const response = await this.apiCall('/api/menu/cart/add/', 'POST', {
                item_id: itemId,
                quantity: quantity
            });

            if (response.success) {
                this.showToast('Item added to cart!', 'success');
                await this.loadCart();
            } else {
                this.showToast(response.message || 'Failed to add item to cart', 'error');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showToast('Failed to add item to cart', 'error');
        }
    }

    async loadCart() {
        if (!this.authToken) return;

        try {
            const response = await this.apiCall('/api/menu/cart/', 'GET');
            if (response.success) {
                this.cart = response.cart;
                this.updateCartDisplay();
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    }

    updateCartDisplay() {
        const cartCount = document.getElementById('cartCount');
        if (cartCount) {
            cartCount.textContent = this.cart.total_items || 0;
            cartCount.style.display = (this.cart.total_items > 0) ? 'flex' : 'none';
        }
    }

    async showCartModal() {
        if (!this.authToken) {
            this.showToast('Please login to view cart', 'warning');
            this.showModal('loginModal');
            return;
        }

        await this.loadCart();
        this.renderCart();
        this.showModal('cartModal');
    }

    renderCart() {
        const container = document.getElementById('cartContent');
        if (!container) return;

        if (!this.cart.items || this.cart.items.length === 0) {
            container.innerHTML = `
                <div class="cart-empty">
                    <i class="fas fa-shopping-cart" style="font-size: 3rem; color: var(--light-gray); margin-bottom: 1rem;"></i>
                    <h3>Your cart is empty</h3>
                    <p>Add some delicious items from our menu!</p>
                </div>
            `;
            return;
        }

        const itemsHtml = this.cart.items.map(item => `
            <div class="cart-item">
                <img src="${item.image_url}" alt="${item.name}"
                     onerror="this.src='https://via.placeholder.com/80x80?text=${item.name}'">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">₹${item.price}</div>
                    <div class="cart-item-controls">
                        <button class="quantity-btn" onclick="app.updateCartItem('${item.item_id}', ${item.quantity - 1})">-</button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="quantity-btn" onclick="app.updateCartItem('${item.item_id}', ${item.quantity + 1})">+</button>
                        <button class="remove-btn" onclick="app.removeFromCart('${item.item_id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="cart-items">${itemsHtml}</div>
            <div class="cart-summary">
                <div class="summary-row">
                    <span>Subtotal:</span>
                    <span>₹${this.cart.subtotal}</span>
                </div>
                <div class="summary-row">
                    <span>Delivery Fee:</span>
                    <span>₹${this.cart.delivery_fee}</span>
                </div>
                <div class="summary-row total">
                    <span>Total:</span>
                    <span>₹${this.cart.total_amount}</span>
                </div>
                <button class="btn btn-primary btn-full" onclick="app.proceedToOrder()">
                    Proceed to Order
                </button>
            </div>
        `;
    }

    async updateCartItem(itemId, newQuantity) {
        if (newQuantity < 1) {
            await this.removeFromCart(itemId);
            return;
        }

        try {
            const response = await this.apiCall(`/api/menu/cart/update/${itemId}/`, 'PUT', {
                quantity: newQuantity
            });

            if (response.success) {
                await this.loadCart();
                this.renderCart();
            }
        } catch (error) {
            console.error('Error updating cart item:', error);
        }
    }

    async removeFromCart(itemId) {
        try {
            const response = await this.apiCall(`/api/menu/cart/remove/${itemId}/`, 'DELETE');

            if (response.success) {
                this.showToast('Item removed from cart', 'success');
                await this.loadCart();
                this.renderCart();
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
        }
    }

    // Order Methods
    proceedToOrder() {
        this.hideModal('cartModal');
        this.showOrderModal();
    }

    showOrderModal() {
        // Pre-fill user info if available
        if (this.currentUser) {
            const phoneInput = document.getElementById('orderPhone');
            const addressInput = document.getElementById('orderAddress');

            if (phoneInput && this.currentUser.phone) {
                phoneInput.value = this.currentUser.phone;
            }
            if (addressInput && this.currentUser.address) {
                addressInput.value = this.currentUser.address;
            }
        }

        this.renderOrderSummary();
        this.showModal('orderModal');
    }

    renderOrderSummary() {
        const container = document.getElementById('orderSummary');
        if (!container || !this.cart.items) return;

        const itemsHtml = this.cart.items.map(item => `
            <div class="order-item-row">
                <span>${item.name} x ${item.quantity}</span>
                <span>₹${(item.price * item.quantity).toFixed(2)}</span>
            </div>
        `).join('');

        container.innerHTML = `
            <h4>Order Summary</h4>
            ${itemsHtml}
            <div class="summary-row">
                <span>Subtotal:</span>
                <span>₹${this.cart.subtotal}</span>
            </div>
            <div class="summary-row">
                <span>Delivery Fee:</span>
                <span>₹${this.cart.delivery_fee}</span>
            </div>
            <div class="summary-row total">
                <span>Total:</span>
                <span>₹${this.cart.total_amount}</span>
            </div>
        `;
    }

    async handleOrder(e) {
        e.preventDefault();

        const orderData = {
            delivery_address: document.getElementById('orderAddress').value,
            phone: document.getElementById('orderPhone').value,
            payment_method: document.getElementById('orderPaymentMethod').value,
            special_instructions: document.getElementById('orderInstructions').value
        };

        if (!orderData.delivery_address || !orderData.phone) {
            this.showToast('Please fill in required fields', 'error');
            return;
        }

        try {
            this.showLoading();
            const response = await this.apiCall('/api/orders/create/', 'POST', orderData);

            if (response.success) {
                this.hideModal('orderModal');
                this.showToast('Order placed successfully!', 'success');
                await this.loadCart(); // Refresh cart (should be empty now)

                // Show order confirmation
                setTimeout(() => {
                    this.showToast(`Order #${response.order.order_number} is being prepared!`, 'success');
                }, 1000);
            } else {
                this.showToast(response.message || 'Failed to place order', 'error');
            }
        } catch (error) {
            console.error('Error placing order:', error);
            this.showToast('Failed to place order. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    // My Orders
    async showMyOrders() {
        if (!this.authToken) {
            this.showToast('Please login to view orders', 'warning');
            return;
        }

        try {
            this.showLoading();
            const response = await this.apiCall('/api/orders/my-orders/', 'GET');

            if (response.success) {
                this.renderMyOrders(response.orders);
                this.showModal('myOrdersModal');
            }
        } catch (error) {
            console.error('Error loading orders:', error);
            this.showToast('Failed to load orders', 'error');
        } finally {
            this.hideLoading();
        }
    }

    renderMyOrders(orders) {
        const container = document.getElementById('ordersContent');
        if (!container) return;

        if (!orders || orders.length === 0) {
            container.innerHTML = `
                <div class="cart-empty">
                    <i class="fas fa-receipt" style="font-size: 3rem; color: var(--light-gray); margin-bottom: 1rem;"></i>
                    <h3>No orders yet</h3>
                    <p>Place your first order to see it here!</p>
                </div>
            `;
            return;
        }

        const ordersHtml = orders.map(order => `
            <div class="order-item">
                <div class="order-header">
                    <div class="order-number">Order #${order.order_number}</div>
                    <div class="order-status status-${order.status}">${order.status.replace('_', ' ')}</div>
                </div>
                <div class="order-items">
                    ${order.items.map(item => `
                        <div class="order-item-row">
                            <span>${item.name} x ${item.quantity}</span>
                            <span>₹${(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="order-total">
                    <span>Total: ₹${order.total_amount}</span>
                    <small>${new Date(order.created_at).toLocaleDateString()}</small>
                </div>
            </div>
        `).join('');

        container.innerHTML = `<div class="orders-list">${ordersHtml}</div>`;
    }

    // Utility Methods
    async apiCall(url, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (this.authToken) {
            options.headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        return await response.json();
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    toggleDropdown() {
        const dropdown = document.getElementById('dropdownContent');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }

    closeDropdown() {
        const dropdown = document.getElementById('dropdownContent');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('show');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    scrollToSection(sectionId) {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }

    formatErrors(errors) {
        if (!errors) return '';

        const errorMessages = [];
        Object.keys(errors).forEach(key => {
            if (Array.isArray(errors[key])) {
                errorMessages.push(...errors[key]);
            } else {
                errorMessages.push(errors[key]);
            }
        });

        return errorMessages.join(', ');
    }
}

// Global functions
function switchModal(from, to) {
    app.hideModal(from);
    app.showModal(to);
}

function scrollToMenu() {
    app.scrollToSection('menu');
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SrinuFoodsApp();
});
