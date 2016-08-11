import os
import logging
import logging.handlers
import sys
import getopt

def usage():
  print "Logger tester; for example: python test.py --server=128.97.98.11:25000 --url=/log/insert --name=zhehao --msg=log!" 
  return

if __name__ == "__main__":
  # Arg parse
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:u:n:m:", ["help", "server=", "url=", "name=", "msg="])
  except getopt.GetoptError as err:
    # print help information and exit:
    print str(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
  
  server = '127.0.0.1:5000'
  url = '/log/insert'
  username = 'test_user'
  msg = 'my log'

  for o, a in opts:
    if o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-s", "--server"):
      server = a
    elif o in ("-u", "--url"):
      url = a
    elif o in ("-n", "--name"):
      username = a
    elif o in ("-m", "--msg"):
      msg = a  
    else:
      assert False, "unhandled option"

  # Logger configuration
  rootLogger = logging.getLogger('')
  rootLogger.setLevel(logging.DEBUG)

  print "Test logging at: " + server + url

  httpHandler = logging.handlers.HTTPHandler(
    server,
    url,
    method='POST',
  )
  # don't bother with a formatter, since a socket handler sends the event as
  # an unformatted pickle
  rootLogger.addHandler(httpHandler)

  # Now, we can log to the root logger, or any other logger. First the root...
  #logging.info('Jackdaws love my big sphinx of quartz.')

  # Now, define a couple of other loggers which might represent areas in your
  # application:
  logger1 = logging.getLogger(username)
  #logger2 = logging.getLogger('myapp.area2')

  d = {'host': '192.168.0.1', 'user': username, 'associated_object': '{\"character\": \"zhehao\"}'}

  logger1.debug(msg, extra=d)
  #logger1.info('How quickly daft jumping zebras vex.')
  #logger2.warning('Jail zesty vixen who grabbed pay from quack.')
  #logger2.error('The five boxing wizards jump quickly.')