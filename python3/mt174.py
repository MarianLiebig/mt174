#!/usr/bin/env python

#links:
#https://wiki.volkszaehler.org/hardware/channels/meters/power/edl-ehz/iskraemeco_mt174
#https://volkszaehler-users.demo.volkszaehler.narkive.com/oAtfnMjs/vz-users-iskra-mt-171-vzlogger-conf

import serial
import time
import re
import subprocess
import datetime
import logging
from logging.handlers import RotatingFileHandler
import sys

log_file = 'mt174.log'
logger   = logging.getLogger()
logger.setLevel(logging.DEBUG)
fmt      = logging.Formatter('%(asctime)s\t%(filename)s(%(lineno)d)\t%(levelname)s\t%(funcName)s()\t%(message)s')
log_hdlr = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=10)
log_hdlr.setFormatter(fmt)
con_hdlr = logging.StreamHandler(sys.stdout)
con_hdlr.setFormatter(fmt)
logger.addHandler(log_hdlr)
logger.addHandler(con_hdlr)

if __name__ == '__main__':
   t_start = time.time()
   
   SERIALPORT = '/dev/ttyUSB0'
   BAUDRATE = 300

   ser = serial.Serial(SERIALPORT, BAUDRATE, serial.SEVENBITS, serial.PARITY_EVEN)
   try:
      ser.timeout = 5
      ser.write(b'\x2F\x3F\x21\x0D\x0A')

      time.sleep(0.2)
      
      #regex pattern to identify current meter reading
      pat = r'.*?\((.*)\*kWh.*'

      while True:
         response = ser.readline()
         logger.debug(f'{response}')
         if response == b'!\r\n':
            break    
         
         #increase baud rate after identifier
         if b'/ISk5MT174-0001' in response:
            ser.write(bytearray('\x06050\r\n','ascii'))
            time.sleep(0.2)
            ser.baudrate=9600

         #this is what I'm interested in ...
         if b'1-0:1.8.0*255' in response:
            match = re.search(pat, response.decode())
            if match:
               logger.debug('match')
               value = match.group(1)
               logger.info(f'current meter reading: {value}')
            else:
               logger.warning('no match')

   except Exception as e:
      logger.error(f'caught exception {e}')
      logger.warning('trying to read everything and close the port')
      while True:
         dat = ser.read() #until timeout
         logger.warning(f'read: {dat}')
         if len(dat) == 0:
            logger.warning('seems empty')
            break
   ser.close()
   logger.info(f'took {time.time()-t_start:.2} s')
