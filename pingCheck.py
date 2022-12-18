
#!/usr/bin/env python3

import os, sys, getopt, json, smtplib

def send_email(sendToAddress, userName, password, message):

	# send via gmail (the email address has to be a gmail
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()

	# this is way easier than I expected
	server.login(userName, password)

	# use message headers -- you need a blank line between the subject and the message body
	message = "\r\n".join(["From: {0}".format(userName), "To: {0}".format(sendToAddress), "Subject: Ping test failed", message])

	# actually sends it
	server.sendmail(userName, sendToAddress, message)
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
			sendEmail = True
		elif opt in ['-f', '--file']:
			emailConfigFile = arg
		elif opt in ['--target']:
			sendTo = arg

	print("Email config file {0}".format(emailConfigFile))

	with open(emailConfigFile) as conf:
		configData = json.load(conf)

	errorMessage = "Hello,\nFailed when testing the following: \n{0}\n -Rpi"
	failedList = []
	for x in range(len(configData["monitor"])):

		ip = configData["monitor"][x]["IP"]
		name = configData["monitor"][x]["name"]

		print("Pinging {0} using IP {1}".format(name, ip))

		response = os.system("ping -c 1 " + ip)

		#and then check the response...
		if response == 0:
			print("Got a valid response for {0} ({1})".format(name, ip))
		else:
			print("Did not get a valid response for {0} ({1})".format(name, ip))
			failedList.append("{0},{1}".format(name, ip))

	if len(failedList) > 0 and sendEmail:
		failedStr = "\n".join(failedList)

		print("Sending email to {0} with {1} failures".format(sendTo, len(failedList)))

		send_email(sendTo, configData["username"], configData["password"], errorMessage.format(failedStr))

# call main
if __name__ == "__main__":
	main(sys.argv[1:])

