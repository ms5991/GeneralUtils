#!/usr/bin/env python3

from socket import *
import os, os.path, sys, getopt, json, smtplib, time, datetime, http.client, urllib

def send_pushover(userKey, token, message):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
                "token": token,
                "user": userKey,
                "message": message,
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

        print ("Successfully sent Pushover notification")


def receive(localip):
	# specify Host and Port
	HOST = localip
	PORT = 80

	soc = socket(AF_INET, SOCK_STREAM)

	try:
		soc.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    		# With the help of bind() function
    		# binding host and port
		soc.bind((HOST, PORT))

	except socket.error as message:

	    	# if any error occurs then with the
   	 	# help of sys.exit() exit from the program
    		print('Bind failed. Error Code : ' + str(message[0]) + ' Message ' + message[1])
    		sys.exit()

	# print if Socket binding operation completed
	print('Socket binding operation completed')

	# With the help of listening () function
	# starts listening
	soc.listen(9)

	conn, address = soc.accept()
	# print the address of connection
	print('Connected with ' + address[0] + ':' + str(address[1]))
	result = []
	for i in range(6):
		data = conn.recv(1)
		result.append(data)

	conn.close()
	soc.close()
	return result

def main(argv):

	# parse options, all are required
	try:
		opts, args = getopt.getopt(sys.argv[1:], "p", ["localip=","config="])
	except (getopt.GetoptError, e):
		print('pingCheck.py: {0}'.format(str(e)))
		sys.exit(2)

	usePushover = False
	localIp = None
	configFile = None
	for opt, arg in opts:
		# pushover integration
		if opt in ['-p']:
			usePushover = True
		elif opt in ['--localip']:
			localIp = arg
		# email address to send to
		elif opt in ['--config']:
			configFile = arg

	print("Email config file {0}".format(configFile))

        # load the config file
	with open(configFile) as conf:
        	configData = json.load(conf)

	stateFileLocation = configData["statefilelocation"]

	while True:

		allData = receive(localIp)

		ct = datetime.datetime.now()
		all = ''
		shouldSend = False
		with open(stateFileLocation) as sf:
			stateFile = json.load(sf)

		for i in range(len(allData)):

			if allData[i] == b'\x01':
				if stateFile["states"][i]["state"] == "Closed":
					message = "" + str(ct) + " " + configData["byteordermapping"][i]["name"] + " is open"
					all = all + "\n" + message
					shouldSend = True

				stateFile["states"][i]["state"] = "Open"
			else:
				if stateFile["states"][i]["state"] == "Open":
					message = "" + str(ct) + " " + configData["byteordermapping"][i]["name"] + " is closed"
					all = all + "\n" + message
					shouldSend = True
				stateFile["states"][i]["state"] = "Closed"

			stateFile["states"][i]["lastupdate"] = str(ct)

		print (all)

		# write the state file
		with open(stateFileLocation,"w") as sf:
			json.dump(stateFile, sf)

		if usePushover and shouldSend:
			print ("Send to pushover" + all)
			send_pushover(configData["pushoveruserkey"], configData["pushovertoken"], all)

# call main
if __name__ == "__main__":
        main(sys.argv[1:])
