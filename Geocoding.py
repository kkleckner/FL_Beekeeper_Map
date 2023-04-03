#Geocoding Florida beekeeper addresses
#Kaylin Kleckner
#All files are available on github:
#https://github.com/kkleckner/FL_Beekeeper_Map.git

#This script converts the addresses of Florida beekeepers (reported to FDACS) to coordinates for mapping
#The corresponding R file is "Map.R"

#These are resources I used:
#https://towardsdatascience.com/geocode-with-python-161ec1e62b89
#https://github.com/shakasom/geocoding/blob/master/geocoding.ipynb

####SET UP####

#Using python in R studio (AKA posit) takes some setting up and adjusting.
#First, download python from the internet. Here is a beginner guide to getting set up:
##https://wiki.python.org/moin/BeginnersGuide

#Once it is installed, you can select a Python file and change your environment to Python
#You can manually run the following line in the consule to switch coding languages:
##reticulate::repl_python()
#Resource: https://posit.co/blog/three-ways-to-program-in-python-with-rstudio/#:~:text=To%20get%20started%20writing%20Python,the%20contents%20of%20Python%20modules.

#Alternatively, you can type a python command and R studio should run the line above for you.
#Here is a simple python command to test it out: 
print("hello")

#You will see ">>>" in the console when the command has finished running. This is helpful later on

#While R is great at working with dataframes, python can do almost anything
#You can create videogames, mine data from the internet, etc. 
#The coding language itself is different and the set up requires more knowledge of computer science
#I'm not going to explain everything here, but there are A LOT of free resources online

#We need to install modules (the equivalent of R packages) to run our script
#You will manually install the modules in the terminal tab (beside Console) or in your computer's terminal
#Think of the terminal like the inner workings of your computer
#You can do everything you do with a mouse click on the terminal - it is very powerful but intimidating!

#Check what version of python you are using by entering:
#python -- version (notes: no # and just click enter in the terminal)
#If you just downloaded it, you should be up to date. You need some verion of python 3 (ie. 3.11.2)

#Install modules using pip (you may need to trouble shoot)
#Resources: https://careerkarma.com/blog/python-pip-command-not-found/
##https://www.tutorialspoint.com/How-to-install-a-Python-Module

#You can enter the following line:
#pip install ModuleName (noteL no # and fill in the ModuleName)

#Install all the needed modules in the terminal
##Needed modules: pandas, fiona (prereq), geopandas, geopy, matplotlib, folium, time
#You need to install fiona to get GeoPandas (https://gis.stackexchange.com/questions/330840/error-installing-geopandas)

#Import the modules by running the following lines:
import pandas as pd
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded, GeocoderUnavailable
import matplotlib.pyplot as plt
import folium
from folium.plugins import FastMarkerCluster
import time


####DATAFRAME PREP####

#Load in dataframe with pandas (module abbreviated to pd)
df = pd.read_csv("Address_list.csv") #csv file from FDACS

#Check first 5 rows. Note python starts with 0 (not 1)
df.head() 

#To convert the address to coordinates, we need to have the full address in a single column
#Combine columns of street info, city, state, and zipcode. Add country
df['ADDRESS'] = df['Address'].astype(str) + ',' + \
                df['City'] + ',' + \
                df['State'] + ',' + \
                df['Zip_Code'].astype(str) + ',' + 'United States'   
                #note: highlight the whole code block to run correctly

#Check first 5 rows again
df.head()


####API PREP####
#We are going to connect to an API (Application Programming Interface).
#An API is a server that you can use to retrieve and send data to using code.

#Set up Nominatim, a tool for connecting to programs like OpenStreetMap
#The timeout will allow the script to move on after 15 seconds if it doesn't work
#https://stackoverflow.com/questions/27914648/geopy-catch-timeout-error
#https://medium.com/@grasscall/geocodertimedout-a-real-pain-9ed621d076e0
locator = Nominatim(user_agent="myGeocoder", timeout=15) 

#We can test the locator with a single address
#Input address into the locator
location = locator.geocode("7904 NW 170TH ST,ALACHUA,FL,32615,United States")

#Print the location address. This is the address the API has found based on the one provided
print(location.address)

#Print the coordinates
print("Latitude = {}, Longitude = {}".format(location.latitude, location.longitude))
#Hooray! It works!


####GEOCODING FULL DATASET#####

#1. Define the function geocode_me. It includes a rate limiter and a try/except statement
#Function source: https://stackoverflow.com/questions/58439692/convert-physical-addresses-to-geographic-locations-latitude-and-longitude

#Rate limiter:
#The API has a limit for the number of times and speed you can request information per day
#The time.sleep slows the code down, only making one request per 1.1 seconds
#https://gis.stackexchange.com/questions/395735/getting-non-successful-status-code-502-error-when-reverse-geocoding-of-large-d

#Try/except:
#The try and except statement allows the program to skip over an error instead of quitting all together


