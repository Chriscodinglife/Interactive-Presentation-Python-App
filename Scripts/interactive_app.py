#!/usr/bin/env python3

'''                                                                                                                                                                                           
Chris Orellana
April 2022

##### DESCRIPTION #######
This Python Script is designed to allow organizations, teams, and devs create interactive
presentations made in Google Slides and add call to action buttons to them.

This is an ideal app to use for onboarding how to computer sessions for new hires in a company
for example and have users set up their machines and following along with a
presenter.

Below are test parameters as well as JAMF parameters that can be commented out
and right under the constructor init function of the interactive app. You can use
this sys.argv passed parameters if you want to use this script with JAMF in Self Service
and having JAMF pass in the gist URLS of your button and presentation data.
'''

#### IMPORT

import os
import sys
import json
import requests
import webbrowser
import tkinter.ttk
import tkinter as tk
from tkinter import * 
from tkinter.ttk import *
from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps

#### CODE

class interactive_app:
    def __init__(self, master=None):
        
        #### FOR USING WITH JAMF - UNCOMMENT THESE LINES IF YOU WANT TO USE WITH JAMF
        # Parse through the image data and button data provided from the JSON via a URL 
        # and append the data available to lists
        # self.image_json_url = sys.argv[4] # Pass in the Parameters from JSS for the Image JSON URL
        # self.button_json_url = sys.argv[5] # Pass in the Parameters from JSS for the Buttons JSON URL
        # self.local_user = sys.argv[3] # Grab the local user running this script
        ####
        
        #### FOR TESTING LOCALLY - COMMENT THESE LINES IF YOU WANT TO USE WITH JAMF
        self.image_json_url = "<presentation_gist_url_here" # Pass in the Parameters from JSS for the Image JSON URL
        self.button_json_url = "button_data_gist_url_here" # Pass in the Parameters from JSS for the Buttons JSON URL
        self.local_user = "<your_user_name_here" # Grab the local user running this script
        ####
        
        # Comment this following line out if you are using this without Self Service/Jamf
        self.image_icon_location = f"/Users/{self.local_user}/Library/Application Support/com.jamfsoftware.selfservice.mac/Documents/Images/brandingimage.png"
        
        self.image_json_data = requests.get(self.image_json_url)
        self.button_json_data = requests.get(self.button_json_url)
        self.image_names = []
        self.image_data = []
        self.buttons = []
        for row in self.image_json_data.json()['slides']:
            for image_name, image_base64 in row.items():
                self.image_names.append(image_name)
                self.image_data.append(image_base64)
                
        self.length_of_slides = len(self.image_data)
        
        for image_name in self.button_json_data.json():
            self.buttons.append(self.button_json_data.json()[image_name])
        
        # Set the position of certain elements like the progress bar and the buttons
    
        # Define some generic colors to use later
        self.black_color = "#000000"
        self.white_color = "#FFFFFF"
                    
        # Define Master Window
        self.masterWindow = tk.Tk() if master is None else tk.Toplevel(master)
        self.masterWindow.title('Welcome to Greenhouse!')
        self.icon = PhotoImage(file = self.image_icon_location)
        self.masterWindow.call('wm','iconphoto', self.masterWindow._w, self.icon)
        self.screen_width = self.masterWindow.winfo_screenwidth()
        self.screen_height = self.masterWindow.winfo_screenheight()
        self.setwidth = "1280" #192 Arbitrary math to make the images stay in the right shape. TL;DR - lots of troubleshooting
        self.setheight = "820"
        self.masterWindow.configure(width=self.setwidth, height=self.setheight)
        self.masterWindow.resizable(False, False)
        self.masterWindow.update()
        self.window_width = self.masterWindow.winfo_width()
        self.window_height = self.masterWindow.winfo_height()
        posX = int(self.masterWindow.winfo_screenwidth()/2 - self.window_width/2)
        posY = int(self.masterWindow.winfo_screenheight()/2.6 - self.window_height/2)
        self.masterWindow.geometry(f"+{posX}+{posY}")
        # Bring the window the front and in focus
        self.window = NSRunningApplication.runningApplicationWithProcessIdentifier_(os.getpid())
        self.window.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
        
        self.progress_bar_xpos = self.window_width / 2
        self.progress_bar_ypos = self.window_height - 125
        self.back_button_xpos = (self.window_width / 2) - 130
        self.back_button_ypos = self.window_height - 60
        self.next_button_xpos = (self.window_width / 2) + 130
        self.next_button_ypos = self.window_height - 60
        self.action_button_1_xpos = (self.window_width / 2) - 130
        self.action_button_1_ypos = self.window_height - 170
        self.action_button_2_xpos = (self.window_width / 2) + 130
        self.action_button_2_ypos = self.window_height - 170

        # Configure Columns
        self.masterWindow.columnconfigure(2, minsize=200)
        self.masterWindow.columnconfigure(3, minsize=200)
        self.masterWindow.columnconfigure(4, minsize=200)
        
        # Create the Grey Background that will act as the lower grey bar with the grey icons
        self.greyBackground = tk.Canvas(self.masterWindow)
        self.greyBackground.configure(background=self.black_color, height=self.setheight, width=self.setwidth)
        self.greyBackground.grid(column='0', columnspan='7', row='0', rowspan='6')
        # Create the White background where the Main Presentation will sit        
        self.whiteBackground = tk.Canvas(self.masterWindow)
        self.whiteBackground.configure(background=self.white_color, height=str(int(self.setheight)-100), highlightbackground=self.white_color, width=self.setwidth)
        self.whiteBackground.grid(column='0', columnspan='7', row='0', rowspan='5')
        
        # # This area is where certain Images and buttons will be available for the user to click on
        self.actionImageCanvas = tk.Canvas(self.masterWindow)
        self.actionImageCanvas.configure(background=self.white_color, height=str(int(self.setheight)-100), highlightbackground=self.white_color, width=self.setwidth)
        self.actionImageCanvas.grid(column='0', columnspan='7', row='0', rowspan='5', sticky='n')
        self.first_image = tk.PhotoImage(data=self.image_data[0])
        self.actionImageCanvas.create_image(0, 0, anchor="nw", image=self.first_image)
        
        # This will be the progress bar
        self.slide_start_value = 0
        self.slide_end_value = self.length_of_slides - 1
        self.style = tkinter.ttk.Style()
        self.style.theme_use('alt')
        self.style.configure("green.Horizontal.TProgressbar", foreground='#24A47F', background='#24A47F', troughcolor='#efefef', thickness=5)
        self.progressbar = tkinter.ttk.Progressbar(self.masterWindow)
        self.progressbar.configure(length='600', style="green.Horizontal.TProgressbar", maximum=self.slide_end_value, orient='horizontal', mode='determinate', value=self.slide_start_value)
        self.progressbar.place(x=self.progress_bar_xpos, y=self.progress_bar_ypos, anchor="center")

        # Create the Back and Next Buttons for the user to click on to get to the next screen
        self.BackButton = tk.Button(self.masterWindow)
        self.BackButton.configure(text='Close', highlightbackground=self.black_color, width=8)
        self.BackButton.configure(command=self.close)
        self.BackButton.place(x=self.back_button_xpos, y=self.back_button_ypos, anchor="center")

        self.NextButton = tk.Button(self.masterWindow)
        self.NextButton.configure(default='active', text='Next', highlightbackground=self.black_color, width=8)
        self.NextButton.configure(command=self.nextButton)
        self.NextButton.place(x=self.next_button_xpos, y=self.next_button_ypos, anchor="center")

        # Create the Action Buttons and Hide Them
        self.actionButton1 = tk.Button(self.masterWindow)
        self.actionButton1.configure(default='active', text='random1')
        self.actionButton1.place(x=self.action_button_1_xpos, y=self.action_button_1_ypos, anchor="center")
        self.actionButton1.place_forget()
      
        self.actionButton2 = tk.Button(self.masterWindow)
        self.actionButton2.configure(default='active', text='random2')
        self.actionButton2.place(x=self.action_button_2_xpos, y=self.action_button_2_ypos, anchor="center")
        self.actionButton2.place_forget()


    def __str__(self):
        return "This app is for helping New Hires setting up their machine for the first time during the How To session"

    # Functions to Control the Progress Bar Length    
    def addProgressBar(self):
        '''This will increment the progress bar by 1 until the progress bar value reaches the maximum which is the total amount of slides'''

        self.progressbar['value'] += 1

        if self.progressbar['value'] >= self.slide_end_value:
            self.progressbar['value'] = self.slide_end_value


    def subtractProgressBar(self):
        '''This will lower the progress bar by 1 until the progress bar value reaches the first slide which is 0'''

        self.progressbar['value'] -= 1

        if self.progressbar['value'] <= 0:
            self.progressbar['value'] = 0
    
    
    # Forward and Back Buttons for the Slides and Progress Bar
    def nextButton(self):
        '''This will call the addProgressBar method and contains logic for the Next button displayed on the screen'''

        self.addProgressBar()

        if self.progressbar['value'] >= 1 and self.progressbar['value'] < self.slide_end_value:
            self.BackButton.configure(text="Back", command=self.backButton)
            self.BackButton.place(x=self.back_button_xpos, y=self.back_button_ypos, anchor="center")
        elif self.progressbar['value'] == self.slide_end_value:
            self.BackButton.place_forget()
            self.masterWindow.update()
            self.NextButton.configure(text="Finish", command=self.close)
            self.NextButton.place(x=int(self.setwidth)/2, y=self.next_button_ypos, anchor="center")
            
        self.switchSlides(self.progressbar['value'])
        self.masterWindow.update()
        

    def backButton(self):
        ''' This will call the subractProgressBar method and contains logic on the back Button displayed on the screen'''

        self.subtractProgressBar()

        if self.progressbar['value'] == 0:
            self.BackButton.configure(text='Close', highlightbackground="#efefef", width=8)
            self.BackButton.configure(command=self.close)

        self.switchSlides(self.progressbar['value'])
        self.masterWindow.update()


    # Exit the GUI upon request
    def close(self):
        '''This will close the Python Gui when called.'''
        self.masterWindow.quit()
    
    
    # The Slide Controller!
    # Switch the Slides based on the value of the Progress Bar
    def switchSlides(self, slide_current_value):
        '''This method will handle the logic of switching between slides which takes in the slide_current_value as a parameter.'''

        if not slide_current_value == self.length_of_slides:
            
            self.slideImage = tk.PhotoImage(data=self.image_data[slide_current_value])
            self.actionImageCanvas.create_image(0, 0, anchor='nw', image=self.slideImage)
        elif slide_current_value == self.length_of_slides:
            print("The Progress Bar Value is: {self.progressbar['value']}")
            
        # Extract values for the Action buttons
        self.button_slide_number = self.buttons[slide_current_value]
        self.button_trigger = self.button_slide_number['buttons']
        self.button_text_1 = self.button_slide_number['button_text_1']
        self.action_type_1 = self.button_slide_number['action_link_1'][0]
        self.action_link_1 = self.button_slide_number['action_link_1'][1]
        self.button_text_2 = self.button_slide_number['button_text_2']
        self.action_type_2 = self.button_slide_number['action_link_2'][0]
        self.action_link_2 = self.button_slide_number['action_link_2'][1]
        
        
        def button_1_command():
            '''This nested function handles when to choose run a command or open a web link depending on the JSON data given but button 1'''
            
            try:
                if self.action_type_1 == "web":
                    webbrowser.open(self.action_link_1, new=2)
                elif self.action_type_2 == "command":
                    os.system(self.action_link_1)
            except:
                print(f"Slide {slide_current_value} was unable to run button 1")
                
        
        
        def button_2_command():
            '''This nested function handles when to choose run a command or open a web link depending on the JSON data given but button 2'''

            try: 
                if self.action_type_2 == "web":
                    webbrowser.open(self.action_link_2, new=2)
                elif self.action_type_2 == "command":
                    os.system(self.action_link_2)
            except:
                print(f"Slide {slide_current_value} was unable to run button 2")
        
        
        if self.button_trigger == True: # display two buttons if true
            self.actionButton1.place(x=self.action_button_1_xpos, y=self.action_button_1_ypos, anchor="center")
            self.actionButton2.place(x=self.action_button_2_xpos, y=self.action_button_2_ypos, anchor="center")
            self.actionButton1.configure(text=self.button_text_1,
                                         command=button_1_command)
            self.actionButton2.configure(text=self.button_text_2,
                                         command=button_2_command)
        elif self.button_trigger == "one_button": # Display only one button
            self.actionButton1.place(x=(self.window_width / 2), y=self.action_button_1_ypos, anchor="center")
            self.actionButton1.configure(text=self.button_text_1,
                                         command=button_1_command)
            self.actionButton2.place_forget()
        elif self.button_trigger == "None": # Hide both buttons
            self.actionButton1.place_forget()
            self.actionButton2.place_forget()


def main():
    '''Run the Greenhouse app mainloop and then exit when finished.'''

    # Start the Tkinter app
    app = interactive_app()
    app.masterWindow.mainloop()
    sys.exit(0)


if __name__ == '__main__':
  main()