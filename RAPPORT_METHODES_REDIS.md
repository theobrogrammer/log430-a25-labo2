# Rapport : Méthodes Redis utilisées dans l'implémentation CQRS

## Question 3 : Quelles méthodes avez-vous utilisées pour ajouter des données dans Redis ?

### Introduction

Dans le cadre de l'implémentation du patron CQRS (Command Query Responsibility Segregation), nous avons intégré Redis comme système de cache pour optimiser les performances de lecture et réduire la charge sur MySQL. À chaque commande ajoutée dans MySQL, celle-ci est également insérée dans Redis, permettant de générer des rapports statistiques sans solliciter la base de données principale.

---

## 1. HSET - Stockage de données structurées

### Description
La méthode `HSET` crée ou met à jour un **hash** (structure de données clé-valeur) dans Redis. Un hash est similaire à un dictionnaire Python et permet de stocker des données structurées sous une clé principale.

### Code d'implémentation
```python
def add_order_to_redis(order_id, user_id, total_amount, items):
    """Insert order to Redis"""
    r = get_redis_conn()
    
    # Créer une clé unique pour la commande
    order_key = f"order:{order_id}"
    
    # Préparer les données de la commande
    order_data = {
        "id": str(order_id),
        "user_id": str(user_id),
        "total_amount": str(total_amount),
        "items_count": str(len(items))
    }
    
    # Stocker la commande dans Redis avec HSET
    r.hset(order_key, mapping=order_data)
```

### Exemple concret
```python
# Données à stocker
order_data = {
    "id": "123",
    "user_id": "5", 
    "total_amount": "45.99",
    "items_count": "2"
}

# Stockage dans Redis
r.hset("order:123", mapping=order_data)

# Résultat dans Redis :
# order:123 → {
#     id: "123",
#     user_id: "5",
#     total_amount: "45.99", 
#     items_count: "2"
# }
```

### Avantages
- Stockage efficace de données structurées
- Accès rapide à des champs spécifiques
- Moins d'espace mémoire qu'un stockage par clés séparées

---

## 2. HGETALL - Lecture complète d'un hash

### Description
`HGETALL` récupère **tous les champs et valeurs** d'un hash en une seule opération atomique. Cette méthode retourne un dictionnaire Python avec tous les champs du hash.

### Code d'implémentation
```python
def delete_order_from_redis(order_id):
    """Delete order from Redis"""
    r = get_redis_conn()
    order_key = f"order:{order_id}"
    
    # Récupérer les informations complètes avant suppression
    order_data = r.hgetall(order_key)
    
    if order_data and "items" in order_data:
        # Utiliser les données récupérées pour mettre à jour les compteurs
        items_str = order_data["items"]
        # ... traitement des items
```

### Exemple concret
```python
# Récupération complète d'une commande
order_data = r.hgetall("order:123")

# Résultat : 
# {
#     'id': '123',
#     'user_id': '5', 
#     'total_amount': '45.99',
#     'items_count': '2',
#     'items': 'product_id:10,quantity:1;product_id:15,quantity:3'
# }
```

### Usage
- Récupération des détails d'une commande avant sa suppression
- Extraction des informations nécessaires pour maintenir la cohérence des compteurs

---

## 3. INCR - Incrémentation atomique de compteurs

### Description
`INCR` incrémente la valeur d'une clé de manière **atomique** (thread-safe). Si la clé n'existe pas, elle est créée avec la valeur 0 puis incrémentée. Cette opération est idéale pour les compteurs et statistiques.

### Code d'implémentation
```python
def add_order_to_redis(order_id, user_id, total_amount, items):
    # ... stockage de la commande principale ...
    
    # Incrémenter le compteur pour chaque produit vendu
    for item in items:
        product_key = f"product:{item['product_id']}:sold"
        r.incr(product_key, int(item['quantity']))
```

### Exemple concret
```python
# Première vente du produit 10 (quantité 2)
r.incr("product:10:sold", 2)  
# Redis: product:10:sold → "2"

# Deuxième vente du produit 10 (quantité 1)
r.incr("product:10:sold", 1)  
# Redis: product:10:sold → "3"

# Troisième vente du produit 10 (quantité 5)
r.incr("product:10:sold", 5)  
# Redis: product:10:sold → "8"
```

### Avantages
- **Atomicité** : Pas de race conditions même avec des accès concurrents
- **Performance** : Opération ultra-rapide en mémoire
- **Automatique** : Création automatique de la clé si elle n'existe pas
- **Statistiques temps réel** : Compteurs instantanément disponibles

---

## 4. DECR - Décrémentation atomique de compteurs

### Description
`DECR` décrémente la valeur d'une clé de manière **atomique**. Cette méthode est utilisée pour "annuler" l'effet d'un INCR lors d'une suppression de commande, maintenant ainsi la cohérence des statistiques.

### Code d'implémentation
```python
def delete_order_from_redis(order_id):
    """Delete order from Redis"""
    r = get_redis_conn()
    order_key = f"order:{order_id}"
    
    order_data = r.hgetall(order_key)
    
    if order_data and "items" in order_data:
        items_str = order_data["items"]
        items_list = items_str.split(";")
        
        for item_str in items_list:
            # Parse "product_id:10,quantity:2"
            item_parts = item_str.split(",")
            product_id = item_parts[0].split(":")[1]
            quantity = int(item_parts[1].split(":")[1])
            
            # Décrémenter le compteur du produit
            product_key = f"product:{product_id}:sold"
            r.decr(product_key, quantity)
```

### Exemple concret
```python
# État initial après plusieurs ventes
# product:10:sold → "8"

# Suppression d'une commande contenant 3 unités du produit 10
r.decr("product:10:sold", 3)

# Résultat final
# product:10:sold → "5"
```

