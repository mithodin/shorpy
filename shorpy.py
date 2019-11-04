#    shorpy: A very small url shortener written in python using mod_wsgi
#    Copyright (C) 2019  Lucas L. Treffenstädt
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import cgi
import json
import os
import sys
import mysql.connector

form="""<!DOCTYPE html>
<html lang="en">
<head>
    <title>create a new link</title>
    <meta charset="utf-8">
    <meta http-equiv="Cache-Control" content="no-cache">
	<style>
		html,body {
			width = 100vw;
			font-family: "Fira Sans", sans-serif;
		}
		p {
			text-align:center;	
		}
	</style>
</head>
<body>
	<form method="post">
		<select name="proto">
			<option value="s">https://</option>
			<option value="u">http://</option>
		</select>
		<input type="text" name="url" placeholder="example.com">
                Password: <input type="password" name="pw" placeholder="your password">
		<input type="submit" value="create">
	</form>
</body>
</html>
"""

class Database:
    conf = None
    sqlserver = None
    get_url_query = """SELECT url FROM redirects WHERE name = %s"""
    set_url_query = """INSERT INTO redirects (name,url) VALUES(%s,%s)"""
    create_table_query = """CREATE TABLE shorpy ( uid INT NOT NULL AUTO_INCREMENT , url VARCHAR(2048) NOT NULL name VARCHAR(20) NOT NULL , PRIMARY KEY (uid), UNIQUE (name))"""
    drop_table_query = """DROP TABLE redirects"""

    def __init__(self, conf):
        self.conf = conf
        self.sqlserver = mysql.connector.connect(host="localhost",user=conf["dbuser"],passwd=conf["dbpw"],database=conf["dbname"])

    def get_url(self, name):
        cursor = self.sqlserver.cursor(prepared=True)
        try:
            cursor.execute(self.get_url_query,(name,))
            res = cursor.fetchall()
        except mysql.connector.ProgrammingError as pe:
            self.handle_error(pe)
        if res:
            return res[0][0].decode("utf-8")

    def set_url(self, name, url):
        cursor = self.sqlserver.cursor(prepared=True)
        done = False
        while not done:
            try:
                cursor.execute(self.set_url_query,(name,url))
                self.sqlserver.commit()
                done = True
            except mysql.connector.ProgrammingError as pe:
                self.handle_error(pe)

    def handle_error(self,error):
        if error.errno == 1146: #table does not exist
            cursor = self.sqlserver.cursor()
            cursor.execute(self.create_table_query)
            self.sqlserver.commit()
        elif error.errno == 1054: #column does not exist
            cursor = self.sqlserver.cursor()
            cursor.execute(self.drop_table_query)
            cursor.execute(self.create_table_query)
            self.sqlserver.commit()
        else: #don't know what the problem is, notify the user
            raise error

def application(environ, start_response):
    with open(os.path.dirname(__file__)+"/config.json") as json_file:
        conf = json.load(json_file)
    
    sql_server = Database(conf)

    name = environ['REQUEST_URI'][1:]
    if not name.isalnum():
        start_response('403 Forbidden', [('Content-Type','text/plain')])
        return(["Nah. Link name is not alphanumeric. Go away.\n".encode("utf-8")])
    
    url = sql_server.get_url(name)
    if not url:
        fields = cgi.FieldStorage(fp = environ['wsgi.input'], environ = environ)
        try:
            proto = "https://" if fields["proto"].value == "s" else "http://"
            url = proto+fields["url"].value
            pw = fields["pw"].value
            if pw == conf["updatepw"]:
                sql_server.set_url(name,url)
                url = sql_server.get_url(name)
            else:
                url = None
        except KeyError:
            url = None

    if url:
        start_response('302 Moved Temporarily', [('Location',url)])
        return(["1".encode("utf-8")])
    else:
        start_response('200 OK', [('Content-Type', 'text/html')])
        return([form.encode("utf-8")])
