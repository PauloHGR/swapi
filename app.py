from flask import Flask, jsonify, request
import requests
import json
import os
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

RELATIONAL_FIELDS = {
            'films': 'films',
            'species': 'species',
            'starships': 'starships',
            'vehicles': 'vehicles',
            'characters': 'characters',
            'residents': 'residents',
            'pilots': 'pilots',
            'people': 'people',
            'planets': 'planets',
            'passangers': 'passangers'
        }

def fetch_all_pages(url):
    page = 1
    people = []
    while True:
        response = requests.get(f"{url}?page={page}", verify=False).json()
        page_data = response.get('results')
        
        if not page_data:
            break

        people.extend(page_data)
        page += 1
    return people

def apply_filter_person(person, filters):
    if filters.get('gender') and filters.get('gender') != person.get('gender','').lower():
        return False
    return True

def apply_filter_film(film, filters):
    if filters.get('episode_id') and int(filters.get('episode_id')) != int(film.get('episode_id')):
        return False
    return True

def apply_filters(item, filters, type):
    fields = filters.keys()

    for field in fields:
        if filters.get(field) and field not in RELATIONAL_FIELDS:
            filter_value = str(filters[field]).lower()
            item_value = str(item.get(field, '')).lower()
            if filter_value not in item_value:
                return False
    if type == 'people':
        return apply_filter_person(item, filters)
    if type == 'films':
        return apply_filter_film(item, filters)
    return True

def apply_sort_option(data, sort_by, sort_dir):
    return sorted(data, 
                  key= lambda item : item.get(sort_by,''), 
                  reverse= sort_dir =='desc')

def parse_relational_filters(fields):
    return {
        field: request.args.get(name, 'false') for field, name in fields.items()
    }

def fetch_relational_field(person, field):
    related_items = []
    for url in person.get(field, []):
        try:
            response = requests.get(url, verify=False).json()
            if response:
                name = response.get('title') or response.get('name')
                related_items.append({"Name": name})
        except requests.RequestException:
            related_items.append({"error": "An error occurs."})
    return related_items

def get_relational_data_from_entity(entities, filters):

    for entity in entities:
        for field, value in filters.items():
            if value.lower() == 'true':
                entity[field] = fetch_relational_field(entity, field)
    return entities

def fetch_homeworld_from_planet(source):
    for s in source:
        homeworld_url = s.get("homeworld")
        if homeworld_url:
            try:
                response = requests.get(homeworld_url, verify=False).json()
                s["homeworld"] = {"name": response.get('name')}
            except requests.exceptions.RequestException as e:
                s["homeworld"] = {"error": "Unable to get homeworld"}
    return source

def fetch_all_relational_field(person, field):
    related_items = []
    for url in person.get(field, []):
        try:
            response = requests.get(url, verify=False).json()
            if response:
                related_items.append(response)
        except requests.RequestException:
            related_items.append({"error": "An error occurs."})
    return related_items

def get_relational_data_from_all_entities(entity, filters):

    for field, value in filters.items():
        if value.lower() == 'true':
            entity[field] = fetch_all_relational_field(entity, field)
    return entity

@app.route("/<string:type>", methods=["GET"])
@jwt_required()
def get_entity(type):
    try:
        data = fetch_all_pages(f"https://swapi.dev/api/{type}/")
        filters = request.args.to_dict()
        sort_by = filters.pop('sort_by', 'created')
        sort_dir = filters.pop('sort_dir', 'asc')
        
        filtered_data = [item for item in data if apply_filters(item, filters, type)]
        relational_filters = parse_relational_filters(RELATIONAL_FIELDS)
        filtered_data = apply_sort_option(filtered_data, sort_by, sort_dir)
        
        if type == 'people' or type == 'species':
            filtered_data = fetch_homeworld_from_planet(filtered_data)

        filtered_data = get_relational_data_from_entity(filtered_data, relational_filters)
        return jsonify({"status": "success", "data": filtered_data})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message":str(e)})

@app.route("/<string:type>/<int:id>", methods=["GET"])
@jwt_required()
def get_entity_by_id(type, id):
    try:
        response = requests.get(f"https://swapi.dev/api/{type}/{id}/", verify=False).json()
        relational_filters = parse_relational_filters(RELATIONAL_FIELDS)
        response = get_relational_data_from_all_entities(response, relational_filters)
        return jsonify({"status": "success", "data": response})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def get_value():
    try:
       
        response = requests.get("https://swapi.dev/api/", verify=False)
        data = response.json()
        return jsonify({"status": "success", "data": data})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message":str(e)})

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", "")
    password = request.json.get("password", "")

    if username == "admin" and password == "admin":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401
    
if __name__ == '__main__':
    app.run(debug=True)
