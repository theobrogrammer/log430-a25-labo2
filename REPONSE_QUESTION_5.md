# Question 5 : Rapport des produits les plus vendus avec Redis

## Analyse des données actuelles dans Redis

### Données disponibles actuellement

Dans notre implémentation Redis actuelle, nous stockons :

1. **Commandes principales** (clés `order:*`) :
```python
order_data = {
    "id": "123",
    "user_id": "5",
    "total_amount": "45.99",
    "items_count": "2",
    "items": "product_id:10,quantity:1;product_id:15,quantity:3"
}
```

2. **Compteurs de vente par produit** (clés `product:*:sold`) :
```python
# Exemple dans Redis :
product:10:sold → "15"    # 15 unités vendues du produit 10
product:15:sold → "8"     # 8 unités vendues du produit 15
```

## Réponse : Les données Redis sont-elles suffisantes ?

**OUI**, les données actuellement stockées dans Redis sont **suffisantes** pour créer un rapport des produits les plus vendus ! Nous avons déjà tous les éléments nécessaires grâce aux compteurs `product:*:sold` qui sont maintenus à jour par les opérations INCR/DECR.

## Implémentation du rapport des produits les plus vendus

### Méthode utilisant uniquement Redis

```python
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

def get_best_selling_products_with_details():
    """Version enrichie avec détails des produits depuis MySQL"""
    try:
        # 1. Obtenir les top ventes depuis Redis
        best_selling = get_best_selling_products_from_redis()
        
        if not best_selling:
            return []
        
        # 2. Enrichir avec les détails depuis MySQL
        from db import get_sqlalchemy_session
        from models.product import Product
        
        session = get_sqlalchemy_session()
        enriched_results = []
        
        for product_id, quantity_sold in best_selling:
            # Récupérer les détails du produit depuis MySQL
            product = session.query(Product).filter(Product.id == product_id).first()
            
            if product:
                enriched_results.append({
                    'product_id': product_id,
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'product_price': float(product.price),
                    'quantity_sold': quantity_sold,
                    'revenue_generated': float(product.price) * quantity_sold
                })
        
        session.close()
        return enriched_results
        
    except Exception as e:
        print(f"Error retrieving detailed best selling products: {e}")
        return []
```

## Exemple d'utilisation et résultats

### Utilisation basique (Redis uniquement)
```python
# Résultat : [(product_id, quantity_sold), ...]
best_sellers = get_best_selling_products_from_redis()
print(best_sellers)
# Exemple : [(15, 25), (10, 18), (7, 12), (3, 8), ...]
```

### Utilisation enrichie (Redis + MySQL)
```python
# Résultat enrichi avec détails des produits
detailed_report = get_best_selling_products_with_details()
for item in detailed_report:
    print(f"Produit: {item['product_name']} - Vendu: {item['quantity_sold']} unités - Revenus: ${item['revenue_generated']:.2f}")

# Exemple de sortie :
# Produit: MacBook Pro - Vendu: 25 unités - Revenus: $37500.00
# Produit: iPhone 14 - Vendu: 18 unités - Revenus: $14400.00
# Produit: AirPods Pro - Vendu: 12 unités - Revenus: $2988.00
```

## Informations supplémentaires optionnelles

### Si nous voulions éviter complètement MySQL

Pour un rapport 100% Redis, nous pourrions enrichir nos données en stockant également :

```python
def add_product_details_to_redis(product_id, name, sku, price):
    """Ajouter les détails des produits dans Redis pour éviter MySQL"""
    redis_conn = get_redis_conn()
    
    product_key = f"product:{product_id}:details"
    product_data = {
        "id": str(product_id),
        "name": name,
        "sku": sku,
        "price": str(price)
    }
    
    redis_conn.hset(product_key, mapping=product_data)

def get_best_selling_products_full_redis():
    """Version 100% Redis avec détails des produits"""
    try:
        redis_conn = get_redis_conn()
        
        # 1. Obtenir les ventes
        product_sales_keys = redis_conn.keys("product:*:sold")
        enriched_results = []
        
        for key in product_sales_keys:
            product_id = key.split(":")[1]
            quantity_sold = int(redis_conn.get(key) or 0)
            
            # 2. Récupérer les détails depuis Redis
            details_key = f"product:{product_id}:details"
            product_details = redis_conn.hgetall(details_key)
            
            if product_details and quantity_sold > 0:
                enriched_results.append({
                    'product_id': int(product_id),
                    'product_name': product_details.get('name', 'Unknown'),
                    'quantity_sold': quantity_sold,
                    'price': float(product_details.get('price', 0)),
                    'revenue': quantity_sold * float(product_details.get('price', 0))
                })
        
        # 3. Trier et limiter
        return sorted(enriched_results, key=lambda x: x['quantity_sold'], reverse=True)[:10]
        
    except Exception as e:
        print(f"Error in full Redis report: {e}")
        return []
```

## Conclusion

### Données suffisantes ? **OUI**

Les compteurs Redis `product:*:sold` maintenus par nos opérations INCR/DECR sont **parfaitement suffisants** pour générer un rapport des produits les plus vendus. Cette approche offre :

- **Performance maximale** : Lecture directe des compteurs Redis
- **Données temps réel** : Compteurs mis à jour à chaque vente
- **Simplicité** : Une seule opération pour obtenir les statistiques

### Améliorations optionnelles

Pour enrichir le rapport avec des détails (nom, prix), deux approches sont possibles :
1. **Hybride** (recommandée) : Statistics depuis Redis + détails depuis MySQL
2. **Full Redis** : Dupliquer les détails produits dans Redis

L'approche hybride est généralement préférable car elle maintient MySQL comme source de vérité pour les données de référence tout en utilisant Redis pour les statistiques haute performance.

### Code d'intégration dans le contrôleur

```python
# Dans controllers/order_controller.py
def get_product_sales_report():
    """Contrôleur pour le rapport des meilleures ventes"""
    try:
        return get_best_selling_products_with_details()
    except Exception as e:
        print(f"Error in sales report controller: {e}")
        return f"Erreur lors de la génération du rapport: {str(e)}"
```

Cette implémentation démontre parfaitement comment Redis peut servir de source unique pour les statistiques tout en maintenant la flexibilité d'enrichir les données depuis MySQL selon les besoins.