#!/usr/bin/env python
# -*- coding: utf-8 -*-

# LINC is an open source shared database and facial recognition
# system that allows for collaboration in wildlife monitoring.
# Copyright (C) 2016  Wildlifeguardians
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For more information or to contact visit linclion.org or email tech@linclion.org

# Define a path that we can find the Monguo models
import sys
sys.path.append('/home/vagrant/linc-api/app')
from os.path import realpath,dirname
from json import loads,dumps
from datetime import datetime
import site
site.addsitedir('/home/vagrant/linc-api/app')

# Import models
from models.organization import Organization
from models.user import User
from models.animal import Animal
from models.imageset import ImageSet,Image
from models.cv import CVRequest,CVResult

from schematics.exceptions import ValidationError


jsonpath = dirname(realpath(__file__))
jsonpath = jsonpath[:-8]
jsonpath = jsonpath +'/pg_exported2json/'
print('Workdir:'+jsonpath)

import pymongo as pm
# Connection to Mongo DB
try:
    conn=pm.MongoClient()
    print("MongoDB Connected successfully!!!")
except:
   print("Could not connect to MongoDB")
conn.drop_database('linc-api-lions')
db = conn['linc-api-lions']

files = ['organizations.json','users.json','lions.json','image_sets.json',
'images.json','cv_requests.json','cv_results.json']

def readData(filename):
    # read data from json file
    f = open(filename)
    data = f.readlines()
    f.close()

    # Cleaning lines generated by psql
    data = data[2:-2]

    # Loading JSON structures to Python structures
    for n,d in enumerate(data):
        data[n] = loads(d)

    return data

