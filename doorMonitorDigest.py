#!/usr/bin/env python3

import os, os.path, sys, getopt, json, smtplib, time, datetime, http.client, urllib
from email.message import EmailMessage

def send_email(sendToAddress, userName, password, message):

	# send via gmail (the email address has to be gmail)
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()

        # this is way easier than I expected
	server.login(userName, password)

	msg = EmailMessage()
	msg['Subject'] = "Daily door activity digest"
	msg['From'] = userName
	msg['To'] = sendToAddress
	msg.set_content(message)

        # actually sends it
	server.send_message(msg)
	server.quit()

def main(argv):

        # parse options, all are required
	try:
		opts, args = getopt.getopt(sys.argv[1:], "", ["file=","target="])
	except (getopt.GetoptError, e):
		print('pingCheck.py: {0}'.format(str(e)))
		sys.exit(2)

	for opt, arg in opts:
		if opt in ['--file']:
			emailConfigFile = arg
                # email address to send to
		elif opt in ['--target']:
			sendTo = arg

        # load the config file
	with open(emailConfigFile) as conf:
		configData = json.load(conf)

	sendFrom = configData["username"]
	password = configData["password"]

	logFile = configData["outputfile"]

	if os.path.isfile(logFile):
		with open(logFile,"r") as sf:
			allToSend = sf.read()
		send_email(sendTo, sendFrom, password, allToSend)

# call main
if __name__ == "__main__":
	main(sys.argv[1:])
