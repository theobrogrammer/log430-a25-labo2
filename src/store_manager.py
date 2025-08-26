"""
Order manager application
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from flask import Flask, request, jsonify
from controllers.order_controller import create_order, remove_order
from controllers.product_controller import create_product, remove_product, get_product
from controllers.user_controller import create_user, remove_user, get_user
app = Flask(__name__)

@app.get('/health')
def health():
    """Return OK if app is up and running"""
    return jsonify({'status':'ok'})

# Write routes (Commands)
@app.post('/orders')
def post_orders():
    """Create a new order based on information on request body"""
    return create_order(request)

@app.delete('/orders/<int:order_id>')
def delete_orders_id(order_id):
    """Delete an order with a given order_id"""
    return remove_order(order_id)

@app.post('/products')
def post_products():
    """Create a new product based on information on request body"""
    return create_product(request)

@app.delete('/products/<int:product_id>')
def delete_products_id(product_id):
    """Delete a product with a given product_id"""
    return remove_product(product_id)

@app.post('/users')
def post_users():
    """Create a new user based on information on request body"""
    return create_user(request)

@app.delete('/users/<int:user_id>')
def delete_users_id(user_id):
    """Delete a user with a given user_id"""
    return remove_user(user_id)

# Read routes (Queries) 
@app.get('/orders/<int:order_id>')
def get_order(order_id):
    """Get order with a given order_id"""
    return get_order(order_id)

@app.get('/products/<int:product_id>')
def get_product(product_id):
    """Get product with a given product_id"""
    return get_product(product_id)

@app.get('/users/<int:user_id>')
def get_user(user_id):
    """Get user with a given user_id"""
    return get_user(user_id)

@app.get('/orders/reports/highest_spenders')
def get_orders_highest_spending_users():
    """Get list of highest speding users, order by total expenditure"""
    return "Not implemented yet"

@app.get('/orders/reports/best_sellers')
def get_orders_report_best_selling_products():
    """Get list of best selling products, order by number of orders"""
    return "Not implemented yet"

# Start Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
