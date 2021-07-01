from odc_server import app


@app.errorhandler(400)
def error400_view(exception):
    return {"id": "400", "message": "Bad request"}, 400


@app.errorhandler(401)
def error401_view(exception):
    return {"id": "401", "message": "Unauthorized"}, 401


@app.errorhandler(403)
def error403_view(exception):
    return {"id": "403", "message": "Forbidden"}, 403


@app.errorhandler(404)
def error404_view(exception):
    return {"id": "404", "message": "Not found"}, 404


@app.errorhandler(405)
def error404_view(exception):
    return {"id": "405", "message": "Not allowed"}, 405


@app.errorhandler(500)
def error500_view(exception):
    return {"id": "500", "message": "Internal server error"}, 500
