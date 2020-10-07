# Explore the Bio Medical Evidence Graph (BMEG)

## Setup

Python 3 and docker are assumed to be already set up on your machine. The gripql config file `bmeg_app/db/__init__.py` **must be saved as** `bmeg_app/secrets/bmeg_credentials.json`. Instructions on generating the BMEG credential file can be found at [Installing gripql and Getting Started](https://bmegio.ohsu.edu/analyze/getting_started/)


## Run BMEG Viewer

```
docker-compose up
```

## App Structure

Learn more about the organization of this app at [app-structure.md](app-structure.md)

## Helpful Links

On the [BMEG Website](https://bmegio.ohsu.edu) there are several relevant links:

+ [Installing gripql and Getting Started](https://bmegio.ohsu.edu/analyze/getting_started/)

+ [Databases Loaded into BMEG](https://bmegio.ohsu.edu/explore/data)

+ [Graph Database Schema](https://bmegio.ohsu.edu/explore/schema)

+ [Contact BMEG](https://gitter.im/bmeg/)


## git hooks

* installation: see git-hooks/README.md
* pre-commit: runs flake8 on bmeg_app/ dir.  skip via `git commit --no-verify ...`
* pre-push: runs cypress/ tests.  skip via `git push --no-verify ...`