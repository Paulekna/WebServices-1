# -*- coding: UTF-8 -*-
from flask import Flask
#from redis import Redis
from flask import request
from flask import jsonify
from flask import abort
from flask import make_response
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
import os
import requests
import json
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
#redis = Redis(host='redis',port=6379)

now = datetime.datetime.now()
@app.route('/')
def hello():
	#redis.incr('counter')
	return 'TV programa %s/%s/%s.' % (now.year, now.month, now.day)

tv_db = [
	{
		'id' : 1,
		'television' : 'LRT TELEVIZIJA',
		'type' : 'Vaidybinis serialas',
		'title' : 'Seserys',
		'start_time' : '05:00',
		'description' : '',
		'release_year' : '2016',
		'legal_age' : 'N-7',
		'football_teams' : [
			{'id' : 1},
			{'id' : 2}
		]
	},
	{
		'id' : 2,
		'television': 'LRT TELEVIZIJA',
		'type' : 'Žinios',
		'title' : 'Žinios',
		'start_time' : '06:30',
		'description' : '',
		'release_year' : '',
		'legal_age' : '',
		'football_teams' : []
	},
	{
		'id' : 3,
		'television': 'LNK',
		'type' : 'Animacinis serialas',
		'title' : "Tomas ir Džeris",
		'start_time' : '15:30',
		'description' : '',
		'release_year' : '1980',
		'legal_age' : '',
		'football_teams' : []

	},
        {
                'id' : 4,
                'television': 'TV3',
                'type' : 'Kriminalinė drama',
                'title' : 'Specialioji jūrų policijos tarnyba',
                'start_time' : '01:20',
                'description' : '',
                'release_year' : '2011',
                'legal_age' : 'N-7',
		'football_teams' : []

        },
        {
                'id' : 5,
                'television': 'Viasat Sport Baltic',
                'type' : 'Krepšinio rungtynės',
                'title' : 'Baskonia-Žalgiris',
                'start_time' : '21:30',
                'description' : 'Eurolygos rungtynės',
                'release_year' : '',
                'legal_age' : '',
		'football_teams' : []

        },
        {
                'id' : 6,
                'television': 'BTV',
                'type' : 'Kriminalinė drama',
                'title' : 'Sunkūs laikai',
                'start_time' : '21:00',
                'description' : 'Vaidina Charles Bronson, James Cpburn',
                'release_year' : '1975',
                'legal_age' : '',
		'football_teams' : []

        }
]
#404 and 400 error handling
@app.errorhandler(404)
def not_found(error):
    	return make_response(jsonify({'error': 'Not found'}), 404)
@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

#GET
#curl -i http://localhost:80/tv_program
@app.route('/tv_programs', methods=['GET'])
def programs():
	tv_programs = []
	television = request.args.get('television')
	if television is None:
		return jsonify(tv_db)
	for i in tv_db:
        	if television in i['television']:
                        tv_programs.append(i)
	return jsonify(tv_programs)
#GET/<OPTION>
#curl -i http://localhost:80/tv_programs/<id>
@app.route('/tv_programs/<int:id>', methods=['GET'])
def tv_program_by_id(id):
	program = []
	for i in tv_db:
		if i['id'] == id:
			program = i
	if len(program) == 0:
		abort(404)
	return jsonify(program)

#POST
#curl -i -H "Content-Type: application/json" - X POST -d '{"title":"<>", "television":"<>","start_time":"<>", etc <optional>}' https://localhost:80/tv_programs 
@app.route('/tv_programs', methods=['POST'])
def new_program():
    if not request.json or not 'title' in request.json  or not 'television' in request.json or not 'start_time' in request.json:
       abort(400)
    id = tv_db[-1]['id'] + 1
    for team in request.json.get('football_teams', [{}]):
        try:
            ft = team['id']
            url = "http://web2:81/football_teams/%s" %ft
            r = requests.get(url).text
            data = json.loads(r)
        except ValueError:
	    return abort(404)
    program = {
        'id': id,
	'television': request.json['television'],
	'type': request.json.get('type',""),
	'title': request.json['title'],
        'description': request.json.get('description', ""),
	'release_year': request.json.get('release_year', ""),
	'legal_age': request.json.get('legal_age', ""),
	'start_time': request.json['start_time'],
	'football_teams': request.json.get('football_teams',[])
    }
    tv_db.append(program)
    response = jsonify({'CREATED':'true'})
    response.status_code = 201
    response.headers['location'] = '/tv_programs/%s' %id
    return response

