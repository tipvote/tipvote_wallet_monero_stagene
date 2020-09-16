import requests
from decimal import Decimal
from requests.auth import HTTPDigestAuth
import json
from walletconfig import rpcpassword,\
    rpcusername,\
    url
from app import db


from monero_addtotransactions_stagenet import\
    monero_addtransaction
from monero_helper_functions_stagenet import\
    get_money,\
    get_amount

from app.models import \
    MoneroWalletWorkStagenet, \
    MoneroBlockHeightStagenet, \
    MoneroWalletStagenet

# standard json header
headers = {'content-type': 'application/json'}


def getwalletofperson(userid):
    getuserswallet = MoneroWalletStagenet.query\
        .filter(MoneroWalletStagenet.user_id == userid)\
        .first()
    return getuserswallet


def getblockheight():
    lastblockheight = MoneroBlockHeightStagenet.query.get(1)
    return lastblockheight


def add_error(f, response_json):

    if "error" in response_json:
        if "message" in response_json["error"]:
            theerror = response_json["error"]['message']
            if theerror == 'not enough unlocked money':
                f.type = 300
            elif theerror.startsiwth("WALLET_RPC_ERROR_CODE_WRONG_ADDRESS:"):
                f.type = 307
            else:
                f.type = 304
        else:
            f.type = 300

        db.session.add(f)


def sendcoin(sendto, amount, user_id):
    """
    This will send the coin.
    If it fails turn the work to 105 for error
    Update the send transaction with txid

    """
    destination_address = str(sendto)

    int_amount = int(get_amount(amount))

    # just to make sure that amount->coversion->back
    # gives the same amount as in the initial number
    assert amount == Decimal(get_money(str(int_amount))),\
        "Amount conversion failed"

    # send specified xmr amount to the given destination_address
    recipents = [{"address": destination_address,
                  "amount": int_amount}]

    # using given mixin
    mixin = 5

    # get some random payment_id

    rpc_input = {
        "method": "transfer",
        "params": {"destinations": recipents,
                   "mixin": mixin,
                   "account_index": user_id
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

    # pretty print json output
    response_json = response.json()
    print(json.dumps(response_json, indent=4))

    return response_json


def add_transaction(f, sendto, amount, user_id):

    userswallet = getwalletofperson(userid=user_id)
    response_json = sendcoin(sendto=sendto,
                             amount=amount,
                             user_id=user_id
                             )
    # see if successful
    if "result" in response_json:
        theblockheight = getblockheight()

        thetxid = response_json["result"]['tx_hash']
        feefromtx = response_json["result"]['fee']
        thefee = Decimal(get_money(str(feefromtx)))

        monero_addtransaction(category=2,
                              amount=amount,
                              user_id=f.user_id,
                              txid=thetxid,
                              block=theblockheight.blockheight,
                              balance=userswallet.currentbalance,
                              confirmed=1,
                              fee=thefee,
                              address=sendto
                              )

        f.type = 0
        db.session.add(f)

    elif "error" in response_json:
        add_error(f, response_json)
        give_money_back(userswallet, amount)
    else:
        pass


def give_money_back(userswallet, amount):
    newbalance = userswallet.currentbalance + amount
    db.session.add(newbalance)


def main():
    """
    this will look for work to do.
      setup to provice furture expansion
    type 1: send coin offsite
    type 2: create a wallet

    """

    work = MoneroWalletWorkStagenet.query \
        .filter(MoneroWalletWorkStagenet.type == 1) \
        .order_by(MoneroWalletWorkStagenet.created.desc()) \
        .all()

    if work:
        for f in work:
            if f.type == 1:
                add_transaction(f,
                                sendto=f.sendto,
                                amount=f.amount,
                                user_id=f.user_id
                                )
        db.session.commit()


if __name__ == '__main__':
    main()
