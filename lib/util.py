

def read_category_maps():
    """ Category codes from: http://www.ffiec.gov/hmdarawdata/FORMATS/2012HMDACodeSheet.pdf"""
    
    import os
    import csv
    
    d = os.path.dirname(__file__)
    
    maps = {}
    
    with open(os.path.join(d,'category_maps.csv')) as f:
        for row in csv.DictReader(f):
            if row['column'] not in maps:
                maps[row['column']] = {}
                

            maps[row['column']][str(row['code'])] = row['label']
        
        
    return maps
    
def add_category_column(df, column, maps = None):
    """Create a category column, with a _c suffix, from a colum that has it's name specified in the 
    category_maps.csv file"""
    
    name = column.name
    cat_col_name = column.name+"_c"
    
    if maps is None:
        maps = read_category_maps()
    col_map = maps[name]
    
    df[cat_col_name] = column.astype('category')
    df[cat_col_name].cat.rename_categories([ col_map[str(i)] for i in list(df[cat_col_name].cat.categories)], inplace = True)
  
def add_all_category_columns(df):
    
    maps = read_category_maps()
    
    for column_name, v in maps.items():
        print "Adding category column for ", column_name
        add_category_column(df, df[column_name], maps)
    

def reformat_tract(v):
    v = str(v)
    if '.' in v:
        try:
            a,b = v.split('.')
        except ValueError:
            print "Failed to split: ",v
            raise
        return u"{:04d}.{:02d}".format(int(a),int(b))
    else:
        return u"{:04s}".format(v)


def add_income_group(df):
    import numpy as np
    
    ranges = {
        (0,.5): 'low',
        (.5,.8): 'mod',
        (.8,1.2): 'mid',
        (1.2,np.inf): 'high'
    }
    
    def ig(x):
        if x == 0:
            return 'na'
        elif 0.0 < x < .5:
            return 'low'
        elif 0.5 <= x < .8:
            return 'mod'
        elif 0.8 <= x < 1.2:
            return 'mid'
        elif 1.2 < x:
            return 'high'
        
    def to_float(v):
        try:
            return float(v)
        except:
            return 0
        
    
    df.loc[:,'income_group'] = df.apply(lambda row: ig( to_float(row.applicant_income) * 100 / row.hud_median_family_income) , 
                                        axis=1)
 
def add_purpose_type(df):
    """Combine the Purpose and Type values into four values"""
    
    
    def apt(x):
        
        if x.loan_purpose == 1:  # Purchase
            if x.loan_type == 1: # Conventional
                return "purchase-conventional"
            else:                # Insured, guaranteed by govt
                return "purchase-govt"
        elif x.loan_purpose == 2:  
                return 'improvement'
        elif x.loan_purpose == 3:
                return 'refinance'
        else:
                return 'unknown'
                
    df.loc[:,'purpose_type'] = df.apply(lambda row: apt(row), axis=1)
            
        
    
     
def add_race_eth(df):
    eth_map = {
        1: 'h',
        2: 'nh',
        3: None,
        4: None,
        5: None
    }

    race_map = {
        1: 'aian',
        2: 'as',
        3: 'b',
        4: 'pi',
        5: 'w',
        6: None,
        7: None,
        8: None
    }

    re_map = {
        ('h','aian'): 'h',    ('nh','aian'): 'aian', (None,'aian'): 'aian',
        ('h','as')  : 'h',    ('nh','as')  : 'as',   (None,'as')  : 'as',
        ('h','b')   : 'b',    ('nh','b')   : 'b',    (None,'b')   : 'b',
        ('h','pi')  : 'h',    ('nh','pi')  : 'pi',   (None,'pi')  : 'pi',
        ('h','w')   : 'h',    ('nh','w')   : 'w',    (None,'w')   : 'w',
        ('h',None)  : 'h',    ('nh',None)  : 'w',    (None,None)  : None,
    }

    df.loc[:,'race_eth'] = df.apply(lambda row: re_map[(eth_map[row.applicant_ethnicity], race_map[row.applicant_race_1])], axis=1)
        

        
def tester():
    print 2
    
def tract_to_ua():
    import pandas as pd
    
    tract_to_ua = pd.read_csv('../data/ca_tract_to_ua.csv')
    sd_ua = tract_to_ua[tract_to_ua.county == 6073].copy()

    sd_ua['census_tract_number'] =  sd_ua.apply(lambda row: reformat_tract(row.tract), axis=1)
    sd_ua.set_index('census_tract_number',inplace = True)
    
    return sd_ua
    
def tract_to_msa():
    import pandas as pd
    
    tract_to_msa = pd.read_csv('../data/ca_tract_to_msa.csv')
    sd_msa = tract_to_msa[tract_to_msa.county == 6073].copy()

    sd_msa['census_tract_number'] =  sd_msa.apply(lambda row: reformat_tract(row.tract), axis=1)
    sd_msa.set_index('census_tract_number',inplace = True)
    
    return sd_msa
    
    
    