import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify (cafe = random_cafe.to_dict())

@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    return jsonify (cafes = [cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search_cafe_by_location():
    location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location = location).all()
    if cafes:
        return jsonify(cafes = [cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error = {"Not Found": "Sorry, there is no cafe at that location"})

@app.route("/add", methods = ["POST"])
def add_new_cafe():
    new_cafe = Cafe(
        name = request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(int(request.form.get("sockets"))),
        has_toilet=bool(int(request.form.get("toilet"))),
        has_wifi=bool(int(request.form.get("wifi"))),
        can_take_calls=bool(int(request.form.get("calls"))),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response = {"success": "Successfully added the new cafe."})

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_coffee_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response = {"success": "Successfully updated coffee price"}), 200
    else:
        return jsonify(response = {"error": "Sorry, a cafe with that id was not found in the database"}), 404

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    api_key = request.args.get("api-key")
    if cafe:
        if api_key == "MySecretApiKey":
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response = {"success": "Successfully removed closed cafe"}), 200
        else:
            return jsonify(response = {"Forbidden": "Sorry, you don't have premission to remove cafe, check your api-key"}), 403
    else:
        return jsonify(response = {"Not Found": "Sorry, a cafe with that id was not found in the database"}), 404


if __name__ == '__main__':
    app.run(debug=True)
