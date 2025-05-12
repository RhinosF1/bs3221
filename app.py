import os
import mysql.connector

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, flash, render_template_string)
mydb = mysql.connector.connect(
  host=os.environ.get("DB_HOST", "localhost"),
  user=os.environ.get("DB_USERNAME", "root"),
  password=os.environ.get("DB_PASSWORD", "password"),
  database="fire_warden"
)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")


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
  if name:
    # stub this data, assume AD can provide this
    data  = {
      "123456": "Test User",
      "234567": "Test Person", 
      "345678": "Test Staff",
    }
    data_reversed = {v: k for k, v in data.items()}
    buildings = [
      "Alwyn Hall",
      "Beech Glade",
      "Bowers Building",
      "Burma Road Student Village",
      "Centre for Sport",
      "Chapel",
      "The Cottage",
      "Fred Wheeler Building",
      "Herbert Jarman Building",
      "Holm Lodge",
      "Kenneth Kettle Building",
      "King Alfred Centre",
      "Martial Rose Library",
      "Masters Lodge",
      "Medecroft",
      "Medecroft Annexe",
      "Paul Chamberlain Building",
      "Queen’s Road Student Village",
      "St Alphege",
      "St Edburga",
      "St Elizabeth’s Hall",
      "St Grimbald’s Court",
      "St James’ Hall",
      "St Swithun’s Lodge",
      "The Stripe",
      "Business School",
      "Tom Atkinson Building",
      "West Downs Centre",
      "West Downs Student Village",
      "Winton Building",
      "Students’ Union"
  ]

    name_found = False

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM fire_warden_activity")
    result = cursor.fetchall()
    #print(result)
    table = """
  <table>
    <thead>
      <tr>
        <th>Staff Name</th>
        <th>Staff Number</th>
        <th>Location</th>
        <th>Floor</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
  """

    for row in result:
      staff_id = row[1]
      staff_name = data[str(staff_id)]
      location = row[2]
      floor = row[3]
      if staff_name == name:
        name_found = True
        location_dropdown = '<select name="location">'
        for loc in location_list:
            selected_attr = 'selected' if loc == location else ''
            location_dropdown += f'<option value="{loc}" {selected_attr}>{loc}</option>'
        location_dropdown += '</select>'
        table += f"""
          <tr>
            <form method="POST" action="/update">
              <td>{staff_name}</td>
              <td>{staff_id}</td>
              <td>{location_dropdown}</td>
              <td>
                <input type="text" name="floor" placeholder="Enter floor" value="{floor}">
              </td>
              <td>
              <input type="hidden" name="staff_name" value="{staff_name}">
                <input type="hidden" name="staff_id" value="{staff_id}">
                <input type="submit" value="Update">
            </form>
            <form method="POST" action="/delete" style="display:inline; margin-left:5px;">
            <input type="hidden" name="staff_id" value="{staff_id}">
            <input type="hidden" name="staff_name" value="{staff_name}">
            <input type="submit" value="Remove Warden" onclick="return confirm('Are you sure you want to delete this row?');">
             </form>
             </td>
          </tr>
          """
      else:
          table += f"""
          <tr>
            <td>{staff_name}</td>
            <td>{staff_id}</td>
            <td>{location}</td>
            <td>{floor}</td>
            <td></td>
          </tr>
          """
    if not name_found:
        staff_id = data_reversed.get(name)

        if staff_id is not None:
            # Dropdown for location with no selection
            location_dropdown = '<select name="location">'
            for loc in location_list:
                location_dropdown += f'<option value="{loc}">{loc}</option>'
            location_dropdown += '</select>'

            table += f"""
            <tr>
              <form method="POST" action="/register">
                <td>{name}</td>
                <td>{staff_id}</td>
                <td>{location_dropdown}</td>
                <td><input type="text" name="floor" placeholder="Enter floor"></td>
                <td>
                  <input type="hidden" name="staff_id" value="{staff_id}">
                  <input type="hidden" name="staff_name" value="{name}">
                  <input type="submit" value="Register">
                </td>
              </form>
            </tr>
            """
    table = table + "</tbody></table>"
    return render_template('hello.html', name = name, table = table)
  else:
    print('Request for hello page received with no name or blank name -- redirecting')
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update():
  staff_id = request.form['staff_id']
  location = request.form['location']
  floor = request.form['floor']
  staff_name = request.form['staff_name']
  try:
    update_query = """
              UPDATE fire_warden_activity
              SET fwa_location = %s, fwa_floor = %s
              WHERE fwa_staff_id = %s
          """
    cursor = mydb.cursor()
    cursor.execute(update_query, (location, floor, staff_id))
    mydb.commit()

    flash("Update successful", "success")
  except mysql.connector.Error as err:
    mydb.rollback()
    flash(f"Update failed: {err}", "danger")
  return render_template_string("""
    <html>
      <body>
        <form id="post_redirect" action="{{ url_for('hello') }}" method="POST">
          <input type="hidden" name="name" value="{{ staff_name }}">
        </form>
        <script>
          document.getElementById("post_redirect").submit();
        </script>
      </body>
    </html>
    """, staff_name=staff_name)


@app.route('/delete', methods=['POST'])
def delete():
    staff_id = request.form['staff_id']
    staff_name = request.form['staff_name']
    try:
      cursor = mydb.cursor()
      cursor.execute("DELETE FROM fire_warden_activity WHERE fwa_staff_id = %s", (staff_id,))
      mydb.commit()
    except mysql.connector.Error as err:
        mydb.rollback()
        return f"Delete failed: {err}", 500
    return render_template_string("""
    <html>
      <body>
        <form id="post_redirect" action="{{ url_for('hello') }}" method="POST">
          <input type="hidden" name="name" value="{{ staff_name }}">
        </form>
        <script>document.getElementById("post_redirect").submit();</script>
      </body>
    </html>
    """, staff_name=staff_name)


@app.route('/register', methods=['POST'])
def register():
    staff_id = request.form['staff_id']
    staff_name = request.form['staff_name']
    location = request.form['location']
    floor = request.form['floor']
    try:
      cursor = mydb.cursor()
      cursor.execute("""
            INSERT INTO fire_warden_activity (fwa_staff_id, fwa_location, fwa_floor)
            VALUES (%s, %s, %s)
        """, (staff_id, location, floor))
      mydb.commit()
    except mysql.connector.Error as err:
        mydb.rollback()
        return f"Register failed: {err}", 500
    return render_template_string("""
    <html>
      <body>
        <form id="post_redirect" action="{{ url_for('hello') }}" method="POST">
          <input type="hidden" name="name" value="{{ staff_name }}">
        </form>
        <script>document.getElementById("post_redirect").submit();</script>
      </body>
    </html>
    """, staff_name=staff_name)

if __name__ == '__main__':
   app.run()
