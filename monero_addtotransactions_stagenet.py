from datetime import datetime

from app import db
from app.models import MoneroTransactionsStagenet


def monero_addtransaction(category,
                          amount,
                          user_id,
                          txid,
                          block,
                          balance,
                          confirmed,
                          fee,
                          address):
    """
    # this function adds the transaction recording
    :param category:
    :param amount:
    :param user_id:
    :param txid:
    :param block:
    :param balance:
    :param confirmed:
    :param fee:
    :param address:
    :return:
    """

    now = datetime.utcnow()

    trans = MoneroTransactionsStagenet(
        category=category,
        user_id=user_id,
        confirmations=0,
        confirmed=confirmed,
        txid=str(txid),
        amount=amount,
        balance=balance,
        block=int(block),
        created=now,
        address=address,
        fee=fee,
        orderid=0,
        senderid=0,
        digital_currency=4,
        note=''

    )
    db.session.add(trans)
    db.session.commit()

