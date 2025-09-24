#!/usr/bin/env python3
"""
Script de débogage pour tester les connexions MySQL et Redis
"""

import os
import sys

# Ajouter le répertoire src au path
sys.path.insert(0, '/app/src')

print("=== DEBUG CONNEXIONS ===")

# Test du chargement du fichier a.env
print("\n1. Test du chargement de la configuration:")
try:
    from dotenv import load_dotenv
    load_dotenv('a.env')
    
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    
    print(f"DB_HOST: {DB_HOST}")
    print(f"DB_PORT: {DB_PORT}")
    print(f"DB_NAME: {DB_NAME}")
    print(f"DB_USER: {DB_USER}")
    print(f"DB_PASS: {'***' if DB_PASS else 'None'}")
    print(f"REDIS_HOST: {REDIS_HOST}")
    print(f"REDIS_PORT: {REDIS_PORT}")
    
except Exception as e:
    print(f"Erreur lors du chargement de la configuration: {e}")
    sys.exit(1)

# Test de la connexion MySQL
print("\n2. Test de la connexion MySQL:")
try:
    import mysql.connector
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    print("✓ Connexion MySQL réussie")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()
    print(f"✓ Nombre d'utilisateurs dans la table: {result[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"✗ Erreur de connexion MySQL: {e}")

# Test de la connexion Redis
print("\n3. Test de la connexion Redis:")
try:
    import redis
    r = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0, decode_responses=True)
    r.ping()
    print("✓ Connexion Redis réussie")
    
    keys = r.keys("*")
    print(f"✓ Nombre de clés dans Redis: {len(keys)}")
    
except Exception as e:
    print(f"✗ Erreur de connexion Redis: {e}")

# Test de SQLAlchemy
print("\n4. Test de SQLAlchemy:")
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    connection_string = f'mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}'
    print(f"Connection string: mysql+mysqlconnector://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Test simple query
    result = session.execute("SELECT COUNT(*) FROM users")
    count = result.fetchone()[0]
    print(f"✓ SQLAlchemy fonctionne, nombre d'utilisateurs: {count}")
    
    session.close()
    
except Exception as e:
    print(f"✗ Erreur SQLAlchemy: {e}")

print("\n=== FIN DEBUG ===")