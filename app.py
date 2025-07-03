from flask import Flask, render_template, request, redirect, url_for #for saving and redirecting
from flask_sqlalchemy import SQLAlchemy
from weather import main as get_weather
from flask import Response
import csv

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class WeatherEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(100))

    def __repr__(self):
        return f"<Weather {self.city} - {self.date}>"   #preview 

@app.route('/', methods=['GET', 'POST'])  # single page application
def index():
    data = None
    city = None
    error = None 

    if request.method == 'POST': #retrival
        city = request.form['cityName']
        state = request.form['stateName']
        country = request.form['countryName']
        try:
            data = get_weather(city, state, country)
        except ValueError as e:
            error = str(e)

    return render_template('index.html', data=data, city=city, error=error)

@app.route('/add', methods=['GET', 'POST'])
def add_weather():
    if request.method == 'POST':
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        date = request.form['date']

        result = get_weather(city, state, country)
        temperature = result['current'].temperature
        condition = result['current'].description

        new_entry = WeatherEntry(
            city=city,
            state=state,
            country=country,
            date=date,
            temperature=temperature,
            condition=condition
        )
        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('history'))

    return render_template('add.html')

@app.route('/history')
def history():
    entries = WeatherEntry.query.all()
    return render_template('history.html', entries=entries)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_entry(id):
    entry = WeatherEntry.query.get_or_404(id)

    if request.method == 'POST':
        entry.city = request.form['city']
        entry.state = request.form['state']
        entry.country = request.form['country']
        entry.date = request.form['date']
        entry.temperature = request.form['temperature']
        entry.condition = request.form['condition']

        db.session.commit()
        return redirect(url_for('history'))

    return render_template('edit.html', entry=entry)

@app.route('/delete/<int:id>')
def delete_entry(id):
    entry = WeatherEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('history'))

@app.route('/export/csv')
def export_csv():
    entries = WeatherEntry.query.all()

    def generate():
        yield 'City,State,Country,Date,Temperature,Condition\n'
        for entry in entries:
            yield f'{entry.city},{entry.state or ""},{entry.country},{entry.date},{entry.temperature},{entry.condition}\n'

    return Response(generate(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=weather_history.csv'}) 
#response to trigger donload here
       




if __name__ == '__main__':
    app.run(debug=True) 