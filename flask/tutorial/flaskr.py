#import
import mongo_utils
from pymongo import MongoClient,errors
import urllib
from urllib2 import Request,urlopen,URLError,HTTPError
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import config_utils
import monk_adapter
from collections import OrderedDict
import reset_module
import json
#configuration
DATABASE = 'DATABASE'
DEBUG = True
SECRET_KEY = 'A Key'
USERNAME = 'admin'
PASSWORD = 'password'
HOST='HOST'

options={}

first_layer = 20

second_layer = 1

app = Flask(__name__)
#app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS')


def diff(a, b):
        b = set(b)
        return [aa for aa in a if aa not in b]

def connect_db():
	password = urllib.quote_plus(app.config['PASSWORD'])
	mongo_url = 'mongodb://%s:%s@%s/%s' %(	app.config['USERNAME'],
						password,
						app.config['HOST'],
						app.config['DATABASE']
						)
						
	return MongoClient(mongo_url,27017)


def top_entries(ids,entries_):
	entries = []
	for e in entries_:
		if e['id'] in ids:
			entries.append(e)
	return entries

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g,'db',None)
	if db is not None:
		db.close()


def make_first_message(e):
	return {'id':str(e['id']),'message':e['title']}

def make_second_message(e):
	return {'id':str(e['id']),'message':'#'.join([e['title'],e['educate'],e['salary'],e['site'],e['exp_year'],e['attract'],e['description']])}


def make_first_raw_message(e):
	return e['title']

def make_second_raw_message(e):
	return '#'.join([e['title'],e['educate'],e['salary'],e['site'],e['exp_year'],e['attract'],e['description']])




def find_specific_category(ids_results,categoryId):

	ids_scores = {}

	for id_r in ids_results:
		if id_r['result'] is None: 
			ids_scores[int(id_r['id'])]=0.0
		elif id_r['result']['Id'] == categoryId: ids_scores[int(id_r['id'])]=id_r['result']['Score']

	ordered_ids_scores = OrderedDict(sorted(ids_scores.items(), key=lambda t:-t[1]))

	ids = []
	for it in ordered_ids_scores.items()[:first_layer]:
		ids.append(it[0])

	return ids


@app.route('/')
def show_entries():
	collection_hm = g.db.lgcompany.hero_monk
	rows = mongo_utils.get_non_labeled_records(collection_hm)
	entries_ = [dict(id=row['id'],
			educate=row['educate'],
			description=row['description'],
			title=row['title'],
			salary=row['salary'],
			site=row['site'],
			exp_year=row['exp_year'],
			attract=row['attract']
			) for row in rows]
	show_entries = {}
	print len(entries_)

	first_messages = []
	for e in entries_:
		first_messages.append(make_first_message(e))
	first_results = monk_adapter.get_judged_by_records(options['groupid01'],first_messages)
	first_posi_ids = find_specific_category(first_results,options['category_like'])
	print "After first test, there is %d records left" % len(first_posi_ids)
	first_posi_e = mongo_utils.get_records_by_ids(collection_hm,first_posi_ids)
	second_messages = []
	for e in first_posi_e:
		second_messages.append(make_second_message(e))
	second_results = monk_adapter.get_judged_by_records(options['groupid02'],second_messages)

	for result in second_results:
		print  result
		if result['result'] is None :
			show_entries[int(result['id'])] = 0.0
		elif result['result']['Id'] == options['s_category_like']:
			show_entries[int(result['id'])] = result['result']['Score']
		else:
			show_entries[int(result['id'])] = -result['result']['Score']	

	ordered_show_entries = OrderedDict(sorted(show_entries.items(), key=lambda t:-t[1]))

	show_ids = []
	for it in ordered_show_entries.items()[:second_layer]:
		show_ids.append(it[0])

	print show_ids	
 	print ordered_show_entries.items()[:second_layer]      
	entries = top_entries(set(show_ids),entries_)

	session['entries_id'] = [ e['id'] for e in entries]

	return render_template('show_entries.html',entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/model', methods=['POST'])
def model():
	posi_ids = request.form.getlist('like')
	print posi_ids
	posi_ids = [ int(pid) for pid in posi_ids]
	ids = session['entries_id']
	nega_ids = diff(ids,posi_ids)
	print posi_ids
	print nega_ids

	collection = g.db.lgcompany.hero_monk
	posi_records = mongo_utils.get_records_by_ids(collection,posi_ids)
	nega_records = mongo_utils.get_records_by_ids(collection,nega_ids)
	mongo_utils.update_posi_records_by_ids(collection,posi_ids)
	mongo_utils.update_nega_records_by_ids(collection,nega_ids)
	for r in posi_records:
		monk_adapter.add_record(options['category_like'],make_first_raw_message(r))
#	for r in nega_records:
#		monk_adapter.add_record(options['category_unlike'],make_first_raw_message(r))
	posi_records.rewind()
	for r in posi_records:
		monk_adapter.add_record(options['s_category_like'],make_second_raw_message(r))
	nega_records.rewind()
#	for r in nega_records:
#		monk_adapter.add_record(options['s_category_unlike'],make_second_raw_message(r))



	

	flash('New model request has been successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/reset_model',methods=['GET'])
def reset_model():
	reset_module.reset_module()
	global options
        options = config_utils.read_config("./monk_adapter.conf","MonkAccount")
        print options
	collection = g.db.lgcompany.hero_monk
	mongo_utils.reset_all_data_label(collection)
	flash('Model has been reset')
        return redirect(url_for('show_entries'))	

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))



if __name__ == '__main__':
	print app.config['DATABASE']
	global options 
	options = config_utils.read_config("./monk_adapter.conf","MonkAccount")
	print options
	app.run(host= '0.0.0.0')