def geocode_me(locations):
    time.sleep(1.1) 
    try:
        return locator.geocode(locations)
    except (GeocoderTimedOut, GeocoderQuotaExceeded, GeocoderUnavailable) as e: 
        if GeocoderQuotaExceeded:
            print(e)
        else:
            print(f'Location not found: {e}')
            return None


#2. Use the geocode_me() function to create a new column entitled "location"
df['location'] = df['ADDRESS'].apply(lambda x: geocode_me(x))  # ←  the x represents each row in the ADDRESS column
#^This line takes a LONG time to run (+2 hours)
#Even if errors pop up, check for the creation of the location column 


#3. Create longitude, latitude and altitude from location column (returns tuple)
df['point'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None)


#4. Split point column into latitude, longitude and altitude columns
df[['latitude', 'longitude', 'altitude']] =   pd.DataFrame(df['point'].tolist(), index=df.index)

#Check the bottom of the dataframe for the latitude and longitude (altitude comes back 0 for all)
df.tail()


####FAILED ADDRESSES####

#And this is where things get complicated...
#When I finally got step 2 to run, it didn't work for over half the addresses
#Even when I tested a few failed addresses one by one, an error popped up saying the address could not be found

#I checked to see how many addresses did not work (and the row was filled with NaN)
df['longitude'].isna().sum()  
#2690 NAs

#I also made the same number of addresses failed for latitude as longitude
df['latitude'].isna().sum() 
#2690 NAs

#Let's at least export the ones that worked:
#I created a separate dataframe for only the full geocoded addresses
df2=df.dropna(subset=['longitude'])

#I exported that dataframe as a csv file. I imported and cleaned this file in the R script. 
df2.to_csv('Coordinates_specific.csv')


#I wanted to try to repeat the process without the street information
#I created a separate dataframe for the failed addresses
dfNA = df[df['longitude'].isna()]

#And I forgot to save the dfNA as csv file... *facepalm*
#As soon as you click onto an R file, everything you have in your python environment vanishes
#This is the line I should have run:
##dfNA.to_csv('Coordinates_failed.csv')

#Alternatively, I should have just carried on and wrote this script all the way through. 
#This isn't a great option since troubleshooting can take a long time. It is better to save csv files as you go.


#I did not want to rerun the geocoding function that took +2 hours the first time.
#But I needed a way to know what addresses failed. So...

#I reloaded the orignal csv file under a new object name
original = pd.read_csv("Address_list.csv")
original.head()

#I also loaded in the csv file of the successful geocoded addresses (that I just exported above)
cord = pd.read_csv("Coordinates_specific.csv")
cord.head()

#I merged the orginal dataframe with the succesful geocoded address dataframe
full = pd.merge(df, cord, on="Firm_Name", how="outer")
#This filled in the coordinates of the succesful addresses, and left the failed ones as NA's
#This also made a lot of duplicate columns. I tried troubleshooting to avoid it, but eventually gave up.

#For all of the duplicated columns it added on a _x or _y to the column name
#I dropped the second set (_y) of columns that I didn't need
full = full.drop(["Firm_Number_y", "APIARY_REG_NO_y", "Address_y", "City_y", "State_y", "County_y", "Zip_Code_y", "Phone_Number_y"], axis=1)

#I then made a new dataframe with just the rows without coordinates (ie. geocoding failed)
errors = full[full['longitude'].isna()]
errors.head() #check the structure
#And now I'm caught up! Would have been a lot easier to just save the csv file...

#I dropped the columns full of NAs from the previous attempt
errors = errors.drop(["ADDRESS", "location", "point", "longitude", "latitude", "altitude"], axis=1)

#Now let's repeat the process :')

#I combined columns for single address column, but left out the street information
errors['ADDRESS'] = errors['City_x'] + ',' + \
                errors['State_x'] + ',' + \
                errors['Zip_Code_x'].astype(str) + ',' + 'United States'  
              
#1. Let's set up the locator             
locator = Nominatim(user_agent="myGeocoder", timeout=15)

#2. Use the geocode_me() function and create location column
errors['location'] = errors['ADDRESS'].apply(lambda x: geocode_me(x))
#This also took a while to run. Check for location column despite errors:
errors.head()

#3. Create longitude, latitude and altitude from location column (returns tuple)
errors['point'] = errors['location'].apply(lambda loc: tuple(loc.point) if loc else None)

# 4. Split point column into latitude, longitude and altitude columns
errors[['latitude', 'longitude', 'altitude']] =   pd.DataFrame(errors['point'].tolist(), index=errors.index)

#Woohoo!
#Let's see how many failed this time
errors['longitude'].isna().sum()  
#31 NAs - Not bad, I'll take it! Less than 1%

errors['latitude'].isna().sum()  
#31 NA's - same as longitude

#I dropped the 31 rows with NA's
errors2=errors.dropna(subset=['longitude'])

#I saved the geocoded city addresses as a csv file
errors2.to_csv('Coordinates_general.csv')

#I then picked up this process in R with the two exported csv files
#Check out Map.R for the rest! :)

