"""
USer (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from db import get_sqlalchemy_session
from models.user import User

def get_user_by_id(user_id):
    """Get user by ID """
    session = get_sqlalchemy_session()
    return session.query(User).filter_by(id=user_id).all()

