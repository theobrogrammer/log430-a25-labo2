# Configuration des Secrets GitHub pour CI/CD

Pour que le pipeline CI/CD fonctionne avec votre VM, vous devez configurer les secrets suivants dans GitHub.

## 🔧 Configuration des Secrets GitHub

### 1. Accéder aux paramètres du repository
- Allez sur votre repository GitHub
- Cliquez sur **Settings** (en haut à droite)
- Dans le menu de gauche, cliquez sur **Secrets and variables** → **Actions**

### 2. Ajouter les secrets suivants

#### **VM_HOST**
- **Nom** : `VM_HOST`
- **Valeur** : `10.194.32.231` (l'IP de votre VM de l'école)

#### **VM_USER** 
- **Nom** : `VM_USER`
- **Valeur** : `log430` (votre nom d'utilisateur SSH)

#### **VM_SSH_PRIVATE_KEY**
- **Nom** : `VM_SSH_PRIVATE_KEY`
- **Valeur** : Votre clé privée SSH (voir instructions ci-dessous)

## 🔑 Générer et configurer la clé SSH

### Sur votre machine Windows :

```powershell
# Générer une paire de clés SSH spécifique pour le CI/CD
ssh-keygen -t rsa -b 4096 -C "github-actions@youremail.com" -f github-actions-key

# Cela créera deux fichiers :
# - github-actions-key (clé privée)
# - github-actions-key.pub (clé publique)
```

### Copier la clé publique sur votre VM :

```powershell
# Via PuTTY ou scp, copiez le contenu de github-actions-key.pub
# et ajoutez-le au fichier ~/.ssh/authorized_keys sur votre VM
```

### Sur votre VM via PuTTY :

```bash
# Créer le dossier SSH si nécessaire
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Ajouter la clé publique aux clés autorisées
echo "CONTENU_DE_VOTRE_CLE_PUBLIQUE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Vérifier les permissions
ls -la ~/.ssh/
```

### Ajouter la clé privée dans GitHub :

1. Ouvrez le fichier `github-actions-key` (clé privée)
2. Copiez tout le contenu (de `-----BEGIN OPENSSH PRIVATE KEY-----` à `-----END OPENSSH PRIVATE KEY-----`)
3. Ajoutez-le comme secret `VM_SSH_PRIVATE_KEY` dans GitHub

## 🚀 Pipeline CI/CD Expliqué

Le pipeline comprend 3 jobs principaux :

### **1. Test (ubuntu-latest)**
- ✅ Lance MySQL et Redis comme services
- ✅ Installe les dépendances Python
- ✅ Crée le fichier .env
- ✅ Exécute les tests avec pytest
- ✅ Génère un rapport de couverture

### **2. Build (ubuntu-latest)**
- 🐳 Construit l'image Docker
- 🧪 Teste que l'image fonctionne
- 📦 Sauvegarde l'image comme artifact

### **3. Deploy (ubuntu-latest → VM)**
- 🚀 Se connecte à votre VM via SSH
- 📁 Upload les fichiers et l'image Docker
- 🔄 Redémarre les conteneurs avec `docker compose`
- ✅ Vérifie que le déploiement fonctionne

## 🔗 Accès à l'application après déploiement

Une fois déployé, l'application sera accessible :

### Via tunnel SSH (recommandé) :
```bash
ssh -L 5000:localhost:5000 log430@10.194.32.231
# Puis accédez à http://localhost:5000 dans votre navigateur
```

### Directement (si autorisé par l'école) :
```
http://10.194.32.231:5000
```

## 🛠️ Dépannage

### Si le pipeline échoue :

1. **Échec de connexion SSH** :
   - Vérifiez que la clé privée est correcte dans les secrets
   - Testez la connexion manuellement : `ssh log430@10.194.32.231`

2. **Échec des tests** :
   - Vérifiez les logs du job "Test"
   - Assurez-vous que les services MySQL/Redis démarrent

3. **Échec du déploiement** :
   - Vérifiez que Docker est installé sur la VM
   - Vérifiez les logs : `ssh log430@10.194.32.231 "docker compose logs"`

## 🔄 Workflow automatique

Une fois configuré :
- ✅ **Push sur main** → Tests + Build + Déploiement automatique
- ✅ **Pull Request** → Tests seulement
- ✅ **Notifications** en cas de succès/échec

Votre application sera automatiquement déployée sur votre VM à chaque push ! 🎉