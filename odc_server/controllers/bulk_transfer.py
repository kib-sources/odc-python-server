import rsa
from bson import ObjectId
from flasgger import swag_from
from flask import request

from odc_server import app, db, bpk
from odc_server.crypto import hash_items, verify_with_public_key, sign_with_private_key
from odc_server.utils import random_numerical_string, is_hex, verify_time_is_near_current


def error_response(bnid, message):
    return "Failed", {"bnid": bnid, "reason": message}


def process_banknote(wallet, banknote_data):
    bnid = banknote_data["bnid"]
    uuid = banknote_data["uuid"]
    time = banknote_data["time"]
    otok = banknote_data["otok"]
    otok_signature = banknote_data["otok_signature"]
    transaction_signature = banknote_data["transaction_signature"]

    if not is_hex(bnid, 24):
        return error_response(bnid, "bnid should be 24 char hex string")

    banknote = db.banknotes.find_one({"_id": ObjectId(bnid)})
    if banknote is None:
        return error_response(bnid, "bnid does not exist")
    if len(banknote["chains"]) > 0:
        return error_response(bnid, "This banknote is already in circulation")
    if any([block["uuid"] == uuid for block in banknote["chains"]]):
        return error_response(bnid, "uuid is already in use")

    sok = wallet["sok"]
    try:
        rsa.PublicKey.load_pkcs1(otok.encode())
    except:
        return error_response(bnid, "Failed to parse otok")

    if not is_hex(otok_signature, 128):
        return error_response(bnid, "otok_signature should be 128 char hex string")

    otok_hash = hash_items([otok])
    if not verify_with_public_key(otok_hash, otok_signature, sok):
        return error_response(bnid, "Invalid otok signature")

    if type(time) != int:
        return error_response(bnid, "time should be an integer (Unix Epoch time)")
    if not verify_time_is_near_current(time, 6000):
        return error_response(bnid, "time should be within [current - 60, current] (Unix Epoch time)")

    if not is_hex(transaction_signature, 128):
        return error_response(bnid, "transaction_signature should be 128 char hex string")

    transaction_hash = hash_items([uuid, otok, bnid, time])
    if not verify_with_public_key(transaction_hash, transaction_signature, sok):
        return error_response(bnid, "Invalid transaction signature")

    magic = random_numerical_string(16)
    transaction_hash_signed = sign_with_private_key(transaction_hash, bpk)

    new_block = {"uuid": uuid, "parent_uuid": "", "otok": otok, "time": time, "magic": magic,
                 "transaction_hash": transaction_hash, "transaction_hash_signed": transaction_hash_signed}

    db.banknotes.update_one({"_id": ObjectId(bnid)},
                            {"$push": {"chains": new_block}})

    return "OK", {"bnid": bnid, "magic": magic, "time": time,
                  "transaction_hash": transaction_hash, "transaction_hash_signed": transaction_hash_signed}


@app.route("/receive-banknotes", methods=["POST"])
@swag_from("apidocs/receive_banknotes.yml")
def receive_banknotes():
    request_json = request.get_json()
    if request_json is None:
        return {"code": 400, "message": "Could not parse request body (must be raw json)"}, 400

    wid = request_json["wid"]
    wallet = db.wallets.find_one({"_id": ObjectId(wid)})
    if wallet is None:
        return {"code": 400, "message": "wid not registered"}, 400

    if "banknotes" not in request_json:
        return {"code": 400, "message": "Banknote list not provided"}, 400

    banknotes = request_json["banknotes"]
    if len(banknotes) == 0:
        return {"code": 400, "message": "Banknote list is empty"}, 400

    received_banknotes = list()
    rejected_banknotes = list()
    for banknote in banknotes:
        status, new_banknote_data = process_banknote(wallet, banknote)
        if status == "OK":
            received_banknotes.append(new_banknote_data)
        else:
            rejected_banknotes.append(new_banknote_data)

    return {"received_banknotes": received_banknotes, "rejected_banknotes": rejected_banknotes}
