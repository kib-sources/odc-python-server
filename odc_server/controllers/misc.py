import rsa
from bson import ObjectId
from flasgger import swag_from
from flask import request

from odc_server import app, db, bpk, bok
from odc_server.crypto import hash_items, sign_with_private_key
from odc_server.utils import is_hex, current_epoch_time


@app.route("/bok", methods=["GET"])
@swag_from("apidocs/bok.yml")
def fetch_bok():
    return {"code": 200, "bok": bok}


@app.route("/register-wallet", methods=["POST"])
@swag_from("apidocs/register_wallet.yml")
def register_wallet():
    request_json = request.get_json()
    if request_json is None:
        return {"code": 400, "message": "Could not parse request body (must be raw json)"}, 400

    sok = request_json["sok"]

    try:
        rsa.PublicKey.load_pkcs1(sok.encode())
    except:
        return {"code": 400, "message": "Failed to parse sok"}, 400

    if db.wallets.find_one({"sok": sok}) is not None:
        return {"code": 409, "message": "sok already registered"}, 409

    signed_sok = sign_with_private_key(hash_items([sok]), bpk)
    wid = db.wallets.insert_one({"sok": sok, "sok_signature": signed_sok}).inserted_id
    return {"code": 200, "wid": str(wid), "sok_signature": signed_sok}


@app.route("/issue-banknotes", methods=["POST"])
@swag_from("apidocs/issue_banknotes.yml")
def issue_banknotes():
    request_json = request.get_json()
    if request_json is None:
        return {"code": 400, "message": "Could not parse request body (must be raw json)"}, 400

    wid = request_json["wid"]
    amount = request_json["amount"]

    if type(amount) != int or amount < 1:
        return {"code": 400, "message": "Amount should be a non-zero integer"}, 400

    if not is_hex(wid, 24):
        return {"code": 400, "message": "wid should be 24 char hex string"}, 400

    wallet = db.wallets.find_one({"_id": ObjectId(wid)})
    if wallet is None:
        return {"code": 400, "message": "wid not registered"}, 400

    amount = int(amount)
    give_amounts = dict()
    # banknote is defined as [amount, batch size]
    banknote_amounts = [[1, 30], [2, 30],
                        [5, 10], [10, 10], [50, 10], [100, 10], [500, 10], [1000, 10], [2000, 10], [5000, 10]]
    is_forward = True
    while True:
        for banknote_amount in banknote_amounts:
            count = amount // banknote_amount[0]
            if count > banknote_amount[1]:
                count = banknote_amount[1]
            if count == 0:
                continue
            if banknote_amount[0] not in give_amounts:
                give_amounts[banknote_amount[0]] = count
            else:
                give_amounts[banknote_amount[0]] += count
            amount -= count * banknote_amount[0]
            if amount == 0:
                break
        if amount == 0:
            break
        if is_forward:
            is_forward = False
            banknote_amounts = list(reversed(banknote_amounts))

    current_time = current_epoch_time()
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
