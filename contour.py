import json
import math
import os

from flask import Flask, render_template, request

from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
cache = SimpleCache()

contours = ['PERSON Height', 'CHEST Width', 'WAIST Width', 'NECK Width']
views = ['FRONT', 'SIDE']
pi = 3.14

profile = {}
deltas = {}


@app.route("/")
def main():
    return render_template('index.html')

@app.route("/enterHeight", methods=['POST'])
def enterHeight():
    cache.set('height', request.form['userHeight'])
    print (cache.get('height'))
    return render_template('index.html')


@app.route("/photos")
def photos():
    return render_template('photos.html', views=views)


@app.route("/uploadFront")
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
#cacheSide
def cacheSide():
    query_string = request.query_string

    # f = open("static/side.txt", "wb")
    # f.write(query_string)
    # f.close()

    cache.set('side', query_string)

    return render_template('photos.html')


@app.route("/contouring")
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


@app.route("/measurements")
def measurements():
    query_string = str(request.query_string.decode("utf-8")).replace("%22", "\"").replace("%20", " ")
    print (query_string)
    deltas = json.loads(query_string)

    cardTuple = deltas['PERSON Height']
    pixelsPerInch = calibration(cardTuple)
    pixelsPerInchFront = pixelsPerInch[0]
    pixelsPerInchSide = pixelsPerInch[1]

    for contour in contours:
        if contour != 'PERSON Height':
            deltaTuple = deltas[contour]
            profile[contour] = algorithm(deltaTuple, pixelsPerInchFront,
                                         pixelsPerInchSide)

    return render_template('measurements.html', profile=profile)


def algorithm(deltaTuple, pixelsPerInchFront, pixelsPerInchSide):
    a = deltaTuple[0] / (2 * pixelsPerInchFront)
    b = deltaTuple[1] / (2 * pixelsPerInchSide)

    p = 2 * pi * math.sqrt((a**2 + b**2) / 2)

    return p


def calibration(deltaTuple):
    pixelsPerInchFront = deltaTuple[0] / float(cache.get('height'))
    pixelsPerInchSide = deltaTuple[1] / float(cache.get('height'))
    pixelsPerInch = [pixelsPerInchFront, pixelsPerInchSide]
    return pixelsPerInch


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    # initialize cache
