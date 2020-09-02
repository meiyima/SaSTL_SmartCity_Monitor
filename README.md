# Running the tool
Python3 is required.
First make sure requirements are fulfilled:  
pip install -r requirements.txt  
Due to dependency issues (see https://github.com/gboeing/osmnx/issues/45), you may need to manually fix an OSError using sudo apt install python3-rtree on Ubuntu or brew install libspatialindex on MacOS.  
Then, run gui.py.
# Using the tool
"Clear" will reset the tool.
# Labeled Points Input
First input either a city name or coordinates in the form of (latitude,longitude) and a range in km. Points of interest will be considered only within this range of the city or coordinates. Use the points of interest dropdown to add points of interest. Use the button next to "Areas" to either create a new label or add a point to an existing label, or "Add a location" to add a single custom location. Use the "Show Map" button to view the points that have been entered.
# Sensor Locations and Data input
The "Sensor Locations Path" must be set as the "nodes.csv" in a similar format to the example nodes.csv file provdided. For each variable wished to be used, a name and file path must be entered. Each data csv must contain measurements in each row for each node, indexed by timestamp.
# Checking requirements
To input requirements, select values for each dropdown and input field as appropriate, then use the "+" button. If you wish to type in an SaSTL formula instead (examples of the syntax can be found in "reqs.txt"), use the button next to "Requirements". In order to check all requirements that have been added, press "Start the monitor."
# Sample data
The data provided is the from Chicago provided by Array of Things (AoT), after preprocessing. It is contained in the chicago\_data\_2018-10-08/ directory.

