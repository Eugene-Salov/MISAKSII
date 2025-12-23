from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# === HTML-шаблон (адаптивный) ===
TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>🌍 Страны мира</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(to bottom right, #e0eafc, #cfdef3);
            color: #333;
        }
        header {
            background: #1a73e8;
            color: white;
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            margin: 0;
            font-size: 1.8rem;
        }
        main {
            padding: 20px;
            max-width: 1000px;
            margin: 0 auto;
        }
        form {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        label {
            margin: 5px 10px;
            font-weight: 500;
        }
        input, select, button {
            margin: 5px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 1rem;
        }
        button {
            background-color: #1a73e8;
            color: white;
            cursor: pointer;
            border: none;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #155ab6;
        }
        table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background: #1a73e8;
            color: white;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background: #f9f9f9;
        }
        img {
            width: 50px;
            border-radius: 4px;
        }

        /* 📱 Адаптивный дизайн */
        @media (max-width: 768px) {
            form {
                flex-direction: column;
                align-items: stretch;
            }
            input, select, button {
                width: 100%;
            }
            table, th, td {
                font-size: 0.9rem;
            }
            img {
                width: 40px;
            }
        }

        @media (max-width: 480px) {
            h1 { font-size: 1.4rem; }
            th, td { padding: 6px; }
            img { width: 35px; }
        }
    </style>
</head>
<body>
    <header>
        <h1>🌍 Информация о странах</h1>
    </header>

    <main>
        <form method="GET" action="/">
            <label>Регион:</label>
            <select name="region">
                <option value="">— Все регионы —</option>
                {% for r in regions %}
                    <option value="{{ r }}" {% if r == selected_region %}selected{% endif %}>{{ r }}</option>
                {% endfor %}
            </select>

            <label>или страна:</label>
            <input type="text" name="country" value="{{ country or '' }}" placeholder="Введите название страны">

            <button type="submit">Поиск</button>
        </form>

        {% if countries %}
            <table>
                <tr>
                    <th>Флаг</th>
                    <th>Название</th>
                    <th>Столица</th>
                    <th>Регион</th>
                    <th>Население</th>
                    <th>Языки</th>
                    <th>Валюта</th>
                </tr>
                {% for c in countries %}
                <tr>
                    <td><img src="{{ c['flag'] }}"></td>
                    <td>{{ c['name'] }}</td>
                    <td>{{ c['capital'] }}</td>
                    <td>{{ c['region'] }}</td>
                    <td>{{ c['population'] }}</td>
                    <td>{{ c['languages'] }}</td>
                    <td>{{ c['currencies'] }}</td>
                </tr>
                {% endfor %}
            </table>
        {% elif country or selected_region %}
            <p style="text-align:center; margin-top:20px; font-weight:bold;">❌ Ничего не найдено.</p>
        {% endif %}
    </main>
</body>
</html>
"""

# === Функции для работы с API ===

def get_all_countries():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,region,population,languages,currencies,flags"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

def get_countries_by_region(region):
    url = f"https://restcountries.com/v3.1/region/{region}?fields=name,capital,region,population,languages,currencies,flags"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

def search_country(name):
    url = f"https://restcountries.com/v3.1/name/{name}?fields=name,capital,region,population,languages,currencies,flags"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

def format_country_data(data):
    formatted = []
    for c in data:
        formatted.append({
            "name": c["name"]["common"],
            "capital": ", ".join(c.get("capital", ["—"])),
            "region": c.get("region", "—"),
            "population": f"{c.get('population', 0):,}".replace(",", " "),
            "languages": ", ".join(c.get("languages", {}).values()) or "—",
            "currencies": ", ".join(c.get("currencies", {}).keys()) or "—",
            "flag": c.get("flags", {}).get("png", "")
        })
    return formatted

@app.route("/", methods=["GET"])
def index():
    regions = ["Africa", "Americas", "Asia", "Europe", "Oceania"]
    region = request.args.get("region", "")
    country = request.args.get("country", "").strip()
    countries = []

    if country:
        data = search_country(country)
        countries = format_country_data(data)
    elif region:
        data = get_countries_by_region(region)
        countries = format_country_data(data)

    return render_template_string(
        TEMPLATE,
        regions=regions,
        countries=countries,
        selected_region=region,
        country=country
    )

if __name__ == "__main__":
    app.run()

