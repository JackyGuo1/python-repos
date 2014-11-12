#!/usr/bin/python
# coding= utf-8
from lxml import etree
import lxml.html as html
import re
from pymongo import MongoClient
import pymssql
def content_clean(content):
    cleaned = content.replace(" ","").replace("\r\n"," ").replace("\r"," ").replace("\n"," ").lstrip(" ").rstrip(" ")
    return cleaned

def content_clean_with_space_include(content):
    cleaned = content.replace("\r\n"," ").replace("\r"," ").replace("\n"," ").lstrip(" ").rstrip(" ")
    return cleaned


def print_dict(input_dict):
    for key in iter(input_dict):
        print key, input_dict[key]


def get_basic(doc):
    try:
        dom_text = doc.xpath("//ul[@class='terminal-ul clearfix']")[0].text_content().replace(u'\xa0',u' ' ).replace(" ","")
    except IndexError:
        print "Description format is different from template"
        return dict()
    salary_p = re.compile(u'职位月薪：(\d+)-(\d+)元/月\r\n')
    location_p = re.compile(u'工作地点：(.*)\r\n')
    education_background_p = re.compile(u'最低学历：(.*)\r\n')
    work_exp_year_p = re.compile(u'工作经验：(?P<year>(\d+)|(\d+-\d+))(.*)\r\n')
    title_p = re.compile(u'职位类别：(.*)\r\n')
    
    salary_m = salary_p.search(dom_text)
    location_m =  location_p.search(dom_text)
    education_background_m = education_background_p.search(dom_text)
    work_exp_year_m = work_exp_year_p.search(dom_text)
    title_m = title_p.search(dom_text)
    
    basic_info = dict()
    if salary_m:
        basic_info['salary'] = '-'.join([salary_m.group(1),salary_m.group(2)])
    if location_m:
        basic_info['location'] = location_m.group(1)
    if education_background_m:
        basic_info['education_background'] = education_background_m.group(1)
    if work_exp_year_m:
        basic_info['work_exp_year'] = work_exp_year_m.group('year')
    if title_m:
        basic_info['title'] = title_m.group(1)
    return basic_info

def get_detail(doc):
    detail_info = dict()
    try:
        requirement_text = doc.xpath("//div[@class='tab-cont-box']/div[@class='tab-inner-cont']")[0].text_content().replace(u'\xa0',u' ')
    except IndexError:
        print "Description format is different from template"
        return dict()
    detail_info['requirement'] = content_clean_with_space_include(requirement_text)
    narratage_text = doc.xpath("//div[@class='tab-cont-box']/div[@class='tab-inner-cont']")[1].text_content().replace(u'\xa0',u' ')
    detail_info['narratage'] = content_clean_with_space_include(narratage_text)
    return detail_info


def make_record(jd_id,basic_info,detail_info):
    record = dict()
    list_key = ['salary','location','education_background','work_exp_year','title']
    for key in list_key:
        record[key] = basic_info.get(key,None)
    list_key = ['requirement','narratage']
    for key in list_key:
        record[key] = detail_info.get(key,None)   
    record['name'] = jd_id
    return record

def parse_description(jd_id,html_file):
    # file = open(path,"rb")
    # html_file = file.read()
    # file.close()
    doc = html.document_fromstring(html_file)
    basic_info = get_basic(doc)
    detail_info = get_detail(doc)    
    record = make_record(jd_id,basic_info,detail_info)
    return record

def test_exists(conn,jd_id):
    cursor = conn.cursor()
    cursor.execute('SELECT UserId FROM Message  WHERE Name=%s', jd_id)
    row = cursor.fetchone()
    return False if row is None else True


def get_connection(servername,username,password_string,dbname):
    conn = pymssql.connect(host=servername,user=username, password=password_string,database=dbname)
    return conn
