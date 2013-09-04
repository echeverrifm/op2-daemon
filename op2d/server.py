
from application import log
from application.notification import IObserver, NotificationCenter
from application.python import Null
from application.python.types import Singleton
from sipsimple.account import Account, BonjourAccount
from sipsimple.application import SIPApplication
from sipsimple.configuration.settings import SIPSimpleSettings
from sipsimple.storage import FileStorage
from threading import Event
from zope.interface import implements

from op2d.accounts import AccountModel
from op2d.configuration.account import AccountExtension, BonjourAccountExtension
from op2d.configuration.settings import SIPSimpleSettingsExtension
from op2d.resources import ApplicationData
from op2d.sessions import SessionManager
from op2d.web import WebHandler

__all__ = ['OP2Daemon']


class OP2Daemon(object):
    __metaclass__ = Singleton
    implements(IObserver)

    def __init__(self):
        self.application = SIPApplication()
        self.stop_event = Event()

        Account.register_extension(AccountExtension)
        BonjourAccount.register_extension(BonjourAccountExtension)
        SIPSimpleSettings.register_extension(SIPSimpleSettingsExtension)

        self.account_model = AccountModel()
        self.session_manager = SessionManager()
        self.web_handler = WebHandler()

    def start(self):
        self.account_model.start()
        self.session_manager.start()
        notification_center = NotificationCenter()
        notification_center.add_observer(self)
        notification_center.add_observer(self, sender=self.application)
        self.application.start(FileStorage(ApplicationData.directory))

    def stop(self):
        self.session_manager.stop()
        self.account_model.stop()
        self.application.stop()
        self.application.thread.join()
        self.stop_event.set()

    def handle_notification(self, notification):
        handler = getattr(self, '_NH_%s' % notification.name, Null)
        if not notification.name.startswith('SIPEngine'):
            print notification
        handler(notification)

    def _NH_SIPApplicationDidStart(self, notification):
        log.msg('SIP application started')
        self.web_handler.start()

    def _NH_SIPApplicationWillEnd(self, notification):
        self.web_handler.stop()

    def _NH_SIPApplicationDidEnd(self, notification):
        log.msg('SIP application ended')

