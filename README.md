# Explore the Bio Medical Evidence Graph (BMEG)

## Setup 

Python 3, pip, and docker are assumed to be already set up on your machine. The gripql config file `bmeg_app/db/__init__.py` **must be saved as** `bmeg_app/secrets/bmeg_credentials.json`. Instructions on generating the BMEG credential file can be found at [Installing gripql and Getting Started](https://bmegio.ohsu.edu/analyze/getting_started/)

Install an environment module and app dependencies. Here the **virtualenv** module is used.

```
# Install virtualenv
#On macOS and Linux
python3 -m venv venv 
#On Windows 
py -m venv venv  


# Activate and Install Dependencies
. venv/bin/activate
pip install -r requirements.txt
```

## Run BMEG Viewer

```
docker-compose up
```

## Helpful Links

On the [BMEG Website](https://bmegio.ohsu.edu) there are several relevant links:

+ [Installing gripql and Getting Started](https://bmegio.ohsu.edu/analyze/getting_started/)

+ [Databases Loaded into BMEG](https://bmegio.ohsu.edu/explore/data)

+ [Graph Database Schema](https://bmegio.ohsu.edu/explore/schema)

+ [Contact BMEG](https://gitter.im/bmeg/)
