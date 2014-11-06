import os
import sys
import signal
import logging

from optparse import OptionParser

from flask import current_app

from flask.ext.script import Command, Manager, Option

from address_deduper import *

def serve_forever(listener):
   logging.info('Starting worker with pid: {}, parent pid: {}'.format(os.getpid(), os.getppid()))
   WSGIServer(listener, app).serve_forever() 

class GeventServer(Command):
    option_list = (
        Option('--host', '-t', dest='host', default='0.0.0.0'),
        Option('--port', '-p', dest='port', type=int, default=5000),
    )

    def __init__(self, manager):
        self.manager = manager

    def run(self, host, port, *args, **kw):
        from gevent.pywsgi import WSGIServer
        from gevent.monkey import patch_all; patch_all()
        logger = logging.getLogger('gevent')
        logger.info('Starting gevent on port: {}'.format(port))
        http_server = WSGIServer(('', port), self.manager.app)
        http_server.serve_forever()


def sigterm_handler(signum, frame):
    if hasattr(manager.command, 'service'):
        print >> sys.stederr, "%s done" % manager.command.service
    else:
        print >> sys.stderr, "Done"
    sys.exit(0)


option_parser = OptionParser()
option_parser.add_option('-c', '--config', dest='config',
                         help='config name', metavar='CONFIG')

def main():
    env = 'dev'
    try:
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'use_env')
        env = open(env_file).read().strip()
        if env != 'dev':
            config_module = env + '_config'
            __import__('address_normalizer.' + config_module)
    except IOError:
        pass

    manager = Manager(create_app)
    manager.add_option('-e', '--env', required=False, default=env)
    manager.add_option('-c', '--config', required=False)

    manager.add_command('serve', GeventServer(manager))

    signal.signal(signal.SIGTERM, sigterm_handler)

    manager.run()

if __name__ == '__main__':
    main()
