from flask import Flask, jsonify
import csv
import os
from collections import Counter

app = Flask(__name__)
CSV_FILE = "logs/attacks.csv"

def get_attack_data():
    attacks = []
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    attacks.append(row)
        except Exception as e:
            print(f"Error reading CSV: {e}")
    return attacks

@app.route("/api/stats")
def stats():
    attacks = get_attack_data()
    
    total_attacks = len(attacks)
    countries = [a["Country"] for a in attacks if a.get("Country")]
    top_country = Counter(countries).most_common(1)[0][0] if countries else "None"
    
    response = jsonify({
        "total": total_attacks,
        "top_country": top_country,
        "attacks": attacks[::-1]
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5001)