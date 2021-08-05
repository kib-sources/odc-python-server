import requests
from os import environ

environ["bpk_location"] = "../example_keys/key"
environ["bok_location"] = "../example_keys/key.pub"

from odc_server.crypto import sign_with_private_key, hash_items
from odc_server.utils import current_epoch_time, random_numerical_string


def example():
    # SIM RSA-ключи (Sim Open/Private Key)
    sok = """-----BEGIN RSA PUBLIC KEY-----
    MEgCQQC5ohEmk4zwb6YdoBrWjkCr/jZLc729AYc7QC8sabaSLiujiRcd6VwL7drx
    QJymxN/gHrvHYDU1xxtiuYCk7nF7AgMBAAE=
    -----END RSA PUBLIC KEY-----"""
    spk = """-----BEGIN RSA PRIVATE KEY-----
    MIIBPQIBAAJBALmiESaTjPBvph2gGtaOQKv+Nktzvb0BhztALyxptpIuK6OJFx3p
    XAvt2vFAnKbE3+Aeu8dgNTXHG2K5gKTucXsCAwEAAQJAeP+Yqkp3DanY32qi08N5
    iCJ1hYz12iMK4KYfmZV15WrMpZFk2/MVJQ1MShGgUqYQn+hx5HRfN6eV/WWoq9ja
    8QIjAONqGRRqCO7zVn932/BSPOQGi77OWasaCROCdvc537Trmy0CHwDQ93+pCB/w
    2iz9mvrVas6YWIpiUQZ7EidsLPfRCEcCIwDjF3vb6tbo5o4l0+cJYNX1TqQV8bGR
    LvqJROrPjjdaTzwxAh5HHsUrIWHFlmvTkIioVCamQRQwLAV5o48ZSSC62wcCIwDa
    T92B+tNQFleSvrNVUWUffShTtm18JaF0knNIhhlB0VxC
    -----END RSA PRIVATE KEY-----"""

    # One Time Open Key RSA-ключ, для простоты будем использовать один ключ для всех банкнот
    otok = """-----BEGIN RSA PUBLIC KEY-----
    MEgCQQC5ohEmk4zwb6YdoBrWjkCr/1ZLc729AYc7QC8sabaSLiujiRcd6VwL7drxQJymxN/gHrvHYDU1xxtiuYCk7nF7AgMBAAE=
    -----END RSA PUBLIC KEY-----"""

    # Перед началом работы регистрируем кошелек на сервере
    register_response = requests.post("http://127.0.0.1:5000/register-wallet", json={"sok": sok})
    register_response_code = register_response.status_code

    if register_response_code == 409:
        print("Этот sok уже используется, необходимо сбросить базу данных или использовать другой.")
        return

    if register_response_code == 400:
        print("sok не является RSA-ключем правильного формата")
        return

    register_response_json = register_response.json()

    # Дополнаяем доступные данные
    sok_signature = register_response_json["sok_signature"]
    wid = register_response_json["wid"]

    amount_to_issue = 10

    # Для получения банкнот их необходимо выпустить
    issue_response = requests.post("http://127.0.0.1:5000/issue-banknotes",
                                   json={"amount": amount_to_issue, "wid": wid})
    issue_response_code = issue_response.status_code

    if issue_response_code == 400:
        print("wid не был найден в базе данных")
        return

    issue_response_json = issue_response.json()

    # Дополнаяем доступные данные
    issued_banknotes = issue_response_json["issued_banknotes"]

    print(f"Выпущено(-а) {len(issued_banknotes)} банкнот(-а)")

    # Регистрируем каждую выпущенную банкноту
    for i, banknote in enumerate(issued_banknotes):
        # Идентификатор банкноты
        bnid = banknote["bnid"]
        # Подписываем хэш otok клиентским spk, это необходимо чтобы гарантировать подлинность otok
        otok_hash = hash_items([otok])
        otok_signature = sign_with_private_key(otok_hash, spk)
        # Выбираем текущее время как время транзакции
        current_time = current_epoch_time()
        # Случайный уникальный идентификатор
        uuid = random_numerical_string(12)
        # Хэш параметров транзакции, подписанный spk, это необходимо чтобы гарантировать валидность операции
        transaction_hash = hash_items([uuid, otok, bnid, current_time])
        transaction_signature = sign_with_private_key(transaction_hash, spk)

        banknote_initial_chain = {"bnid": bnid, "otok": otok, "wid": wid, "time": current_time, "uuid": uuid,
                                  "otok_signature": otok_signature, "transaction_signature": transaction_signature, }
        receive_response = requests.post("http://127.0.0.1:5000/receive-banknote", json=banknote_initial_chain)
        receive_code = receive_response.status_code

        if receive_code != 200:
            print(f"Не удалось получить банкноту №{i + 1}")

        receive_json = receive_response.json()
        print(f"Получена банкнота №{i + 1}")
        print(receive_json)


example()