response = {'messages':list()}
for fn in files:
    print(jsonpath+fn)
    data = readData(jsonpath+fn)
    if fn == 'organizations.json':
        print('Importing Organizations')
        for d in data:
            obj = dict(d)
            obj['iid'] = obj['id']
            del obj['id']
            obj['created_at'] = datetime.strptime(obj['created_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['updated_at'] = datetime.strptime(obj['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
            try:
                newobj = Organization(obj)
                newobj.validate()
                nob = db.organizations.insert(newobj.to_native())
                print 'added: '+str(nob)+' - '+obj['name']
            except ValidationError, e:
                print('Fail to import organizations. Errors: '+str(e))
                break
        response['messages'].append('organizations imported')
    elif fn == 'lions.json':
        print('Importing Organizations')
        for d in data:
            obj = dict(d)
            obj['iid'] = obj['id']
            del obj['id']
            obj['organization_iid'] = obj['organization_id']
            del obj['organization_id']
            obj['primary_image_set_iid'] = obj['primary_image_set_id']
            del obj['primary_image_set_id']
            obj['updated_at'] = datetime.strptime(obj['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['created_at'] = datetime.strptime(obj['created_at'], '%Y-%m-%d %H:%M:%S.%f')
            try:
                newobj = Animal(obj)
                newobj.validate()
                nob = db.lions.insert(newobj.to_native())
                print 'added: '+str(nob)+' - '+obj['name']
            except ValidationError, e:
                print('Fail to import Lions. Errors: '+str(e))
                break
        response['messages'].append('lions imported')
    elif fn in ['users.json']:
        print('Importing Users')
        for d in data:
            obj = dict(d)
            obj['iid'] = obj['id']
            del obj['id']
            obj['last_sign_in_at'] = datetime.strptime(obj['last_sign_in_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['updated_at'] = datetime.strptime(obj['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['created_at'] = datetime.strptime(obj['created_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['current_sign_in_at'] = datetime.strptime(obj['current_sign_in_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['trashed'] = False
            if 'reset_password_sent_at' in obj.keys():
                del obj['reset_password_sent_at']
            del obj['authentication_token']
            obj['organization_iid'] = obj['organization_id']
            del obj['organization_id']
            obj['admin'] = False
            del obj['remember_created_at']
            if '_remember_created_at' in obj.keys():
                del obj['_remember_created_at']
            try:
                newobj = User(obj)
                newobj.validate()
                nob = db.users.insert(newobj.to_native())
                print 'added: '+str(nob)+' - '+obj['email']
            except ValidationError, e:
                print('Fail to import Users. Errors: '+str(e))
                break
        response['messages'].append('users imported')
    elif fn == 'image_sets.json':
        print('Importing ImageSets')
        for d in data:
            obj = dict(d)
            obj['iid'] = obj['id']
            del obj['id']
            obj['animal_iid'] = obj['lion_id']
            del obj['lion_id']
            obj['main_image_iid'] = obj['main_image_id']
            del obj['main_image_id']
            obj['uploading_organization_iid'] = obj['uploading_organization_id']
            del obj['uploading_organization_id']
            obj['uploading_user_iid'] = obj['uploading_user_id']
            del obj['uploading_user_id']
            obj['owner_organization_iid'] = obj['owner_organization_id']
            del obj['owner_organization_id']

            if 'is_verified' not in obj.keys():
                obj['is_verified'] = False
            lat = obj['latitude']
            lng = obj['longitude']
            obj['location'] = [[lat,lng]]
            del obj['latitude']
            del obj['longitude']
            if 'gender' not in obj.keys():
                obj['gender'] = None
            if 'is_primary' in obj.keys():
                del obj['is_primary']

            obj['updated_at'] = datetime.strptime(obj['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['created_at'] = datetime.strptime(obj['created_at'], '%Y-%m-%d %H:%M:%S.%f')
            #if obj['photo_date']:
            #    obj['photo_date'] = datetime.strptime(obj['photo_date'], '%Y-%m-%d %H:%M:%S.%f')
            if obj['date_of_birth']:
                obj['date_of_birth'] = datetime.strptime(obj['date_of_birth'], '%Y-%m-%d %H:%M:%S.%f')
            if 'date_stamp' not in obj.keys():
                obj['date_stamp'] = '-'
            obj['tags'] = dumps(obj['tags'])
            if 'notes' not in obj.keys():
                obj['notes'] = ''
            obj['trashed'] = False

            del obj['decimal']
            del obj['photo_date']

            try:
                newobj = ImageSet(obj)
                newobj.validate()
                nob = db.imagesets.insert(newobj.to_native())
                print 'added: '+str(nob)+' - '+str(obj['iid'])
            except ValidationError, e:
                print('Fail to import ImageSets. Errors: '+str(e))
                break
        response['messages'].append('image sets imported')
    elif fn == 'images.json':
        print('Importing Images')
        imgs = list()
        for d in data:
            obj = dict(d)
            obj['iid'] = obj['id']
            del obj['id']
            obj['image_set_iid'] = obj['image_set_id']
            del obj['image_set_id']
            obj['updated_at'] = datetime.strptime(obj['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['created_at'] = datetime.strptime(obj['created_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['trashed'] = obj['is_deleted']
            obj['hashcheck'] = ''
            del obj['is_deleted']
            del obj['full_image_uid']
            del obj['main_image_uid']
            del obj['thumbnail_image_uid']
            url = obj['url']
            imgs.append({'iid':obj['iid'],'url':obj['url']})
            idx = url.index('.com/')
            pt1 = url[:idx+5]
            pt2 = url[idx+5:-4]
            #print('\n\n'+str(pt1))
            #print('\n\n'+str(pt2))
            obj['url'] = pt2
            try:
                newobj = Image(obj)
                newobj.validate()
                nob = db.images.insert(newobj.to_native())
                print 'added: '+str(nob)+' - '+str(obj['iid'])
            except ValidationError, e:
                print('Fail to import Images. Errors: '+str(e))
                break
        response['messages'].append('images imported')
        #f = open('images_url.json','w+')
        #f.write(dumps(imgs))
        #f.close()
        for url in imgs:
            resp = db.urlimages.insert(url)

    elif fn == 'cv_requests.json':
        print('Importing CVRequest')
        for d in data:
            obj = dict(d)
            obj['iid'] = obj['id']
            del obj['id']
            obj['image_set_iid'] = obj['image_set_id']
            del obj['image_set_id']
            obj['requesting_organization_iid'] = obj['uploading_organization_id']
            del obj['uploading_organization_id']
            obj['updated_at'] = datetime.strptime(obj['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['created_at'] = datetime.strptime(obj['created_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['request_body'] = ''
            if not obj['server_uuid']:
                continue
            try:
                newobj = CVRequest(obj)
                newobj.validate()
                nob = db.cvrequests.insert(newobj.to_native())
                print 'added: '+str(nob)+' - '+str(obj['iid'])
            except ValidationError, e:
                print('Fail to import CVRequest. Errors: '+str(e))
                break
        response['messages'].append('cv requests imported')
    elif fn == 'cv_results.json':
        print('Importing CVResults')
        cvd = dict()
        for d in data:
            if d['cv_request_id'] not in cvd.keys():
                cvd[d['cv_request_id']] = list()
            cvd[d['cv_request_id']].append(dict(d))
        #print(cvd)
        nid = 1
        for k,v in cvd.items():
            #print(k)
            #print(v)
            obj = dict()
            obj['iid'] = nid
            nid = nid + 1
            obj['cvrequest_iid'] = k
            obj['updated_at'] = datetime.strptime(v[0]['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
            obj['created_at'] = datetime.strptime(v[0]['created_at'], '%Y-%m-%d %H:%M:%S.%f')

            m = list()
            for ml in v:
                m.append({'id':ml['lion_id'],'confidence':ml['match_probability']})
            obj['match_probability'] = dumps(m)
            try:
                newobj = CVResult(obj)
                newobj.validate()
                nob = db.cvresults.insert(newobj.to_native())
                print 'added: '+str(nob)+' - '+str(obj['iid'])
            except ValidationError, e:
                print('Fail to import CVResults. Errors: '+str(e))
                break
        response['messages'].append('cv results imported')
print(response)
print('\nChecking counts: ')
print('Organizations:')
print db.organizations.count()
print('Users:')
print db.users.count()
print('Lions:')
print db.lions.count()
print('ImageSets:')
print db.imagesets.count()
print('Images:')
print db.images.count()
print('CVRequests:')
print db.cvrequests.count()
print('CVResults:')
print db.cvresults.count()
print('URLImages:')
print db.urlimages.count()

print('\nCalculate next integers ID:')
cols = ['organizations','users','lions','imagesets','images','cvrequests','cvresults']
for collec in cols:
    for x in db[collec].find({},{'iid':1}).sort("iid",pm.DESCENDING).limit(1):
        db.counters.insert({'_id':collec,'next':x['iid']+1})
    db[collec].create_index([('iid', pm.ASCENDING)],unique=True)

print('\nCounters')
for x in db.counters.find():
    print x

print ('\nCreating indexes ...')
db.organizations.create_index([('name', pm.ASCENDING)],unique=True)
db.users.create_index([("email", pm.ASCENDING)],unique=True)
db.lions.create_index([('name', pm.ASCENDING)],unique=True)
db.cvrequests.create_index([('image_set_iid', pm.ASCENDING)],unique=True)
db.cvresults.create_index([('cvrequest_iid', pm.ASCENDING)],unique=True)

db.organizations.create_index([('iid', pm.ASCENDING),('trashed', pm.ASCENDING)])
db.users.create_index([('iid', pm.ASCENDING),('trashed', pm.ASCENDING)])
db.lions.create_index([('iid', pm.ASCENDING),('trashed', pm.ASCENDING)])
db.imagesets.create_index([('iid', pm.ASCENDING),('trashed', pm.ASCENDING)])
db.images.create_index([('iid', pm.ASCENDING),('trashed', pm.ASCENDING)])
db.cvrequests.create_index([('iid', pm.ASCENDING),('trashed', pm.ASCENDING)])
db.cvresults.create_index([('iid', pm.ASCENDING),('trashed', pm.ASCENDING)])

db.imagesets.create_index([('location','2d')])

print('\nCleaning inconsistences')
idximgset = [x['iid'] for x in db.imagesets.find({},{'iid':1})]
dels = db.lions.remove({'primary_image_set_iid': { '$nin' : idximgset}},multi=True)
print 'Lions without primary_image_set_id removed:'+str(dels)
dels = db.images.remove({'image_set_iid': { '$nin' : idximgset}},multi=True)
print 'Images without image_set_id removed:'+str(dels)
dels = db.cvrequests.remove({'image_set_iid': { '$nin' : idximgset}},multi=True)
print 'CVRquests without image_set_id removed:'+str(dels)
idxcvreqs = [x['iid'] for x in db.cvrequests.find({},{'iid':1})]
dels = db.cvresults.remove({'cvrequest_iid': { '$nin' : idxcvreqs}},multi=True)
print 'CVResults without image_set_id removed:'+str(dels)
