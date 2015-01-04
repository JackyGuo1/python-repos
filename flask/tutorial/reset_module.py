import monk_adapter
import mongo_utils
import config_utils
import json


def reset_module():
	options = config_utils.read_config("./monk_adapter.conf","MonkAccount")
	print options
	monk_adapter.remove_all_data(options['accountid'],options['groupid01'])
	options['groupid01'] = monk_adapter.add_group(options['accountid'],"group01","dataCollection01")
	monk_adapter.remove_all_data(options['accountid'],options['groupid02'])
	options['groupid02'] = monk_adapter.add_group(options['accountid'],"group02","dataCollection02")

	#reCreate Categories
	like_category_id = monk_adapter.add_category(options['groupid01'],'like')
	unlike_category_id = monk_adapter.add_category(options['groupid01'],'unlike')

	s_like_category_id = monk_adapter.add_category(options['groupid02'],'like')
	s_unlike_category_id = monk_adapter.add_category(options['groupid02'],'unlike')


	pairs = {'groupid01':options['groupid01'],'category_like':like_category_id,'category_unlike':unlike_category_id,
		'groupid02':options['groupid02'],'s_category_like':s_like_category_id,'s_category_unlike':s_unlike_category_id}

	config_utils.write_config("./monk_adapter.conf","MonkAccount",pairs)




if __name__ == "__main__":
	reset_module()
