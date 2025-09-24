"""
Orders (write-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from models.product import Product
from models.order_item import OrderItem
from models.order import Order
from queries.read_order import get_orders_from_mysql
from db import get_sqlalchemy_session, get_redis_conn

def add_order(user_id: int, items: list):
    """Insert order with items in MySQL, keep Redis in sync"""
    if not user_id or not items:
        raise ValueError("Vous devez indiquer au moins 1 utilisateur et 1 item pour chaque commande.")

    try:
        product_ids = []
        for item in items:
            product_ids.append(int(item['product_id']))
    except Exception as e:
        print(e)
        raise ValueError(f"L'ID Article n'est pas valide: {item['product_id']}")
    session = get_sqlalchemy_session()

    try:
        products_query = session.query(Product).filter(Product.id.in_(product_ids)).all()
        price_map = {product.id: product.price for product in products_query}
        total_amount = 0
        order_items_data = []
        
        for item in items:
            pid = int(item["product_id"])
            qty = float(item["quantity"])

            if not qty or qty <= 0:
                raise ValueError(f"Vous devez indiquer une quantité superieure à zéro.")

            if pid not in price_map:
                raise ValueError(f"Article ID {pid} n'est pas dans la base de données.")

            unit_price = price_map[pid]
            total_amount += unit_price * qty
            order_items_data.append({
                'product_id': pid,
                'quantity': qty,
                'unit_price': unit_price
            })
        
        new_order = Order(user_id=user_id, total_amount=total_amount)
        session.add(new_order)
        session.flush() 
        
        order_id = new_order.id

        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            session.add(order_item)

        session.commit()

        # TODO: ajouter la commande à Redis
        add_order_to_redis(order_id, user_id, total_amount, items)

        return order_id

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def delete_order(order_id: int):
    """Delete order in MySQL, keep Redis in sync"""
    session = get_sqlalchemy_session()
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        
        if order:
            session.delete(order)
            session.commit()

            # TODO: supprimer la commande à Redis
            delete_order_from_redis(order_id)
            return 1  
        else:
            return 0  
            
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def add_order_to_redis(order_id, user_id, total_amount, items):
    """Insert order to Redis"""
    r = get_redis_conn()
    
    try:
        # Créer une clé unique pour la commande
        order_key = f"order:{order_id}"
        
        # Préparer les données de la commande
        order_data = {
            "id": str(order_id),
            "user_id": str(user_id),
            "total_amount": str(total_amount),
            "items_count": str(len(items))
        }
        
        # Ajouter les informations des items
        items_list = []
        for item in items:
            item_str = f"product_id:{item['product_id']},quantity:{item['quantity']}"
            items_list.append(item_str)
        order_data["items"] = ";".join(items_list)
        
        # Stocker la commande dans Redis
        r.hset(order_key, mapping=order_data)
        print(f"Order {order_id} added to Redis")
        
        # Incrémenter le compteur pour chaque produit vendu (pour les rapports)
        for item in items:
            product_key = f"product:{item['product_id']}:sold"
            r.incr(product_key, int(item['quantity']))
            
    except Exception as e:
        print(f"Error adding order {order_id} to Redis: {e}")

def delete_order_from_redis(order_id):
    """Delete order from Redis"""
    r = get_redis_conn()
    
    try:
        order_key = f"order:{order_id}"
        
        # Récupérer les informations de la commande avant de la supprimer
        # pour décrémenter les compteurs de produits
        order_data = r.hgetall(order_key)
        
        if order_data and "items" in order_data:
            # Parse les items pour décrémenter les compteurs
            items_str = order_data["items"]
            if items_str:
                items_list = items_str.split(";")
                for item_str in items_list:
                    # Parse product_id:123,quantity:2
                    item_parts = item_str.split(",")
                    if len(item_parts) == 2:
                        product_id = item_parts[0].split(":")[1]
                        quantity = int(item_parts[1].split(":")[1])
                        
                        # Décrémenter le compteur du produit
                        product_key = f"product:{product_id}:sold"
                        r.decr(product_key, quantity)
        
        # Supprimer la commande de Redis
        deleted_count = r.delete(order_key)
        if deleted_count > 0:
            print(f"Order {order_id} deleted from Redis")
        else:
            print(f"Order {order_id} was not found in Redis")
            
    except Exception as e:
        print(f"Error deleting order {order_id} from Redis: {e}")

def sync_all_orders_to_redis():
    """ Sync orders from MySQL to Redis """
    # redis
    r = get_redis_conn()
    orders_in_redis = r.keys(f"order:*")
    rows_added = 0
    try:
        if len(orders_in_redis) == 0:
            # mysql - récupérer toutes les commandes depuis MySQL
            orders_from_mysql = get_orders_from_mysql()
            for order in orders_from_mysql:
                # Créer une clé unique pour chaque commande dans Redis
                order_key = f"order:{order.id}"
                
                # Stocker les informations de la commande dans Redis comme un hash
                order_data = {
                    "id": str(order.id),
                    "user_id": str(order.user_id),
                    "total_amount": str(order.total_amount),
                    "created_at": str(order.created_at) if hasattr(order, 'created_at') else ""
                }
                
                # Ajouter la commande à Redis
                r.hset(order_key, mapping=order_data)
                print(f"Synchronized order {order.id} to Redis")
            
            rows_added = len(orders_from_mysql)
            print(f"Successfully synchronized {rows_added} orders from MySQL to Redis")
        else:
            print('Redis already contains orders, no need to sync!')
    except Exception as e:
        print(f"Error during synchronization: {e}")
        return 0
    finally:
        return len(orders_in_redis) + rows_added