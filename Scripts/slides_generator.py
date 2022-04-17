#!/usr/bin/env python3

'''                                                                                                                                                                                           
Chris Orellana
April 2022

##### DESCRIPTION #######
This is the slide generator script that can parses through your Google Slides via it's Presentation ID.
It will do the following:

1. Parse through each Google Slide and grab its Image URL
2. Download each image to a local folder in slide order, in this case the 'images_to_convert' folder
3. Take each image and change the size to a resolution of 1280x720
4. Take the image data convert each image to base64
5. Take each base64 image data and append it to a list
6. Output all the image data to a 'presentation_data.json' file locally
7. Output a 'button_data.json' file for customizing and tailoring to the presentation
'''

from __future__ import print_function
import json

import os
import requests
import glob
import base64
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/presentations.readonly']

# The ID of a sample presentation.
PRESENTATION_ID = input("Please input your Google Slide Presentation ID: ")


def main():
    '''Shows basic usage of the Slides API. Prints the number of slides and elments in a sample presentation.'''
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Create a local directory to store the images we will download per the Google Slides
    image_directory = 'images_to_convert'
    if not os.path.exists(image_directory):
        try:      
            os.mkdir(image_directory)
        except OSError as error:
            print(error)
    else:
        files = glob.glob(f"{image_directory}/*")
        for file in files:
            os.remove(file)
        
    # Iterate through a given presentation based on the Presentation ID and parse through each Slide ObjectID to gain a Content URL
    # The Content URL will provide for us a URL that we can use to download an image for each slide
    try:
        service = build('slides', 'v1', credentials=creds)

        # Call the Slides API
        presentation = service.presentations().get(
            presentationId=PRESENTATION_ID).execute()
        slides = presentation.get('slides')


        for i, slide in enumerate(slides):
            
            object_id = slide.get("objectId")
            slide_image = service.presentations().pages().getThumbnail(
                            presentationId=PRESENTATION_ID, 
                            pageObjectId=object_id,
                            thumbnailProperties_thumbnailSize='LARGE'
                            ).execute()
            content_url = slide_image['contentUrl']
            
            image_download = requests.get(content_url)
            if image_download.status_code == 200:
                with open(f"{image_directory}/image_{i}.png", 'wb') as output_image:
                    output_image.write(image_download.content)
            
    except HttpError as err:
        print(err)
    
    os.chdir(image_directory)
    json_slides = {}
    json_buttons = {}
    base_width = 1280
    for image in sorted(os.listdir('.'), key=os.path.getmtime):
        if image.endswith('.png'):
            img = Image.open(image)
            width_percent = (base_width/float(img.size[0]))
            height_size = int((float(img.size[1])*float(width_percent)))
            img = img.resize((base_width, height_size), Image.ANTIALIAS)
            img.save(image)
            
            with open(f"./{image}", "rb") as img_file:
                base64_string = base64.b64encode(img_file.read()).decode('utf-8')
                json_slides.update({image:base64_string})
                json_buttons.update({image:{"buttons": True, "button_text_1": "button_1", "action_link_1": ["command", "this_link"], "button_text_2": "button_2", "action_link_2": ["command", "this_link"]}})
    
    image_body = { 'slides' : [json_slides]}
    
    os.chdir("..")
    with open("presentation_data.json", "w") as image_json_file:
        json.dump(image_body, image_json_file)
        
    with open("button_data.json", "w") as button_json_file:
        json.dump(json_buttons, button_json_file)

if __name__ == '__main__':
    main()