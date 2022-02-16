import time
import warnings
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from tld import get_tld



pattern = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
special_characters = "[$&+,:;=?@#|'<>.-^*()%!]"


X_train_columns = ['tlds_ip', 'strange_url', 'countleft_bracket', 'count$', 'count&',
       'count+', 'count,', 'count:', 'count;', 'count=', 'count?', 'count@',
       'count#', 'count|', "count'", "countleft_arrow", "count>", "count.",
       'count-', 'count^', 'count*', 'count(', 'count)', 'count%', 'count!',
       'countright_bracket', 'count_digits', 'count_alpha', 'url_length',
       'tlds_length', 'subdir']


# All functions
def count_digits(url):
    total = 0
    for i in url:
        if i.isnumeric():
            total += 1
    return total
        

def count_alpha(url):
    total = 0
    for i in url:
        if i.isalpha():
            total += 1
    return total



def urlextract_remaining(url):
    url_split=url.split(".")
    if len(url_split) <= 2:
        if url_split[0].startswith('0x'):
            return url_split[0].split('/')[0]
    
        else:
            return url_split[-1]
        
    else:
        return url_split[2].split('/')[0]

def clean_input(url, columns = X_train_columns):
    
		# 1) Get TLD
		url_df = pd.DataFrame(columns = ['url'])
		url_df.loc['url'] = url
		
		url_df.loc["tlds"] = get_tld(url, fix_protocol = True)
		url_df = url_df.T.reset_index().drop(columns = 'index')
		
		


		#2) Get country/region code if any
	#     url_df['countries'] = url_df['tlds'][~url_df['tlds'].isnull()].str.split('.').apply(lambda x: x[-1] if len(x[-1]) == 2 else np.nan)
		
		#3) get ip addresses if any
		url_df['tlds_ip'] = url_df[url_df['tlds'].isnull()]['url'].str.contains(pattern)

		#4) if tlds is still null:
		
		url_df.loc[url_df["tlds"].isnull(), "tlds"] = urlextract_remaining(url)
		
		
		#5) for strange urls:
		
		url_df.loc[url_df['tlds'].isnull() & url_df['tlds_ip'].isin([False,np.nan]),'strange_url'] = True
			
			
		url_df['strange_url'] = url_df['strange_url'].fillna(False)    
		#6) count no. of special chars:
		for i in special_characters:
			url_df['count' + i] = [url_df['url'][j].count(i) for j in url_df.index]
		
		#7) Count digits
		url_df['count_digits'] = count_digits(url)

		url_df.loc[url_df['count_digits'].isnull(), "count_digits"] = 0
		
		#8) Count alphabets
		url_df['count_alpha'] = count_alpha(url)

		url_df.loc[url_df['count_alpha'].isnull(), "count_alpha"] = 0
		
		#9) Count length of url
		url_df['url_length'] = len(url) 
		
		#10) Count length of tld
		url_df['tlds'] = url_df['tlds'].astype(str)
		url_df['tlds_length'] = url_df['tlds'].str.len()
		url_df.loc[url_df['tlds_length'].isnull(), "tlds_length"] = 0
		
		#11) presence of path/sub-dir
		sub_pattern = re.compile('[^/]\/{1}[^/]')
		url_df['subdir'] = re.match(sub_pattern,url)
		
		#12) Data encoding:
	#     url_df = pd.get_dummies(url_df, columns = ['tlds','countries'])
		#13) Encoding `tlds_ip`, `subdir`, `strange_url`
		url_df = url_df.rename(columns = {"count[":"countleft_bracket","count]":"countright_bracket","count<":"countleft_arrow"})
		url_df.replace(True, 1,inplace = True)
		url_df.replace(False,0,inplace = True)
		url_df.replace(np.nan,0, inplace = True)
		#14) Drop these as we have already dummified/deconstructed them
		url_df = url_df.drop(columns = ['url','tlds'])
		
		return url_df