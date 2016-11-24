import json
import math

from flask import Flask, render_template, request


app = Flask(__name__)

contours = ['CARD', 'CHEST', 'WAIST', 'NECK']
views = ['FRONT', 'SIDE']
pi = 3.14

profile = {}
deltas = {}


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/photos")
def photos():
    return render_template('photos.html', views=views)


@app.route("/uploadFront")
def uploadFront():
    query_string = request.query_string

    f = open("static/front.txt", "wb")
    f.write(query_string)
    f.close()

    return render_template('photos.html')


@app.route("/uploadSide")
def uploadSide():
    query_string = request.query_string

    f = open("static/side.txt", "wb")
    f.write(query_string)
    f.close()

    return render_template('photos.html')


@app.route("/contouring")
def contouring():
    fronttxt = open("static/front.txt", "rb").read().decode("utf-8")
    sidetxt = open("static/side.txt", "rb").read().decode("utf-8")
    return render_template(
        'contouring.html',
        fronttxt=json.dumps(fronttxt),
        sidetxt=json.dumps(sidetxt),
        contours=json.dumps(contours), views=json.dumps(views)
    )


@app.route("/measurements")
def measurements():
    query_string = str(request.query_string, 'utf-8').replace("%22", "\"")
    deltas = json.loads(query_string)

    cardTuple = deltas['CARD']
    pixelsPerInch = cardCalibration(cardTuple)
    pixelsPerInchFront = pixelsPerInch[0]
    pixelsPerInchSide = pixelsPerInch[1]

    for contour in contours:
        if contour != 'CARD':
            deltaTuple = deltas[contour]
            profile[contour] = algorithm(deltaTuple, pixelsPerInchFront,
                                         pixelsPerInchSide)

    return render_template('measurements.html', profile=profile)


def algorithm(deltaTuple, pixelsPerInchFront, pixelsPerInchSide):
    a = deltaTuple[0] / (2 * pixelsPerInchFront)
    b = deltaTuple[1] / (2 * pixelsPerInchSide)

    p = 2 * pi * math.sqrt((a**2 + b**2) / 2)

    return p


def cardCalibration(deltaTuple):
    pixelsPerInchFront = deltaTuple[0] / 3.37
    pixelsPerInchSide = deltaTuple[1] / 3.37
    pixelsPerInch = [pixelsPerInchFront, pixelsPerInchSide]
    return pixelsPerInch


if __name__ == "__main__":
    app.run()
