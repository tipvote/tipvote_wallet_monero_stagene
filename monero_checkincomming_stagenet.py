
import requests
from requests.auth import HTTPDigestAuth
import json
from walletconfig import rpcpassword, rpcusername, url
from app import db

from monero_addtotransactions_stagenet import monero_addtransaction
from decimal import Decimal
from app.generalfunctions import floating_decimals
from monero_helper_functions_stagenet import get_money

from app.models import \
    MoneroWalletStagenet, \
    MoneroBlockHeightStagenet, \
    MoneroTransactionsStagenet, \
    MoneroUnconfirmedStagenet, \
    MoneroTransOrphanStagenet


# standard json header
headers = {'content-type': 'application/json'}


def update_block_height(newheight):
    current_blockheight = MoneroBlockHeightStagenet.query.get(1)
    current_blockheight.blockheight = newheight
    db.session.add(current_blockheight)


def get_unconfirmed_db(user_id):
    """
    Get uses unconfirmed table
    :param user_id:
    :return:
    """
    unconfirmedtable = MoneroUnconfirmedStagenet.query.\
        filter_by(user_id=user_id)\
        .first()
    return unconfirmedtable


def addtounconfirmed(amount, user_id, txid):
    """
    # this function can track multiple incomming unconfirmed amounts
    :param amount:
    :param user_id:
    :param txid:
    :return:
    """
    unconfirmedtable = get_unconfirmed_db(user_id)

    decimalamount = floating_decimals(amount, 12)
    if unconfirmedtable is None:

        newunconfirmed = MoneroUnconfirmedStagenet(
            user_id=user_id,
            unconfirmed1=0,
            unconfirmed2=0,
            unconfirmed3=0,
            unconfirmed4=0,
            unconfirmed5=0,
        )
        db.session.add(newunconfirmed)
    else:

        if unconfirmedtable.unconfirmed1 == 0:
            unconfirmedtable.unconfirmed1 = decimalamount
            unconfirmedtable.txid1 = txid

        elif unconfirmedtable.unconfirmed2 == 0:
            unconfirmedtable.txid2 = txid
            unconfirmedtable.unconfirmed2 = decimalamount

        elif unconfirmedtable.unconfirmed3 == 0:
            unconfirmedtable.txid3 = txid
            unconfirmedtable.unconfirmed3 = decimalamount

        elif unconfirmedtable.unconfirmed4 == 0:
            unconfirmedtable.txid4 = txid
            unconfirmedtable.unconfirmed4 = decimalamount

        elif unconfirmedtable.unconfirmed5 == 0:
            unconfirmedtable.unconfirmed5 = decimalamount
            unconfirmedtable.txid5 = txid
        else:
            pass

        db.session.add(unconfirmedtable)


def removeunconfirmed(user_id, txid):
    """
    # this function removes the amount from unconfirmed
    :param user_id:
    :param txid:
    :return:
    """

    unconfirmeddelete = get_unconfirmed_db(user_id)

    if unconfirmeddelete.txid1 == txid:
        unconfirmeddelete.txid1 = ''
        unconfirmeddelete.unconfirmed1 = 0

    elif unconfirmeddelete.txid2 == txid:
        unconfirmeddelete.txid2 = ''
        unconfirmeddelete.unconfirmed2 = 0

    elif unconfirmeddelete.txid3 == txid:
        unconfirmeddelete.txid3 = ''
        unconfirmeddelete.unconfirmed3 = 0

    elif unconfirmeddelete.txid4 == txid:
        unconfirmeddelete.txid4 = ''
        unconfirmeddelete.unconfirmed4 = 0

    elif unconfirmeddelete.txid5 == txid:
        unconfirmeddelete.txid5 = ''
        unconfirmeddelete.unconfirmed5 = 0

    else:
        pass

    db.session.add(unconfirmeddelete)


def getbalanceunconfirmed(user_id):

    """
    # this function gets amount of unconfirmed
    :param user_id:
    :return:
    """

    unconfirmeddelete = get_unconfirmed_db(user_id)

    a = Decimal(unconfirmeddelete.unconfirmed1)
    b = Decimal(unconfirmeddelete.unconfirmed2)
    c = Decimal(unconfirmeddelete.unconfirmed3)
    d = Decimal(unconfirmeddelete.unconfirmed4)
    e = Decimal(unconfirmeddelete.unconfirmed5)

    total = a + b + c + d + e

    get_user_wallet = MoneroWalletStagenet.query.\
        filter_by(user_id=user_id).first()
    totalchopped = floating_decimals(total, 12)
    get_user_wallet.unconfirmed = totalchopped

    db.session.add(get_user_wallet)
    return totalchopped


def createorphan(hashid, amount):
    """
    Creates an orphan transaction
    :param hashid:
    :param amount:
    :return:
    """
    checkorphan = MoneroUnconfirmedStagenet.query.\
        filter_by(txid1=hashid).first()
    if checkorphan is None:
        # orphan transaction..put in background.
        trans = MoneroTransOrphanStagenet(
            xmr=amount,
            txid=hashid,
        )
        db.session.add(trans)


