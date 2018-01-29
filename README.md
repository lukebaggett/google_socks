This script is used to allow two sockets to communicate while relaying data through Google Drive.

Check out this [blog post](http://www.blackhillsinfosec.com/?p=5230) for more details.

Follow these steps to get started:

1. Install needed python modules (see below)
2. Run "python2 ./google_socks.py --setup" and follow the instructions
3. Read the help information here: "python ./google_socks.py -h"

### Needed Python Modules
    pip2 install google-auth google-auth-oauthlib google-auth-httplib2 python-dateutil google-api-python-client

### Help
    Usage: google_socks.py [options]
    
    Options:
      -h, --help  show this help message and exit
      --setup     Setup script with Drive App
      -c CREDS    Index of creds in credentials array to use (default: 0)
      -d          Delete files with names provided to -s and -r
      -l          Enable Socket Mode: Listener
      -i IP       Enable Socket Mode: Connect
      -p PORT     Port number for socket mode (default: 8000)
      -s SEND     Sending channel (default: 0)
      -r RECV     Receiving channel (default: 1)
      -P POLL     Poll every x seconds (default: 0)
      -j JITTER   Amount of randomness in polling (default: 1.0)
      -v          Enable verbose output
      --debug     Enable debug output

### Performance Tip
If you need to send data as fast as possible, set no polling (-P 0) or jitter (-j 0). If you get an error from going over the API rate limit, try raising your polling time little by little until you find a sweetspot. I found .2 seconds worked well.
