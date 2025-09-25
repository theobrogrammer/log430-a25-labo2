"""
Product (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from sqlalchemy import desc
from db import get_sqlalchemy_session, get_redis_conn
from models.product import Product

def get_product_by_id(product_id):
    """Get product by ID """
    session = get_sqlalchemy_session()
    result = session.query(Product).filter_by(id=product_id).all()

    if len(result):
        return {
            'id': result[0].id,
            'name': result[0].name,
            'sku': result[0].sku,
            'price': result[0].price
        }
    else:
        return {}

def get_products(limit=9999):
    """Get last X products"""
    session = get_sqlalchemy_session()
    return session.query(Product).order_by(desc(Product.id)).limit(limit).all()

def get_best_selling_products_from_redis():
    """Obtient le top 10 des produits les plus vendus depuis Redis uniquement"""
    try:
        redis_conn = get_redis_conn()
        
        # 1. Récupérer tous les compteurs de vente
        product_sales_keys = redis_conn.keys("product:*:sold")
        
        if not product_sales_keys:
            print("No product sales data found in Redis")
            return []
        
        # 2. Collecter les données de vente
        product_sales = []
        for key in product_sales_keys:
            try:
                # Extraire l'ID du produit de "product:123:sold" -> "123"
                product_id = key.split(":")[1]
                
                # Récupérer la quantité vendue
                quantity_sold = int(redis_conn.get(key) or 0)
                
                if quantity_sold > 0:
                    product_sales.append((int(product_id), quantity_sold))
                    
            except (IndexError, ValueError) as e:
                print(f"Error parsing key {key}: {e}")
                continue
        
        # 3. Trier par quantité vendue (ordre décroissant) et limiter au top 10
        best_selling_products = sorted(
            product_sales,
            key=lambda item: item[1],  # Trier par quantité (index 1)
            reverse=True
        )[:10]
        
        print(f"Found {len(best_selling_products)} best selling products")
        return best_selling_products
        
    except Exception as e:
        print(f"Error retrieving best selling products: {e}")
        return []