import rsa
from bson import ObjectId
from flasgger import swag_from
from flask import request

from odc_server import app, db, bpk, bok
from odc_server.crypto import hash_items, verify_with_public_key, sign_with_private_key
from odc_server.utils import random_numerical_string, is_hex


@app.route("/receive-banknote", methods=["POST"])
@swag_from("apidocs/receive_banknote.yml")
def receive_banknote():
    request_json = request.get_json()
    bnid = request_json["bnid"]
    uuid = request_json["uuid"]
    otok = request_json["otok"]
    wallet_signature = request_json["wallet_signature"]
    sok = request_json["sok"]
    sok_signature = request_json["sok_signature"]

    if not is_hex(bnid, 24):
        return {"code": 400, "message": "bnid should be 24 char hex string"}, 400

    banknote = db.banknotes.find_one({"_id": ObjectId(bnid)})
    if banknote is None:
        return {"code": 400, "message": "bnid does not exist"}, 400

    try:
        rsa.PublicKey.load_pkcs1(otok.encode())
    except:
        return {"code": 400, "message": "Failed to parse otok"}, 400

    try:
        rsa.PublicKey.load_pkcs1(sok.encode())
    except:
        return {"code": 400, "message": "Failed to parse sok"}, 400

    sok_hash = hash_items([sok])
    if not verify_with_public_key(sok_hash, sok_signature, bok):
        return {"code": 401, "message": "Invalid sok signature"}, 401

    transaction_hash = hash_items([uuid, otok, bnid])
    if not verify_with_public_key(transaction_hash, wallet_signature, sok):
        return {"code": 401, "message": "Invalid wallet signature"}, 401

    magic = random_numerical_string(16)
    transaction_hash_signed = sign_with_private_key(transaction_hash, bpk)

    new_block = {"uuid": uuid, "parent_uuid": "", "otok": otok, "magic": magic, "transaction_hash": transaction_hash,
                 "transaction_hash_signed": transaction_hash_signed}

    db.banknotes.update_one({"_id": ObjectId(bnid)},
                            {"$push": {"chains": new_block}})

    return {"code": 200, "magic": magic, "transaction_hash": transaction_hash,
            "transaction_hash_signed": transaction_hash_signed}
