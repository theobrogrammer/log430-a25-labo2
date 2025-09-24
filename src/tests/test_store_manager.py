"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import sys
import os
from dotenv import load_dotenv

# Ajouter le répertoire parent (src/) au Python path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger le fichier a.env depuis le répertoire racine du projet
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_file = os.path.join(project_root, 'a.env')
load_dotenv(env_file)

# Set environment variables for tests if not set (fallback)
if not os.getenv('DB_HOST'):
    os.environ['DB_HOST'] = 'mysql'
    os.environ['DB_PORT'] = '3306'
    os.environ['DB_NAME'] = 'labo02_db'
    os.environ['DB_USER'] = 'labo02'
    os.environ['DB_PASS'] = 'labo02'
    os.environ['REDIS_HOST'] = 'redis'
    os.environ['REDIS_PORT'] = '6379'
    os.environ['REDIS_DB'] = '0'

from commands.write_order import sync_all_orders_to_redis
from controllers.order_controller import create_order, remove_order
from db import get_redis_conn
from views.report_view import show_highest_spending_users, show_best_sellers

def test_sync_all_orders_to_redis():     
    orders_added = sync_all_orders_to_redis()
    assert orders_added > 0

def test_add_remove_order():
    user_id = 1
    items = [
        {'product_id': 1, 'quantity': 21}
    ]
    order_id = create_order(user_id, items)
    assert isinstance(order_id, int)
    assert order_id > 0

    r = get_redis_conn()
    order_in_redis = r.keys(f"order:{order_id}")
    assert len(order_in_redis) == 1

    removal_status = remove_order(int(order_id))
    assert removal_status == 1

    order_in_redis = r.keys(f"order:{order_id}")
    assert len(order_in_redis) == 0

def test_report_highest_spenders():
    report_html = show_highest_spending_users()
    assert "<!DOCTYPE html>" in report_html
    assert "Les plus gros acheteurs" in report_html

def test_report_best_sellers():
    report_html = show_best_sellers()
    assert "<!DOCTYPE html>" in report_html
    assert "Les articles les plus vendus" in report_html
