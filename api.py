from flask import Flask, jsonify, request, abort
import pandas as pd
import sqlite3

FINAL_TABLE_NAME = "sales_by_country"
API_KEY = "secret123"

app = Flask(__name__)


@app.before_request
def check_api_key():
    if request.args.get("api_key") != API_KEY:
        abort(401)


def run_query(query):
    conn = sqlite3.connect("bookworld_final.db")
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/sales-by-country", methods=["GET"])
def sales_by_country():
    query = f"""
    SELECT
        country_code,
        country_name,
        total_orders,
        total_quantity,
        total_revenue_gbp,
        total_revenue_eur
    FROM {FINAL_TABLE_NAME}
    ORDER BY total_revenue_gbp DESC
    """
    df = run_query(query)
    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=False)
