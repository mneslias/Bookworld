import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup

def extract():
    try :
        sales = pd.read_csv("sales_raw.csv")
        print("CSV chargé avec succès.")
        return sales
    except FileNotFoundError as e :
        print(f"Fichier CSV introuvable : {e}")
    
    except pd.errors.ParserError as e :
        print(f"Le format du CSV est incorrect : {e}")

def scrap():
    url = "https://books.toscrape.com/"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP : {e}")

    else:
        try:
            soup = BeautifulSoup(response.text, "html.parser")

            livres = [
                {
                    "titre": livre.select_one("h3 a").get("title"),
                    "prix_en_livres": float(livre.select_one(".price_color").get_text(strip=True).replace("Â£", "").replace("£", ""))
                }
                for livre in soup.select("article.product_pod")
                if livre.select_one("h3 a") and livre.select_one(".price_color")
                     ]

            if livres:
                print(f"Scraping réussi : {len(livres)} livres récupérés.")
                print(livres)
                return livres
            else:
                print(
                    "Aucun titre ou prix trouvé. "
                    "La structure de la page a peut-être changé."
                )

        except Exception as e:
            print(f"Erreur lors de l'analyse du HTML : {e}")


def charger_requetes_sql():
    try:
        with open("queries.sql", "r", encoding="utf-8") as fichier:
            contenu = fichier.read()

        resultats = []

        with sqlite3.connect("bookworld_reference.db") as conn:
            for requete in contenu.split(";"):
                if requete.strip():
                    resultats.append(pd.read_sql_query(requete, conn))

        print(f"Chargement terminé : {len(resultats)} requête(s) exécutée(s).")
        return resultats

    except FileNotFoundError:
        print("Erreur : le fichier queries.sql est introuvable.")
        return []


def recuperer_taux_moyen_2025():
    url = "https://api.frankfurter.dev/v2/rates?from=2025-01-01&to=2025-12-31&base=GBP&quotes=EUR"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        taux_liste = [item["rate"] for item in data]

        return sum(taux_liste) / len(taux_liste)

    except (requests.exceptions.RequestException, KeyError, ZeroDivisionError) as e:
        print(f"Erreur : {e}")
        return None


def creer_dataframe_livres(taux_gbp_eur):
    livres = scrap()

    if not livres:
        print("Aucun livre à convertir.")
        return pd.DataFrame()

    df_livres = pd.DataFrame(livres)

    print("Taux récupéré :", taux_gbp_eur)
    print("Colonnes avant conversion :", df_livres.columns.tolist())

    if taux_gbp_eur is None:
        return df_livres

    df_livres["prix_en_euros"] = (
        df_livres["prix_en_livres"] * taux_gbp_eur
    ).round(2)

    return df_livres


def convertir_cout_acquisition(channels_category, taux_gbp_eur):

    if taux_gbp_eur is None:
        return channels_category

    channels_category["acquisition_cost_eur"] = (
        channels_category["acquisition_cost_gbp"] * taux_gbp_eur
    ).round(2)

    return channels_category


def nettoyage():

    sales_raw = extract() 

    sales_raw["order_date"] = pd.to_datetime(sales_raw["order_date"])
    sales_raw = sales_raw.drop(
        columns=["customer_first_name", "customer_last_name"]
    )

    return sales_raw


def ajouter_revenus(sales_raw, df_livres, channels_category, taux_gbp_eur):

    sales = sales_raw.merge(
        df_livres[["titre", "prix_en_livres", "prix_en_euros"]],
        left_on="book_name",
        right_on="titre",
        how="left"
    )

    sales["total_revenue_livres"] = (
        sales["prix_en_livres"]
        * sales["quantity"]
        * (1 - sales["discount_rate"])
    )

    sales["total_revenue_euros"] = (
        sales["prix_en_euros"]
        * sales["quantity"]
        * (1 - sales["discount_rate"])
    )

    sales = sales.merge(
        channels_category[["channel_code", "acquisition_cost_gbp"]],
        on="channel_code",
        how="left"
    )

    sales["acquisition_cost_eur"] = (
        sales["acquisition_cost_gbp"] * taux_gbp_eur
    ).round(2)

    sales["net_revenue_gbp"] = (
        sales["total_revenue_livres"] - sales["acquisition_cost_gbp"]
    )

    sales["net_revenue_eur"] = (
        sales["total_revenue_euros"] - sales["acquisition_cost_eur"]
    )

    return sales.drop(columns="titre")

def creer_sales_by_country(sales_raw, countries_actifs):
    sales_with_country = sales_raw.merge(
        countries_actifs[["country_code", "country_name"]],
        on="country_code",
        how="left",
        validate="many_to_one"
    )

    sales_by_country = (
        sales_with_country
        .groupby(["country_code", "country_name"], as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_quantity=("quantity", "sum"),
            total_revenue_gbp=("total_revenue_livres", "sum"),
            total_revenue_eur=("total_revenue_euros", "sum")
        )
    )

    return sales_by_country


def load(sales_by_country):
    FINAL_TABLE_NAME = "sales_by_country"

    conn = sqlite3.connect("bookworld_final.db")

    sales_by_country.to_sql(
        FINAL_TABLE_NAME,
        conn,
        if_exists="replace",
        index=False,
    )

    check_df = pd.read_sql_query(
        f"SELECT * FROM {FINAL_TABLE_NAME} LIMIT 5",
        conn,
    )
    columns_df = pd.read_sql_query(
        f"PRAGMA table_info({FINAL_TABLE_NAME})",
        conn,
    )

    conn.close()

    print(f"Table SQLite créée : {FINAL_TABLE_NAME}")
    print("\nAperçu des données enregistrées :")
    print(check_df)

    print("\nColonnes de la table :")
    print(columns_df[["name", "type"]])

def main():
    resultats = charger_requetes_sql()

    countries_actifs = resultats[0]
    channels_category = resultats[1]

    taux_gbp_eur = recuperer_taux_moyen_2025()

    sales_raw = nettoyage()

    df_livres = creer_dataframe_livres(taux_gbp_eur)

    channels_category = convertir_cout_acquisition(channels_category, taux_gbp_eur)

    sales_raw = ajouter_revenus(
        sales_raw,
        df_livres,
        channels_category,
        taux_gbp_eur
    )

    sales_by_country = creer_sales_by_country(
        sales_raw,
        countries_actifs
    )

    print(sales_by_country)

    load(sales_by_country)


if __name__ == "__main__":
    main()
    
