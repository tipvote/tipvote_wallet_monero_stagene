from app import db
from app.models import Notifications
import datetime


def notification(thetypeofnote, user_id):
    now = datetime.datetime.utcnow()
    addnotice = Notifications(
                            created=now,
                            read=0,
                            user_id=user_id,
                            user_name='',
                            subcommon_id=0,
                            subcommon_name=0,
                            post_id=0,
                            comment_id=0,
                            msg_type=thetypeofnote

                             )
    db.session.add(addnotice)
    db.session.commit()
