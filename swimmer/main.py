"""
Swimmer web application that stores
data about swimmers and allows to insert,
delete, update, get rows, as well as search
for swimmers summary from wikipedia and adding
it to database.
Tags: #Flask, #Backend.
"""

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests

# Flask, variables setup
app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
wrong_id = f"Swimmer with provided id does not exist"


class Swimmer(db.Model):
    """
    Swimmer class with attributes:
    - id (int)
    - name - full name
    - is_swimmer (bool)
    - summary (text). Can be taken from wikipedia
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    is_swimmer = db.Column(db.Boolean, nullable=False)
    summary = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"{self.name}|{self.is_swimmer}|{self.summary}"


@app.before_first_request
def create_tables():
    """
    Init database
    """
    db.create_all()


@app.route('/')
def index():
    """
    Entry page
    """
    return 'Hello Swimming World'


@app.route('/swimmer/<id>')
def get_swimmer(id):
    swimmer = Swimmer.query.get_or_404(id)
    return str(swimmer)


@app.route('/list_swimmers')
def list_swimmers():
    """
    Returns all swimmers from database
    in format json
    """
    data = Swimmer.query.all()
    format_data = {}
    for n, i in enumerate(data):
        sub_dict = {}
        sub_dict["name"] = i.name
        sub_dict["is_swimmer"] = i.is_swimmer
        sub_dict["summary"] = i.summary
        format_data[n] = sub_dict

    return str(format_data)


@app.route('/swimmer/<id>', methods=['DELETE'])
def delete_swimmer(id):
    swimmer = Swimmer.query.get(id)
    if swimmer is not None:
        db.session.delete(swimmer)
        db.session.commit()
        message = f"Swimmer with id {id} is deleted"
    else:
        message = wrong_id

    return message


@app.route('/search_swimmer', methods=['GET', 'POST'])
def search_swimmer():
    """
    Search for a swimmer in wikipedia
    and returns summary after pressing
    'search' button.
    Adds swimmer summary to database
    after pressing 'add' button.
    """
    if request.method == 'POST':
        name = request.form.get("name")
        summary = get_person_summary(name)
        if request.form.get("submit_button") == "Search":
            return render_template('form.html', summary=summary, name=name)
        elif request.form.get("submit_button") == "Add":
            swimmer = Swimmer(name=name, is_swimmer=True, summary=summary)
            db.session.add(swimmer)
            db.session.commit()
            return render_template('form.html', summary='Swimmer added')
    return render_template('form.html')


@app.route('/swimmer/<id>', methods=['PUT'])
def update_swimmer(id):
    swimmer = Swimmer.query.get_or_404(id)

    name = request.json['name']
    is_swimmer = request.json['is_swimmer']
    summary = request.json['summary']

    swimmer.name = name
    swimmer.is_swimmer = is_swimmer
    swimmer.summary = summary

    db.session.commit()

    return str(swimmer)


def get_person_summary(subject):
    """
    Search for 'subject' on wikipedia.
    'subject' is a swimmer full name.
    Returns swimmer symmary.
    """
    url = 'https://en.wikipedia.org/w/api.php'

    # subjects = ['Mark Spitz', 'Dick Roth', 'Martha Randall', 'Claudia Kolb']
    params = {
        'action': 'query',
        'format': 'json',
        'titles': subject,
        'prop': 'extracts',
        'exintro': '',
        'explaintext': ''
    }

    data = requests.get(url, params).json()['query']['pages']

    # writes key at the top of 'data' (json) to next_key
    next_key = None
    for i in data:
        next_key = i

    summary = data[i]['extract']
    # search for word 'swimmer' in summary
    if summary.find('swimmer') == -1:
        return 'No swimmers found'

    return summary


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
