BookWorld — pipeline de ventes et API
Ce projet charge des ventes brutes, enrichit les données avec les livres de Books to Scrape, convertit les prix GBP en EUR via l'API Frankfurter, puis agrège le chiffre d'affaires par pays dans SQLite. Une API Flask expose ensuite les résultats.
Fonctionnement

sales_raw.csv est lu par pipeline.py.
Les colonnes order_date sont converties en dates et les noms/prénoms clients sont supprimés.
Les livres et leurs prix en livres sterling sont récupérés depuis books.toscrape.com.
Le taux GBP → EUR est récupéré depuis https://api.frankfurter.dev/v2/rate/gbp/eur.
Les pays actifs et les règles de catégories/canaux actifs sont lus dans bookworld_reference.db par les requêtes de queries.sql.
Les revenus bruts, coûts d'acquisition et revenus nets sont calculés au niveau des ventes.
Les résultats sont regroupés par pays puis écrits dans la table sales_by_country de bookworld_final.db.

Le pipeline dépend donc de deux services externes accessibles sur le réseau. Les fonctions de scraping et de taux disposent d'une gestion d'erreur.
Pré-requis

Python 3.9 ou plus récent recommandé.
Accès réseau sortant vers books.toscrape.com et api.frankfurter.dev pour exécuter le pipeline complet.
SQLite.

Installation
Depuis la racine du projet, là où se trouvent pipeline.py, sales_raw.csv, queries.sql et les bases SQLite :
python3 -m venv .venv
source .venv/bin/activate       # Windows : .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install pandas requests beautifulsoup4 flask
Le code importe les modules Python suivants : pandas, requests, bs4 (beautifulsoup4), flask et sqlite3 (bibliothèque standard).
Exécuter le pipeline
Le répertoire courant doit être la racine du projet, car le script ouvre les fichiers avec des chemins relatifs :
cd /chemin/vers/bookworld
source .venv/bin/activate
python pipeline.py
Le pipeline affiche notamment le nombre de livres récupérés, les données agrégées et un aperçu de la table créée. À la fin, bookworld_final.db contient ou remplace la table sales_by_country (if_exists="replace").
Vérifier le résultat
sqlite3 bookworld_final.db \
  'SELECT country_code, country_name, total_orders, total_quantity, total_revenue_gbp, total_revenue_eur FROM sales_by_country ORDER BY total_revenue_gbp DESC;'
La base finale fournie contient actuellement 6 lignes : BE, DE, ES, FR, IE et IT. Le CSV source contient 240 lignes, avec les pays BE, DE, ES, FR, IE, IT, NL, PT et les canaux APP, MKT et WEB. Les lignes dont le pays n'est pas actif ou dont le pays n'est pas renvoyé par la requête de pays actifs ne contribuent pas à l'agrégat final.
Calculs principaux
Pour chaque vente :
revenu_gbp = prix_en_livres × quantity × (1 - discount_rate)
revenu_eur = prix_en_euros × quantity × (1 - discount_rate)
coût_acquisition_eur = acquisition_cost_gbp × taux_gbp_eur
revenu_net_gbp = revenu_gbp - acquisition_cost_gbp
revenu_net_eur = revenu_eur - coût_acquisition_eur
Les totaux exposés par l'API sont les commandes distinctes, la quantité totale et les revenus totaux GBP/EUR. Le code ne charge pas les lignes détaillées dans la base finale : seule l'agrégation par pays est persistée.
Lancer l'API
L'API lit la table sales_by_country de bookworld_final.db. Exécutez-la depuis la racine du projet, après avoir généré ou conservé cette table :
cd /chemin/vers/bookworld
source .venv/bin/activate
python api.py
Le serveur Flask est configuré dans le code avec debug=True et écoute par défaut sur http://127.0.0.1:5000.
Exemples — la clé est requise pour les deux routes, y compris /health :
curl "http://127.0.0.1:5000/health?api_key=secret123"
curl "http://127.0.0.1:5000/sales-by-country?api_key=secret123"
Réponse de santé attendue :
{"status":"ok"}
GET /sales-by-country renvoie un tableau JSON trié par total_revenue_gbp décroissant, avec les champs country_code, country_name, total_orders, total_quantity, total_revenue_gbp et total_revenue_eur.
Authentification et sécurité
L'API utilise une clé API simple :

La clé configurée dans le code est secret123.
Elle est transmise dans le paramètre d'URL api_key.
La fonction @app.before_request vérifie la clé pour toutes les routes, y compris /health.
Une clé absente ou incorrecte entraîne une réponse 401 Unauthorized.

Pour un projet réel, évitez de conserver une vraie clé dans le code ou de la transmettre dans l'URL : les URL peuvent être enregistrées dans l'historique du navigateur ou dans les journaux serveur. Préférez une variable d'environnement pour stocker la clé et un en-tête HTTP pour la transmettre. Si l'API est publiée au-delà de la machine locale, utilisez également HTTPS et désactivez le mode debug.
Description des fichiers
Copier le tableau


Fichier
Rôle



pipeline.py
Pipeline ETL complet : extraction du CSV, scraping des livres, conversion GBP/EUR, enrichissement, agrégation par pays et écriture de bookworld_final.db.


api.py
Application Flask avec /health et /sales-by-country, lecture seule de la table finale.


queries.sql
Deux requêtes exécutées sur bookworld_reference.db : pays actifs ; règles de catégories actives jointes aux canaux actifs.


sales_raw.csv
Source de ventes brutes : 240 lignes et 10 colonnes, dont commande, date, livre, pays, canal, quantité, remise et identité client.


bookworld_reference.db
Référentiel SQLite avec les tables countries, channels et category_rules.


bookworld_final.db
Base SQLite de sortie ; la version fournie contient la table agrégée sales_by_country.


schema_final.sql
Schéma SQL documentaire/exporté décrivant des tables de ventes, canaux, pays et agrégats. Il n'est pas appelé par pipeline.py et sa syntaxe/types ressemblent à un export MySQL, contrairement aux bases SQLite utilisées à l'exécution.


Schéma des relations
Le flux logique réellement utilisé par le code est le suivant :
<img width="764" height="425" alt="schema_bases" src="https://github.com/user-attachments/assets/56c16204-0896-4659-b422-6005b264f7b4" />

Relations déclarées dans schema_final.sql — à considérer comme de la documentation, et non comme le schéma SQLite effectivement créé par le pipeline :

sales_raw.country_code → countries_actifs.country_code ;
sales_raw.channel_code → channels_category.channel_code ;
countries_actifs.country_code → sales_by_country.country_code.

En pratique, pipeline.py ne crée pas les tables sales_raw, channels_category ou countries_actifs. Il lit les tables de référence existantes (countries, channels, category_rules) et crée uniquement sales_by_country avec pandas.DataFrame.to_sql.
Résultats différents
Les prix du catalogue et le taux de change sont récupérés en ligne au moment de l'exécution : les valeurs peuvent donc varier. La base finale fournie est un instantané et peut différer d'une nouvelle exécution.
