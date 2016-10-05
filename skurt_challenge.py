import sys
import time
import math
import json
import urllib
import logging
import smtplib
import requests
import email_config
from optparse import OptionParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Written by Ben Johnston (github: benjdj6)
#Last Edited: 5 Oct, 2016

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename="skurt-challenge.log",level=logging.DEBUG,format=FORMAT)

#Keeps track of data freshness
oldLoc = {}
#Keeps track of which cars are already considered out of bounds
#and what time a warning email was last sent for them
outCars = {}

#Sets options for test mode and quiet mode
parser = OptionParser()
parser.set_defaults(testMode=False, quietMode=False)
parser.add_option("-t", "--test", action="store_true", dest="testMode",
	help="Runs script in testMode so only car id 11 is checked every 5 seconds.")
parser.add_option("-q", "--quiet", action="store_true", dest="quietMode",
	help="""Only sends email once per out-of-bounds offense. Once car returns in-bounds \
and goes out-of-bounds again a new email will be generated and sent.""")
(options, args) = parser.parse_args()

#Builds and sends the email based on parameters stored in email_config.py
def notify(subj, plain, html):
	#Build the message and send via SMTP connection to Gmail
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subj
	msg['From'] = email_config.sender

	plain = MIMEText(plain, 'plain')
	html = MIMEText(html, 'html')

	msg.attach(plain)
	msg.attach(html)

	try:
		#Connect to Gmail and send the email
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(email_config.sender,email_config.email_pass)
		server.sendmail(email_config.sender,email_config.recipients,msg.as_string())
		server.close()        
		logging.info("Successfully sent email: {0}".format(subj))
		return True
	except smtplib.SMTPException:
		logging.error("Error sending email with message", msg)
		return False

#Checks if pos is contained within the range defined by poly
def insideRange(pos,poly):
	#Check if position is one of the vertices
	if pos in poly:
		return True
	#Check if position is on a boundary
	for i in range(1, len(poly)):
		a = poly[i-1]
		b = poly[i]
		
		dist_ab = ((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2)
		dist_ab = math.sqrt(dist_ab)
		
		dist_apos = ((a[0] - pos[0]) ** 2) + ((a[1] - pos[1]) ** 2)
		dist_apos = math.sqrt(dist_apos)

		dist_posb = ((pos[0] - b[0]) ** 2) + ((pos[1] - b[1]) ** 2)
		dist_posb = math.sqrt(dist_posb)

		if dist_apos + dist_posb == dist_ab:
			return True
	#Check how many boundaries a line drawn from position crosses
	#If an odd number of boundaries are crossed then position is inside
	#If even, outside
	inside = False
	a = poly[0]
	for i in range(0, len(poly)+1):
		xinter = None
		b = poly[i % len(poly)]

		if pos[1] > min(a[1], b[1]) and pos[1] <= max(a[1], b[1]) and pos[0] <= max(a[0], b[0]):
			if a[1] != b[1]:
				xinter = (pos[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]) + a[0]
			if a[0] == b[0] or xinter is not None and pos[0] <= xinter:

				inside = not inside
		a = b
	return inside

#If the car is already marked out of bounds and we're running in quiet mode
#then don't send a warning email. If we aren't in quiet mode
#send an email if one hasn't been sent for that car in at least 5 minutes
def shouldSendEmail(carID):
	if carID not in outCars:
		return True
	elif carID in outCars and time.time()-outCars[carID] >= 300:
		if options.quietMode:
			return False
		return True
	else:
		return False

def polling(carIDs, defSleepTime=120, newDataSleepTime=10):
	i = 0
	while True:
		try:
			stime = defSleepTime
			#Reset i to prevent going out of range
			if i > len(carIDs) - 1:
				i = 0
			resp = requests.get("http://skurt-interview-api.herokuapp.com/carStatus/{0}".format(carIDs[i]), 
				timeout = 10)

			if resp.status_code != 200:
				#If the server doesn't return OK send an email alert
				subj = email_config.err_subj.format(resp.status_code)
				plain = email_config.err_plain_msg.format(resp.status_code)
				html = resp.text
				notify(subj, plain, html)
			else:
				data = resp.text
				resp = resp.json()
				position = resp["features"][0]["geometry"]["coordinates"]
				polygon = resp["features"][1]["geometry"]["coordinates"][0]

				logging.debug("Server response: {0}".format(data))
				logging.debug("Last known locations: {0}".format(oldLoc))
				logging.debug("Cars currently out: {0}".format(outCars))
				logging.debug("Is Car #{0} inside range: {1}".format(carIDs[i], 
					insideRange(position, polygon)))

				if carIDs[i] not in oldLoc or oldLoc[carIDs[i]] != position:
					#When new data comes in reduce sleep time to 10 seconds for more
					#accurate and timely warnings
					oldLoc[carIDs[i]] = position
					stime = newDataSleepTime
				#If the car is out of range then send an email warning
				if not insideRange(position, polygon) and shouldSendEmail(carIDs[i]):
					#Generate a url for a geojson map to send in the email
					urldata = urllib.quote(data, safe = '')
					carmap = "http://geojson.io/#data=data:application/json,{0}".format(urldata)

					#Get relevant email data from email_config
					subj = email_config.oob_subj.format(carIDs[i])
					plain = email_config.oob_plain_msg.format(carIDs[i], carmap)
					html = email_config.oob_html_msg.format(carIDs[i], carmap)
					notify(subj, plain, html)
					#Mark the car as being out of bounds
					outCars[carIDs[i]] = time.time()

				elif insideRange(position, polygon) and carIDs[i] in outCars:
					#Remove the car as it is now in bounds.
					del outCars[carIDs[i]]
			i += 1
		#If requests raises an exception send an warning email as something may be
		#wrong with the location API
		except requests.exceptions.RequestException:
			notify(email_config.tout_subj, email_config.tout_plain, None)
			break
		time.sleep(stime)

def main():
	if options.testMode:
		print ("Polling in Test Mode...")
		polling([11], 5, 5)
	else:
		print ("Polling...")
		polling([1,2,3,4,5,6,7,8,9,10])

if __name__ == "__main__":
    main()