### Cohérence des données
Cette méthode garantit que les compteurs de ventes restent précis même lors de suppressions de commandes, maintenant l'intégrité des statistiques.

---

## 5. DELETE - Suppression de clés

### Description
`DELETE` supprime complètement une clé et toutes ses données de Redis. Cette méthode retourne le nombre de clés effectivement supprimées et libère immédiatement la mémoire.

### Code d'implémentation
```python
def delete_order_from_redis(order_id):
    # ... mise à jour des compteurs ...
    
    # Supprimer la commande de Redis
    deleted_count = r.delete(order_key)
    
    if deleted_count > 0:
        print(f"Order {order_id} deleted from Redis")
    else:
        print(f"Order {order_id} was not found in Redis")
```

### Exemple concret
```python
# Avant suppression : order:123 existe avec ses données
result = r.delete("order:123")
print(result)  # Affiche 1 (1 clé supprimée)

# Tentative de suppression d'une clé inexistante
result = r.delete("order:999") 
print(result)  # Affiche 0 (aucune clé supprimée)
```

---

## 6. KEYS - Recherche de clés par pattern

### Description
`KEYS` trouve toutes les clés qui correspondent à un **pattern** (motif). Le caractère `*` est un wildcard qui signifie "n'importe quoi". Cette méthode est utilisée pour la synchronisation et les vérifications.

### Code d'implémentation
```python
def sync_all_orders_to_redis():
    """Sync orders from MySQL to Redis"""
    r = get_redis_conn()
    
    # Vérifier si des commandes existent déjà dans Redis
    orders_in_redis = r.keys("order:*")
    
    if len(orders_in_redis) == 0:
        # Synchroniser depuis MySQL
        orders_from_mysql = get_orders_from_mysql()
        # ... synchronisation ...
    else:
        print(f'Redis contains {len(orders_in_redis)} orders, sync skipped')
```

### Exemple concret
```python
# Si Redis contient : order:1, order:15, order:23, user:5, product:10:sold
keys = r.keys("order:*")
print(keys)  # ['order:1', 'order:15', 'order:23']

# Compter le nombre de commandes
count = len(r.keys("order:*"))
print(f"Nombre de commandes : {count}")  # "Nombre de commandes : 3"
```

---

## 7. Exemple complet : Flux d'ajout d'une commande

### Séquence complète d'opérations

```python
def add_order_to_redis(order_id, user_id, total_amount, items):
    """Exemple complet d'utilisation combinée des méthodes Redis"""
    r = get_redis_conn()
    
    try:
        # 1. HSET - Stocker la commande principale
        order_key = f"order:{order_id}"
        
        # Préparation des données
        items_list = []
        for item in items:
            item_str = f"product_id:{item['product_id']},quantity:{item['quantity']}"
            items_list.append(item_str)
        
        order_data = {
            "id": str(order_id),
            "user_id": str(user_id),
            "total_amount": str(total_amount),
            "items_count": str(len(items)),
            "items": ";".join(items_list)  # Format sérialisé des items
        }
        
        # Stockage du hash principal
        r.hset(order_key, mapping=order_data)
        print(f"Order {order_id} added to Redis")
        
        # 2. INCR - Mise à jour des statistiques de vente
        for item in items:
            product_key = f"product:{item['product_id']}:sold"
            r.incr(product_key, int(item['quantity']))
            print(f"Product {item['product_id']} counter incremented by {item['quantity']}")
            
    except Exception as e:
        print(f"Error adding order {order_id} to Redis: {e}")
```

### État de Redis après ajout d'une commande

```
# Hash principal de la commande
order:123 → {
    id: "123",
    user_id: "5",
    total_amount: "45.99",
    items_count: "2",
    items: "product_id:10,quantity:1;product_id:15,quantity:3"
}

# Compteurs de vente mis à jour
product:10:sold → "1"    # +1 unité vendue
product:15:sold → "3"    # +3 unités vendues
```

---

## Avantages de cette architecture Redis

### 1. **Performance optimisée**
- Toutes les opérations Redis se font en mémoire
- Temps de réponse sub-millisecondes
- Pas de requêtes SQL coûteuses pour les consultations

### 2. **Atomicité garantie**
- Les opérations INCR/DECR sont atomiques
- Pas de race conditions même avec des accès concurrents
- Cohérence des compteurs assurée

### 3. **Statistiques temps réel**
- Les compteurs de vente sont instantanément disponibles
- Génération de rapports sans impact sur MySQL
- Métriques business en temps réel

### 4. **Scalabilité**
- Réduction drastique de la charge sur MySQL
- Possibilité de scaler Redis horizontalement
- Architecture prête pour de forts volumes

### 5. **Flexibilité des données**
- Structure de hash permettant des données complexes
- Sérialisation personnalisée des items de commande
- Extension facile pour de nouveaux champs

---

## Conclusion

L'implémentation de ces méthodes Redis dans notre architecture CQRS démontre une utilisation avancée qui va bien au-delà d'un simple cache. En combinant les structures de données hash (HSET/HGETALL) pour le stockage principal et les compteurs atomiques (INCR/DECR) pour les statistiques, nous avons créé un système de données en mémoire robuste et performant.

Cette approche permet de :
- Maintenir MySQL comme source de vérité pour les écritures
- Utiliser Redis comme système optimisé pour les lectures et statistiques  
- Garantir la cohérence des données entre les deux systèmes
- Offrir des performances exceptionnelles pour les consultations

Les méthodes Redis utilisées (`HSET`, `HGETALL`, `INCR`, `DECR`, `DELETE`, `KEYS`) forment un ensemble cohérent qui répond parfaitement aux exigences d'une application à forte charge nécessitant des statistiques temps réel sans impacter les performances de la base de données principale.