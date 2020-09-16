import requests
from requests.auth import HTTPDigestAuth
import json
from walletconfig import rpcpassword, rpcusername, url

from app import db
from app.models import \
    MoneroWalletWorkStagenet,\
    MoneroWalletStagenet,\
    User

# standard json header
headers = {'content-type': 'application/json'}


def labelit(account_index,username):
    """
    This function adds the name to the account index
    :param account_index:
    :param username:
    :return:
    """
    rpc_input = {
        "method": "label_account",
        "params": {"account_index": int(account_index),
                   "label": str(username)
                   }
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


def createaccount(user_id):
    """
    This functions creates an account in the wallet
    :param user_id:
    :return:
    """
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


def checkforwork():
    # query for work ..#2 = create a wallet
    work = MoneroWalletWorkStagenet.query \
        .filter(MoneroWalletWorkStagenet.type == 2) \
        .all()
    if work:
        for f in work:
            # get user wallet
            user_wallet = MoneroWalletStagenet.query.filter(MoneroWalletStagenet.user_id == f.user_id).first()

            # get a user
            theuser = User.query.get(f.user_id)
            # create an account
            userinfo = createaccount(user_id=f.id)
            # get new address
            useraddress = userinfo["result"]["address"]
            # label account
            labelit(f.id, theuser.user_name)
            # put address into database from new account
            user_wallet.address1 = useraddress
            # label work as done
            f.type = 0
            # add to db
            print(theuser)
            print(useraddress)
            db.session.add(user_wallet)
            db.session.add(f)
        db.session.commit()
    else:
        print("no work")

if __name__ == '__main__':
    checkforwork()

