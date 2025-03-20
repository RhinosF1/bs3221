import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')
   data  = [
     {"name": "Test User", "Number": "123456", "Location": "Alwyn Hall"},
     {"name": "Test Person", "Number": "234567", "Location": "WDC"}, 
     {"name": "Test Staff", "Number": "345678", "Location": "St Elizabeth’s Hall"}
   ]
  table = """<table><thead>
  <tr>
    <th>Staff Name</th>
    <th>Staff Number</th>
    <th>Location</th>
    <th></th>
  </tr></thead>
<body>"""
   for row in data:
     table = table + f"<tr><td>{row['name']}</td><td>{row['Number']}</td><td>{row['Location']}</td><td></td></tr>"
   table = table + "</tbody></table>"
   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
