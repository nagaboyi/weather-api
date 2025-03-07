from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# OpenWeatherMap API Configuration
API_KEY = 'f46cd661c0f35867375c42d0234023c2'  # Replace with your API key
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    weekly_forecast = None
    if request.method == 'POST':
        city = request.form['city']
        # Fetch current weather
        current_url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
        current_response = requests.get(current_url)
        if current_response.status_code == 200:
            current_data = current_response.json()
            weather_data = {
                'city': current_data['name'],
                'temp': current_data['main']['temp'],
                'description': current_data['weather'][0]['description'],
                'icon': current_data['weather'][0]['icon'],
                'humidity': current_data['main']['humidity'],
                'wind': current_data['wind']['speed'],
                'lat': current_data['coord']['lat'],
                'lon': current_data['coord']['lon']
            }

            # Fetch 5-day/3-hour forecast
            forecast_url = f"{FORECAST_URL}?q={city}&appid={API_KEY}&units=metric"
            forecast_response = requests.get(forecast_url)
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                weekly_forecast = process_forecast(forecast_data['list'])

    return render_template('index.html', weather=weather_data, weekly_forecast=weekly_forecast)

def process_forecast(forecast_list):
    daily_data = {}
    for entry in forecast_list:
        date = entry['dt_txt'].split(' ')[0]  # Extract date (YYYY-MM-DD)
        if date not in daily_data:
            daily_data[date] = {
                'temp_min': entry['main']['temp_min'],
                'temp_max': entry['main']['temp_max'],
                'weather': entry['weather'][0]['description'],
                'icon': entry['weather'][0]['icon'],
            }
        else:
            # Update min and max temperatures
            if entry['main']['temp_min'] < daily_data[date]['temp_min']:
                daily_data[date]['temp_min'] = entry['main']['temp_min']
            if entry['main']['temp_max'] > daily_data[date]['temp_max']:
                daily_data[date]['temp_max'] = entry['main']['temp_max']

    # Convert to a list of daily summaries
    return [
        {
            'date': date,
            'temp_min': data['temp_min'],
            'temp_max': data['temp_max'],
            'weather': data['weather'],
            'icon': data['icon'],
        }
        for date, data in daily_data.items()
    ]

if __name__ == '__main__':
    app.run(debug=True)