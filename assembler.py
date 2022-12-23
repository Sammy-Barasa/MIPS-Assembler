#!/usr/bin/env python3
# from cProfile import label
# import opcode

import sys
import os
import re
from pathlib import Path

class CompileAssembly():

    BASE_DIR = ""
    all_lines=[]
    all_lines_info={}
    labels={}
    preprocessor_cmd={}
    comment_char=""
    start_memory_location=0
    registers = {'$zero':0,'$at':1,'$v0':2,'$v1':3,'$a0':4,'$a1':5,'$a2':6,'$a3':7,
                '$t0':8,'$t1':9,'$t2':10,'$t3':11,'$t4':12,'$t5':13,'$t6':14,'$t7':15,
                '$s0':16,'$s1':17,'$s2':18,'$s3':19,'$s4':20,'$s5':21,'$s6':22,'$s7':23,
                '$t8':24,'$t9':25,'$k0':26,'$k1':27,'$gp':28,'$sp':29,'$fp':30,'$ra':31}
    last_offset = None
    file_name =""
    offset_list = {}
    opcode_table = {
	'add'   : ['0x20','rs','rt','rd','shamt','0x20'],
	'addi'  : ['0x08','rs','rt','imm'],
	'addiu' : ['0x09','rs','rt','imm'],
	'addu'  : ['0x21','rs','rt','rd','shamt','0x21'],
	'and'   : ['0x24','rs','rt','rd','shamt','0x24'],
	'andi'  : ['0x0C','rs','rt','imm'],
	'beq'   : ['0x04','rs','rt','imm'],
	'bne'   : ['0x05','rs','rt','imm'],
	'jr'    : ['0x08','rs','rt','rd','shamt','0x08'],
	'lbu'   : ['0x24','rs','rt','imm'],
	'lhu'   : ['0x25','rs','rt','imm'],
	'll'    : ['0x30','rs','rt','imm'],
	'lui'   : ['0x0F','rs','rt','imm'],
	'lw'    : ['0x23','rs','rt','imm'],
	'nor'   : ['0x27','rs','rt','rd','shamt','0x27'],
	'or'    : ['0x25','rs','rt','rd','shamt','0x25'],
	'ori'   : ['0x0D','rs','rt','imm'],
	'slt'   : ['0x2A','rs','rt','rd','shamt','0x2A'],
	'slti'  : ['0x0A','rs','rt','imm'],
    'sltiu' : ['0x0B','rs','rt','imm'],
	'sltu'  : ['0x2B','rs','rt','rd','shamt','0x2B'],
    'sll'  : ['0x00','rs','rt','rd','shamt','0x00'],
	'sb'    : ['0x28','rs','rt','imm'],
	'sc'    : ['0x38','rs','rt','imm'],
	'sh'    : ['0x29','rs','rt','imm'],
    'sw'    : ['0x2B','rs','rt','imm'],
	'sub'   : ['0x22','rs','rt','rd','shamt','0x22'],
	'subu'  : ['0x23','rs','rt','rd','shamt','0x23'],
    'div'   : ['0x1A','rs','rt','rd','shamt','0x1A'],
	'divu'  : ['0x1B','rs','rt','rd','shamt','0x1B'],
    'mfhi'  : ['0x10','rs','rt','rd','shamt','0x10'],
	'mflo'  : ['0x12','rs','rt','rd','shamt','0x12'],

	}

    def __init__(self,comment_char,base_dir):
        self.comment_char = comment_char
        self.BASE_DIR = base_dir

    


    def readLines(self,file):
        # read file input
        full_path = os.path.join(self.BASE_DIR,file)
        self.file_name=file.split(".")[0]
        
        try:
            with open(full_path) as f:
            # read lines and store all_lines[]
                self.all_lines=f.readlines()
        except:
            raise
    def convert(self,lines):
        # first run: get labels and line numbers store in dictionary, labels{}

        # get preprocessor directives
        for i in range(0,len(lines)):
            line = lines[i].find(".")
            if (line != -1):
                self.preprocessor_cmd[lines[i].strip()]=i
                # lines.remove(lines[i])

        # get labels
        for i in range(0,len(lines)):
            line = lines[i].find(":")
            if (line != -1):
                sp = lines[i].split(":")
                label_part = sp[0].strip() # label
                x = sp[1] # rest of insructions
                self.labels[label_part]=i 
                if len(x)!= 0:
                   # maintain rest of instructions remain
                   lines[i] = x.strip()  
                else:
                   # no rest of instructions  
                   lines[i] = label_part
                    
        # second run: string to hex, comments, commas, remove spaces,  

        # replace string values with hex 
        self.process_string(lines)

        # removing comments
        for i in range(0,len(lines)):
            lines[i].strip()
            line = lines[i].find(self.comment_char)
            if (line != -1):
                line_splt=lines[i].split(self.comment_char)
                lines[i]=line_splt[0] # maintain part before comment character

        # remove commas
        for i in range(0,len(lines)):
            line = lines[i].find(",")
            if (line != -1):
                lines[i]=lines[i].replace(","," ")
                
        # remove spaces
        for i in range(0,len(lines)):
            lines[i]=lines[i].split()
        # update line info: {"0":[start_addres,end_address]}
        start_addr = self.start_memory_location
        end_addr = 0
        for i in range(len(lines)):
            end_addr = start_addr+31
            info = {"start":hex(start_addr), "end":hex(end_addr)}
            self.all_lines_info[str(i)]= info
            start_addr=end_addr+1
            
        # replace labels start address
        for value,key in enumerate(self.labels):
            print(self.all_lines_info[str(value)]["start"])
            self.labels[key]=self.all_lines_info[str(value)]["start"]
            
            
        # third run: change instructions to hex, everything to 4 bytes
        for i in range(0,len(lines)):
            
            opcode = ""
            rs = ""
            rt = ""
            rd =""
            immediate = ""
            address =""
            # ignore preprocessor_cmd and labels
            lines_to_ignnore = list(self.preprocessor_cmd.values())
            # lines_to_ignnore =  [x for x in lines_to_ignnore]
            # print("lines_to_ignnore",lines_to_ignnore)
            
            if i in lines_to_ignnore :
                continue
            # only 3 ways to write instructions in MIPS, R= 6 segments, I= 4 segments, J=2 segments  
            segment_len = len(lines[i])
            valid_seg_len = [2,3,4,6]
            
            if (segment_len not in valid_seg_len):
                self.printLines(lines)
                
                # raise SyntaxError(f"UnrecognizedInstructionFormat at line {i+1}")
                print((f"InstructionFormatError: Unrecognized instruction format at line {i+1}"))
                print(f"line {i+1}: {lines[i][:]} <--")
                sys.exit()
                
            elif segment_len == valid_seg_len[0]:
                # J
                # print("J")
                # change opcode instructions to hex from opcode table

                # change registers to hex from register table
                # change opcode instructions to hex from opcode table
                # change last byte to MSB and LSB hex
                opcode = lines[i][0]
                lines[i][0] = self.process_opcode(opcode,i=i)
                addrs=lines[i][1]
                address = self.return_address_processed(i,1,addrs)
                
            elif ( valid_seg_len[0]< segment_len <= valid_seg_len[2]):
                # I: opcode, rs, rt, immediate
                # print("I")
                                
                immediate = ''
                #
                rs=lines[i][1]
                rs = self.return_rs_processed(i,1,rs)
                            
                if(segment_len==3):
                   
                   #  check for offset from of set list
                   #  fill in immediate with offset
                   #  or with nothing

                   rt_res =""
                   rt=lines[i][2]
                   rt_res = self.return_rt_processed(i,2,rt)
                                     
                   if(str(i) in self.offset_list.keys() and self.offset_list[str(i)]["position"]==2):
                        
                        last_rt = lines[i]
                        last_rt.append((self.offset_list[str(i)]["value"])) # append to the end  
                   else:
                    #    no segment
                        rt_res = self.return_rt_processed(i,2,rt)
                   rt = rt_res
                   lines[i][2]=rt
                   
                   immediate = lines[i][2]
                   
                   opcode = lines[i][0]
                   lines[i][0] = self.process_opcode(opcode,rs=rs,rt=rt,i=i)                                       
                else: 
                    # len is 4 
                    
                    rt=lines[i][2]
                    rt = self.return_rt_processed(i,2,rt)
                    imm = lines[i][3]
                    
                    # print("Imm begining: ",imm)
                    # print(f"{i+1},{3}- {lines[i][0]}")
                    # print("imm: ",self.return_immediate_processed(i,3,imm))
                    immediate = self.return_immediate_processed(i,3,imm)

                # change instruction to hex from register table
                opcode = lines[i][0]
                lines[i][0] = self.process_opcode(opcode,immediate=immediate,i=i,rt=rt,rs=rs)
                
            elif (valid_seg_len[2] < segment_len <= valid_seg_len[3]):
                # R
                # print("R")
                # change opcode instructions to hex from opcode table

                # change registers to hex from register table

                # change last byte to MSB and LSB hex
                
                rs=lines[i][2]
                rs = self.return_rs_processed(i,1,rs)
                rt=lines[i][3]
                rt = self.return_rt_processed(i,2,rt)
                rd = lines[i][1]
                rd = self.return_rd_processed(i,3,rd)
                shamt = hex(0)
                # shamt = self.return_shamt_processed(i,4,shamt)
                funct = lines[i][0]
                funct = self.return_shamt_processed(i,5,funct)

                opcode = 0
                res = self.process_opcode(funct,rd=rd,rs=rs,rt=rt,i=i)
                lines[i][0]
                
                # block_1 = self.hex2bin(opcode,6)
                # block_2 = self.hex2bin(rs,5)
                # block_3 = self.hex2bin(rt,5)
                # block_4 = self.hex2bin(rd,5)
                # block_5 = self.hex2bin(shamt,5)
                # block_6 = self.hex2bin(funct,5)
                # R= [block_1, block_2,block_3,block_4,block_5,block_6]
                # binary_result = block_1+block_2+block_3+block_4+block_5+block_6
            
    def process_string(self,lines):
        for i in range(0,len(lines)):
            line = lines[i].find('"') or lines[i].find("'") # double qute string priority, single string prioty : change order for preference
            if(line != -1):
                    my_string_list = re.findall(r'"([^"]*)"', lines[i]) or re.findall(r"'([^']*)'", lines[i])
                    
                    for j in range(0,len(my_string_list)):
                            replace_with = ""
                            my_string= my_string_list[j]
                            for k in range(0,len(my_string)):
                                replace_with= replace_with +" "+ str(hex(ord(my_string[k])))[2:]
                            lines[i] = replace_with
                            return replace_with
    
    def process_string_segment(self,i,j,seg):
             
        replace_with = ""
        if(len(seg) == 1):
            replace_with = hex(ord(seg)) 
        else:   
            for j in range(0,len(seg)+1):
                    
                    replace_with += hex(ord(seg[j]))
        self.all_lines[i][j] = replace_with           
        return replace_with
        
                                            
    def process_segment(self,i,j,seg):
        #  segment: lines[i][1]
        # can either be register, data, string, or label, check for offset
        # 10($v0)/($v0)/($6)/ $v0 $6, 4, 'n','loop'
         
        offset = self.last_offset
        rs_v = seg.find("(")
        if(rs_v != -1):
            # with brackets
            # 10($v0)/($v0)/($6)
            rs_result_bracket=""

            if(seg[rs_v-1]!=')'):
                # yes offset
                offset = hex(int(seg[:rs_v]))
                # print(f"offset at line {i+1} segment {j+1}:{offset}")
                self.last_offset=offset
                
                self.offset_list[str(i)]={"position":j,"value":offset}
                
                seg = seg[rs_v+1:seg.find(")")]
                # print("New segment after offset is:",seg)
                
                try:
                    # ($v0)
                    rs_result_bracket = hex(self.registers[seg])
                except:
                    # ($6)
                    rs_result_bracket = hex(int(seg[1:]))
                seg = rs_result_bracket
                # print("New segment stored after offset is:",seg)
                self.all_lines[i][j]=seg
                # print(self.all_lines[i])
                return seg
            else:
                # no offset
                self.last_offset=None
                try:
                    # ($v0)
                    res = re.search('\((.*)\)', seg).groups()[0]
                    rs_result_bracket = hex(self.registers[res])
                    
                except:
                    # ($2)
                    seg = re.search('\((.*)\)', seg).groups()[0]
                    rs_result_bracket = hex(int(seg[rs_v+1:]))
                seg = rs_result_bracket
                self.all_lines[i][j]=seg
                return seg   
            
        
        elif(seg.find("$")!=-1):
            # no () brackets
            #  $v0 $6
            rs_no_bracket_result =""
            try:
               
                # $v0 or $2
                if(int(seg[seg.find("$")+1:])):
                    # $2
                    rs_v = seg.find("$")
                    rs_no_bracket_result += hex(int(seg[rs_v+1:]))
                                   
                seg = rs_no_bracket_result
                
                self.all_lines[i][j]=seg
                # print(f"$v0 $0 {i} no barcket seg: {seg} ")
            except:
                # $v0
                
                rs_no_bracket_result += hex(self.registers[seg])
                seg = rs_no_bracket_result
                self.all_lines[i][j]=seg
                
            return seg
        
        elif(seg in self.labels.keys()):
            # print("This is a label:", seg)
            self.all_lines[i][j]=self.labels[seg]
            
        else:
            # this is data
            # in int but string format, string in string format
            
            try:
                # int but string format
                self.all_lines[i][j]=hex(int(seg))
            except:
                self.process_string_segment(i,j,seg)
                            
            
    def process_opcode(self, instruction,immediate=None,rd=None,rt=None,rs=None,i=None):

        if(instruction in self.opcode_table.keys()):
            
            result = self.opcode_table[instruction][0].lower()
            return result
        
        if(instruction == 'beq'):
            ((int(rs) - int(self.all_lines[i][2]) + 4)/4)
            return ((int(rs) + int(self.all_lines[i][2]) + 4)/4)
        
        if(instruction == 'li' and immediate!=None):
            return self.all_lines[i][1]
        
        if(instruction == 'move'):
            # will add to destination register
            return '0x20'
        
        if(instruction == 'clear'):
            return '0x20'
        
        if(instruction == 'j'):
            return self.all_lines_info[str(i)]["end"]
        
        if(instruction == 'bge' and rs!=None and rt!=None):
            print("from opcode ", self.all_lines[i][2])
            if(int(rs,16))>=int(rt,16):
                
                return self.all_lines_info[str(i)]["end"]
            return self.all_lines_info[str(i+1)]["start"]
        
        if(instruction == 'ble'and rs!=None and rt!=None):
            if(int(rs,16)<=int(rt,16)):
               
                return self.all_lines_info[str(i+1)]["start"]
            return self.all_lines_info[str(i)]["end"]
        
        if(instruction == 'blt' and rs!=None and rt!=None):
            if(int(rs,16)<int(rt,16)):
               
                return self.all_lines_info[str(i)]["end"]
            return self.all_lines_info[str(i+1)]["start"]
        
        if(instruction == 'bgt' and rs!=None and rt!=None):
            if(int(rs,16)>int(rt,16)):
                
                return self.all_lines_info[str(i)]["end"]
            return self.all_lines_info[str(i+1)]["start"]
        
        if(instruction == 'jal'):
            return hex(3)
            
        else:
            # print("Throwing and error")
            return instruction
            
    def return_rs_processed(self,i,j,seg):
        return self.process_segment(i,j,seg)
    
    def return_rt_processed(self,i,j,seg):
        return self.process_segment(i,j,seg)
    
    def return_immediate_processed(self,i,j,seg):
        return self.process_segment(i,j,seg)
    
    def return_rd_processed(self,i,j,seg):
        return self.process_segment(i,j,seg)  
    
    def hex2bin(self, hex_val, num_bits):
        
        twos_complement = False
        if '-' in hex_val:
            twos_complement = True
            hex_val = hex_val.replace('-', '')

        bit_string = '0' * num_bits
        bin_val    = str(bin(int(hex_val, 16)))[2:]
        bit_string = bit_string[0: num_bits - len(bin_val)] + bin_val + bit_string[num_bits:]

        # Two's complement if negative hex value
        if twos_complement:
            tsubstring = bit_string[0:bit_string.rfind('1')]
            rsubstring = bit_string[bit_string.rfind('1'):]
            tsubstring = tsubstring.replace('1', 'X')
            tsubstring = tsubstring.replace('0', '1')
            tsubstring = tsubstring.replace('X', '0')
            bit_string = tsubstring + rsubstring

        return  
    
    def return_funct_processed(self,i,j,seg):
        return self.process_segment(i,j,seg)  
    
    def return_address_processed(self,i,j,seg):
        return self.process_segment(i,j,seg)  

    def printLines(self,lines):
        for i in range(0,len(lines)):
            print(f"{i+1}:{lines[i]}")
        
        for i in range(0,len(lines)):   
            start_val = self.all_lines_info[str(i)]["start"]
            line_val = f"{start_val}: "
            for j in range(0,len(lines[i])):
                seg = lines[i][j]
                line_val = line_val + f" {seg}"
                
            self.all_lines[i] = line_val
            
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.writelines(f"{l}\n" for l in lines)    
            
        print("ASM FILE INFORMATION")
        
        print("Labels: ")
        print(self.labels)
        print("")
        print("Pre_processor commands: ")
        print(self.preprocessor_cmd)
        print("")
        print("Offsetlist:" )
        print(self.offset_list)
        print("")
        print("Line info: " )
        print(self.all_lines_info)
        print("")     
      
    def startProgram(self):
        cmd = sys.argv
        if len(cmd) < 2:
            print("use commands:")
            print("[assemble filename.s]")
            print("[assemble read filename.s]")
            print("[assemble generate filename.obj]")
            print(cmd)
        
        elif cmd[1]== "read":
            # read *.s file
            
            self.readLines(cmd[2])
            self.convert(self.all_lines)
            self.printLines(self.all_lines)
        elif cmd[1]== "generate":
            # compile *.s file
            self.readLines(cmd[2])
            self.convert(self.all_lines)
            self.printLines(self.all_lines)

        else:
            print("[assemble filename.s]")
            print("[assemble read filename.s]")
            print("[assemble generate filename.txt]")
            sys.exit()


if __name__ == "__main__":
    
    base_dir = Path().resolve()
    compile_assembly = CompileAssembly("#",base_dir)
    compile_assembly.startProgram()
    
    