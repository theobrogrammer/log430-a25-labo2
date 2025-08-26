"""
Orders (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from db import get_redis_conn
from collections import defaultdict

def get_order_by_id(order_id):
    """Get order by ID from Redis"""
    r = get_redis_conn()
    return r.hgetall(order_id)

def get_highest_spending_users():
    """Get report of top 10 highest spending users"""
    r = get_redis_conn()
    result = []
    all_orders = r.keys("order:*")
    
    # TODO: complétez la méthode
    # triez par total dépensé (ordre décroissant), limite 10
    limit = 10
    highest_spending_users = []
    for user in highest_spending_users:
        result.append({
            "user_id": user[0],
            "total_expense": round(user[1], 2)
        })

    return result

def get_best_selling_products():
    """Get report of best selling products"""
    # TODO: écrivez la méthode
    # triez le résultat par nombre de commandes (ordre décroissant)
    return []