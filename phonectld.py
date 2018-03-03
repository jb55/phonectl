

import sys
import re
import logging
import os
import getpass
import time
import socket

from time import sleep
from collections import deque
from optparse import OptionParser
from sleekxmpp import ClientXMPP

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input



class PhoneCtl(ClientXMPP):

    def __init__(self, jid: str, password: str, phonejid: str):
        ClientXMPP.__init__(self, jid, password)

        self.available = False
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("changed_status", self.phone_status)
        self.phonejid = phonejid
        self.queue = deque()

        # If you wanted more functionality, here's how to register plugins:
        # self.register_plugin('xep_0030') # Service Discovery
        # self.register_plugin('xep_0199') # XMPP Ping

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

        # If you are working with an OpenFire server, you will
        # need to use a different SSL version:
        # import ssl
        # self.ssl_version = ssl.PROTOCOL_SSLv3

    def phone_status(self, data):
        status = data['type']
        jid = str(data['from']).split('/')[0]
        if jid == self.phonejid:
            logging.info("phone_status %s %s", jid, status)
            self.available = status == "available"

    def respond(self, msg: str) -> None:
        self.ctlconnection.sendall(bytes(msg, 'utf-8'))
        self.ctlconnection.close()
        self.done_response = True

    def message(self, msg: str) -> None:
        self.respond(msg['body'] + "\n")

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()


    def listen(self, socket_path: str, timeout=5000) -> bool:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        ok = True

        try:
            os.unlink(socket_path)
        except:
            pass

        print(socket_path)
        sock.bind(socket_path)
        sock.listen(1)
        done = False
        self.done_response = False

        while not done:
            tries = 0
            timed_out = False
            self.done_response = False
            connection, client_address = sock.accept()
            self.ctlconnection = connection

            try:
                buf = bytes()
                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(1024)

                    if not self.available:
                        self.respond("phone is offline\n")
                        break

                    if data:
                        buf += data

                    if not data or len(data) < 1024:
                        cmd = re.sub("\n$", "", buf.decode("utf-8"))
                        logging.debug('received %s', cmd)
                        if cmd == 'quit':
                            connection.close()
                            done = True
                            break
                        logging.info("sending cmd %s", cmd)
                        self.cmd(cmd)
                        while not timed_out and not self.done_response:
                            time.sleep(0.05)
                            tries += 1
                            timed_out = 1000 * 0.05 * tries >= timeout
                        if timed_out:
                            logging.info("timed_out %s", str(timed_out))
                        break

            except Exception as e:
                ok = False
                logging.error(e)
            finally:
                # Clean up the connection
                connection.close()
        sock.close()
        return ok

    def cmd(self, msg: str) -> None:
        self.send_message(mto=self.phonejid, mbody=msg, mtype='chat')



if __name__ == '__main__':
    # Setup the command line arguments.
    # Setup logging.
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(message)s')

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.

    passwd   = os.environ['PHONECTLPASS']
    user     = os.environ['PHONECTLUSER']
    phone    = os.environ['PHONECTLPHONE']
    sockpath = os.getenv('PHONECTLSOCK', '/tmp/phonectl.sock')

    phonectl = PhoneCtl(user, passwd, phone)

    phonectl.register_plugin('xep_0030') # Service Discovery
    phonectl.register_plugin('xep_0199') # XMPP Ping

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    if phonectl.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        phonectl.process(block=False)
        phonectl.listen(sockpath)
        phonectl.disconnect(wait=True)
    else:
        print("Unable to connect.")
