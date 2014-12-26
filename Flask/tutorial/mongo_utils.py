from pymongo import MongoClient,errors
import urllib


def connect_db():
        password = urllib.quote_plus('Server2008!')
        mongo_url = 'mongodb://%s:%s@%s/%s' %(  'lguser',
                                                password,
                                                '118.192.89.126',
                                                'lgcompany'
                                                )

        return MongoClient(mongo_url,27017)

def get_records_by_ids(collection,ids):
	rows =  collection.find({"id":{"$in":ids}}) #"[295829, 295830, 295831]"}})
	return rows

def get_n_records(collection,num):
	return collection.find().limit(int(num))

def insert_records(collection,records):
	for r in records:
		collection.insert(r)
def get_records_by_criteria(collection,criteria):
	return collection.find(criteria);

def update_nega_records_by_ids(collection,ids):
	collection.update({"id":{"$in":ids}},{"$set":{'labeled':-1}},multi=True)
def update_posi_records_by_ids(collection,ids):
	collection.update({"id":{"$in":ids}},{"$set":{'labeled':1}},multi=True)
def get_nega_records(collection):
	pass
def get_posi_records(collection):
	pass
def get_non_labeled_records(collection):
	return collection.find({"labeled":0}).limit(20)


def test():
	db = connect_db()
#	ids = [295829,295830,295831]
#	collection = db.lgcompany.positions
#	get_records_by_ids(collection,ids)
#	db.close()
	collection_posi = db.lgcompany.positions
	collection_monk = db.lgcompany.hero_monk
	records = get_n_records(collection_posi,100)
	insert_records(collection_monk,records)
	
if __name__ == "__main__":
	test()
