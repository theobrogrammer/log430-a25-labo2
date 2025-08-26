"""
Order controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from flask import jsonify
from commands.write_order import insert_order, delete_order
from queries.read_order import get_order_by_id

def create_order(request):
    """Create order, use WriteOrder model"""
    payload = request.get_json() or {}
    user_id = payload.get('user_id')
    items = payload.get('items', [])
    try:
        order_id = insert_order(user_id, items)
        return jsonify({'order_id': order_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def remove_order(order_id):
    """Delete order, use WriteOrder model"""
    try:
        deleted = delete_order(order_id)
        if deleted:
            return jsonify({'deleted': True})
        return jsonify({'deleted': False}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_order(order_id):
    """Create order, use ReadOrder model"""
    try:
        order = get_order_by_id(order_id)
        return jsonify(order), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def get_report_highest_spending_users():
    """Get orders report: highest spending users"""
    # TODO: appeler la méthode correspondante dans read_order.py
    return []

def get_report_best_selling_products():
    """Get orders report: best selling products"""
    # TODO: appeler la méthode correspondante dans read_order.py
    return []