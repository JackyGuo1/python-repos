#coding=utf-8
import requests
import json

def handler(uri,method,payload=None):
	if method == "GET":
		print uri
		r = requests.get(uri)
		print r
	elif method == "POST":
		r = requests.post(uri,data=payload)
	else:
		print "Except \'GET\' and \'POST\' method, others are not supported currently"
		return
	#print str(r.headers).encode("utf-8")
	print  r.text.encode("utf-8")
	return r.text.encode("utf-8")

def make_msg(record):
#	row['educate'],
#        description=row['description'],
#        title=row['title'],
#        salary=row['salary'],
#        site=row['site'],
#        exp_year=row['exp_year'],
#        attract=row['attract']

	return '#'.join([record['title'],record['educate'],record['salary'],record['site'],record['exp_year'],record['attract'],record['description']])

def add_record(category_id,record):
	payload = { "data":record,"categoryId":category_id}
	msg = handler("http://192.168.1.5/zhike/Data/CreateData","POST",json.dumps(payload))
	return msg

def get_judged_by_records(groupId,record):
	payload = { "groupId":groupId, "msgList":record, "takeCount":"3" }
	responses = handler("http://192.168.1.5/zhike/Category/TestCategories","POST",json.dumps(payload))
        results = json.loads(responses)['Result']
        ids_results = []
        for r in results:
                print r
                result = r['Result']
                id =  r['Id']
                if result is None: ids_results.append({'id':id,'result':None})
                elif len(result) == 0 :ids_results.append({'id':id,'result':None})
                else :ids_results.append({'id':id,'result':result[0]})

        return ids_results


def remove_all_data(accountId,groupId):
	uri = "http://192.168.1.5/zhike/Group/RemoveGroup?accountId=%s&groupId=%s" %(accountId,groupId)
	msg = handler(uri,"GET")
	print msg
	return msg


def add_category(groupId,name):
        create_category_url = "http://192.168.1.5/zhike/Category/CreateCategory?groupId=%s&categoryName=%s" % (groupId,name)
        response = handler(create_category_url,"GET")
        #response :  {"Flag":true,"Message":"","Result":"54a0f658264b7b196019154e"}
        category_id = json.loads(response)["Result"]
	return category_id

def add_group(accountId,groupName,dataCollection):
	create_group_url = "http://192.168.1.5/zhike/Group/CreateGroup?accountId=%s&groupName=%s&dataCollection=%s" %(accountId,groupName,dataCollection)
	response =  handler(create_group_url,"GET")
	group_id = json.loads(response)["Result"]['GroupId']
	return group_id

def test():
	#handler("http://192.168.1.5/zhike/Account/CreateAccountNoMd5?userName=guojiaqi01&password=password","GET")
	#handler("http://192.168.1.5/zhike/Group/CreateGroup?accountId=549cd48f264b7d17e819ef47&groupName=1111&dataCollection=dataCollection1111","GET")
	handler("http://192.168.1.5/zhike/Category/CreateCategory?groupId=549d2b0b264b7b11f4b698b9&categoryName=NotCare","GET")
#	payload = { "data":"职位描述   本公司目前处于上升期，有良好的发展潜力和平台，实行人性化管理，诚邀优秀人士加盟！   任职资格：1、相关专业本科以上学历，5年以上相关项目管理或咨询规划经验，并具有至少1个大项目管理经验；2、有良好的沟通表达能力，优秀的领导能力，具有主动性、创造性和抗压性；有强烈的责任心和使命感。3、具有丰富的软件工程领域的知识，有CMM，CMMI经验者或者PMP、项目管理师认证者优先；4、具有信息系统产品经理经验者优先；5、具有政府领域信息化工作经验者优先；6、具备智慧城市公共信息平台（包括IaaS、PaaS、DaaS、SaaS等）、基础数据库建设等相关经验者优先。岗位职责：1、开展行业市场分析、产品调研分析、竞争产品研究、市场应用技术趋势研究等工作，撰写研究分析报告；2、收集并整理客户需求，建立技术需求文档；3、负责产品规划，并组织开展技术架构选型；4、协助进行产品市场及业务支持，协助解答客户业务及技术问题，开展产品培训等售前支持工作；5、负责专项项目的整体实施工作，包括项目总体控制、项目分解、项目分包、项目执行及项目监控等；6、与客户进行日常交流，跟踪客户的疑问和客户所关心的事情。", "categoryId":"549cd6e8264b7d17e819ef49" }
#	handler("http://192.168.1.5/zhike/Data/CreateData","POST",json.dumps(payload))
#	payload = { "groupId":"549d2b0b264b7b11f4b698b9", "message":"好的沟通表达能力，优秀的领导能力，具有主动性、创造性和抗压性", "takeCount":"3" }

#	response = handler("http://192.168.1.5/zhike/Category/TestCategory","POST",json.dumps(payload))
#	print json.loads(response)['Result'][0]['Score']

#	remove_all_data('549cd48f264b7d17e819ef47','549cd6e8264b7d17e819ef49')
#	handler("http://192.168.1.5/zhike/Category/RemoveCategory?categoryId=549d2b9b264b7b11f4b698c6&delData=False","GET")
#	handler("http://192.168.1.5/zhike/Category/GetCategoryTree?groupId=549d2b0b264b7b11f4b698b9","GET")
if __name__ == "__main__":
	test()
