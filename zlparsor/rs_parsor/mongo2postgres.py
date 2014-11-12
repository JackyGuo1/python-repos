#!/usr/bin/python
# coding= utf-8
from lxml import etree
from StringIO import StringIO
import lxml.html as html
import re
from pymongo import MongoClient
import gridfs
from os import getenv
import pymssql
import datetime

def content_clean(content):
    cleaned = content.replace(" ","").replace("\r\n"," ").replace("\r"," ").replace("\n"," ").lstrip(" ").rstrip(" ")
    return cleaned

def content_clean_with_space_include(content):
    cleaned = content.replace("\r\n"," ").replace("\r"," ").replace("\n"," ").lstrip(" ").rstrip(" ")
    return cleaned

def get_profile(doc):
     #Basic Info    
     try:
         profile_dom =  doc.xpath("//div[@id='resumeContentBody']/div[@class='summary']/div[@class='summary-top']")[0].text_content()
     except IndexError :
         print "Resume is missing"
         return dict()
     profile_raw =  profile_dom.replace(u'\xa0',u' ')#.encode("utf-8")

     # patterns = {
     # "sex": re.compile(r"男|女"),
     # "workexp": re.compile(r"(\d+)年工作经验"),
     # "marriage": re.compile(r"已婚|未婚"),
     # "birth": re.compile(r"(\d+)年(\d+)月") ,
     # "address": re.compile(r"现居住地：(.*?)\|")}
     # for pat_name,pat in patterns.items():


     sex_p = re.compile(u"男|女")
     workexp_p = re.compile(u"(\d+)年工作经验")
     marriage_p = re.compile(u"已婚|未婚")
     yyyyMM_p = re.compile(u"(\d+)年(\d+)月") 
     address_p = re.compile(u"现居住地：(.*?)\|")
 
     sex_m = sex_p.search(profile_raw)
     yyyyMM_m = yyyyMM_p.search(profile_raw)
     workexp_m =workexp_p.search(profile_raw)
     marriage_m = marriage_p.search(profile_raw) 
     address_m = address_p.search(profile_raw)
     
     
     profile = dict()

     if sex_m:
         profile['sex'] = sex_m.group()
     if yyyyMM_m:
         profile['birth'] =  yyyyMM_m.group(1)
     if workexp_m:
         profile['workexp_year'] =  workexp_m.group(1)
     if marriage_m:
         profile['marriage'] =  marriage_m.group()
     if address_m:
         profile['address'] =  address_m.group(1)
     return profile


def get_intention(intention_raw):
    expect_city_p = re.compile(u'期望工作地区：\r\n(.*)\r\n') 
    salary_rang_p = re.compile(u'期望月薪：\r\n(\d+)-(\d+)元/月')
    intention_pre =  intention_raw.replace(" ","")
    intention = dict()
    city_m = expect_city_p.search(intention_pre)
    salary_m = salary_rang_p.search(intention_pre)
    if city_m:
        intention['city'] = city_m.group(1)
    if salary_m:
        intention['salary'] = '-'.join([salary_m.group(1),salary_m.group(2)])
    return intention   


def get_education(education_raw):
    education_pre = education_raw.lstrip(" ").rstrip(" ")
    education_p = re.compile(u'(\d+).(\d+)\s+-\s+(((\d+).(\d+))|(至今))(\s+)(?P<college>.*)') 
    education_m = education_p.search(education_pre)
    education = None
    if education_m:
        education = education_m.group('college').strip('\r\n')
    return education


def get_detail(doc):
    resume_component_keys = []
    resume_component_values = []
    for i in doc.xpath("//div[@class='resume-preview-all']"):
         resume_component_keys.append([j.text for j in i.findall("*") if j.tag =="h3"])
         resume_component_values.append([k.text_content().replace(u'\xa0',u' ') for k in i.findall("*") if k.tag !="h3"])

    detail_info = dict()
    for i in range(0,len(resume_component_keys)):
        header =" ".join([j for j in resume_component_keys[i]])
        content ="\n".join([j for j in resume_component_values[i]])
        if header == u'求职意向':
            detail_info['intention'] = get_intention(content)
        if header == u'教育经历':
            detail_info['education'] = get_education(content)
        if header == u'专业技能':
            detail_info['exp_skill'] =content_clean_with_space_include(content)
        if header == u'项目经历':
            detail_info['project_skill'] = content_clean(content)
        if header == u'自我评价':
            detail_info['narratage'] = content_clean(content)
        if header == u'证书':
            detail_info['certification'] = content_clean_with_space_include(content)
    return detail_info


def get_work_experience(doc):
    resume_component_keys = []
    resume_component_values = []
    for i in doc.xpath("//div[@class='resume-preview-all workExperience']"):
         resume_component_keys.append([j.text for j in i.findall("*") if j.tag =="h3"])
         resume_component_values.append([k.text_content() for k in i.findall("*") if k.tag !="h3"]) #.replace(u'\xa0',u' ')
    work_exp = None
    for i in range(0,len(resume_component_keys)):
        header =" ".join([j for j in resume_component_keys[i]])
        content ="\n".join([j for j in resume_component_values[i]])
        if header == u'工作经历':
            work_exp = content_clean(content)
    return  work_exp


def print_dict(input_dict):
#    print " ".join([input_dict[i] for i in iter(input_dict)])
    for i in iter(input_dict):
        print i+':'
        print input_dict[i]
        print "---------------------------------------------------------------------"
    print "==================================================================="

def print_resume(list_key,dict_resume):
    for key in list_key:
        print key
        if key in dict_resume:
            if type(dict_resume[key]) is dict:
                print_dict(dict_resume[key])
            else:
                print dict_resume[key]
        else:
            print "There is no content available"
        print  '==================================================='

