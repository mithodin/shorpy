# shorpy
A very small url shortening service in python using mod_wsgi.

## Requirements
 - Apache with `mod_wsgi` and Python 3 (!!)
 - MySQL database

## Installation
 - Upload `shorpy.py` to a directory that is not going to be accessible via the web.
 - Create `config.json` in the same directory. Look at `config.json.example` for the needed configuration parameters.
 - Create the database with the authentication parameters in your config file.
 - Configure apache to handle requests with the installed script by putting `WSGIScriptAlias / <path/to/the/script/directory>/shorpy.py` in your site configuration.

## Usage
Let's say your installation of shorpy is hosted at `https://s.example.com`.
 - Visit `https://s.example.com/<your_new_link_name>` to create a new link. Fill in the form. Click "create". If it worked, you will be redirected immediately to your newly created link.
   The link name must only contain alphanumeric characters.
 - Send your link wherever you like. Shorpy redirects users via a temporary redirect (302 status code).
 - Shorpy does currently not have an interface to delete or edit links. Do that directly in the database.
