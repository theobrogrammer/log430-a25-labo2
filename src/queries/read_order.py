"""
Orders (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from db import get_sqlalchemy_session, get_redis_conn
from sqlalchemy import desc
from models.order import Order

def get_order_by_id(order_id):
    """Get order by ID from Redis"""
    r = get_redis_conn()
    
    try:
        # Utiliser le bon format de clé
        order_key = f"order:{order_id}"
        order_data = r.hgetall(order_key)
        
        if order_data:
            return order_data
        else:
            print(f"Order {order_id} not found in Redis")
            return {}
            
    except Exception as e:
        print(f"Error retrieving order {order_id} from Redis: {e}")
        return {}

def get_orders_from_mysql(limit=9999):
    """Get last X orders"""
    session = get_sqlalchemy_session()
    return session.query(Order).order_by(desc(Order.id)).limit(limit).all()

def get_orders_from_redis(limit=9999):
    """Get last X orders from Redis"""
    r = get_redis_conn()
    orders = []
    
    try:
        # 1. Récupérer toutes les clés de commandes
        order_keys = r.keys("order:*")
        
        # 2. Trier les clés par ID (les plus récentes en premier)
        # Extraire les IDs numériques des clés pour le tri
        order_ids = []
        for key in order_keys:
            try:
                # Extraire l'ID de la clé "order:123" -> 123
                order_id = int(key.split(":")[1])
                order_ids.append(order_id)
            except (IndexError, ValueError):
                continue
        
        # Trier par ID décroissant (plus récentes en premier)
        order_ids.sort(reverse=True)
        
        # 3. Limiter les résultats
        limited_ids = order_ids[:limit]
        
        # 4. Récupérer les données de chaque commande
        for order_id in limited_ids:
            order_key = f"order:{order_id}"
            order_data = r.hgetall(order_key)
            
            if order_data:
                # Créer un objet similaire à celui de MySQL pour compatibilité
                class OrderFromRedis:
                    def __init__(self, data):
                        self.id = int(data.get('id', 0))
                        self.user_id = int(data.get('user_id', 0))
                        self.total_amount = float(data.get('total_amount', 0.0))
                        self.items_count = int(data.get('items_count', 0))
                        self.items = data.get('items', '')
                
                order_obj = OrderFromRedis(order_data)
                orders.append(order_obj)
                
        print(f"Retrieved {len(orders)} orders from Redis (limit: {limit})")
        return orders
        
    except Exception as e:
        print(f"Error retrieving orders from Redis: {e}")
        return []

def get_highest_spending_users():
    """Get report of highest spending users from Redis"""
    from collections import defaultdict
    
    try:
        # Récupérer toutes les commandes depuis Redis
        orders = get_orders_from_redis()
        
        if not orders:
            print("No orders found in Redis")
            return []
        
        # Calculer les dépenses totales par utilisateur
        expenses_by_user = defaultdict(float)
        for order in orders:
            expenses_by_user[order.user_id] += order.total_amount
        
        # Trier par total dépensé (ordre décroissant) et limiter au top 10
        highest_spending_users = sorted(
            expenses_by_user.items(), 
            key=lambda item: item[1], 
            reverse=True
        )[:10]
        
        print(f"Found {len(highest_spending_users)} highest spending users")
        return highest_spending_users
        
    except Exception as e:
        print(f"Error retrieving highest spending users: {e}")
        return []