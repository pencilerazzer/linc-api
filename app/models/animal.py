#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields import StringField,DateTimeField,\
    ReferenceField,BooleanField,IntField
from motorengine.document import Document
from datetime import datetime

animal = 'lion'
animals = 'lions'

class Animal(Document):
    __collection__ = animals
    name = StringField(required=True,unique=True)
    iid = IntField(required=True,unique=True)
    organization_iid = IntField(required=False,default=-1)
    created_at = DateTimeField(required=True,default=datetime.now())
    updated_at = DateTimeField(required=True,default=datetime.now())
    primary_image_set_iid = IntField(required=False,default=-1)

    @classmethod
    def set_collection(cls,collname):
        """ Changes the default collection name for a object in MongoDB """
        cls.__collection__ = collname

    def list_animals(self):
        """ List animals in the database """
        pass # code for listing lions