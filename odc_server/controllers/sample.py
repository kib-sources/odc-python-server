from odc_server import app


@app.route('/')
def hello_world():
    return 'Hello world!'
