#!/usr/bin/env python3

import requests
import json
import sys
import os
import re
import sys
import time
from enum import Enum

NEW_RESOURCE_ENDPOINT = "v1/resources"
UPDATE_RESOURCE_ENDPOINT = "v1/values"


class IMPORT_TYPE(Enum):
    CREATE = 1
    UPDATE = 2


class DataSource:
    def __init__(self):
        self.data_list = []


class ImportData:
    def __init__(self, import_type, key, json_data):
        self.import_type = import_type
        self.key = key
        self.json_data = json_data

    def __str__(self):
        return "%s %s" % (self.import_type, self.key)

    def __repr__(self):
        return self.__str__()


class UpdateData(ImportData):
    def __init__(self, key, json_data):
        super().__init__(IMPORT_TYPE.UPDATE, key, json_data)


class CreateData(ImportData):
    def __init__(self, key, json_data, image_filename, image_type):
        super().__init__(IMPORT_TYPE.CREATE, key, json_data)
        self.image_filename = image_filename
        self.image_type = image_type

    def __str__(self):
        return super().__str__()+(" %s %s" % (self.image_filename, self.image_type))


def loadConfig(config_file):
    url = None
    email = None
    password = None
    with open(config_file, 'r') as f:
        config_json = json.load(f)
        for key in config_json:
            if key == "url":
                url = config_json[key].strip('/')
            if key == "email":
                email = config_json[key]
            if key == "password":
                password = config_json[key]
    return url, email, password


def loadDataList(data_list):
    dataList = []
    with open(data_list) as fp:
        for cnt, line in enumerate(fp):
            lineStripped = line.strip()
            if len(lineStripped.strip()) > 0 and not lineStripped.startswith('#'):
                dataList.append(lineStripped.split())
    return dataList


def findImageFile(folder, basefilename):
    img_file = None
    img_type = None
    img_jpg = os.path.join(folder, basefilename+'.jpg')
    if os.path.exists(img_jpg):
        img_file = img_jpg
        img_type = "image/jpeg"
    img_png = os.path.join(folder, basefilename+'.png')
    if os.path.exists(img_png):
        img_file = img_png
        img_type = "image/png"
    return img_file, img_type


def scanFiles(folder, extension):
    json_files = []
    for f in os.listdir(folder):
        full_f = os.path.join(folder, f)
        basefilename, file_extension = os.path.splitext(full_f)
        if file_extension == "."+extension:
            img_file, img_type = findImageFile(folder, basefilename)
            json_files.append([full_f, img_file, img_type])
    return sorted(json_files, key=lambda tup: tup[0])


def resolveLinks(content, link_resolver):
    res = content
    regex = r"<%(.*?)%>"
    matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
    for matchNum, match in enumerate(matches):
        for groupNum in range(0, len(match.groups())):
            link = match.group(1)
            iri = link_resolver[link]
            print("\t\t-> resolved link "+link+" into "+iri)
            res = res.replace('<%'+link+'%>', iri)
    return res


def createDataSourceList(data_list):
    root_folder = os.path.dirname(data_list)
    data_source = DataSource()
    data_list = loadDataList(data_list)
    for type, folder in data_list:
        import_type = IMPORT_TYPE[type]
        full_folder = os.path.join(root_folder, folder)
        for json_file_bulk in scanFiles(full_folder, "json"):
            json_file, image_file, image_type = json_file_bulk
            with open(json_file, 'r') as fp:
                json_data = fp.read().replace('\n', '')
            key = folder+'/'+os.path.basename(json_file)
            if import_type == IMPORT_TYPE.CREATE:
                import_data = CreateData(
                    key, json_data, image_file, image_type)
            if import_type == IMPORT_TYPE.UPDATE:
                import_data = UpdateData(key, json_data)
            data_source.data_list.append(import_data)
    return data_source


def createData(url, email, password, create_data, link_resolver):
    full_url = url+'/'+NEW_RESOURCE_ENDPOINT
    json_data_resolved = resolveLinks(create_data.json_data, link_resolver)
    json_obj = json.loads(json_data_resolved)
    if create_data.image_filename:
        r = requests.post(
            full_url,
            data={'json': json.dumps(json_obj)},
            files={
                'file': (
                    create_data.image_filename,
                    open(create_data.image_filename, 'rb'),
                    create_data.image_type
                )
            },
            auth=(email, password))
    else:
        r = requests.post(
            full_url,
            json=json_obj,
            auth=(email, password))
    if not r.ok:
        raise Exception(r.text)
    res = json.loads(r.text)
    return res['res_id']


def updateData(url, email, password, update_data, link_resolver):
    full_url = url+'/'+UPDATE_RESOURCE_ENDPOINT
    json_data_resolved = resolveLinks(update_data.json_data, link_resolver)
    json_obj = json.loads(json_data_resolved)
    r = requests.post(
        full_url,
        json=json_obj,
        auth=(email, password))
    if not r.ok:
        raise Exception(r.text)


if len(sys.argv) != 3:
    print("Usage: "+os.path.basename(sys.argv[0]) +
          " <connection.json> <data.list>")
    sys.exit(1)

config_file = os.path.abspath(sys.argv[1])
data_list = os.path.abspath(sys.argv[2])
include_pattern = None
if len(sys.argv) >= 4:
    include_pattern = sys.argv[3]


start = time.time()
print("")
print("- Load config file: "+config_file)
[url, email, password] = loadConfig(config_file)
if not url or not email or not password:
    print("Cannot find url, email or password in json config file.")
    sys.exit(1)
print("   * url=%s email=%s password=%s" % (url, email, password))

print("")
print("- Check user/password")
r = requests.post(
    url+"/v2/authentication",
    json={
        "email": email,
        "password": password
    })

if not r.ok:
    print("*** ERROR ***")
    print(r)
    print(r.text)
    sys.exit(1)

print("")
print("- Create data source from data list: "+data_list)

data_source = createDataSourceList(os.path.abspath(data_list))

print("")
nb_ops = len(data_source.data_list)
print("- Load data source (nb operations: %s)" % str(nb_ops))

link_resolver = {}
count = 0
nb_objs_created = 0
nb_objs_updated = 0
nb_images = 0

for data in data_source.data_list:
    count += 1
    print("")
    if data.import_type == IMPORT_TYPE.CREATE:
        print("\t-> %s/%s Create %s" % (count, nb_ops, data.key))
        if data.image_filename:
            print("\t\t-> Related image : %s %s" %
                  (data.image_type, data.image_filename))
            nb_images += 1
        iri = createData(url, email, password, data, link_resolver)
        print("\t\t-> IRI: %s" % iri)
        link_resolver[data.key] = iri
        nb_objs_created += 1

    if data.import_type == IMPORT_TYPE.UPDATE:
        print("\t-> %s/%s Update %s" % (count, nb_ops, data.key))
        updateData(url, email, password, data, link_resolver)
        nb_objs_updated += 1

print("")
print("- Done: created %s and updated %s objects, added %s images [%s s]" %
      (nb_objs_created, nb_objs_updated, nb_images, str(time.time() - start)))
print("")
