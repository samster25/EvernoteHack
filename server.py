from upload import EvernoteUploader
import os
import json
import hashlib
import time
from BusAuc import getToken

def main():
	monitorDir = "/Users/Sammy/Dropbox/EverBox"
	# token = "S=s1:U=8f639:E=14fa45f98ae:C=1484cae6a60:P=1cd:A=en-devtoken:V=2:H=93c15bd8ccbff04139e1567f24ec179e"
	# uploader = EvernoteUploader(token)
	while 1:
		token = getToken()
		uploader = EvernoteUploader(token)
		dirSting = json.dumps(list(os.walk(monitorDir)))
		new_hash = dirSting.__hash__()
		toCheck = open("hashDir","r")
		old_hash = toCheck.read()
		toCheck.close()
		if str(new_hash) != old_hash:
			uploader.upload_directory_tree(monitorDir)
			dirSting = json.dumps(list(os.walk(monitorDir)))
			toWrite = open("hashDir","w")
			toWrite.write(str(dirSting.__hash__()))
			toWrite.close()
		time.sleep(1)


		#toCheck.write(hash_string)

if __name__ == "__main__":
	main()
