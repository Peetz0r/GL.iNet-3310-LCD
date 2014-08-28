#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, subprocess, datetime, urllib2, random, BaseHTTPServer, urlparse, json, logging, logging.handlers, socket, os.path, signal

class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		global screen
		if(self.path == "/"):
			self.send_response(200)
			try:
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				f = open("/root/index.html")
				self.wfile.write(f.read())
				f.close()
			except:
				logging.exception("")
		elif(self.path == "/screen"):
			self.send_response(200)
			try:
				self.send_header('Content-type', 'text/json')
				self.end_headers()
				self.wfile.write(json.dumps(screen))
			except:
				logging.exception("")
		elif(self.path == "/source"):
			self.send_response(200)
			self.end_headers()
			f = open(__file__)
			self.wfile.write(f.read())
			f.close()
		else:
			self.send_response(404)

	def do_POST(self):
		global screen
		if(self.path == "/"):
			self.send_response(200)
			try:
				length = int(self.headers.getheader('content-length'))
				data = json.loads(self.rfile.read(length))
				gotoxy(data[0], data[1])
				lcd_data(data[2])
				screen[data[0]][data[1]] = data[2]
			except:
				logging.exception("")
		else:
			self.send_response(404)

def signal_handler(signal, frame):
	logging.info('SIGINT received, shutting down')
	shutdown()
	sys.exit(0)

def main():
	setup()

	if os.path.isfile("/root/init.png"):
		from PIL import Image
		im = Image.open("/root/init.png")
		if im.size == (84,48):
			logging.info("drawing init.png")
			pix = im.load()
			gotoxy(0,0)
			for i in range(6):
				for j in range(84):
					data = 0
					for k in range(8):
						if pix[j, 8*i+k] == 1:
							data += 2 ** k
					screen[j][i] = data
					lcd_data(data)

	server = BaseHTTPServer.HTTPServer(('', 80), WebHandler)
	logging.info('started httpserver')
	server.serve_forever()

def gotoxy(x,y):
	lcd_cmd(x+128)
	lcd_cmd(y+64)

def cls():
	lcd_cmd(0x24)
	gotoxy(0,0)
	for i in range(84):
		for j in range(6):
			lcd_data(0)
	lcd_cmd(0x20)

def setup():
	global fp_sclk, fp_din, fp_dc, fp_rst, screen

	signal.signal(signal.SIGINT, signal_handler)

	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	handler = logging.handlers.SysLogHandler(address = ("192.168.3.10", 514))
	handler.setFormatter(logging.Formatter(fmt="[3310]: %(message)s"))
	logger.addHandler(handler)
	logging.info("starting 3310 setup")

	for gpio in (18, 19, 21, 22):
		fp_export = open("/sys/class/gpio/export","w")
		fp_export.write(str(gpio))
		fp_export.close()
		fp_direction = open("/sys/class/gpio/gpio"+str(gpio)+"/direction","w")
		fp_direction.write("out")
		fp_direction.close()

	fp_sclk = open("/sys/class/gpio/gpio19/value","w", 0)
	fp_din  = open("/sys/class/gpio/gpio18/value","w", 0)
	fp_dc   = open("/sys/class/gpio/gpio22/value","w", 0)
	fp_rst  = open("/sys/class/gpio/gpio21/value","w", 0)

	fp_rst.write("0")
	fp_rst.write("1")

	lcd_cmd(0x21) # extended mode
	lcd_cmd(0xc8) # contrast
	lcd_cmd(0x05) # start position
	lcd_cmd(0x40) # start position
	lcd_cmd(0x14) # bias mode
	lcd_cmd(0x20) # clear
	lcd_cmd(0x0C) # normal mode

	screen = [[0 for x in xrange(6)] for x in xrange(84)]

	cls()

def shutdown():
	global fp_sclk, fp_din, fp_dc, fp_rst
	fp_sclk.close()
	fp_din.close()
	fp_dc.close()
	fp_rst.close()
	for gpio in (18, 19, 21, 22):
		fp_unexport = open("/sys/class/gpio/unexport","w")
		fp_unexport.write(str(gpio))
		fp_unexport.close()

def SPI(c):
	for i in range(8):
		if((c & (1 << (7-i))) > 0):
			fp_din.write("1")
		else:
			fp_din.write("0")
		fp_sclk.write("1")
		fp_sclk.write("0")

def lcd_cmd(c):
	fp_dc.write("0")
	SPI(c)

def lcd_data(c):
	fp_dc.write("1")
	SPI(c)

if __name__ == "__main__":
	main()
