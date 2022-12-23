
import re
import sys
with open("test3.txt") as f:
     lines=f.readlines()
labels ={}
preprocessor_cmd ={}
comment = "#"
registers = {'$zero':0,'$at':1,'$v0':2,'$v1':3,'$a0':4,'$a1':5,'$a2':6,'$a3':7,
                '$t0':8,'$t1':9,'$t2':10,'$t3':11,'$t4':12,'$t5':13,'$t6':14,'$t7':15,
                '$s0':16,'$s1':17,'$s2':18,'$s3':19,'$s4':20,'$s5':21,'$s6':22,'$s7':23,
                '$t8':24,'$t9':25,'$k0':26,'$k1':27,'$gp':28,'$sp':29,'$fp':30,'$ra':31}

def return_rs_processed(rs):
        #  segment: lines[i][1]
        offset = 0
        rs_v = rs.find("(")
        if(rs_v != -1 and rs_v!=0):
            # 10($v0)
            offset = hex(int(rs[0:rs_v]))
            rs_result_bracket=""
            if (offset):
                rs = rs[rs_v:]
                # ($v0)
                res = re.search('\((.*)\)', rs).groups()[0]
                rs_result_bracket = hex(registers[res])
            else:
                # no offset
                
                try:
                    # ($v0)
                    res = re.search('\((.*)\)', rs).groups()[0]
                    rs_result_bracket = hex(registers[res])
                except:
                    # ($2)
                    rs_v = re.search('\((.*)\)', rs).groups()[0].find("$")
                    # print(rs)
                    rs_result_bracket = hex(int(rs[rs_v+1:]))
            rs = rs_result_bracket
            lines[i][1]=rs
        else:
            # no () brackets
            rs_result =""
            try:
                
                # $2
                rs_v = rs.find("$")
                print("116",rs)
                rs_result = hex(int(rs[rs_v+1:]))
                print("118",rs)
            except:
                # $v0
                print("120",rs)
                res =rs
                rs_result = hex(int(registers[res]))

            rs = rs_result
            lines[i][1]=rs
            return rs

# get preprocessor directives
for i in range(0,len(lines)):
    line = lines[i].find(".")
    if (line != -1):
        preprocessor_cmd[lines[i]]=i+1

# get labels
for i in range(0,len(lines)):
    line = lines[i].find(":")
    if (line != -1):
        labels[lines[i][0:line]]=i+1

# second run: string to hex, comments, commas, remove spaces,  

# replace string values with hex 
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

# removing comments
for i in range(0,len(lines)):
    lines[i].strip()
    line = lines[i].find(comment)
    if (line != -1):
        line_splt=lines[i].split(comment)
        lines[i]=line_splt[0] # maintain part before comment character

# remove commas
for i in range(0,len(lines)):
    line = lines[i].find(",")
    if (line != -1):
        lines[i]=lines[i].replace(","," ")
# remove spaces
for i in range(0,len(lines)):
    lines[i]=lines[i].split()
print(labels)
print(preprocessor_cmd)
for i in range(0,len(lines)):
    print(f"{i+1}:{lines[i]}")
# third run: change instructions to hex, everything to 4 bytes
for i in range(0,len(lines)):
    # ignore preprocessor_cmd and labels
    lines_to_ignnore = list(preprocessor_cmd.values()) + list(labels.values())
    lines_to_ignnore =  [x-1 for x in lines_to_ignnore]
    
    if i in lines_to_ignnore :
        continue
    # only 3 ways to write instructions in MIPS, R= 6 segments, I= 4 segments, J=2 segments  
    segments = len(lines[i])
    valid_seg_len = [2,3,4,6]
    if (segments not in valid_seg_len):

        # raise SyntaxError(f"UnrecognizedInstructionFormat at line {i+1}")
        print((f"InstructionFormatError: Unrecognized instruction format at line {i+1}"))
        print(f"line {i+1}: {lines[i][:]} <--")
        sys.exit()
    elif segments == valid_seg_len[0]:
        # J
        # print("J")
        # change opcode instructions to hex from opcode table

        # change registers to hex from register table

        # change last byte to MSB and LSB hex
        pass
    elif (valid_seg_len[0]< segments <=valid_seg_len[2]):
        # I: opcode, rs, rt, immediate
        # print("I")
        opcode = ""
        rs = ""
        rt = ""
        immediate = ""
        # change opcode instructions to hex from opcode table
        opcode = lines[i][0]
        # change registers to hex from register table
        rs=lines[i][1]
        # offset = 0
        # rs_v = rs.find("(")
        # if(rs_v != -1 and rs_v!=0):
        #     # 10($v0)
        #     offset = hex(int(rs[0:rs_v]))
        #     rs_result_bracket=""
        #     if (offset):
        #         rs = rs[rs_v:]
        #         # ($v0)
        #         res = re.search('\((.*)\)', rs).groups()[0]
        #         rs_result_bracket = hex(registers[res])
        #     else:
        #         # no offset
                
        #         try:
        #             # ($v0)
        #             res = re.search('\((.*)\)', rs).groups()[0]
        #             rs_result_bracket = hex(registers[res])
        #         except:
        #             # ($2)
        #             rs_v = re.search('\((.*)\)', rs).groups()[0].find("$")
        #             # print(rs)
        #             rs_result_bracket = hex(int(rs[rs_v+1:]))
        #     rs = rs_result_bracket
        #     lines[i][1]=rs
        # else:
        #     # no () brackets
        #     rs_result =""
        #     try:
                
        #         # $2
        #         rs_v = rs.find("$")
        #         print("116",rs)
        #         rs_result = hex(int(rs[rs_v+1:]))
        #         print("118",rs)
        #     except:
        #         # $v0
        #         print("120",rs)
        #         res =rs
        #         rs_result = hex(int(registers[res]))

        #     rs = rs_result
        #     lines[i][1]=rs
        rs = return_rs_processed(rs)
        if(segments==3):
            # print("last_byte_to_16_bits -0") 
            pass

            # change last byte to MSB and LSB hex
        # print("last_byte_to_16_bits_values")
        # is 4
        pass
    elif (valid_seg_len[2] < segments <= valid_seg_len[3]):
        # R
        # print("R")
        # change opcode instructions to hex from opcode table

        # change registers to hex from register table

        # change last byte to MSB and LSB hex
        pass
for i in range(0,len(lines)):
    print(lines[i])