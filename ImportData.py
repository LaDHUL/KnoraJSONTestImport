#!/usr/bin/env python3

import requests
import json
import sys
import os
import re
import sys
import time

if len(sys.argv) != 3:
  print("Usage: "+sys.argv[0]+" <config.json> <data_folder>")
  sys.exit(1)

config_file = os.path.abspath(sys.argv[1])
data_folder = os.path.abspath(sys.argv[2])

start = time.time()
print("")
print("- Load config file: "+config_file)

with open(config_file, 'r') as f:
    config_json = json.load(f)

for x in config_json:
  if x == "url":
    url = config_json[x]
  print("   * %s: %s" % (x, config_json[x]))

print("")
print("- Login")
r = requests.post(
    url+"v2/authentication",
    json=config_json)

if not r.ok:
  print("*** ERROR ***")
  print(r)
  print(r.text)
  sys.exit(1)

token=r.json()['token']
print("   * token: %s" % token)

print("")
print("- Send data from folder "+data_folder)

res_dict = {}
folders=[]
nb_objs=0
nb_images=0
for root, dirs, files in os.walk(data_folder):
    for dir in dirs:
        folders.append(dir)
for folder in sorted(folders):
  print("")
  print(" => "+folder)
  res_dict[folder] = {}
  filenames=[]
  for root, dirs, files in os.walk(data_folder+"/"+folder):
      for f in files:
        filenames.append(f)
  for filename in sorted(filenames):
    fullpath = data_folder+"/"+folder
    if filename.split('.')[1] == 'json':
      print("")
      print("   -> "+filename)
      with open(fullpath+"/"+filename, 'r') as fp:
        file_content=fp.read().replace('\n', '')
        regex = r"<%(.*?)%>"
        matches = re.finditer(regex, file_content, re.MULTILINE | re.DOTALL)
        for matchNum, match in enumerate(matches):
          for groupNum in range(0, len(match.groups())):
            link = match.group(1)
            link_folder,link_filename = link.split('/')
            linked_iri=res_dict[link_folder][link_filename]
            print("   -> resolved link "+link+" into "+linked_iri)
            file_content = file_content.replace('<%'+link+'%>',linked_iri)
        json_obj = json.loads(file_content)
        img_file_png = filename.split('.')[0]+'.png'
        full_img_file_png = os.path.abspath(fullpath+"/"+img_file_png)
        img_file_jpg = filename.split('.')[0]+'.jpg'
        full_img_file_jpg = os.path.abspath(fullpath+"/"+img_file_jpg)
        if os.path.isfile(full_img_file_png):
          file = {
            'file': (
              full_img_file_png,
              open(full_img_file_png, 'rb'),
              "image/png"
              )
            }
          nb_images+=1
        elif os.path.isfile(full_img_file_jpg):
          file = {
            'file': (
              full_img_file_jpg,
              open(full_img_file_jpg, 'rb'),
              "image/jpeg"
              )
            }
          nb_images+=1
        else:
          file=None
        if file:
          print("   -> related image "+file['file'][0])
          r = requests.post(
                url+"v1/resources",
                data={'json': json.dumps(json_obj)},
                files=file,
                headers={
                    'Authorization': 'Bearer ' + token
                })
        else:
          r = requests.post(
                url+"v1/resources",
                json=json_obj,
                headers={
                    'Authorization': 'Bearer ' + token
                })
        if not r.ok:
          print("*** ERROR ***")
          print(r)
          print(r.text)
          sys.exit(1)
        res = json.loads(r.text)
        nb_objs+=1
        print("   -> "+str(r)+" | Created object "+folder+"/"+filename+" iri="+str(res['res_id']))
        res_dict[folder][filename]=res['res_id']

print("")
print("- Done: created "+str(nb_objs)+" objects and added "+str(nb_images)+" images ["+str(time.time() - start)+" s]")
print("")
