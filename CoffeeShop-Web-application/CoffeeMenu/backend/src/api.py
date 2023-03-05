import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this functon will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_all_drinks():
    all_drinks = Drink.query.all()
    
    fmt_drinks = [drink.short() for drink in all_drinks]

    if fmt_drinks:
        return jsonify({
            'success':True,
            'drinks':fmt_drinks
        })

    else:
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth(permission='get:drinkdetails')
def get_drink_details(payload):
    all_drinks = Drink.query.all()
    
    fmt_drinks = [drink.long() for drink in all_drinks]

    if fmt_drinks:
        return jsonify({
            'success':True,
            'drinks':fmt_drinks
        })

    else:
        abort(404)
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink is an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def add_drink(payload):
    body = request.get_json()

    if not body:
        abort(400)

    new_title = body.get("title")
    new_recipe = json.dumps(body.get("recipe"))
    # new_recipe = 'Milk and Chocolate'

    try:
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
        
        updated_drinks = Drink.query.filter(Drink.title==new_title).one_or_none()
        drinks = []
        dictDrinks = updated_drinks.long()
        drinks.append(dictDrinks)

        return jsonify({
            'success':True,
            'drinks':drinks
        })

    except:
        abort(400)
        # abort(Response('This error has already been flagged!'))

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink is an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drinks(payload, id):
    body = request.get_json()

    new_title = body.get('title')

    drink = Drink.query.filter(Drink.id==id).one_or_none()

    if not drink:
        abort(404)

    try:
        drink.title = new_title
        drink.update()

        drinkList = []
        new_drink = Drink.query.filter(Drink.id==id).one_or_none().long()

        drinkList.append(new_drink)
        return jsonify({
            'success':True,
            'drinks':drinkList
        })

    except Exception:
        abort(405)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()

    if not drink:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            "success":True,
            "deleted":id
        })

    except:
        abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404

@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400

