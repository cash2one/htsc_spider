# -*- coding: utf-8 -*-

from  avro import schema
from avro.io import DatumWriter, BinaryEncoder
from cStringIO import StringIO

from common.config import GlobalConfig


class AvroUtils(object):
    @staticmethod
    def getConsensusSchema():
        return schema.parse(open(GlobalConfig.project_home+"/avrotools/consensus.avsc").read())
    
    @staticmethod
    def getNewsSchema():
        return schema.parse(open(GlobalConfig.project_home+"/avrotools/news.avsc").read())
    
    @staticmethod
    def getCommentsSchema():
        return schema.parse(open(GlobalConfig.project_home+"/avrotools/comments.avsc").read())
    
    '''  
    #@staticmethod
    def createAvroFileRecord(data,schema):
        print "createAvroRecord invoked"
        writer = DataFileWriter(open(GlobalConfig.project_home+"/avrotools/news.avro", "a"), DatumWriter(), schema)
        writer.append(dict(data))
        writer.close()
    '''
    
    @staticmethod
    def createAvroMemoryRecord(data,schema):
        f = StringIO()
        encoder = BinaryEncoder(f)
        writer = DatumWriter(schema)
        writer.write(dict(data),encoder)
        return f.getvalue()