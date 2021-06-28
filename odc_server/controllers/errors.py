from odc_server import app


@app.errorhandler(400)
def error400_view(exception):
    return {"id": "400", "message": "Bad request"}


@app.errorhandler(401)
def error401_view(exception):
    return {"id": "401", "message": "Unauthorized"}


@app.errorhandler(403)
def error403_view(exception):
    return {"id": "403", "message": "Forbidden"}


@app.errorhandler(404)
def error404_view(exception):
    return {"id": "404", "message": "Not found"}


@app.errorhandler(405)
def error404_view(exception):
    return {"id": "405", "message": "Not allowed"}


@app.errorhandler(500)
def error500_view(exception):
    return {"id": "500", "message": "Internal server error"}