def make_record(resume_id,profile,details,work_exp):
    record = dict()
    profile_keys = ['sex','birth','workexp_year','marriage','address' ]
    detail_keys = [ 'intention','education','exp_skill','project_skill','narratage','certification']

    for key in profile_keys:
        if key in profile:
            record[key] = profile[key]
    for key in detail_keys:
        if key in details:
            if key == 'intention':
               if 'city' in details['intention']:
                   record['city'] = details['intention']['city']
               if 'salary' in details['intention']:
                   record['salary'] = details['intention']['salary']
            else:
               if key in details:
                   record[key] = details[key]
    record['work_exp'] = work_exp
    record['name'] = resume_id
    return record 

def parse_resume(resume_id,html_file):
     
    doc = html.document_fromstring(html_file)
    profile = get_profile(doc)
    details = get_detail(doc)
    work_exp = get_work_experience(doc)
    
    return make_record(resume_id,profile,details,work_exp)  


class ResumeDB(object):
    def __init__(self):
        self.db = MongoClient("mongodb://192.168.1.11:27017/").grid_example
        self.fs = gridfs.GridFS(self.db)

    def save_resume(self, resume_id, resume_link, resume_content, referer):
        self.fs.put(resume_content, filename=resume_id, url=resume_link, encoding="utf-8", referer=referer)

    def open_resume(self, resume_id):
        return self.fs.get_last_version(filename=resume_id)

    def read_resume(self, resume_id):
        return self.fs.get_last_version(filename=resume_id).read()

    def exists(self, resume_id):
        return self.fs.exists(filename=resume_id)



def get_connection(servername,username,password_string,dbname):
    server = getenv(servername)
    user = getenv(username)
    password = getenv(password_string)
    conn = pymssql.connect(host=servername,user=username, password=password_string,database=dbname)
    return conn

def normal(text):
    return ("" if text is None else text).encode("utf-8").replace('\'','\'\'')

def generate_sql(filename,record,cur_id):
#    print """INSERT INTO \"User\" (\"Name\",\"UserType\",\"CreatedDatetime\",\"UpdatedDatetime\",\"Enabled\") 
#                          VALUES ('%s',%d,clock_timestamp(),clock_timestamp(),'t') ;""" % (record.get('name'),4)
   
    filename.write("""INSERT INTO \"User\" (\"Name\",\"UserType\",\"CreatedDatetime\",\"UpdatedDatetime\",\"Enabled\")
                          VALUES ('%s',%d,clock_timestamp(),clock_timestamp(),'t') ;\n""" % (record.get('name'),4))
#    print """INSERT INTO \"ZhilianUser\" (\"UserId\",\"NickName\",\"Type\",\"Sex\",\"City\" ) VALUES(%d,'%s',%d,'%s','%s') ; """ % (cur_id,
#                                                                    normal(record.get('name')),1,
#                                                                    normal(record.get('sex')),
#                                                                    normal(record.get('city')) )
    filename.write("""INSERT INTO \"ZhilianUser\" (\"UserId\",\"NickName\",\"Type\",\"Sex\",\"City\" ) VALUES(%s,'%s',%d,'%s','%s') ;\n """ % ('currval(\'\"hero_reduce\".\"user_id_seq\"\')',
                                                                    normal(record.get('name')),1,
                                                                    normal(record.get('sex')),
                                                                    normal(record.get('city')) ))

#    print """INSERT INTO \"Resume\" (\"UserId\",\"Name\",\"School\",\"WorkingAge\",\"Description\") 
#                          VALUES(%d,'%s','%s',%d,'%s') ;""" %  (cur_id,normal(record.get('name')),
#                            normal(record.get('school')),
#                            int( '0' if record.get('workexp_year') is None else record.get('workexp_year')),
#                            normal(" ".join([ '' if record.get('exp_skill') is None else record.get('exp_skill'),
#                                              '' if record.get('ceritification') is None else record.get('ceritification')
#                                            ]))
#                           )
    filename.write("""INSERT INTO \"Resume\" (\"UserId\",\"Name\",\"School\",\"WorkingAge\",\"Description\")
                          VALUES(%s,'%s','%s',%d,'%s') ;\n""" %  ('currval(\'\"hero_reduce\".\"user_id_seq\"\')',normal(record.get('name')),
                            normal(record.get('school')),
                            int( '0' if record.get('workexp_year') is None else record.get('workexp_year')),
                            normal(" ".join([ '' if record.get('exp_skill') is None else record.get('exp_skill'),
                                              '' if record.get('ceritification') is None else record.get('ceritification')
                                            ]))
                           ))
    filename.write("COMMIT;\n")
    filename.flush()

def get_html(path):
    file = open(path,"r")
    html_file = file.read()
    file.close()
    return html_file

def test_exists(conn,resume_id):
    cursor = conn.cursor()
    cursor.execute('SELECT UserId FROM Message  WHERE Name=%s', resume_id)
    row = cursor.fetchone()
    return False if row is None else True

def main():
    
    rdb = ResumeDB()
    count = 0
    filename = open('rs_data.sql','wb')
    for resume_id in rdb.fs.list():
        count = count+1
        if count%10 ==0:
            print "================================== "+str(count)+" (CV) records have been added"+" =================================="
        print resume_id
	r = rdb.read_resume(resume_id)
        record = parse_resume(resume_id,r)
        #Resume is missong
        if 'sex' not in record or 'address' not in record:
           continue 
        generate_sql(filename,record,count)

def describe_unicode(s):
    import unicodedata
    for i in [(i,unicodedata.category(i)) for i in s]:
        if i[1] in ["Co"]:
            print i[0], i[1]


def unicode_filter(s):
    import unicodedata
    return "".join([i for i in s if unicodedata.category(i) not in ["Co"]])


if __name__ == "__main__":
    main()
