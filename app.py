#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Create an Api instance
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Resource for /heroes
class HeroListResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes], 200

# Resource for /heroes/:id
class HeroResource(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero:
            return hero.to_dict(), 200
        return {'error': 'Hero not found'}, 404

# Resource for /powers
class PowerListResource(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict(only=('id', 'name', 'description')) for power in powers], 200

# Resource for /powers/:id
class PowerResource(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power:
            return power.to_dict(), 200
        return {'error': 'Power not found'}, 404

    def patch(self, id):
        power = Power.query.get(id)
        if power:
            data = request.get_json()
            if 'description' in data and len(data['description']) >= 20:
                power.description = data['description']
                db.session.commit()
                return power.to_dict(), 200
            else:
                return {'errors': ['Description must be at least 20 characters long.']}, 400
        return {'error': 'Power not found'}, 404

# Resource for /hero_powers
class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            strength = data['strength']
            if strength not in ['Strong', 'Weak', 'Average']:
                raise ValueError('Invalid strength value.')

            hero_power = HeroPower(
                strength=strength,
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(hero_power)
            db.session.commit()

            return hero_power.to_dict(), 201
        except ValueError as e:
            return {'errors': [str(e)]}, 400

# Register routes with Api
api.add_resource(HeroListResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:id>')
api.add_resource(PowerListResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
