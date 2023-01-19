# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 19:02:02 2023

@author: ammar
"""
import math
import pandas as pd
import re
from ast import literal_eval
#------------------------------------------------------------------------------
#read json file: A reference file of SIC/XE instructions:

sicxe_inst = pd.read_json("inst.json")
print("\n","Set of SIC/XE instructions reference","\n")
print(sicxe_inst)
print('------------------------------------------------------------') 
  
     
# read txt file of instructions input:      


input_set = pd.read_csv("test.txt", sep=".", header=None, names=["atts"], skiprows=0 ,skipinitialspace =True)
input_set['REF'],input_set['OPCODE'],input_set['OPERAND'] = zip(*input_set['atts'].str.split())
del input_set['atts']

#print("\n","Set of input instructions imported from test.txt","\n")
#print(input_set)


#Merge sicxe_insts and input dataframes and add looctr col.-------------------------------



def createLocctr(inst_set,sicxe,firstloc=hex(0)):
    # Add column of + sign for format 4
    #trim + sign from opcode to be able to merge successfully 
    inst_set['signal'] = inst_set.apply(lambda row:int(bool(re.findall('[+]',row.OPCODE))), axis = 1)
    inst_set['OPCODE'] = inst_set['OPCODE'].str.replace('+','')
    
    
    
    #merge the two dataframes
    inst_set1= pd.merge(sicxe,inst_set,on='OPCODE', how='right', copy='True')
    inst_set1['LOCCTR'] = inst_set1.apply(lambda row: row.FORMAT, axis = 1)
    current_loc=firstloc
    inst_set1['LOCCTR'][0]=current_loc
    increment=0
    for i in range(len(inst_set1)):
       inst_set1['OPCODEVAL'][i]=str(inst_set1['OPCODEVAL'][i])
       inst_set1['OPERAND'][i]=str(inst_set1['OPERAND'][i])
       if inst_set1['OPCODEVAL'][i]!='nan' :
           inst_set1['OPCODEVAL'][i]=hex(int(inst_set1['OPCODEVAL'][i],16))
       
           
       if  inst_set1['FORMAT'][i] in ['1','2']:
           increment=int(inst_set1['FORMAT'][i])          
       elif  inst_set1['FORMAT'][i]=='3/4':
           increment=3
           if inst_set1['signal'][i]:
               increment=4
       elif inst_set1['FORMAT'][i]=='NaN':
           if inst_set1['OPCODE'][i]=='RESW':
               increment= 3* int(inst_set1['OPERAND'][i],10)           
           elif inst_set1['OPCODE'][i]=='RESB':
               increment=int(inst_set1['OPERAND'][i],10)
           elif inst_set1['OPCODE'][i]=='WORD':
               increment=3
           elif inst_set1['OPCODE'][i]=='BYTE' :
               increment=1
           elif inst_set1['OPCODE'][i]=='BASE':
               increment=0
    
       current_loc = hex(increment+int(current_loc,16))
       inst_set1['LOCCTR'][i+1]=int(current_loc,16)
    
    for n in ['P', 'X', 'F', 'C']:
        del inst_set1[n]
    for flag in ['n','i','x','p','b','e']:
        inst_set1[flag]=inst_set1.apply(lambda row: row.signal*0, axis = 1)
    inst_set1=inst_set1[['FORMAT','REF','OPCODE','OPCODEVAL','OPERAND','signal','n','i','x','p','b','e','LOCCTR']]
    return inst_set1

#.................................................................................

def get_symtab(inst_set):
    df=pd.DataFrame()
    df=inst_set[['REF','LOCCTR']]
    return df
    
      

          
print('\n*************************************** END OF SIC/XE ASSEMBLER PASS 1 ****************************************')
 #PASS 2........................................................................................
#addressing mode :

add_mode= pd.read_table('add_mode.txt',sep='.',skipinitialspace =True ,names=["addMode"],skiprows=0 )
add_mode['AddMode'],add_mode['FLAGS'],add_mode['Disc']=zip(*add_mode['addMode'].str.split(','))

del add_mode['addMode']
print(add_mode)
del add_mode['Disc']
name=''
for i in range(len(add_mode)):
    if add_mode['AddMode'][i]:
        name=add_mode['AddMode'][i]
    else:
        add_mode['AddMode'][i]=name
#.......................................................................................        
    
print('\n add mode table \n',add_mode)
print(add_mode['FLAGS'][1].split())

print('------------------------------------------------------------') 



print("\n","Set of input instructions modified","\n")
input_set1=createLocctr(input_set, sicxe_inst)
print(input_set1)

print('Get sym-table\n')
print(get_symtab(input_set1)) 