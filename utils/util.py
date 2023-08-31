#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json

def dir_path_check(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    
def load_json_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            content = json.load(f)
    except: 
        content = {}
    return content

def remove_space(string):
    string=re.sub('\s+',' ',string)
    return string

def save_json_file(path, cont):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cont, f, ensure_ascii=False, indent=4)
