from app import db
from app.models import MoneroWalletWorkStagenet


# run once every ten minutes
def deleteoldorder():

    getwork = MoneroWalletWorkStagenet.query\
        .filter_by(type=0)\
        .all()
    for f in getwork:
        db.session.delete(f)
    db.session.commit()


if __name__ == '__main__':
    deleteoldorder()