#PUT
#curl -i -H "Content-Type: application/json" - X PUT -d '{"<>":"<>"}' https://localhost:80/tv_programs/<program_id>
@app.route('/tv_programs/<int:id>', methods=['PUT'])
def update_program(id):
	program = []
	for i in tv_db:
        	if i['id'] == id:
                        program = i
	if len(program) == 0:
		abort(404)
	if not request.json:
		abort(400)
	program['title'] = request.json.get('title', program['title'])
	program['description'] = request.json.get('description', program['description'])
	program['television'] = request.json.get('television', program['television'])
	program['type'] = request.json.get('type', program['type'])
	program['start_time'] = request.json.get('start_time', program['start_time'])
	program['release_year'] = request.json.get('release_year', program['release_year'])
	program['legal_age'] = request.json.get('legal_age', program['legal_age'])
        program['football_teams'] = request.json.get('football_teams', program['football_teams'])
	return jsonify({'UPDATED':'true'}), 200
#DELETE
#curl -i -H "Content-Type: application/json" -X DELETE http://localhost:80/tv_program/<program_id>
@app.route('/tv_programs/<int:id>', methods=['DELETE'])
def delete_program(id):
        program = []
        for i in tv_db:
                if i['id'] == id:
                        program = i
        if len(program) == 0:
                abort(404)
        tv_db.remove(program)
        return jsonify({'DELETED':'true'})

# Antra uzduotis

@app.route('/football_teams', methods=['GET'])
def get_all_teams():
	r = requests.get('http://web2:81/football_teams').text
	r = json.loads(r)
	return jsonify(r), 200


@app.route('/tv_programs/<int:id>/football_teams', methods=['GET'])
def get_football_team(id):
        program = []
        for i in tv_db:
                if i['id'] == id:
                        program = i
        if len(program) == 0:
                abort(404)
	url = 'http://web2:81/football_teams'
	r = requests.get(url).text
	r = json.loads(r)
	program_by_team = []
	for i in r:
		for j in program['football_teams']:
			if j['id'] == i['ID']:
				program_by_team.append(i)
	return jsonify(program_by_team)

@app.route('/tv_programs/<int:id>/football_teams', methods=['POST'])
def new_football_team(id):
    url = 'http://web2:81/football_teams'
    new_football_team = {
		'Name': request.json['Name'],
		'Country': request.json['Country'],
		'Stadium': request.json['Stadium'],
		'Attendance': request.json['Attendance'],
		'Captain': request.json['Captain'],
	}
    r = requests.post(url, json=new_football_team)
    r = json.loads(r.text)
    for i in tv_db:
        if i['id'] == id:
            i['football_teams'].append({'id':r['ID']})
  #  if len(program) == 0:
   #         abort(404)
    response = jsonify({'CREATED':'true'})
    response.status_code = 201
    return response
#location
@app.route('/tv_programs/<int:id>/football_teams/<int:f_id>', methods=['DELETE'])
def delete_football_team(id, f_id):
    url = 'http://web2:81/football_teams/'+str(f_id)
    r = requests.delete(url)
    team = []
    for i in tv_db:
        if i['id'] == id:
            i['football_teams'].remove({'id':f_id})
	    break
  #  if len(program) == 0:
   #         abort(404) id?? f_id+
    response = jsonify({'DELETED':'true'})
    response.status_code = 200
    return response


if __name__== "__main__":
	app.run(host="0.0.0.0",debug=True, port=5000)
