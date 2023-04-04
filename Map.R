#Map of Florida beekeepers
#Kaylin Kleckner
#All files are available on github:
#https://github.com/kkleckner/FL_Beekeeper_Map.git

#This script maps the location of Florida beekeepers (reported to FDACS)
#This is the location of beekeeper residences, so not necessarily the location of apiaries.
#Many beekeepers have multiple apiaries and move hives around the state.
#Points outside of FL represent beekeepers that live out of state but keep bees in Florida for at least part of the year.

#The addresses of Florida beekeepers were first converted to coordinates in python.
#The corresponding python file is "Geocoding.py"
#The code for cleaning the datasets from python is at the end of this script

#Resources: https://map-rfun.library.duke.edu/01_georeference.html

####SET UP####
#Load in packages
library(mapview)
library(tidyverse)
library(sf)
library(webshot)

#Load in csv file of all coordinates
all <- read.csv("Coordinates_all.csv")

#Look at dataset structure
glimpse(all)

####MAPPING####
#I mapped the coordiantes I extracted in python with the mapview function
#This creates an interactive map that is nice to zoom in/out on
#You can take a screenshot of it for a still image, or use a different function to make a stationary figure

#Mapview pointers:
#The "show in new window button" is on the top bar to the right of the broom icon.
#It will open the map in a safari browser.
#You can hover over each point to see the coordinates.
#You can click one each point for the full information.

#I could not get the exact coordinates for about half of the full beekeeper addresses.
#Instead, I got the coordinates for the city they were located in (see python script for more details).
#I mapped the full address coordinates and city address coordinates separately.
#Lastly, I mapped all coordinates (from full and city addresses).

######SPECIFIC SITES######
mapviewOptions(fgb = FALSE)#specify this for creating the HTML file later on

#Map only coordinates from full addresses
all %>%
  filter(Coordinate_Address_Type == "Full") %>% #filter by address type
  st_as_sf(coords = c("Longitude", "Latitude"), crs = 4269) %>% #crs is the coordinate system type
  st_jitter(factor = 0.0005) %>% #jitter points to avoid complete overlap
  mapview #create interactive map


######GENERAL SITES######

#Map only coordinates from city addresses
all %>%
  filter(Coordinate_Address_Type == "City") %>% 
  st_as_sf(coords = c("Longitude", "Latitude"), crs = 4269) %>% 
  st_jitter(factor = 0.0005) %>%
  mapview


######ALL SITES######

#Map all coordinates
all %>%
  st_as_sf(coords = c("Longitude", "Latitude"), crs = 4269) %>% 
  st_jitter(factor = 0.0005) %>%
  mapview


#Create HTML of map with all coordinates
install_phantomjs()

html <- all %>%
  st_as_sf(coords = c("Longitude", "Latitude"), crs = 4269) %>% 
  st_jitter(factor = 0.0005)

m = mapview(html)

mapshot(m, url = "FLBeekeeperMap.html", file=".html")#downloads HTML to directory folder


####DATA CLEANING####

#This is how I cleaned up and combined the two csv files I exported from python.
#You don't need to run this code to see the maps, but
#I left this code in so you can fully follow along with what I did.
#All of this could have been done in python but I prefer to use tidyverse in R.

######SPECIFIC SITES######

#These are the sites that I could get coordinates from the full address

#I loaded in each csv file
specific_sites <- read.csv("Coordinates_specific.csv")

#I created a column to describe the type of address used to generate the coordinates
#This is for easy identification when the two datasets are combined
specific_sites$Coordinate_Address_Type <- "Full"

#I looked at the dataset strucutre to see what needed to be changed
specific_sites %>% glimpse()

#I used piping (%>%) to string together a series of commands
specific_sites <- specific_sites %>% 
  select(-X, -altitude, -location, -point) %>% #I removed the uninformative columns
  rename(Apiary_Registration = APIARY_REG_NO, #i created uniform column names for joining the two datasets
         Street = Address,
         Coordinate_Address = ADDRESS, #I clarified vague column names
         Latitude = latitude, #Made sure everything capitalized, etc.
         Longitude = longitude)


######GENERAL SITES######

#These are the sites that I could not get coordinates from the full address,
#so I got coordinates for the city (ie. no street information).

#Same steps as above. Load in csv file
general_sites <- read.csv("Coordinates_general.csv")

#Add column for the type of address for the coordinates
general_sites$Coordinate_Address_Type <- "City"

#Check structure
general_sites %>% glimpse()

general_sites <- general_sites %>% 
  select(-X, -altitude, -location, -point, -Unnamed..0) %>% #Remove uninformative columns
  rename(Firm_Number = Firm_Number_x,
         Apiary_Registration = APIARY_REG_NO_x,
         Street = Address_x, #Rename columns to be uniform
         City = City_x, #I am removing the "_x" that python when I rejoined csv files
         State = State_x, #That entire step could have been avoided, but I didn't want to rerun the code
         Zip_Code = Zip_Code_x, #It was easier for me to just fix it here than fight with python
         County = County_x,
         Phone_Number = Phone_Number_x,
         Coordinate_Address = ADDRESS,
         Latitude = latitude,
         Longitude = longitude)

#I joined two cleaned datasets together
all_sites <- full_join(specific_sites, general_sites)

#Lastly, I exported the joined dataset as a csv file
write_csv(all_sites, "Coordinates_all.csv")
#This is the file I use in the mapping code above.
#It is better to have only one csv file and then filter in R.
#I would normally delete these two csv files and corresponding code since it is duplicate information,
#but I wanted you to see what I did :)

#Another tip: At the very end of cleaning (especially when you are renaming and making new datasets),
#clear everything from your environment (broom icon) and rerun the entire script
#to check everything works like it should.
