# Instructions pour accéder à l'application via PuTTY

## 🎯 Configuration pour VM de l'école avec PuTTY

Si vous utilisez PuTTY pour vous connecter à une VM de l'école (ex: 10.194.32.231), voici la configuration complète pour accéder à votre application Flask.

## ⚙️ 1. Configuration du port dans Docker Compose

Assurez-vous que le fichier `docker-compose.yml` contient la correspondance de port pour le service `store_manager` :

```yaml
services:
  store_manager:
    build: .
    volumes:
      - .:/app
    ports:
      - "5000:5000"  # ← Cette ligne est essentielle !
    environment:
      # ... reste de la configuration
```

## 🔧 2. Configuration du tunnel SSH dans PuTTY

### Étapes détaillées :

1. **Ouvrez PuTTY**

2. **Configurez la connexion principale :**
   - Dans la section **Session** :
     - **Host Name** : `10.194.32.231` (IP de votre VM)
     - **Port** : `22` (port SSH par défaut)
     - **Connection type** : `SSH`

3. **Configurez le tunnel SSH :**
   - Dans le menu de gauche, naviguez à : **Connection → SSH → Tunnels**
   - Dans la section "Add new forwarded port" :
     - **Source port** : `5000`
     - **Destination** : `localhost:5000` (ou `127.0.0.1:5000`)
     - Cochez **Local**
     - Cliquez sur **Add**
   - Vous devriez voir apparaître `L5000 localhost:5000` dans la liste

4. **Sauvegardez votre configuration :**
   - Retournez à **Session**
   - Dans "Saved Sessions", entrez un nom (ex: `VM-École-Tunnel`)
   - Cliquez sur **Save**

5. **Connectez-vous :**
   - Cliquez sur **Open**
   - Entrez vos identifiants de connexion SSH

## 🐳 3. Démarrage de l'application Docker

Une fois connecté à votre VM via PuTTY :

```bash
# Naviguez vers votre projet
cd /chemin/vers/log430-a25-labo2

# Vérifiez d'abord si des conteneurs tournent déjà
docker compose ps

# Si aucun conteneur ne tourne, construisez et démarrez
docker compose build
docker compose up -d

# Vérifiez que les conteneurs sont bien démarrés
docker compose ps
# Vous devriez voir: store_manager avec "0.0.0.0:5000->5000/tcp"

# Vérifiez les logs pour détecter les erreurs
docker compose logs store_manager

# Si tout va bien, testez la connectivité
curl http://localhost:5000
```

## 🌐 4. Accès à l'application

### Méthode recommandée : Via tunnel SSH
1. **Gardez PuTTY ouvert** (le tunnel doit rester actif)
2. **Ouvrez votre navigateur** sur votre ordinateur local
3. **Accédez à** : `http://localhost:5000`
4. **L'application devrait s'afficher !** 🎉

### Méthode alternative : Accès direct (si autorisé)
Si votre école autorise l'accès direct aux ports :
- URL : `http://10.194.32.231:5000`
- ⚠️ Vérifiez d'abord avec l'administrateur réseau

## 🛠️ Dépannage

### Problème : Port mapping manquant dans docker compose ps
Si `docker compose ps` ne montre pas `0.0.0.0:5000->5000/tcp` pour store_manager :

```bash
# Les conteneurs ont été créés avant la modification du docker-compose.yml
# Il faut les recréer :

# Arrêtez tout
docker compose down

# Reconstruisez et redémarrez
docker compose build
docker compose up -d

# Vérifiez que le port mapping apparaît maintenant
docker compose ps
# Vous devriez voir: 0.0.0.0:5000->5000/tcp pour store_manager

# Testez la connexion
curl http://localhost:5000
```
```bash
# Sur la VM, vérifiez si Docker tourne
docker compose ps

# Vérifiez les logs de l'application
docker compose logs store_manager

# Testez la connectivité locale
curl http://localhost:5000

# Vérifiez quel processus utilise le port 5000
ss -tlnp | grep :5000
# ou
sudo lsof -i :5000

# Redémarrez si nécessaire
docker compose restart store_manager
```

### Problème : Tunnel SSH ne fonctionne pas
1. Vérifiez que le tunnel est bien configuré dans PuTTY
2. Reconnectez-vous à PuTTY avec la configuration sauvegardée
3. Vérifiez dans PuTTY Event Log s'il y a des erreurs

### Problème : Port 5000 déjà utilisé localement
```bash
# Windows : Vérifiez qui utilise le port 5000
netstat -ano | findstr :5000

# Si nécessaire, utilisez un autre port local dans PuTTY
# Ex: Source port: 5001, puis accédez à http://localhost:5001
```

### Problème : Pare-feu de la VM
```bash
# Ubuntu/Debian
sudo ufw allow 5000
sudo ufw reload
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

## 📝 Notes importantes

> 🔒 **Sécurité** : Le tunnel SSH chiffre tout le trafic entre votre ordinateur et la VM, ce qui est plus sécurisé qu'un accès direct au port.

> ⏰ **Session active** : Gardez votre session PuTTY ouverte tant que vous utilisez l'application, car elle maintient le tunnel SSH.

> 🔄 **Redémarrage** : Si vous fermez PuTTY, vous devrez le rouvrir avec la même configuration pour rétablir le tunnel.

> 🚫 **Conflit de ports** : Si le port 5000 est utilisé localement, changez le "Source port" dans PuTTY (ex: 5001) et accédez à `http://localhost:5001`.

## ✅ Test de validation

Pour vérifier que tout fonctionne :

1. **PuTTY connecté** avec tunnel SSH ✓
2. **Docker containers running** : `docker compose ps` ✓  
3. **Port accessible** : `curl http://localhost:5000` depuis votre VM ✓
4. **Application accessible** : `http://localhost:5000` depuis votre navigateur local ✓

Bonne utilisation ! 🚀