from flask import Flask, render_template, request
import folium
import json
import os

app = Flask(__name__, template_folder='templates')

def load_battles():
    file_path = os.path.join(app.static_folder, 'battles.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print("Opened")
            return json.load(f)
    except FileNotFoundError:
        print('Not found')
        return []

@app.route('/')
def index():
    return render_template('main_page.html')

@app.route('/wikipedia')
def wikipedia():
    return render_template('wikipedia.html')

@app.route('/map', methods=['GET', 'POST'])
def map_view():
    m = folium.Map(location=[49.5, 31.5], zoom_start=6)

    battles = load_battles()


    selected_start_year = request.form.get('start_year')
    selected_end_year = request.form.get('end_year')
    selected_period = request.form.get('period')

    if selected_start_year and selected_end_year:
        battles = [battle for battle in battles if int(selected_start_year) <= battle['year'] <= int(selected_end_year)]
    elif selected_start_year:
        battles = [battle for battle in battles if battle['year'] >= int(selected_start_year)]
    elif selected_end_year:
        battles = [battle for battle in battles if battle['year'] <= int(selected_end_year)]

    if selected_period:
        battles = [battle for battle in battles if battle.get('period') == selected_period]

    for battle in battles:
        if battle.get('latitude') and battle.get('longitude'):
            folium.Marker(
                location=[battle['latitude'], battle['longitude']],
                popup=f"<strong>{battle['name']}</strong><br>Рік: {battle['year']}<br>{battle['info']}",
                tooltip=battle['name']
            ).add_to(m)

    map_html = m._repr_html_()

    return render_template('map.html', map_html=map_html, selected_start_year=selected_start_year, selected_end_year=selected_end_year, selected_period=selected_period)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/wiki_ww1')
def wiki_ww1():
    return render_template('wiki_ww1.html')

@app.route('/wiki_ww2')
def wiki_ww2():
    return render_template('wiki_ww2.html')

@app.route('/wiki_ussr')
def wiki_ussr():
    return render_template('wiki_ussr.html')

@app.route('/wiki_1991')
def wiki_1991():
    return render_template('wiki_1991.html')

@app.route('/wiki_2014')
def wiki_2014():
    return render_template('wiki_2014.html')

@app.route('/wiki_2022')
def wiki_2022():
    return render_template('wiki_2022.html')

if __name__ == '__main__':
    app.run(debug=True)
