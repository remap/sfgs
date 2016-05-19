import os
import logging
import logging.handlers
import sys

if __name__ == "__main__":
  rootLogger = logging.getLogger('')
  rootLogger.setLevel(logging.DEBUG)

  httpHandler = logging.handlers.HTTPHandler(
    '127.0.0.1:5000',
    '/insert',
    method='POST',
  )
  # don't bother with a formatter, since a socket handler sends the event as
  # an unformatted pickle
  rootLogger.addHandler(httpHandler)

  # Now, we can log to the root logger, or any other logger. First the root...
  logging.info('Jackdaws love my big sphinx of quartz.')

  # Now, define a couple of other loggers which might represent areas in your
  # application:

  logger1 = logging.getLogger('myapp.area1')
  logger2 = logging.getLogger('myapp.area2')

  d = {'host': '192.168.0.1', 'user': 'fbloggs'}

  logger1.debug('Quick zephyrs blow, vexing daft Jim.', extra=d)
  logger1.info('How quickly daft jumping zebras vex.')
  logger2.warning('Jail zesty vixen who grabbed pay from quack.')
  logger2.error('The five boxing wizards jump quickly.')