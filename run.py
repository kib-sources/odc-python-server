import os

from odc_server import app

if __name__ == '__main__':
    bind_address = os.getenv("bind_address")
    if bind_address is None:
        bind_address = "127.0.0.1"
    app.run(host=bind_address)
