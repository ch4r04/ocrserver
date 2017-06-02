#coding=utf-8
from SocketServer import ThreadingMixIn,ForkingMixIn,StreamRequestHandler
import socket,select,binascii

import SocketServer
from SocketServer import StreamRequestHandler as SRH
from SocketServer import *
from time import ctime
import struct,time
from handledata import pointdata
from handledata import ByteArrayData

host = '0.0.0.0'
port = 9999
addr = (host, port)

class Servers(SRH):
    CONNECT_FLAG = True
    HEADER = ''
    PKLEN = ''
    REV = ''
    SRC = ''
    DST = ''
    PKTYP = ''
    PKID = ''
    OTHER_CMD = ''
    CMDCODE = ''
    DATLEN = ''
    DATA = ''
    END = ''
    HEX_DATA = ''

    ba = ByteArrayData()

    def handle(self):
        # print 'got connection from ', self.client_address
        self.print_start_con()
        while self.CONNECT_FLAG:
            try:
                data = self.request.recv(1024)
                if not data:
                    print "RECV from ", self.client_address[0]
                    break
                # print data
                # print binascii.b2a_hex(data)
                mdata = binascii.b2a_hex(data)
                self.HEX_DATA = mdata
                self.checkConnectData(mdata)
            except Exception, e:
                print e
                break

    def checkConnectData(self,mdata):
        #check is a vaild packet
        if mdata[0:8] != 'ffffeeee' or mdata[-8:] != 'eeeeffff':
            self.print_unvaild()
            return
        bytelen = mdata[8:16]
        bytelen_int =  int(eval('0x'+bytelen))
        if bytelen_int != len(mdata) / 2:
            self.print_unvaild()
            return
        #data a vaild
        try:
            self.HEADER = mdata[0:8]
            self.PKLEN = mdata[8:16]
            self.REV = mdata[16:24]
            self.SRC = mdata[24:32]
            self.DST = mdata[32:40]
            self.PKTYP = mdata[40:44]
            self.PKID = mdata[44:48]
            self.OTHER_CMD = mdata[48:56]
            self.CMDCODE = mdata[56:64]
            self.DATLEN = mdata[64:72]
            self.DATA = mdata[72:-8]
            self.END = mdata[-8:]
            self.switch_fun(self.CMDCODE)
        except Exception, e:
            print e
            pass


    def switch_fun(self,x):
        if x == "82000000":
            self.req_login(),
        elif x == "82000002":
            self.req_disconnect(),
        elif x == "81000000":
            self.req_startlinesetup(),
        elif x == "81000001":
            self.req_linesetuprefresh(),
        elif x == "81000003":
            self.req_stoplinetest(),
        elif x == "81000005":
            self.req_gettemplate(),
        elif x == "81000007":
            self.req_stopgettemplate(),
        elif x == "81000008":
            self.req_tracefault(),
        elif x == "8100000b":
            self.req_stoptrace(),
        elif x == "8100000c":
            self.req_ocrtest(),
        elif x == "8100000e":
            self.req_stopocrtest()

    #response login packet
    #收到登录
    def req_login(self):
        # print "RECV from ", self.client_address[0]
        self.print_recv_packet(self.client_address[0],"Login",self.CMDCODE,self.DATA,"请求登录")
        login_device = binascii.a2b_hex(self.DATA)
        if self.ba.is_login_identify(login_device) == True:
            self.request.sendall("OK_CONNECT")
        else:
            self.request.sendall("ERROR_CONNECT")
        self.print_send_packet(self.client_address[0],"NULL",self.CMDCODE, "OK_CONNECT","发送连接指令")

    #disconnect
    #收到断开连接
    def req_disconnect(self):
        self.print_recv_packet(self.client_address[0],"Disconnect",self.CMDCODE,self.DATA,"断开连接")
        self.CONNECT_FLAG = False


    #收到开始线路设置请求
    def req_startlinesetup(self):
        # data = "YOU ARE TRING TO LINE SETUP"
        self.print_recv_packet(self.client_address[0],"Start Line Setup",self.CMDCODE,self.DATA,"请求线路设置")
        # 直接返回测试数据了 添加头和尾
        segment_header = binascii.a2b_hex('ffffeeee')
        segment_trai = binascii.a2b_hex('eeeeffff')

        segment_center = self.ba.get_linesetup_bytearray()
        # 构造完整帧
        segment_data = segment_header + segment_center + segment_trai
        #发送完整帧
        self.request.sendall(segment_data)
        self.print_recv_packet(self.client_address[0],"Send Line Setup",self.CMDCODE,segment_data,"发送线路信息成功")

        pointdata.POINT_DATA = []



    #收到刷新线路设置请求
    def req_linesetuprefresh(self):
        # print "linesetup refresh"
        self.print_recv_packet(self.client_address[0],"Line Setup Refresh",self.CMDCODE,self.DATA,"请求刷新线路")

    #停止线路请求
    def req_stoplinetest(self):
        # print "stop line setup"
        self.print_recv_packet(self.client_address[0],"Line Setup Stop",self.CMDCODE,self.DATA,"停止线路设置")

    #收到获取模板请求
    def req_gettemplate(self):
        # print "get template"
        self.print_recv_packet(self.client_address[0],"Get Template",self.CMDCODE,self.DATA,"请求获取模板")
        # 直接返回测试数据了 添加头和尾
        segment_header = binascii.a2b_hex('ffffeeee81000006')
        segment_trai = binascii.a2b_hex('eeeeffff')
        segment_center = self.ba.get_template_bytearray()
        # 构造完整帧
        segment_data = segment_header + segment_center + segment_trai
        self.request.sendall(segment_data)
        self.print_send_packet(self.client_address[0],"Send Get Template",self.CMDCODE,segment_data,"请求获取模板")
        pointdata.POINT_DATA = []

    #收到停止获取template请求
    def req_stopgettemplate(self):
        self.print_recv_packet(self.client_address[0],"Stop Get Template",self.CMDCODE,self.DATA,"停止获取模板")

    #收到故障追踪请求
    def req_tracefault(self):
        # print "tracing fault"
        self.print_recv_packet(self.client_address[0],"Start Trace Fault",self.CMDCODE,self.DATA,"请求故障追踪")
        # 直接返回测试数据了 添加头和尾
        segment_header = binascii.a2b_hex('ffffeeee81000009')
        segment_trai = binascii.a2b_hex('eeeeffff')
        segment_center = self.ba.get_tracefault_bytearray()
        # 构造完整帧
        segment_data = segment_header + segment_center + segment_trai
        self.request.sendall(segment_data)
        pointdata.POINT_DATA = []



    #收到停止故障追踪请求
    def req_stoptrace(self):
        # print "stop strace fault"
        self.print_recv_packet(self.client_address[0],"Stop Trace Fault",self.CMDCODE,self.DATA,"停止故障追踪 ")

    #收到普查测试请求
    def req_ocrtest(self):
        # print "ocr test"
        self.print_recv_packet(self.client_address[0],"Start OCR Test",self.CMDCODE,self.DATA,"开始普查测试")

    #收到停止普查测试 返回测试结果给app客户端
    def req_stopocrtest(self):
        # print "stop ocr test"
        self.print_recv_packet(self.client_address[0],"Stop OCR Test",self.CMDCODE,self.DATA,"停止普查测试")
        segment_header = binascii.a2b_hex('ffffeeee8100000d')
        segment_trai = binascii.a2b_hex('eeeeffff')
        segment_center = self.ba.get_ocrtest_bytearray()
        # 构造完整帧
        segment_data = segment_header + segment_center + segment_trai
        self.request.sendall(segment_data)
        # print "send successful!"
        self.print_send_packet(self.client_address[0],"Send OCR Data", self.CMDCODE, segment_data, "发送普查测试数据")
        pointdata.POINT_DATA = []


    def print_start_con(self):
        print '*****************************************'
        print 'Connecting IP :' + self.client_address[0]
        print 'DATE :' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print '*****************************************'

    def print_recv_packet(self,str_srcip,str_action,str_cmdcode,str_data,other_desc):
        '''打印接受到的ip到控制台'''
        print '*****************************************'
        print 'SRC_IP :' + str_srcip
        print 'ACTION :' + str_action
        print 'CMD :' + str_cmdcode
        print 'REV_DATA :' + str_data
        print 'DESC :' + other_desc
        print '*****************************************'

    def print_send_packet(self,str_dstip,str_action,str_cmdcode,str_data,other_desc):
        '''打印接受到的ip到控制台'''
        print '*****************************************'
        print 'DST_IP :' + str_dstip
        print 'ACTION :' + str_action
        print 'CMD :' + str_cmdcode
        print 'SEND_DATA :' + str_data
        print 'DESC :' + other_desc
        print '*****************************************'

    def print_unvaild(self):
        print '*****************************************'
        print "is not a vaild packet"
        print '*****************************************'





if __name__ == '__main__':
    print '*****************************************'
    print 'server start'
    print '*****************************************'
    server = SocketServer.ThreadingTCPServer(addr, Servers)
    server.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.allow_reuse_address = True
    server.serve_forever()

