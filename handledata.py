#coding=utf-8
#从文件中处理数据
import struct
import binascii
from database import *


#获取到所有数据点
class pointdata:
    TNDP = 0
    TP = 0
    STARTPOINT = 0
    POINT_DATA = []

    def __init__(self,filename):
        with open(filename,'r') as fr:
            all_lines = fr.readlines()
            self.STARTPOINT = int(all_lines[0].strip())
            self.TP = int(all_lines[1].strip())
            self.TNDP = len(all_lines) - 2
            for line in all_lines[2:]:
                self.POINT_DATA.append(int(float(line.strip())*1000000))

    def getbytearray(self):
        segement1 = struct.pack('!i',self.TNDP)
        segement2 =  b''.join(struct.pack('!i', elem) for elem in self.POINT_DATA)
        segement3 = struct.pack('!i',self.TP)
        # print newbyte
        return segement1 + segement2 + segement3

    def template_getbytearray(self):
        #TNDP
        segement1 = struct.pack('!i',self.TNDP)
        #数据点
        segement2 = b''.join(struct.pack('!i', elem) for elem in self.POINT_DATA)
        return segement1 + segement2

    def ocrtest_getbytearray(self):
        #TNDP
        segement1 = struct.pack('!i',self.TNDP)
        #数据点
        segement2 = b''.join(struct.pack('!i', elem) for elem in self.POINT_DATA)
        return segement1 + segement2

    def setPointdata(self,value):
        self.POINT_DATA = value


#吸入线路设置数据库
@db_session
def write_to_linesetup_db():
    data = pointdata('linesetup_data')
    FrameData_Linesetup(TNDP=data.TNDP,POINTS=str(data.POINT_DATA),TP=data.TP)

@db_session
def read_from_linesetup_db():
    data = FrameData_Linesetup.select()[:]
    for d in data:
        print d.TNDP
#

#写入模板获取数据库
@db_session
def write_to_template_db():
    data = pointdata('gettemplate_data')
    FrameData_Template(TNDP=data.TNDP,POINTS=str(data.POINT_DATA))

@db_session
def read_from_template_db():
    data = FrameData_Template.select()[:]
    print data[0].TNDP
#

#光缆普查测试点写入数据库
@db_session
def write_to_ocrtest_db():
    data = pointdata('ocrtest_data')
    FrameData_OCRData(TNDP=data.TNDP,POINTS=str(data.POINT_DATA))
#

#故障追踪测试点写入数据库
@db_session
def write_to_tracefault_db():
    data = pointdata('tracefault_data')
    FrameData_TraceFault(TNDP=data.TNDP, POINTS=str(data.POINT_DATA))

#

class ByteArrayData:

    @db_session
    def get_linesetup_bytearray(self):
        data = FrameData_Linesetup.select()[:]
        point_data = eval(data[0].POINTS)
        segement1 = struct.pack('!i', data[0].TNDP)
        segement2 = b''.join(struct.pack('!i', elem) for elem in point_data)
        segement3 = struct.pack('!i', data[0].TP)
        # print newbyte
        return segement1 + segement2 + segement3

    @db_session
    def get_ocrtest_bytearray(self):
        data = FrameData_OCRData.select()[:]
        point_data = eval(data[0].POINTS)
        #TNDP
        segement1 = struct.pack('!i',data[0].TNDP)
        #数据点
        segement2 = b''.join(struct.pack('!i', elem) for elem in point_data)
        return segement1 + segement2

    @db_session
    def get_tracefault_bytearray(self):
        data = FrameData_TraceFault.select()[:]
        point_data = eval(data[0].POINTS)
        #TNDP
        segement1 = struct.pack('!i',data[0].TNDP)
        #数据点
        segement2 = b''.join(struct.pack('!i', elem) for elem in point_data)
        return segement1 + segement2

    @db_session
    def get_template_bytearray(self):

        data = FrameData_Template.select()[:]
        point_data = eval(data[0].POINTS)
        #TNDP
        segement1 = struct.pack('!i',data[0].TNDP)
        #数据点
        segement2 = b''.join(struct.pack('!i', elem) for elem in point_data)
        return segement1 + segement2

    @db_session
    def is_login_identify(self,ident):
        obj_device = Device.get(dc_identify=ident)
        if obj_device == None:
            return False
        else:
            return True


if __name__ == '__main__':
    # write_to_tracefault_db()
    # read_from_template_db()
    ba = ByteArrayData()
    # print ba.get_template_bytearray()
    print ba.is_login_identify("AAAAAAAAAAAAAAAA")

