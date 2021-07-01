from datetime import datetime

import rsa
from bson import ObjectId
from flasgger import swag_from
from flask import request

from odc_server import app, db, bpk, bok
from odc_server.crypto import hash_items, sign_with_private_key
from odc_server.utils import is_hex, random_numerical_string


@app.route("/bok", methods=["GET"])
@swag_from("apidocs/bok.yml")
def fetch_bok():
    return {"code": 200, "bok": bok}


@app.route("/regw", methods=["POST"])
@swag_from("apidocs/regw.yml")
def register_wallet():
    sok = request.form["sok"]

    try:
        rsa.PublicKey.load_pkcs1(sok.encode())
    except:
        return {"code": 400, "message": "Failed to parse sok"}, 400

    if db.wallets.find_one({"sok": sok}) is not None:
        return {"code": 400, "message": "sok already registered"}, 400

    signed_sok = sign_with_private_key(hash_items([sok]), bpk)
    wid = db.wallets.insert_one({"sok": sok, "sok_signature": signed_sok}).inserted_id
    return {"code": 200, "wid": str(wid), "sok_signature": signed_sok}


@app.route("/issb", methods=["POST"])
@swag_from("apidocs/issb.yml")
def issue_banknotes():
    wid = request.form["wid"]
    amount = request.form["amount"]

    if (not amount.isnumeric()) or int(amount) < 1:
        return {"code": 400, "message": "Amount should be a non-zero integer"}, 400

    if not is_hex(wid, 24):
        return {"code": 400, "message": "wid should be 24 char hex string"}, 400

    wallet = db.wallets.find_one({"_id": ObjectId(wid)})
    if wallet is None:
        return {"code": 400, "message": "wid not registered"}, 400

    amount = int(amount)
    give_amounts = dict()
    banknote_amounts = [5000, 2000, 1000, 500, 100, 50, 10, 5, 2, 1]
    for banknote_amount in banknote_amounts:
        banknote_count = amount // banknote_amount
        amount = amount % banknote_amount
        if banknote_count > 0:
            give_amounts[banknote_amount] = banknote_count
        if amount == 0:
            break

    current_time = datetime.now().strftime("%Y%m%d%H%M%S%f")
    given_banknotes = list()
    for banknote_amount, banknote_count in give_amounts.items():
        banknote_template = {"code": 643, "time": current_time, "amount": banknote_amount}
        for _ in range(banknote_count):
            banknote = dict(banknote_template)

            inserted_id = db.banknotes.insert_one(dict(banknote)).inserted_id

            banknote["bnid"] = str(inserted_id)
            banknote_hash = hash_items(banknote.values())
            banknote["signature"] = sign_with_private_key(banknote_hash, bpk)

            db.banknotes.update_one({"_id": inserted_id},
                                    {"$set": {"signature": banknote["signature"], "chains": list()}})

            given_banknotes.append(banknote)

    return {"code": 200, "issued_banknotes": given_banknotes}
