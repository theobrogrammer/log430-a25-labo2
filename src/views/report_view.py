"""
Report view
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from views.template_view import get_template, get_param
from controllers.product_controller import get_best_selling_products

def show_highest_spending_users():
    """ Show report of highest spending users """
    return get_template("<h2>Les plus gros acheteurs</h2><p>(TODO: Liste avec nom, total depensé)</p>")

def show_best_sellers():
    """ Show report of best selling products """
    try:
        # Récupérer les données depuis le contrôleur
        best_sellers = get_best_selling_products()
        
        # Gestion des erreurs
        if isinstance(best_sellers, str):
            # Le contrôleur a retourné une erreur
            return get_template(f"""
                <h2>Les articles les plus vendus</h2>
                <div class="alert alert-danger">
                    {best_sellers}
                </div>
                <a href="/">← Retour</a>
            """)
        
        # Générer le HTML pour le tableau
        if not best_sellers:
            rows_html = "<tr><td colspan='3'>Aucune donnée de vente disponible</td></tr>"
        else:
            rows = []
            for product_id, quantity_sold in best_sellers:
                rows.append(f"""
                    <tr>
                        <td>{product_id}</td>
                        <td>{quantity_sold}</td>
                        <td>Produit #{product_id}</td>
                    </tr>
                """)
            rows_html = "".join(rows)
        
        return get_template(f"""
            <h2>Les articles les plus vendus</h2>
            <p>Rapport basé sur les données Redis en temps réel</p>
            <table class="table">
                <tr>
                    <th>ID Produit</th>
                    <th>Quantité vendue</th>
                    <th>Nom</th>
                </tr>
                {rows_html}
            </table>
            <a href="/">← Retour</a>
        """)
        
    except Exception as e:
        print(f"Erreur dans show_best_sellers: {e}")
        return get_template(f"""
            <h2>Les articles les plus vendus</h2>
            <div class="alert alert-danger">
                Erreur lors de l'affichage du rapport: {str(e)}
            </div>
            <a href="/">← Retour</a>
        """)