def insert_record(conn,record):
    cur = conn.cursor()
    cur.execute( "INSERT INTO [User] (Type,City) values (%d,%s)",(0,record.get('location',None)) )
    cur.execute("SELECT IDENT_CURRENT('user')")
    UserId = cur.fetchone()[0]

    cur.execute('''INSERT INTO
Message(UserId,Name,Address,Salary,School,WorkingAge,Description,title,RefreshDate)
values (%d,%s,%s,%s,%s,%d,%s,%s,GETDATE()) ''',( int(UserId),
                                    record.get('name',None),
                                    record.get('location',None),
                                    record.get('salary',None),
                                    record.get('education_background',None),
                                    int( 0 if record.get('work_exp_year') is None else record.get('work_exp_year')  ),
                                    " ".join([ "" if  record.get('requirement') is None else record.get('requirement'),
                                               "" if record.get('narratage') is None else record.get('narratage')
                                              ]),
                                    record.get('title',None)
                                   ) )

    print "Job Hunter #"+str(UserId)+" Added"

def normal(text):
    return ("" if text is None else text).replace(r'\r','').encode("utf-8").replace('\'','\'\'')

def generate_jd_sql(filename,record,cur_id):
#    print """INSERT INTO \"User\" (\"Name\",\"UserType\",\"CreatedDatetime\",\"UpdatedDatetime\",\"Enabled\") 
#                              VALUES ('%s',%d,clock_timestamp(),clock_timestamp(),'t') ;""" % (record.get('name','null'),4)
    filename.write("""INSERT INTO \"User\" (\"Name\",\"UserType\",\"CreatedDatetime\",\"UpdatedDatetime\",\"Enabled\")
                              VALUES ('%s',%d,clock_timestamp(),clock_timestamp(),'t') ;\n""" % (record.get('name','null'),4))
#    print "COMMIT;"

#    print """INSERT INTO \"ZhilianUser\" (\"UserId\",\"NickName\",\"Type\",\"Sex\",\"City\" ) VALUES(%s,'%s',%d,'%s','%s') ; """ % ('currval(\'\"hero_reduce\".\"user_id_seq\"\')',
#                                                                        normal(record.get('name','null')),0,
#                                                                        normal(record.get('sex','null')),
#                                                                        normal(record.get('location','null')) ) 
    filename.write("""INSERT INTO \"ZhilianUser\" (\"UserId\",\"NickName\",\"Type\",\"Sex\",\"City\" ) VALUES(%s,'%s',%d,'%s','%s') ; """ % ('currval(\'\"hero_reduce\".\"user_id_seq\"\')',
                                                                        normal(record.get('name','null')),0,
                                                                        normal(record.get('sex','null')),
                                                                        normal(record.get('location','null')) ))

#    print """INSERT INTO \"JobPosition\" (\"UserId\",\"Name\",\"Address\",\"Title\",\"Salary\",\"Description\") 
#                          VALUES(%s,'%s','%s','%s','%s','%s') ;""" %  ( 'currval(\'\"hero_reduce\".\"user_id_seq\"\')' , normal(record.get('name','null')),
#                            normal(record.get('location',None)),
#                            normal(record.get('title',None)),
#                            normal(record.get('salary',None)),
#                            normal(record.get('requirement',None))
#                           )
    filename.write("""INSERT INTO \"JobPosition\" (\"UserId\",\"Name\",\"Address\",\"Title\",\"Salary\",\"Description\")
                          VALUES(%s,'%s','%s','%s','%s','%s') ;\n""" %  ( 'currval(\'\"hero_reduce\".\"user_id_seq\"\')' , normal(record.get('name','null')),
                            normal(record.get('location',None)),
                            normal(record.get('title',None)),
                            normal(record.get('salary',None)),
                            normal(record.get('requirement',None))
                           ))
    filename.write("COMMIT;\n")
#    print "COMMIT;"
    filename.flush()


    


def main():
    # parse_description('./description/120472627250502.htm')
    coll = MongoClient("mongodb://192.168.1.11:27017/").zhaopin_jd["jd"]
    filename = open("./jd_data.sql","wb")
    count = 0

    for jd in coll.find():
        count = count+1
        if count%10 == 0:
            print "================================== "+str(count)+" (JD) records have been added"+" =================================="
        jd_id =  jd['filename']
        print jd_id
        record = parse_description(jd_id,jd['body'])
        generate_jd_sql(filename,record,count)
        #Job Description is missing
        if 'salary' not in record or 'location' not in record:
           continue


if __name__ == "__main__":
    main()
