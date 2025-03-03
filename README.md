Add the following two files to the `inputs` folder before running

### 1 create a file called `server_ip.txt` and add the ipv4 address of the computer running `server.py` (can be found by running `ipconfig` in console)

### 2 create a file called `config.yaml` which should contain the following

* `output_directory:` absolute/path/to/save/output/to
* `width:` frame width
* `height:` frame height
* `calibration:` for list of valid modes see docs string of `display_dot_and_record` in `calibration_utils` although `calibration_quincunx` should be used primarily. For testing of the video call portion use `no_marker`

### How to use

On computer A run `server.py` then of computer B run `client.py`.

First calibration will start this can be aborted with escape but that will stop the whole program.

After calibration window closes the two machines connect. To end the program at this point press `e` on both machines.

When `e` is pressed the program may hang for 10 to 15 seconds, but it will resolve its self and exit gracefully.



