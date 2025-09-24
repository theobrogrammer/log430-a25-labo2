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

### Problème : Port 3306 déjà utilisé (MySQL)
Si vous obtenez l'erreur "Bind for 0.0.0.0:3306 failed: port is already allocated" :

```bash
# Option 1: Arrêter le MySQL système (temporairement)
sudo systemctl stop mysql
# ou
sudo service mysql stop

# Puis redémarrer les conteneurs
docker compose up -d

# Option 2: Si le port a été changé à 3307 dans docker-compose.yml
# Rien à faire de spécial, juste relancer
docker compose down
docker compose up -d

# Vérifiez que tout fonctionne
docker compose ps
curl http://localhost:5000
```
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

## 🔍 **Comment ça fonctionne : Explication technique**

### **Le chemin complet de votre requête :**

```
[Votre navigateur Windows] 
    ↓ http://localhost:5000
[Tunnel SSH PuTTY]
    ↓ Redirige vers la VM (10.194.32.231:5000)
[VM École - Port 5000]
    ↓ Docker port mapping
[Conteneur Docker store_manager - Port 5000]
    ↓ Application Flask
[Application Web] 🎯
```

### **Les ports et leur rôle :**

**1. Port 5000 sur votre Windows (localhost:5000) :**
- C'est un **port virtuel** créé par le tunnel SSH PuTTY
- Quand vous tapez `localhost:5000`, PuTTY intercepte cette connexion
- PuTTY la redirige automatiquement vers la VM via le tunnel SSH chiffré

**2. Port 5000 sur la VM (10.194.32.231:5000) :**
- C'est le **port physique** sur la machine virtuelle de l'école
- Docker mappe ce port vers le conteneur
- Configuration dans `docker-compose.yml` : `"5000:5000"`

**3. Port 5000 dans le conteneur Docker :**
- C'est là où l'application Flask écoute réellement
- L'application Flask est configurée pour écouter sur `0.0.0.0:5000` (toutes les interfaces)
- Cela permet au trafic venant de l'extérieur du conteneur d'atteindre l'app

### **Pourquoi le tunnel SSH est génial :**

**Sécurité :**
- Tout le trafic entre votre Windows et la VM est **chiffré** via SSH
- Même si quelqu'un écoute le réseau, il ne peut pas voir vos données
- Pas besoin d'ouvrir des ports dangereux sur le pare-feu de l'école

**Simplicité :**
- Vous accédez à `localhost:5000` comme si l'app tournait localement
- Mais en réalité elle tourne sur la VM distante
- PuTTY fait toute la magie de redirection en arrière-plan

### **Schéma récapitulatif :**

```
┌─────────────────┐    SSH Tunnel    ┌─────────────────┐    Docker    ┌─────────────────┐
│  Votre Windows  │ ◄─────────────► │   VM École      │ ◄─────────► │  Conteneur      │
│  localhost:5000 │                 │ 10.194.32.231   │             │  Flask App      │
│                 │                 │      :5000      │             │      :5000      │
└─────────────────┘                 └─────────────────┘             └─────────────────┘
        ↑                                   ↑                               ↑
    Navigateur                         Port mapping                    Application
```

### **En résumé :**
1. **PuTTY** : Crée un tunnel sécurisé Windows ↔ VM
2. **Docker port mapping** : Expose le conteneur sur la VM  
3. **Flask app** : Écoute dans le conteneur et répond aux requêtes

Cette architecture est **sécurisée, flexible et professionnelle** - exactement comme les développeurs accèdent à des applications sur des serveurs distants dans le monde professionnel ! 🚀

Bonne utilisation ! 🚀