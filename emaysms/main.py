import sys
from getopt import gnu_getopt as getopt, GetoptError

from . import EmaySMS, EmaySMSException

USAGE = '''
Usage: emaysms.py -k [KEY FILE] [ACTION] [ARGS]


Example
-------


Register a key file. A key file must be registered before it can be used:

    emaysms.py register -k [KEY FILE]


De-register a key file:

    emaysms.py deregister -k [KEY FILE]


Send an SMS. If `-t` option is omitted, the message is sent immediately. Otherwise, the message is sent at the given time by `-t`. SMS content is read from stdin, with up to 500 Chinese characters or 1,000 ASCII characters.

    echo "Hello World!" | emaysms.py send -k [KEY FILE] [-t YYYYMMDDHHMMSS] PHONE1 [PHONE2 ...]


Query account balance:

    emaysms.py balance -k [KEY FILE]


Recharge an account:

    emaysms.py recharge -k [KEY FILE] [PREPAID CARD NUMBER] [PREPAID CARD PASSWORD]


Change password for a key file. Remember to change the old password in the key file:

    emaysms.py changepassword -k [KEY FILE]  [NEW PASSWORD]



Key file format
---------------

    cdkey=AAAA-BBB-CCCC-DDDD
    password=123456
'''


def parse_key_file(filename):
    try:
        for line in open(filename).readlines():
            line = line.strip()
            if line.startswith('cdkey'):
                k, v = line.split('=', 1)
                cdkey = v.strip()
            elif line.startswith('password'):
                k, v = line.split('=', 1)
                password = v.strip()
        return cdkey, password
    except IOError as e:
        if e.errno == 2:
            sys.exit('Key file "{0}" not found. '.format(filename))


class Actions(object):

    ' Command containter '

    @staticmethod
    def send(emay, opts, args):
        if len(args) < 1:
            sys.exit(USAGE)
        numbers = args

        try:
            encoding = opts.get('-c', 'utf8')
            message = sys.stdin.read()
            msg = message.decode(encoding)
        except UnicodeDecodeError:
            sys.exit('Failed to decode message using encoding "{0}". '.format(encoding))

        emay.send(numbers, msg)

    @staticmethod
    def sent(emay, opts, args):
        print emay.sent

    @staticmethod
    def balance(emay, opts, args):
        print emay.balance

    @staticmethod
    def recharge(emay, opts, args):
        card_number = args[0]
        card_password = args[1]
        emay.recharge(card_number, card_password)

    @staticmethod
    def changepassword(emay, opts, args):
        new_password = args[0]
        emay.change_password(new_password)

    @staticmethod
    def register(emay, opts, args):
        emay.register()

    @staticmethod
    def deregister(emay, opts, args):
        emay.deregister()


def main():

    try:
        opts, args = getopt(sys.argv[1:], 'k:hc:', ['help'])
        opts = dict(opts)
    except GetoptError as e:
        sys.exit(str(e) + '\n' + USAGE)

    if '-h' in opts or '--help' in opts:
        sys.exit(USAGE)

    if len(args) > 0:
        action = args[0].lower()
        args = args[1:]
    else:
        sys.exit('Action required. ')

    if not hasattr(Actions, action):
        sys.exit('Unknonw action {0}'.format(action))

    if '-k' in opts:
        cdkey, password = parse_key_file(opts['-k'])
        emay = EmaySMS(cdkey, password)
    else:
        sys.exit('Key file "-k" required. ')

    try:
        getattr(Actions, action)(emay, opts, args)
    except EmaySMSException as e:
        sys.exit(e)
