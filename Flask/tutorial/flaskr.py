#import
import mongo_utils
from pymongo import MongoClient,errors
import urllib
from urllib2 import Request,urlopen,URLError,HTTPError
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import ConfigParser
import monk_adapter
from collections import OrderedDict


#configuration
DATABASE = 'DATABASE'
DEBUG = True
SECRET_KEY = 'A Key'
USERNAME = 'admin'
PASSWORD = 'password'
HOST='HOST'

options={}

app = Flask(__name__)
#app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS')

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

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

	for e in entries_:
		result = monk_adapter.get_judged_by_record(options['groupid'],e)
		print result
		if result is None :
			show_entries[e['id']] = 0.0
		elif result['Id'] == options['category_like']:
			show_entries[e['id']] = result['Score']
		else:
			show_entries[e['id']] = -result['Score']	

	ordered_show_entries = OrderedDict(sorted(show_entries.items(), key=lambda t:-t[1]))

	show_ids = []
	for it in ordered_show_entries.items()[:5]:
		show_ids.append(it[0])

	print show_ids	
       
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
		monk_adapter.add_record(options['category_like'],r)
	for r in nega_records:
		monk_adapter.add_record(options['category_unlike'],r)

	

	flash('New model request has been successfully posted')
	return redirect(url_for('show_entries'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))



if __name__ == '__main__':
	print app.config['DATABASE']
	Config = ConfigParser.ConfigParser()
	Config.read("./monk_adapter.conf")
	global options 
	options = ConfigSectionMap("MonkAccount")
	print options
	app.run(host= '0.0.0.0')
