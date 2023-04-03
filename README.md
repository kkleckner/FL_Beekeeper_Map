# FL_Beekeeper_Map
Geocoding and mapping addresses of Florida beekeepers

The python script (Geocoding.py) uses the original dataset provided from FDACS (Address_list.csv) to convert beekeeper addresses to coordinates. 
A little over half of the addresses could not be geocoded including the specific street information (ie. full address). Instead, the city addresses were geocoded. Less than 1% (31/50004) of the addresses could not be geocoded. The python script generated two separate csv files (Coordinates_specific.csv, Corodinates_general.csv) that were cleaned and joined in the R script (Map.R). The R script also creates an interactive map of the beekeeper locations. A file with all coordinates (Coordinates_all.csv) can be used to map the beekeeper locations. All other files are available to see the entire process.
