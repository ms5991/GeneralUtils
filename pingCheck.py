
#!/usr/bin/env python3

import os, sys, getopt, json, smtplib


def send_email(sendToAddress, emailConfigFile):

	print("Opening {0}".format(emailConfigFile))
	# load config data
	with open(emailConfigFile) as conf:
		print('Loading json email data...')
		emailData = json.load(conf)

	# send via gmail (the email address has to be a gmail
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()

	# this is way easier than I expected
	server.login(emailData["username"], emailData["password"])

	# use message headers -- you need a blank line between the subject and the message body
	message = "\r\n".join(["From: {0}".format(emailData["username"]), "To: {0}".format(sendToAddress), "Subject: Ping test failed", "\nHello, a ping test failed. -Rpi"])

	# actually sends it
	server.sendmail(emailData["username"], sendToAddress, message)
	server.quit()

	print ('Successfully sent email to {0}'.format(sendToAddress))

def main(argv):

	try:
		opts, args = getopt.getopt(sys.argv[1:], "e", ["file=","target="])
	except (getopt.GetoptError, e):
		print('pingCHeck.py: {0}'.format(str(e)))
		sys.exit(2)

	emailConfigFile = 'email_config.json'
	sendEmail = False
	sendTo = None
	for opt, arg in opts:
		if opt in ['-e']:
			print("Sending email due to opt [{0}]".format(opt))
			sendEmail = True
		elif opt in ['-f', '--file']:
			emailConfigFile = arg
		elif opt in ['--target']:
			sendTo = arg

	print("Email config file {0}".format(emailConfigFile))

	response = os.system("ping -c 1 " + "192.168.1.10")

	#and then check the response...
	if response == 0:
		print("Got a valid response")
	else:
		print("Did not get a valid response")

		if sendEmail:
			send_email(sendTo, emailConfigFile)

# call main
if __name__ == "__main__":
	main(sys.argv[1:])

