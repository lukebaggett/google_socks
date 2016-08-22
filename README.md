This script is used to allow two sockets to communicate while relaying data through Google Drive.

Follow these steps to get started:

1. Install needed python modules (see below)
2. Run "python ./google_socks.py --setup" and follow the instructions
3. Read the help information here: "python ./google_socks.py -h"

###Needed Python Modules
    pip install oauth2client
    pip install google-api-python-client

###Help
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
