
import re
import os
import json
import time
import requests
from urlparse import urlparse


# edit here in case Ghost API changes
TOKEN_URL_PATH  = 'ghost/api/v0.1/authentication/token/'
BACKUP_URL_PATH = 'ghost/api/v0.1/db/?access_token='

# default values
OUTPUT_PATH = 'output'
MAX_BACKUP_FILES = 5



def backupBlogs():

	config = getConfig('config.json')

	setGlobalConfigData(config)

	for blog_data in config['blogs']:
		backupBlog(blog_data)
	print 'All done!'


# the config file contains an array with infos about each blog we want to backup in JSON format
# this method simply reads and parses the json
def getConfig (config_file_path):

	with open(config_file_path) as data_file:    
		data = json.load(data_file)
		return data


# yes, I know global variables are evil
# but sometimes they are worth it and easy to use
# this is not one of those cases where using them is very bad
def setGlobalConfigData (config_data):

	settings = config_data['settings']
	if settings:
		if 'output_path' in settings:
			OUTPUT_PATH = settings['output_path']
		if 'max_backup_files' in settings:
			MAX_BACKUP_FILES = settings['max_backup_files']


def backupBlog (blog_data):
	# the backup process involves getting an access token
	# and then passing it via GET to the backup URL request
	with requests.Session() as blog_session:
		
		print 'Creating backup for ' + blog_data['url'] + ' ...'
		
		access_token = getAccessToken(blog_data, blog_session)
		if access_token != None:
			backup_data  = getBackupData(blog_data, access_token, blog_session)
			if backup_data != None:
				createBackupFolder(blog_data)
				saveBackupData(backup_data, blog_data)
				if MAX_BACKUP_FILES != -1:
					removeOlderBackups(blog_data)

		print '\n'


def getAccessToken (blog_data, blog_session):

	payload = composePayload(blog_data)
	token_api_url = blog_data['url'] + TOKEN_URL_PATH

	try:
		response = blog_session.post(token_api_url, data=payload)
		parsed_response = json.loads(response.text)
		if 'access_token' in parsed_response:
			access_token = parsed_response['access_token']
			return access_token
		else:
			err = parsed_response['errors'][0]
			print 'Error! The token could not be retrieved!'
			print 'The site returned an "' + err['errorType'] + '" error with the message "' + err['message'] + '".'
			return None
	except:
		print 'Error! The URL could not be accessed! Backup was not done.'
		return None
	

def composePayload (blog_data):

	payload = {
		'grant_type': 'password',
		'client_id': 'ghost-admin',
		'client_secret': blog_data['client_secret'],
	    'username': blog_data['username'],
	    'password': blog_data['password']
	}

	return payload


def getBackupData (blog_data, access_token, blog_session):

	backup_url = blog_data['url'] + BACKUP_URL_PATH + access_token
	response = blog_session.get(backup_url)

	parsed_response = json.loads(response.text)
	if 'errors' in parsed_response:
		err = parsed_response['errors'][0]
		print 'Error! The backup data could not be exported!'
		print 'The site returned an "' + err['errorType'] + '" error with the message "' + err['message'] + '".'
	else:
		return response.text


def createBackupFolder (blog_data):

	if not os.path.exists(OUTPUT_PATH):
		os.mkdir(OUTPUT_PATH)

	blog_name = getBlogNameFromURL(blog_data['url'])
	blog_folder_path = OUTPUT_PATH + '/' + blog_name
	if not os.path.exists(blog_folder_path):
		os.mkdir(blog_folder_path)


def saveBackupData (backup_data, blog_data):

	backup_save_path = composeBackupSavePath(blog_data)
	backup_file = open(backup_save_path, 'w')
	backup_file.write(backup_data.encode('utf-8'))
	backup_file.close()
	print 'Backup done for ' + blog_data['url'] + '!'


# in this folder the backup json file is saved
# we need this address for other purposes so there is a method to conveniently get it
def composeBlogBackupFolderPath (blog_data):
	blog_name = getBlogNameFromURL(blog_data['url'])
	blog_folder_path = OUTPUT_PATH + '/' + blog_name
	return blog_folder_path

def composeBackupSavePath (blog_data):

	blog_name = getBlogNameFromURL(blog_data['url'])
	backup_date_string = time.strftime("%d%m%Y_%H%M%S")
	backup_filename  =  'backup_' + blog_name + '_' + backup_date_string + '.json'
	blog_folder_path = composeBlogBackupFolderPath(blog_data)
	backup_save_path = blog_folder_path + '/' + backup_filename
	return backup_save_path


# gets a blog url, ex. https://blog.name.domain/
# and returns a "name" like blog_name_domain
# This name will be used inside the backup file name
# to be able to differentiate between backups of different blogs
def getBlogNameFromURL (blog_url):

	parsed_url = urlparse(blog_url)
	netloc = parsed_url.netloc
	blog_name = netloc.replace('.', '_')
	return blog_name


def removeOlderBackups (blog_data):
	blog_folder_path = composeBlogBackupFolderPath(blog_data)
	backup_files = os.listdir(blog_folder_path)
	# sort them by date
	backup_files.sort(key=lambda x: os.path.getmtime(blog_folder_path + '/' + x))
	
	while len(backup_files) > MAX_BACKUP_FILES:
		backup_file = backup_files.pop(0)
		os.remove(blog_folder_path + '/' + backup_file)

	return backup_files

def main ():
	backupBlogs()



if __name__ == "__main__":
    main()




