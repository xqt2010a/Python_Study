import struct, JLink
#import numpy as np

class RttBuf(object):
    def __init__(self, arr):
        self.sName,  self.pBuffer,  self.SizeOfBuffer,  self.WrOff,  self.RdOff,  self.Flags = arr

class RttCB(object):
    def __init__(self, buf, upport, downport):
        self.acID, self.MaxNumUpBuf,  self.MaxNumDownBuf  = struct.unpack("16sii", buf.raw[:24])
        print("len:", len(buf.raw[24:(48+0*24)]))
        for i in range(0, self.MaxNumUpBuf):
            if (i == upport):
                self.aUp = RttBuf(struct.unpack("6L", buf.raw[(24+24*i):(48+24*i)]))
        
        aDown_start = 48+i*24
        for i in range(0, self.MaxNumDownBuf):
            if(i == downport):
                self.aDown = RttBuf(struct.unpack("6L", buf.raw[(aDown_start + 24*i): (aDown_start+24+24*i)]))
            
        
class RTT(object):
    "RTT api"
    def __init__(self, dllpath):
        self.jlink = JLink(dllpath)
        print("hello")
        
    def upBuffEmpty(self, rtt_addr, len, upport, downport):
        buf = self.jlink.read_mem(rtt_addr, len)
        self.rtt_cb = RttCB(buf, upport, downport)
        return self.rtt_cb.aUp.RdOff == self.rtt_cb.aUp.WrOff
        
    def upBuffRead(self, rtt_addr, upport,  downport):
        if self.rtt_cb.aUp.RdOff < self.rtt_cb.aUp.WrOff:
            len = self.rtt_cb.aUp.WrOff - self.rtt_cb.aUp.RdOff
            buf = self.jlink.read_mem(self.rtt_cb.aUp.pBuffer+self.rtt_cb.aUp.RdOff,  len)
            self.rtt_cb.aUp.RdOff += len
            #str = ctypes.create_string_buffer(struct.pack("L", self.rtt_cb.aUp.RdOff))
            #self.jlink.JLINKARM_WriteMem(rtt_addr+24+upport*24+16, 4, str)
            self.jlink.write(rtt_addr+24+upport*24+16, self.rtt_cb.aUp.RdOff)
        else:
            len = self.rtt_cb.aUp.SizeOfBuffer - self.rtt_cb.aUp.RdOff +1
            buf = self.jlink.read_mem(self.rtt_cb.aUp.pBuffer+self.rtt_cb.aUp.RdOff, len)
            self.rtt_cb.aUp.RdOff = 0
            #str = ctypes.create_string_buffer(struct.pack("L", self.rtt_cb.aUp.RdOff))
            #self.jlink.JLINKARM_WriteMem(rtt_addr+24+upport*24+16, 4, str)
            self.jlink.write_mem(rtt_addr+24+upport*24+16, self.rtt_cb.aUp.RdOff)
        return buf.raw.decode("utf_8")   
