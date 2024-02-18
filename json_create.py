import pandas as pd
import numpy as np
import datetime 
import string
import re
import os
import json


def get_drop_key_count(dict_w_keys:dict, p:float=0.1)->int:
    keys_to_drop = dict_w_keys.keys()
    cnt_keys_to_drop = np.random.randint(0, len(keys_to_drop)) if np.random.rand()<p else 0
    if cnt_keys_to_drop>0:
        for i in range(cnt_keys_to_drop):
            key = np.random.choice(list(dict_w_keys.keys()), 1)[0]
            dict_w_keys.pop(key)
    return dict_w_keys


def create_item_info(item_statuses:list, p:float=0.05)->dict:
    dict_item_info = {
        'upc': np.random.randint(100000,999999),
        'status': np.random.choice(item_statuses, 1)[0],
    }
    dict_item_info['upc'] = dict_item_info['upc'] if np.random.rand()>p else '_'
    dict_item_info['status'] = dict_item_info['status'] if np.random.rand()>p else ''
    
    dict_item_info = get_drop_key_count(dict_item_info, p)
    
    return dict_item_info


def create_json_fullinfo(image_issues:list, item_statuses:list, p:float=0.05)->dict:
    cnt_items = np.random.randint(1,20)
    data_json = {
        'imageid': np.random.randint(1000,9999),
        'store': np.random.randint(1,100),
        'zone': np.random.choice(list(string.ascii_uppercase), 1)[0],
        'aisle': np.random.randint(1,9),
        'section': np.random.randint(1,9),
        'image_issue': [np.random.choice(image_issues, 1)[0]],
        'items': [create_item_info(item_statuses) for k in range(1, cnt_items+1)]
    }
    
    data_json = get_drop_key_count(data_json, p)
    
    return data_json


def create_test_jsons(path_data:str, nbr_of_files:int=10, flag_print:bool=True, p:float=0.5):
    
    image_issues = ['blury image', 'angled image', 'perfect image', 'blocked image']
    item_statuses = ['detected', 'undetected', 'empty']
    
    filenames = [f"{idx}"*5 + '.json' for idx in range(1, nbr_of_files)]
    
    l_json_data = []
    for idx in range(1, nbr_of_files):
        json_data = create_json_fullinfo(image_issues, item_statuses, p)
        l_json_data.append(json_data)
        filename = path_data + f"{idx}"*5 + '.json'
        if flag_print:
            print(filename.split("/")[-1], '\n', json_data, '\n\n')
        with open(filename, 'w') as f:
            json.dump(json_data, f)
            
    print(f"{len(l_json_data)} jsons written to: \n{path_data}")
    return l_json_data


if __name__ == 'main':
    
    path_data = 'data_op_json/'

    l_json_data = create_test_jsons(path_data, 10, False, 0.5)