from flask import Flask, render_template
import api
app = Flask(__name__)

#Starting page
@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/artists')
def artists():
    artists = api.get_artists()
    return render_template('artists.html', artist=artists)


if __name__ == '__main__':
    app.run(debug=True)