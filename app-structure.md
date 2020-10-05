# BMEG Analysis App Structure

## Containerization with Docker

App is deployed through Docker, docker image is built from the `Dockerfile` and deployed based on the contents of the `docker-compose.yaml`.

## Configuration

Flask server config contained in `bmeg_app/app.py`

Widget configuration contained in `bmeg_app/config.yaml`

## Database

Grip configuration and memoization is contained in `bmeg_app/db/__init__.py`

## Widgets

Each widget has a stand alone python script in `bmeg_app/views/` that contains `styles`, `NAME`, `LAYOUT`, and a series of callbacks.

+ `styles` loads app wide visuals (ex. font, color palettes, sizing, etc.) contained in `bmeg_app/appLayout.py`

+ `NAME` indicates the string to display in the sidebar. These values are read in from the `view_map` dictionary in `bmeg_app/views/__init__.py`

+ `LAYOUT` indicates the Dash features (and preprocessing steps) that make up the widget. Each feature is a new element in the list of the children field of `LAYOUT = html.Div(children=[])`.

+ A series of callbacks connect features and/or user input to update and display various features.

## Widget Functions

Although some functions are defined within a widget's `views/` file, most functions are defined in `bmeg_app/components/`.

## Locales

All hardcoded widget text is in `bmeg_app/locales/app.en.yaml` and data in `bmeg_app/locales/data.json`

## Assets

Contents of `bmeg_app/assets/` are loaded at app start up. This file may contain `.css` files that allow for more customization and flexibility than standard Dash python framework.

## Navbar

Navigation bar is defined in `bmeg_app/__main__.py` that contains `styles`, `app.layout`, and a series of callbacks. This is a similar format as a widget `views/` file.
