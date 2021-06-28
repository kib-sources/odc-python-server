from flask import request
from flasgger import swag_from

import rsa

from odc_server import app, db


@app.route("/regw", methods=["POST"])
@swag_from("apidocs/regw.yml")
def register_wallet():
    sok = request.form["sok"]

    try:
        rsa.PublicKey.load_pkcs1(sok.encode())
    except:
        return {"id": 400, "message": "Failed to parse sok"}, 400

    if db.wallets.find_one({"sok": sok}) is not None:
        return {"id": 400, "message": "sok already registered"}, 400

    wid = db.wallets.insert_one({"sok": sok}).inserted_id
    return {"id": 200, "wid": str(wid)}
