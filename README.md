# BookWorld — pipeline ETL et API HTTP

Ce projet est un pipeline Python qui transforme des ventes de livres en une synthèse des ventes par pays. Il combine un CSV de ventes, le catalogue public de `books.toscrape.com`, un taux moyen GBP → EUR fourni par Frankfurter et un référentiel SQLite.

Le dépôt contient également une petite API Flask qui expose la table SQLite finale.

> **Confidentialité.** La clé HTTP ne doit jamais être commitée, copiée dans ce README ou publiée dans une commande partagée. Le fichier `api.py` fourni contient actuellement une clé codée en dur : remplacez-la par une valeur locale ou, de préférence, adaptez le code pour la lire depuis une variable d’environnement avant tout déploiement.

## Sommaire

- [Architecture et fonctionnement](#architecture-et-fonctionnement)
- [Fichiers](#fichiers)
- [Installation](#installation)
- [Préparer les fichiers](#préparer-les-fichiers)
- [Exécuter le pipeline](#exécuter-le-pipeline)
- [Démarrer l’API](#démarrer-lapi)
- [Référence HTTP](#référence-http)
- [Résultats fournis](#résultats-fournis)
- [Écarts du schéma](#écarts-du-schéma)
- [Limites et points connus](#limites-et-points-connus)

## Architecture et fonctionnement

Le pipeline `pipeline.py` suit ces étapes :

1. lecture de `sales_raw.csv` ;
2. conversion de `order_date` et suppression des prénoms et noms clients ;
3. scraping de la page d’accueil de `https://books.toscrape.com/` ;
4. récupération du taux moyen GBP → EUR pour l’année 2025 auprès de Frankfurter ;
5. exécution des trois requêtes de `queries.sql` sur `bookworld_reference.db` ;
6. calcul des revenus GBP/EUR et des coûts d’acquisition ;
7. agrégation par pays ;
8. remplacement de la table `sales_by_country` dans `bookworld_final.db`.

Le pipeline utilise des chemins relatifs : lancez-le depuis le répertoire qui contient les fichiers du projet.

## Fichiers

| Fichier | Rôle |
|---|---|
| `pipeline.py` | Pipeline ETL complet : extraction, enrichissement, agrégation et chargement SQLite. |
| `api.py` | Application Flask servant la santé de l’API et les ventes par pays. |
| `sales_raw.csv` | Données brutes de ventes ; le fichier fourni contient 240 lignes et 10 colonnes, dont des données nominatives supprimées par le pipeline. |
| `queries.sql` | Trois requêtes exécutées sur le référentiel : pays, règles/canaux actifs et coûts des canaux actifs. |
| `bookworld_reference.db` | Référentiel SQLite avec `countries`, `channels` et `category_rules`. |
| `bookworld_final.db` | Base SQLite de sortie avec `sales_by_country`. |
| `schema_final.sql` | Schéma SQL documentaire fourni ; il ne correspond pas exactement aux bases SQLite ni aux tables effectivement écrites par Python. |


## Installation

Python 3.9 ou supérieur est recommandé. Depuis la racine du projet :

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell : .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install pandas requests beautifulsoup4 Flask
```
Pour figer ensuite l’environnement installé :

```bash
python -m pip freeze > requirements.txt
```

## Préparer les fichiers

Exécutez depuis le répertoire où vous les avez copiés :

```bash
cp 'pipeline.py' pipeline.py
cp 'queries.sql' queries.sql
cp 'schema_final.sql' schema_final.sql
cp 'sales_raw.csv' sales_raw.csv
cp 'bookworld_final.db' bookworld_final.db
```

Conservez `bookworld_reference.db` sous ce nom. L’API ouvre également exactement `bookworld_final.db` dans son répertoire courant.

Sous Windows PowerShell, l’équivalent est :

```powershell
Copy-Item 'pipeline.py' pipeline.py
Copy-Item 'queries.sql' queries.sql
Copy-Item 'schema_final.sql' schema_final.sql
Copy-Item 'sales_raw.csv' sales_raw.csv
Copy-Item 'bookworld_final.db' bookworld_final.db
```

## Exécuter le pipeline

Depuis la racine contenant `pipeline.py`, `sales_raw.csv`, `queries.sql` et `bookworld_reference.db` :

```bash
python pipeline.py
```

Le script dépend d’Internet pour le scraping et le taux de change. Il écrit ou remplace `bookworld_final.db` et sa table `sales_by_country`.

Vérifier la sortie :

```bash
python - <<'PY'
import sqlite3
with sqlite3.connect("bookworld_final.db") as con:
    print(con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
    print(con.execute("SELECT * FROM sales_by_country LIMIT 5").fetchall())
PY
```

La table finale attendue contient les colonnes suivantes :

- `country_code`
- `country_name`
- `total_orders`
- `total_quantity`
- `total_revenue_gbp`
- `total_revenue_eur`

## Démarrer l’API

L’API fournie est Flask, avec `app = Flask(__name__)`, et démarre via le bloc principal de `api.py` :

```bash
python api.py
```

Le serveur écoute par défaut sur `http://127.0.0.1:5000`. Lancez la commande depuis le répertoire contenant `api.py` et `bookworld_final.db`.

La commande équivalente avec Flask est :

```bash
python -m flask --app api:app run
```

Le code appelle `app.run(debug=False)` lorsqu’il est lancé directement : le mode debug n’est donc pas activé par cette commande.

## Référence HTTP

### Authentification

`api.py` exécute `check_api_key()` avant **chaque** requête. L’authentification attend exactement une **clé dans le paramètre de requête `api_key`** :

```text
?api_key=<CLE_CONFIGUREE_LOCALEMENT>
```

Le code fourni n’attend pas de header `Authorization` et ne lit pas de header `X-API-Key`. Toute requête sans clé, ou avec une clé incorrecte, renvoie HTTP `401 Unauthorized`.

Exemples sans exposer de secret :

```bash
# Remplacez la valeur uniquement dans votre terminal local.
export BOOKWORLD_API_KEY='<CLE_CONFIGUREE_DANS_API_PY>'

curl -i "http://127.0.0.1:5000/health?api_key=${BOOKWORLD_API_KEY}"
curl -i "http://127.0.0.1:5000/sales-by-country?api_key=${BOOKWORLD_API_KEY}"
```

`BOOKWORLD_API_KEY` n’est pas lu automatiquement par le code actuel : cette variable sert seulement à éviter d’écrire la valeur dans l’historique de commande. Pour une vraie configuration par environnement, modifiez `api.py` avant déploiement. Ne publiez jamais la valeur de la clé.

### Routes

| Méthode et route | Succès | Description |
|---|---|---|
| `GET /health?api_key=...` | `200` et `{"status":"ok"}` | Vérifie que l’application répond. |
| `GET /sales-by-country?api_key=...` | `200` et un tableau JSON | Retourne les lignes de `sales_by_country`, triées par `total_revenue_gbp` décroissant. |

La route `/sales-by-country` sélectionne exactement `country_code`, `country_name`, `total_orders`, `total_quantity`, `total_revenue_gbp` et `total_revenue_eur`. Les réponses sont produites par `Flask.jsonify`.

Exemples de réponses de succès :

```json
{"status": "ok"}
```

```json
[
  {
    "country_code": "FR",
    "country_name": "France",
    "total_orders": 1,
    "total_quantity": 2,
    "total_revenue_gbp": 20.0,
    "total_revenue_eur": 23.4
  }
]
```

L’exemple de ligne est illustratif : les valeurs réelles dépendent de la base chargée et ne doivent pas être interprétées comme un résultat vérifié. Si `bookworld_final.db` est absent, si la table n’existe pas ou si SQLite ne peut pas l’ouvrir, l’API renverra une erreur serveur au lieu d’une réponse métier.

## Clé d’API HTTP

**Clé d’API HTTP** : secret applicatif utilisé par `api.py` pour autoriser les appels aux routes Flask. Avec le code actuel, elle passe dans le paramètre `api_key` de l’URL. Elle ne doit pas être commitée ni mise dans ce README.

## Résultats fournis


- `sales_raw.csv` : 240 lignes de données et 10 colonnes ;
- `bookworld_reference.db` : 3 tables (`countries`, `channels`, `category_rules`) ; respectivement 10, 4 et 10 lignes ;
- `bookworld_final.db` : 1 table `sales_by_country` contenant 8 lignes ;
- `sales_by_country` : 6 colonnes, avec des montants en `REAL` et des agrégats numériques.

Le CSV contient les canaux `WEB`, `APP` et `MKT` et 8 codes pays observés. `queries.sql` ajoute conditionnellement les Pays-Bas si le code `NL` n’existe pas, sélectionne les règles et canaux actifs, puis les coûts des canaux actifs.

## Schéma

<img width="1527" height="849" alt="image" src="https://github.com/user-attachments/assets/c869931f-db08-4f9a-a7ac-c5ce32e662ba" />



