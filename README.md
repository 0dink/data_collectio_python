Add the following two files to the `inputs` folder before running

1) create a file called `server_ip.txt` and add the ipv4 address of the computer running `server.py` (can be found by running `ipconfig` in console)

2) create a file called `config.yaml` which should contain the following

* `output_directory:` absolute/path/to/save/output/to
* `width:` frame width
* `height:` frame height
* `fps:` fps to capture at
* `calibration_mode:` for list of valid modes see docs string of `display_dot_and_record` in `calibration_utils` although `calibration_quincunx` should be used primarily. For testing of the video call portion use `no_marker`