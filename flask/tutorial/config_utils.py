import monk_adapter
import mongo_utils
import ConfigParser


def ConfigSectionMap(filename,section):
    dict1 = {}
    Config = ConfigParser.ConfigParser()
    Config.read(filename)
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

def read_config(filename,section):
	options = ConfigSectionMap(filename,section)
	return options

def write_config(filename,section,pairs):
	cfgfile = open(filename)
	Config = ConfigParser.ConfigParser()
    	Config.read(filename)
	if section not in Config.sections():
		Config.add_section(section)
	for key, value in pairs.iteritems():
		Config.set(section,key,value)
	with open(filename,'wb') as configfile:
		Config.write(configfile)
	

if __name__== "__main__":
	options = read_config()
	print options
