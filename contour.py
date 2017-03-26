import json
import math
import os

from flask import Flask, render_template, request, Response

from urlparse import urlparse
from cgi import parse_qs, escape

from werkzeug.contrib.cache import SimpleCache
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

cache = SimpleCache()

app = Flask(__name__)

contours = ['CARD Length', 'CHEST Width', 'WAIST Width', 'NECK Width']

# db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/contour'
db = SQLAlchemy(app)

contours = ['CARD Length', 'CHEST Width', 'WAIST Width', 'NECK Width']
views = ['FRONT', 'SIDE']
pi = 3.14


profile = {}
deltas = {}

# Create our database model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), unique=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Create our database model
class UserSizes(db.Model):
    __tablename__ = "user_sizes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    neck = db.Column(db.Float)
    chest = db.Column(db.Float)
    waist = db.Column(db.Float)

    def __init__(self, user_id, neck, chest, waist):
        self.user_id = user_id
        self.neck = neck
        self.chest = chest
        self.waist = waist


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if db.session.query(User).filter(User.username == username).filter(User.password == password).count():
        cache.set('username', username)
        return True

    return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/enterHeight", methods=['POST'])
def enterHeight():
    cache.set('height', request.form['userHeight'])
    print (cache.get('height'))

@app.route("/addUser", methods=['GET'])
def addUser():
    d = parse_qs(request.query_string)
    print d
    username = d.get('username', [''])[0]
    password = d.get('password', [''])[0]

    newUser = User(username = username,
                    password = password)

    db.session.add(newUser)
    db.session.commit()

    return render_template(
        'newuser.html',
        username=json.dumps(username))

@app.route("/photos")
@requires_auth
def photos():
    print request.authorization.username
    return render_template('photos.html', views=views)


@app.route("/uploadFront")
@requires_auth
#cacheFront
def cacheFront():
    query_string = request.query_string
    # print ("sup")
    # f = open("static/front.txt", "wb")
    # print ("opening file")
    # f.write(query_string)
    # f.close()
    cache.set('front', query_string)

    return render_template('photos.html')


@app.route("/uploadSide")
@requires_auth
#cacheSide
def cacheSide():
    query_string = request.query_string

    # f = open("static/side.txt", "wb")
    # f.write(query_string)
    # f.close()

    cache.set('side', query_string)

    return render_template('photos.html')


@app.route("/contouring")
@requires_auth
def contouring():
    #read from cache
    # fronttxt = open("static/front.txt", "rb").read().decode("utf-8")
    # sidetxt = open("static/side.txt", "rb").read().decode("utf-8")
    fronttxt = cache.get('front').decode("utf-8")
    sidetxt = cache.get('side').decode("utf-8")

    return render_template(
        'contouring.html',
        fronttxt=json.dumps(fronttxt),
        sidetxt=json.dumps(sidetxt),
        contours=json.dumps(contours), views=json.dumps(views)
    )

@app.route("/contourupload")
@requires_auth
def contourupload():
    return render_template(
        'contourupload.html',
        contours=json.dumps(contours), views=json.dumps(views)
    )

@app.route("/measurements")
@requires_auth
def measurements():
    query_string = str(request.query_string.decode("utf-8")).replace("%22", "\"").replace("%20", " ")
    print (query_string)
    deltas = json.loads(query_string)

    cardTuple = deltas['CARD Length']
    pixelsPerInch = cardCalibration(cardTuple)
    pixelsPerInchFront = pixelsPerInch[0]
    pixelsPerInchSide = pixelsPerInch[1]

    for contour in contours:
        if contour != 'CARD length':
            deltaTuple = deltas[contour]
            profile[contour] = algorithm(deltaTuple, pixelsPerInchFront,
                                         pixelsPerInchSide)
    print request.authorization.username
    print profile
    user = db.session.query(User).filter_by(username=request.authorization.username).first()
    user_id = user.id
    neck = profile['NECK Width']
    chest = profile['CHEST Width']
    waist = profile['WAIST Width']

    newUserSize = UserSizes(user_id = user_id,
                    neck = neck,
                    chest = chest,
                    waist = waist)

    db.session.add(newUserSize)
    db.session.commit()

    # round to the nearest integer
    profile['NECK Width'] = int(round(profile['NECK Width']))
    profile['CHEST Width'] = int(round(profile['CHEST Width']))
    profile['WAIST Width'] = int(round(profile['WAIST Width']))

    return render_template('measurements.html', profile=profile)


def algorithm(deltaTuple, pixelsPerInchFront, pixelsPerInchSide):
    a = deltaTuple[0] / (2 * pixelsPerInchFront)
    b = deltaTuple[1] / (2 * pixelsPerInchSide)

    p = 2 * pi * math.sqrt((a**2 + b**2) / 2)

    return p


def cardCalibration(deltaTuple):
    pixelsPerInchFront = deltaTuple[0] / 3.984
    pixelsPerInchSide = deltaTuple[1] / 3.984
    pixelsPerInch = [pixelsPerInchFront, pixelsPerInchSide]
    return pixelsPerInch


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    # initialize cache
