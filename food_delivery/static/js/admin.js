// Srinu Foods - Admin Dashboard Application

class AdminDashboard {
    constructor() {
        this.currentUser = null;
        this.authToken = localStorage.getItem('authToken');
        this.orders = [];
        this.stats = {};

        this.init();
    }

    async init() {
        this.checkAdminAuth();
        this.setupEventListeners();
        await this.loadDashboardStats();
        await this.loadOrders();

        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.refreshDashboard();
        }, 30000);
    }

    async checkAdminAuth() {
        if (!this.authToken) {
            this.redirectToLogin();
            return;
        }

        try {
            const response = await this.apiCall('/api/auth/profile/', 'GET');
            if (!response.success || !response.user.is_staff) {
                this.showToast('Admin access required', 'error');
                this.redirectToLogin();
                return;
            }
            this.currentUser = response.user;
        } catch (error) {
            this.redirectToLogin();
        }
    }

    redirectToLogin() {
        window.location.href = '/';
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item[data-section]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.getAttribute('data-section');
                this.showSection(section);
            });
        });

        // Logout
        document.getElementById('adminLogout')?.addEventListener('click', () => {
            this.logout();
        });

        // Filters
        document.getElementById('statusFilter')?.addEventListener('change', (e) => {
            this.loadOrders(e.target.value);
        });

        // Forms
        document.getElementById('updateStatusForm')?.addEventListener('submit', (e) => {
            this.handleStatusUpdate(e);
        });

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

    showSection(sectionId) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionId}"]`)?.classList.add('active');

        // Show section
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionId)?.classList.add('active');

        // Load data for specific sections
        if (sectionId === 'orders') {
            this.loadOrders();
        }
    }

    async loadDashboardStats() {
        try {
            const response = await this.apiCall('/api/orders/admin/dashboard/stats/', 'GET');
            if (response.success) {
                this.stats = response.stats;
                this.renderDashboardStats();
                this.renderRecentOrders();
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    renderDashboardStats() {
        const stats = this.stats;

        document.getElementById('totalOrders').textContent = stats.total_orders || 0;
        document.getElementById('todayOrders').textContent = stats.today_orders || 0;
        document.getElementById('pendingOrders').textContent = stats.pending_orders || 0;
        document.getElementById('todayRevenue').textContent = `₹${stats.today_revenue || 0}`;
    }

    renderRecentOrders() {
        const container = document.getElementById('recentOrdersTable');
        if (!container) return;

        const orders = this.stats.recent_orders || [];

        if (orders.length === 0) {
            container.innerHTML = '<div class="no-data">No recent orders</div>';
            return;
        }

        const tableHtml = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Order #</th>
                        <th>Customer</th>
                        <th>Status</th>
                        <th>Amount</th>
                        <th>Time</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${orders.map(order => `
                        <tr>
                            <td>${order.order_number}</td>
                            <td>${order.customer_name}</td>
                            <td><span class="order-status status-${order.status}">${order.status.replace('_', ' ')}</span></td>
                            <td>₹${order.total_amount}</td>
                            <td>${new Date(order.created_at).toLocaleString()}</td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="adminDashboard.showOrderDetails('${order.id}')">
                                    View
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHtml;
    }

    async loadOrders(statusFilter = '') {
        try {
            let url = '/api/orders/admin/all/';
            if (statusFilter) {
                url += `?status=${statusFilter}`;
            }

            const response = await this.apiCall(url, 'GET');
            if (response.success) {
                this.orders = response.orders;
                this.renderOrders();
            }
        } catch (error) {
            console.error('Error loading orders:', error);
            this.showToast('Failed to load orders', 'error');
        }
    }

    renderOrders() {
        const container = document.getElementById('ordersContainer');
        if (!container) return;

        if (this.orders.length === 0) {
            container.innerHTML = '<div class="no-data">No orders found</div>';
            return;
        }

        const ordersHtml = this.orders.map(order => `
            <div class="order-card">
                <div class="order-card-header">
                    <div class="order-number">Order #${order.order_number}</div>
                    <div class="order-status status-${order.status}">
                        ${order.status.replace('_', ' ')}
                    </div>
                </div>

                <div class="order-customer">
                    <div>
                        <strong>Customer:</strong>
                        ${order.customer_name}
                    </div>
                    <div>
                        <strong>Phone:</strong>
                        ${order.customer_phone}
                    </div>
                    <div>
                        <strong>Address:</strong>
                        ${order.delivery_address}
                    </div>
                    <div>
                        <strong>Order Time:</strong>
                        ${new Date(order.created_at).toLocaleString()}
                    </div>
                </div>

                <div class="order-items">
                    <h4>Items Ordered:</h4>
                    <div class="order-item-list">
                        ${order.items.map(item => `
                            <div class="order-item-row">
                                <span>${item.name} x ${item.quantity}</span>
                                <span>₹${(item.price * item.quantity).toFixed(2)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="order-total">
                    <strong>Total Amount: ₹${order.total_amount}</strong>
                    <span>Payment: ${order.payment_method.toUpperCase()}</span>
                </div>

                ${order.special_instructions ? `
                    <div class="order-notes">
                        <strong>Special Instructions:</strong>
                        <p>${order.special_instructions}</p>
                    </div>
                ` : ''}

                <div class="order-actions">
                    <button class="btn btn-primary btn-sm" onclick="adminDashboard.showOrderDetails('${order.id}')">
                        View Details
                    </button>
                    <button class="btn btn-warning btn-sm" onclick="adminDashboard.showUpdateStatus('${order.id}', '${order.status}')">
                        Update Status
                    </button>
                    ${order.status === 'pending' ? `
                        <button class="btn btn-success btn-sm" onclick="adminDashboard.quickUpdateStatus('${order.id}', 'confirmed')">
                            Confirm Order
                        </button>
                    ` : ''}
                    ${order.status === 'confirmed' ? `
                        <button class="btn btn-success btn-sm" onclick="adminDashboard.quickUpdateStatus('${order.id}', 'preparing')">
                            Start Preparing
                        </button>
                    ` : ''}
                    ${order.status === 'preparing' ? `
                        <button class="btn btn-success btn-sm" onclick="adminDashboard.quickUpdateStatus('${order.id}', 'ready')">
                            Mark Ready
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');

        container.innerHTML = ordersHtml;
    }

    async showOrderDetails(orderId) {
        try {
            const response = await this.apiCall(`/api/orders/${orderId}/`, 'GET');
            if (response.success) {
                this.renderOrderDetails(response.order);
                this.showModal('orderDetailsModal');
            }
        } catch (error) {
            console.error('Error loading order details:', error);
            this.showToast('Failed to load order details', 'error');
        }
    }

    renderOrderDetails(order) {
        const container = document.getElementById('orderDetailsContent');
        if (!container) return;

        container.innerHTML = `
            <div class="order-detail-section">
                <h4>Order Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">Order Number</div>
                        <div class="detail-value">${order.order_number}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Status</div>
                        <div class="detail-value">
                            <span class="order-status status-${order.status}">
                                ${order.status.replace('_', ' ')}
                            </span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Order Time</div>
                        <div class="detail-value">${new Date(order.created_at).toLocaleString()}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Payment Method</div>
                        <div class="detail-value">${order.payment_method.toUpperCase()}</div>
                    </div>
                </div>
            </div>

            <div class="order-detail-section">
                <h4>Customer Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">Name</div>
                        <div class="detail-value">${order.customer_name}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Email</div>
                        <div class="detail-value">${order.customer_email}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Phone</div>
                        <div class="detail-value">${order.customer_phone}</div>
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Delivery Address</div>
                    <div class="detail-value">${order.delivery_address}</div>
                </div>
                ${order.special_instructions ? `
                    <div class="detail-item">
                        <div class="detail-label">Special Instructions</div>
                        <div class="detail-value">${order.special_instructions}</div>
                    </div>
                ` : ''}
            </div>

            <div class="order-detail-section">
                <h4>Order Items</h4>
                <div class="order-item-list">
                    ${order.items.map(item => `
                        <div class="order-item-row">
                            <span>${item.name} x ${item.quantity}</span>
                            <span>₹${(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="order-total" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--light-gray);">
                    <div class="summary-row">
                        <span>Subtotal:</span>
                        <span>₹${order.subtotal}</span>
                    </div>
                    <div class="summary-row">
                        <span>Delivery Fee:</span>
                        <span>₹${order.delivery_fee}</span>
                    </div>
                    <div class="summary-row" style="font-weight: bold; font-size: 1.1rem;">
                        <span>Total Amount:</span>
                        <span>₹${order.total_amount}</span>
                    </div>
                </div>
            </div>
        `;
    }

    showUpdateStatus(orderId, currentStatus) {
        document.getElementById('updateOrderId').value = orderId;
        document.getElementById('newOrderStatus').value = currentStatus;
        this.showModal('updateStatusModal');
    }

    async handleStatusUpdate(e) {
        e.preventDefault();

        const orderId = document.getElementById('updateOrderId').value;
        const newStatus = document.getElementById('newOrderStatus').value;

        await this.updateOrderStatus(orderId, newStatus);
        this.hideModal('updateStatusModal');
    }

    async quickUpdateStatus(orderId, newStatus) {
        await this.updateOrderStatus(orderId, newStatus);
    }

    async updateOrderStatus(orderId, newStatus) {
        try {
            const response = await this.apiCall(
                `/api/orders/admin/${orderId}/update-status/`,
                'PUT',
                { status: newStatus }
            );

            if (response.success) {
                this.showToast(`Order status updated to ${newStatus.replace('_', ' ')}`, 'success');
                await this.loadOrders(); // Refresh orders list
                await this.loadDashboardStats(); // Refresh stats
            } else {
                this.showToast(response.message || 'Failed to update order status', 'error');
            }
        } catch (error) {
            console.error('Error updating order status:', error);
            this.showToast('Failed to update order status', 'error');
        }
    }

    async refreshDashboard() {
        await this.loadDashboardStats();

        // If orders section is active, refresh orders too
        const ordersSection = document.getElementById('orders');
        if (ordersSection?.classList.contains('active')) {
            const statusFilter = document.getElementById('statusFilter')?.value || '';
            await this.loadOrders(statusFilter);
        }
    }

    logout() {
        localStorage.removeItem('authToken');
        window.location.href = '/';
    }

    // Utility Methods
    async apiCall(url, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.authToken}`
            }
        };

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
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
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
}

// Global functions for onclick handlers
let adminDashboard;

function refreshDashboard() {
    adminDashboard.refreshDashboard();
}

function loadOrders() {
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    adminDashboard.loadOrders(statusFilter);
}

// Initialize admin dashboard
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});
