# Set Up Guide.
unless otherwise noted this guide needs to followed identically for each of the machines, i.e. the machine running `server.py` and the machine running `client.py`

### Step 1: Physical Set Up  
* Front view: Camera Should be centered at top of screen.

![alt text](images/frontview.png)

* Side view: Cameras view should be perpendicular to the screen.

![alt text](images/sideview.png)

### Step 2: Environment  
* Noise and distraction free.
* Well lit but not washed out.
* Each subject in different room
* Stable internet connection

### Step 3: Test Subject
* If subject is wearing glasses ensure that the glare on then is minimal if there is a large amount of glare adjust rooms lighting to remedy this.
* Should not move around too much, some movement is fine but they should avoid large movements.
* Try to remain approximately 2 to 2.5 feet away from the screen.
* The subject eye level should be approximately at the center of screen.
* Head positioned in center of screen, i.e., not off to the left or right.
* Entire face needs to be visible to the subject on the other end.
* Should look at the screen for the duration of the collection.
* Seated at desk


### Step 4: Program Set Up
1) create python environment from included `environment.yaml` (this is most easily done with [ANACONDA](https://www.anaconda.com/))
2) FOR MACHINE RUNNING `client.py` ONLY
   * Find `ipv4` address of machine running `server.py` by running `ipconfig` in terminal
   * Create a text file called `server_ip.txt` and put it in the `\inputs` folder
   * The text file should only contain the `ipv4` address from the machine running `server.py` 
3) Create a file called `config.yaml` and put it in the `\inputs` folder
   * For data collection the `width` should be `1920` and the `height` should be `1080` 
   * For data collection `calibration` should be set to `calibration_quincunx`
     * NOTE: For testing you can set `calibration` to `no_marker` this will greatly shorten the calibration step
   * In the `\inputs` folder an example called `config_example.yaml`
4) Download this [LogiTune](https://www.logitech.com/en-us/video-collaboration/software/logi-tune-software.html) this will be used to turn off auto focus. IMPORTANT: The software is finicky and will sometimes turn autofocus back on. Before starting each collection make sure it is still off. If autofocus is on the data collected will be unusable.
   * Download and open software
   * Select Brio 500
   * Select Image adjustments 
   * Turn off autofocus
5) If client and server wont connect to each other.
   * Try `ping "ip of desired machine"` if it times out but is otherwise connected to internet try turning off the firewall on both machines. 

### Step 5: Data Collection
* Subjects should be briefly introduced to one another before collection starts 
* Subjects should decide on the topic of discussion before collection starts
* Ask subjects if they have anything in particular they would like to discuss, if not here are some suggestions. Also Here is a [list](https://www.mtu.edu/student-leadership/student-orgs/rso-resources/virtual-resources/fun-icebreaking-questions.pdf) of Ice breakers that may work if you do not like any of my suggestions.
  1) Favorite movie or TV show and why. 
  2) Most recent vacation.
  3) Best or worst travel experiences.
  4) What would you do if you won the lottery.
  5) If you could have a super power.
  6) If you had to teach a class on one thing, what would you teach.
  7) Who is your favorite musical artist and what do you like about their music.
  8) What book are you reading right now and what is it about. (can be substituted with tv show)
  9) Favorite sport or sports team and what you like about it.
  10) What is your favorite or least favorite local place to eat.
* Make note of the topic of conversation. 
* The conversations should last for 5 minutes at a minimum and end once a natural stopping point is reached.
* The conversations should be limited to 10 minutes but this is not a hard limit.  
* During the calibration step both user need to follow the red dot on screen.

# How to Use and Expected Behavior
* Ensure that both machines are connected to the same network.
* Ensure that on both machines `Python` is allowed through the computers firewall .
* To start the system the user on the machine whose ip was obtained in step 4.2 must run `server.py` shortly after `client.py` must be run on the other machine.
* After being ran the following message should be printed to console `Estimating camera fps please wait` and the program will do "nothing" for 2 to 3 seconds.
* The calibration screen will appear and after a 3 second countdown a moving red dot will appear. (the calibration step can be aborted with `esc` but this will end the whole program)
* After both machines complete the calibration step the two computers will connect and it should function like any other video call app.
* To end the program press `e` the program may hang for 10 to 15 seconds, but it will resolve itself and exit gracefully.