def addtransaction(user_id,
                   amount,
                   hashid,
                   new_transaction_blockheight,
                   gettransaction,
                   ):
    """
    Updates/adds existing transaction
    :param user_id:
    :param amount:
    :param hashid:
    :param new_transaction_blockheight:
    :param gettransaction:
    :return:
    """

    # check to see how many confirmations

    current_blockheight = MoneroBlockHeightStagenet.query.get(1)
    current_block = current_blockheight.blockheight

    getuserswallet = MoneroWalletStagenet.query\
        .filter(MoneroWalletStagenet.user_id == user_id)\
        .first()
    if gettransaction.confirmed == 0:
        print("transaction exists:", str(hashid))
        howmanyconfirmations = current_block - new_transaction_blockheight
        print("confirmations: ", howmanyconfirmations)
        print(current_block)
        print(new_transaction_blockheight)
        if howmanyconfirmations <= 11:
            print("unconfirmed")
            # add amount to current balance
            gettransaction.confirmations = howmanyconfirmations
            db.session.add(gettransaction)

            # updating incomming amount incase multiple transactions
        else:
            print("Confirmed")
            removeunconfirmed(user_id=getuserswallet.user_id,
                              txid=hashid)

            currentbalance = getuserswallet.currentbalance
            newbalance = Decimal(currentbalance) + (Decimal(amount))
            getuserswallet.currentbalance = newbalance
            db.session.add(getuserswallet)

            gettransaction.confirmations = howmanyconfirmations
            gettransaction.confirmed = 1

            # get the balance with new incomming
            newtransactiobalance = gettransaction.balance + gettransaction.amount
            gettransaction.balance = newtransactiobalance
            db.session.add(gettransaction)

            update_block_height(newheight=new_transaction_blockheight)
            print("User Balance: ", newbalance)

            db.session.commit()


def createnewtransaction(user_id,
                         amount,
                         hashid,
                         new_transaction_blockheight,
                         old_blockheight):
    """
    Found new transaction..creates it in db
    :param user_id:
    :param amount:
    :param hashid:
    :param old_blockheight:
    :param new_transaction_blockheight:
    :return:
    """
    print("Found new transaction:", str(hashid))
    getuserswallet = MoneroWalletStagenet.query.\
        filter(MoneroWalletStagenet.user_id == user_id)\
        .first()

    # add to transactions
    monero_addtransaction(category=3,
                          amount=amount,
                          user_id=getuserswallet.user_id,
                          txid=hashid,
                          block=new_transaction_blockheight,
                          balance=getuserswallet.currentbalance,
                          confirmed=0,
                          fee=0,
                          address=''
                          )

    # add total of incomming
    addtounconfirmed(amount=amount,
                     user_id=getuserswallet.user_id,
                     txid=hashid
                     )

    if int(old_blockheight) < int(new_transaction_blockheight):
        update_block_height(newheight=new_transaction_blockheight)


def checkincomming(fromblockheight):
    """
    Get rpc incomming deposts
    :param fromblockheight:
    :return:
    """

    rpc_input = {
        "method": "get_bulk_payments",
        "params":
            {"payment_ids ": False,
             "min_block_height": fromblockheight}
    }

    # add standard rpc values
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})

    # execute the rpc request
    response = requests.post(
        url,
        data=json.dumps(rpc_input),
        headers=headers,
        auth=HTTPDigestAuth(rpcusername, rpcpassword))

    response_json = response.json()

    return response_json


def find_new_deposits(blockbacklog):
    """
    Controller function for script
    :return:
    """

    current_blockheight_query = MoneroBlockHeightStagenet.query.get(1)
    current_block = current_blockheight_query.blockheight

    blocksfromcurrent = current_block - blockbacklog
    response_json = checkincomming(fromblockheight=blocksfromcurrent)
    if response_json is None or response_json["result"] == {}:
        print(response_json)
        print("no incomming")
    else:
        for incpayments in response_json["result"]["payments"]:
            # info about deposite from json
            print("*" * 10)
            new_transaction_blockheight = incpayments['block_height']

            incomming_address = incpayments['address']
            hashid = incpayments['tx_hash']
            amount = Decimal(get_money(str(incpayments['amount'])))

            # get user with that payment id
            getuserswallet = MoneroWalletStagenet.query.\
                filter(MoneroWalletStagenet.address1 == incomming_address)\
                .first()

            if getuserswallet is None:
                createorphan(hashid, amount)

            else:
                user_id = getuserswallet.user_id
                print("USER:", getuserswallet.user_id)
                # see if already in db
                gettransaction = MoneroTransactionsStagenet.query\
                    .filter_by(txid=hashid)\
                    .first()

                if gettransaction:

                    # update transaction
                    addtransaction(user_id,
                                   amount,
                                   hashid,
                                   new_transaction_blockheight,
                                   gettransaction,
                                   )
                else:
                    # create a new transaction
                    createnewtransaction(user_id,
                                         amount,
                                         hashid,
                                         new_transaction_blockheight,
                                         current_block)

                # get user unconfirmed balance
                getbalanceunconfirmed(user_id)

        db.session.commit()


if __name__ == '__main__':
    find_new_deposits(blockbacklog=100)
