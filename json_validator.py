import pandas as pd
import numpy as np
import datetime
import re
import json


class JsonValidator:
    
    def check_keys_isna(dict_test:dict, keys_expected:list)->dict:
        '''
        returns a dictionary 
        op = {
            'key1': flag_isna,
            'key2': flag_isna
        }
        '''
        keys_isna = list(
            set(JsonDataExtractor.keys_expected)\
            .difference(
                set(dict_test.keys())
            )
        )
        dict_keys_isna = {f"flag_{k}_isna":1 if k in keys_isna else 0 \
                          for k in keys_expected}
        return dict_keys_isna
        
    def check_keys_isempty(dict_test:dict)->dict:
        '''
        returns a dictionary 
        op = {
            'key1': flag_isempty,
            'key2': flag_isempty
        }        
        '''
        dict_keys_isempty = {}
        for k,v in dict_test.items():
            type_list = 1 if type(v) in [list, set] else 0
            if not type_list:
                dict_keys_isempty[f"flag_{k}_isempty"] = 1 if v in [np.nan, '', '_'] else 0
            elif type_list:
                dict_keys_isempty[f"flag_{k}_isempty"] = 0 if len(v)>0 else 1
        return dict_keys_isempty
        

        
class JsonDataExtractor:

    keys_expected = ['imageid', 'store', 'zone', 'aisle', 'section', 'image_issue', 'items']
    keys_expected_in_items = ['upc', 'status']
    
    def __init__(self, json_path:str):
        self.json_path = json_path
        self.imageid = self.get_imageid_from_path(self.json_path)
        self.flag_json_isempty = 0
        self.json_data = self.read_json(self.json_path)
        self.flag_items_isempty = 0
        
    def run(self)->None:
        if self.flag_json_isempty:
            print("json data is empty")
            return None
        dict_keys_isna = JsonValidator.check_keys_isna(self.json_data, 
                                                       JsonDataExtractor.keys_expected)
        dict_keys_isempty = JsonValidator.check_keys_isempty(self.json_data)
        dict_keys_isna.update(dict_keys_isempty)
        self.flag_items_isempty = dict_keys_isna.get('flag_items_isna', 0) | dict_keys_isna.get('flag_items_isempty', 0)
        dict_items_isna = self.check_items_isna(self.json_data)
        if dict_items_isna is not None:
            dict_keys_isna.update(dict_items_isna)
        self.dict_keys_isna = dict_keys_isna
        self.df_item = self.get_items_data(self.json_data)
        self.df_json_level_flags = self.json_level_flags_toframe()
        self.df_item_level_flags = self.item_level_flags_toframe()
        
    def get_imageid_from_path(self, path):
        filename = path.split("/")[-1]
        imageid = filename.split(".")[0]
        return imageid
    
    def read_json(self, path):
        try:
            with open(path) as f:
                raw_data = f.read()
            json_data = json.loads(raw_data)
            return json_data
        except Exception as e:
            self.flag_json_isempty = 1

    def check_items_isna(self, dict_test:dict):
        if self.flag_items_isempty:
            print("items info is empty")
            return None
        dict_item_isna = {}
        cnt_of_items = len(dict_test)  # total items in json
        for idx, dict_item in enumerate(dict_test.get('items')):
            dict_item_isna[f"upc_{idx}"] = self.check_item_isna(dict_item)
        return dict_item_isna
            
    def check_item_isna(self, dict_item:dict)->dict:
        dict_keys_isna = JsonValidator.check_keys_isna(dict_item, 
                                                       JsonDataExtractor.keys_expected_in_items)
        dict_keys_isempty = JsonValidator.check_keys_isempty(dict_item)
        dict_keys_isna.update(dict_keys_isempty)
        return dict_keys_isna
        
    def get_items_data(self, json_data:dict)->pd.DataFrame:
        df_items = pd.DataFrame({k:[] for k in JsonDataExtractor.keys_expected_in_items})
        if self.flag_items_isempty:
            print("items info is empty")
            return df_items
        items = json_data.get('items')
        df_items = pd.DataFrame(items)
        df_items = self.set_image_asindex(df_items)
        return df_items
    
    def set_image_asindex(self, df_raw):
        df = df_raw.copy()
        df['imageid'] = self.imageid
        df.set_index(keys=['imageid'], inplace=True)
        return df
    
    def json_level_flags_toframe(self):
        flags_in_op = list(self.dict_keys_isna.keys())
        flags_in_items = [flag for flag in flags_in_op if re.search('upc_', flag)]
        flags_in_op = [flag for flag in flags_in_op if flag not in flags_in_items]
        
        df_json_level_flags = pd.DataFrame(
            [{
                k:v 
                for k,v in self.dict_keys_isna.items() 
                if k in flags_in_op
            }
            ])
        df_json_level_flags = self.set_image_asindex(df_json_level_flags)
        return df_json_level_flags
    
    def item_level_flags_toframe(self):
        flags_in_op = list(self.dict_keys_isna.keys())
        flags_in_items = [flag for flag in flags_in_op if re.search('upc_', flag)]
        flags_in_op = [flag for flag in flags_in_op if flag not in flags_in_items]
        
        df_item_level_flags = pd.DataFrame(
            {k:v 
             for k,v in self.dict_keys_isna.items() 
             if k in flags_in_items
            }
        ).T\
            .reset_index(drop=False)\
            .rename(columns={'index':'upc'})
        df_item_level_flags = self.set_image_asindex(df_item_level_flags)
        return df_item_level_flags
        