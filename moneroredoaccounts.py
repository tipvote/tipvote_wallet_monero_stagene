import requests
from requests.auth import HTTPDigestAuth
import json
from walletconfig import rpcpassword, rpcusername, url

from app import db
from app.models import \
    MoneroWallet, \
    User, \
    MoneroUnconfirmed

# standard json header
headers = {'content-type': 'application/json'}


def createnewdbentry(userid):
    monero_newunconfirmed = MoneroUnconfirmed(
        user_id=userid,
        unconfirmed1=0,
        unconfirmed2=0,
        unconfirmed3=0,
        unconfirmed4=0,
        unconfirmed5=0,
        txid1='',
        txid2='',
        txid3='',
        txid4='',
        txid5='',
    )

    # creates monero wallet  in db
    monero_walletcreate = MoneroWallet(user_id=userid,
                                       currentbalance=0,
                                       unconfirmed=0,
                                       address1='',
                                       address1status=1,
                                       locked=0,
                                       transactioncount=0,
                                       )

    db.session.add(monero_newunconfirmed)
    db.session.add(monero_walletcreate)

    db.session.commit()


def getbalance(account_index):
    rpc_input = {
        "method": "get_balance",
        "params": {"account_index ": int(account_index)}
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers,
        auth=HTTPDigestAuth(rpcusername, rpcpassword))

    print(json.dumps(response.json(), indent=4))

    return response.json()


def createaccount(user_id):

    rpc_input = {
        "method": "create_account",
        "params": {"label": str(user_id)}
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers,
        auth=HTTPDigestAuth(rpcusername, rpcpassword))

    return response.json()


def gettheaccounts():
    rpc_input = {
        "method": "get_accounts",
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers,
        auth=HTTPDigestAuth(rpcusername, rpcpassword))

    print(json.dumps(response.json(), indent=4))


def getaddress(account_index):

    rpc_input = {
        "method": "get_address",
        "params": {"account_index": int(account_index)}
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers,
        auth=HTTPDigestAuth(rpcusername, rpcpassword))

    return response.json()


def labelit(account_index, username):
    print("account index", account_index)
    print("uname", username)
    rpc_input = {
        "method": "label_account",
        "params": {"account_index": int(account_index), "label": str(username)}
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers,
        auth=HTTPDigestAuth(rpcusername, rpcpassword))

    print(json.dumps(response.json(), indent=4))


def checkforwork():
    the_users = User.query.order_by(User.id.asc()).all()
    for f in the_users:

        print("***********Start*********")
        # stagenet
        user_wallet = MoneroWallet.query \
            .filter(MoneroWallet.user_id == f.id) \
            .first()

        if user_wallet is None:
            print("creating new wallet for user: ", f.user_name)
            # create new thing in database
            createnewdbentry(userid=f.id)

            # re query wallet
            user_wallet = MoneroWallet.query \
                .filter(MoneroWallet.user_id == f.id) \
                .first()

            # see if account with that id exists

            theaccountresponse = getaddress(f.id)

            if "result" in theaccountresponse:

                useraddress = theaccountresponse["result"]["address"]
                user_wallet.address1 = useraddress
                db.session.add(user_wallet)
            else:
                print("Creating account for :", f.user_name)
                # create an account
                userinfo = createaccount(user_id=f.id)
                useraddress = userinfo["result"]["address"]
                user_wallet.address1 = useraddress
                db.session.add(user_wallet)

                # label account
                print("labeling")
                labelit(f.id, f.user_name)
                print(" end labeling")

                print(f.user_name)
                print(user_wallet.address1)
                print("*")
        else:
            print("user exists: ", f.user_name)

            # see if account with that id exists
            theaccountresponse = getaddress(f.id)

            if "result" in theaccountresponse:

                useraddress = theaccountresponse["result"]["address"]
                user_wallet.address1 = useraddress
                db.session.add(user_wallet)
            else:
                print("creating new account")
                # create an account
                userinfo = createaccount(user_id=f.id)
                useraddress = userinfo["result"]["address"]
                # put address into database from new account
                user_wallet.address1 = useraddress
                db.session.add(user_wallet)

                # label account
                print("labeling")
                labelit(f.id, f.user_name)
                print(" end labeling")
                print(f.user_name)
                print(user_wallet.address1)
                print("*")
        print("***********End*********")
    db.session.commit()


if __name__ == '__main__':
    gettheaccounts()
    #checkforwork()