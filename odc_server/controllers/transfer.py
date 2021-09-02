import rsa
from bson import ObjectId
from flasgger import swag_from
from flask import request

from odc_server import app, db, bpk
from odc_server.crypto import hash_items, verify_with_public_key, sign_with_private_key
from odc_server.utils import random_numerical_string, is_hex, verify_time_is_near_current


# Deprecated
@app.route("/receive-banknote", methods=["POST"])
@swag_from("apidocs/receive_banknote.yml")
def receive_banknote():
    request_json = request.get_json()
    if request_json is None:
        return {"code": 400, "message": "Could not parse request body (must be raw json)"}, 400

    wid = request_json["wid"]
    bnid = request_json["bnid"]
    uuid = request_json["uuid"]
    time = request_json["time"]
    otok = request_json["otok"]
    otok_signature = request_json["otok_signature"]
    transaction_signature = request_json["transaction_signature"]

    if not is_hex(bnid, 24):
        return {"code": 400, "message": "bnid should be 24 char hex string"}, 400

    banknote = db.banknotes.find_one({"_id": ObjectId(bnid)})
    if banknote is None:
        return {"code": 400, "message": "bnid does not exist"}, 400
    if len(banknote["chains"]) > 0:
        return {"code": 403, "message": "This banknote is already in circulation"}, 403
    if any([block["uuid"] == uuid for block in banknote["chains"]]):
        return {"code": 400, "message": "uuid is already in use"}, 400

    wallet = db.wallets.find_one({"_id": ObjectId(wid)})
    if wallet is None:
        return {"code": 400, "message": "wid not registered"}, 400
    sok = wallet["sok"]

    try:
        rsa.PublicKey.load_pkcs1(otok.encode())
    except:
        return {"code": 400, "message": "Failed to parse otok"}, 400

    if not is_hex(otok_signature, 128):
        return {"code": 400, "message": "otok_signature should be 128 char hex string"}, 400

    otok_hash = hash_items([otok])
    if not verify_with_public_key(otok_hash, otok_signature, sok):
        return {"code": 401, "message": "Invalid otok signature"}, 401

    if type(time) != int:
        return {"code": 400, "message": "time should be an integer (Unix Epoch time)"}, 400
    if not verify_time_is_near_current(time, 60):
        return {"code": 400, "message": "time should be within [current - 60, current] (Unix Epoch time)"}, 400

    if not is_hex(transaction_signature, 128):
        return {"code": 400, "message": "transaction_signature should be 128 char hex string"}, 400

    transaction_hash = hash_items([uuid, otok, bnid, time])
    if not verify_with_public_key(transaction_hash, transaction_signature, sok):
        return {"code": 401, "message": "Invalid transaction signature"}, 401

    magic = random_numerical_string(16)
    transaction_hash_signed = sign_with_private_key(transaction_hash, bpk)

    new_block = {"uuid": uuid, "parent_uuid": "", "otok": otok, "time": time, "magic": magic,
                 "transaction_hash": transaction_hash, "transaction_hash_signed": transaction_hash_signed}

    db.banknotes.update_one({"_id": ObjectId(bnid)},
                            {"$push": {"chains": new_block}})

    return {"magic": magic, "time": time,
            "transaction_hash": transaction_hash, "transaction_hash_signed": transaction_hash_signed}
