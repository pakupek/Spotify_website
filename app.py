from flask import Flask, render_template
import spotify_api
app = Flask(__name__)

client_id = '67b2ba6ce11547e6b7f5d8459aaaa09c'
client_secret = '4cd84636dbec44efb84c9bac251a9aa0'
client = spotify_api.SpotifyAPI(client_id, client_secret)


#Starting page
@app.route('/')
def homepage():
    releases = client.get_new_releases()
    return render_template("homepage.html", releases = releases)

@app.route('/artists')
def artists():
    artists = client.get_several_artists()
    #artists = spotify_api.SpotifyAPI.get_several_artists(self)
    return render_template('artists.html', artists=artists)


if __name__ == '__main__':
    app.run(debug=True)