
#!/usr/bin/env python3

import os, os.path, sys, getopt, json, smtplib, time, datetime

def send_email(sendToAddress, userName, password, message):

	# send via gmail (the email address has to be gmail)
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

	# parse options, all are required
	try:
		opts, args = getopt.getopt(sys.argv[1:], "e", ["file=","target="])
	except (getopt.GetoptError, e):
		print('pingCheck.py: {0}'.format(str(e)))
		sys.exit(2)

	sendEmail = False
	sendTo = None

	for opt, arg in opts:
		# only send email if -e is used
		if opt in ['-e']:
			sendEmail = True
		# config file location
		elif opt in ['--file']:
			emailConfigFile = arg
		# email address to send to
		elif opt in ['--target']:
			sendTo = arg

	print("Email config file {0}".format(emailConfigFile))

	# load the config file
	with open(emailConfigFile) as conf:
		configData = json.load(conf)

	# if an email is sent, this is the format string
	errorMessage = "Hello,\nThe following endpoints did not respond to ping requests: \n{0}\n -Rpi"

	# keep track of failed addresses that must
	# result in an email this time
	mustSend = []

	# keep track of all failures regardless of email
	allFailures = []

	# number of retries to ping until marking as a failure
	retryLimit = configData["retrylimit"]

	# sleep between retries for this many seconds
	retryDelay = configData["retrydelay"]

	# location for the state file, indicating when emails
	# have been sent for different IP addresses
	stateFileLocation = configData["statefilelocation"]

	# how many seconds to wait before sending an email
	# again for a failed target
	emailLimit = configData["emaillimit"]

	# if the state file exists, load it. If not,
	# create a new dictionary
	if os.path.exists(stateFileLocation):
		with open(stateFileLocation) as sf:
			stateFile = json.load(sf)
	else:
		stateFile = {}

	# get the current time
	now = datetime.datetime.utcnow()
	f = "%Y-%m-%dT%H:%M:%S.%fZ"

	# loop through the ip addresses in the config
	# file to monitor
	for x in range(len(configData["monitor"])):
		# get the IP address to ping
		ip = configData["monitor"][x]["IP"]

		# friendly name of the IP address
		name = configData["monitor"][x]["name"]

		# id to use for state
		identifier = "{0},{1}".format(name, ip)

		# retry up to the limit or until a success is encountered
		for i in range(retryLimit):

			print("Pinging {0} using IP {1}".format(name, ip))

			# execute the ping
			response = os.system("ping -c 1 " + ip)

			# and then check the response...
			if response == 0:
				# a single success is sufficient to stop checking this IP address
				print("Got a valid response for {0} ({1})".format(name, ip))
				break
			elif i == retryLimit - 1:
				# we have retried up to the limit, so this IP address failed
				print("Did not get a valid response for {0} ({1})".format(name, ip))

				# keep track of all failures regardless of
				# state file. If we are going to send an email for
				# any failure, might as well include all failures
				allFailures.append(identifier)

				# check if the state file contains data for this IP address. If not,
				# send an email for this IP. If it does, check if the last time we sent an
				# email was within the emailLimit from config file. If yes, skip email
				# this time. If no, send email.
				if (identifier not in stateFile) or (identifier in stateFile and (now - datetime.datetime.strptime(stateFile[identifier], f)).seconds > emailLimit):
					# this id requires an email to be sent this time
					mustSend.append(identifier)
				else:
					# skip email this time due to statefile
					print("Skipping email for {0} with ip {1} because it has not been {2} seconds since last email".format(name, ip, emailLimit))
			else:
				# failure, sleep for the delay and then retry
				print("Got failure for {0} but will retry...".format(identifier))
				time.sleep(retryDelay)

	# if any IP addresses failed, send an email for
	# all IP addresses that failed
	if len(mustSend) > 0 and sendEmail:
		failedStr = "\n".join(allFailures)

		# update state file for all addresses we are emailing about right now
		for id in allFailures:
			stateFile[id] = datetime.datetime.strftime(now, f)

		print("Sending email to {0} with {1} failures".format(sendTo, len(allFailures)))

		# send the email
		send_email(sendTo, configData["username"], configData["password"], errorMessage.format(failedStr))

	# write the state file
	with open(stateFileLocation,"w") as sf:
		json.dump(stateFile, sf)

# call main
if __name__ == "__main__":
	main(sys.argv[1:])

