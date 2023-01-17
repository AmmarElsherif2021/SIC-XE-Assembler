# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 19:02:02 2023

@author: ammar
"""
import pandas as pd
import re
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

print("\n","Set of input instructions imported from test.txt","\n")
print(input_set)


#Merge sicxe_insts and input dataframes and add looctr col.-------------------------------



def createLocctr(inst_set,sicxe,firstloc=hex(0)):
    # Add column of + sign for format 4
    #trim + sign from opcode to be able to merge successfully 
    inst_set['+'] = inst_set.apply(lambda row:bool(re.findall('[+]',row.OPCODE)), axis = 1)
    inst_set['OPCODE'] = inst_set['OPCODE'].str.replace('+','')
    
    
    
    #merge the two dataframes
    inst_set1= pd.merge(sicxe,inst_set,on='OPCODE', how='right', copy='True')
    inst_set1['LOCCTR'] = inst_set1.apply(lambda row: row.FORMAT, axis = 1)
    current_loc=firstloc
    inst_set1['LOCCTR'][0]=current_loc
    increment=0
    for i in range(len(inst_set1)):
       
       if  inst_set1['FORMAT'][i] in ['1','2']:
           increment=int(inst_set1['FORMAT'][i])
           
       elif  inst_set1['FORMAT'][i]=='3/4':
           increment=3
           if inst_set1['+'][i]:
               increment+=1
       elif inst_set1['FORMAT'][i]=='NaN':
           if inst_set1['OPCODE'][i]=='RESW':
               increment=int(inst_set1['OPERAND'][i])*3
           elif inst_set1['OPCODE'][i]=='RESB':
               increment=int(inst_set1['OPERAND'][i])
           elif inst_set1['OPCODE'][i]=='WORD':
               increment=3
           elif inst_set1['OPCODE'][i]=='BYTE' | inst_set1['OPCODE'][i]=='BASE' :
               increment=1
           
               
       
       current_loc = hex(increment+int(current_loc,16))
       
       inst_set1['LOCCTR'][i+1]=int(current_loc,16)
           
    return inst_set1

print("\n","Set of input instructions modified","\n")
input_set1=createLocctr(input_set, sicxe_inst)
print(input_set1)


print('------------------------------------------------------------') 
               
""" 
#function to fill locctr
def fill_locctr(df,first_loc=hex(0)):
    
    #df2['locctr'][0]=first_loc
    current_loc=first_loc
    for i in range(len(df2)):
        if df2['FORMAT_x'][i]=='NaN':
            if df2['OPCODE'][i]=='WORD':
                current_loc=hex(int(current_loc,16)+3)
            elif df2['OPCODE'][i]=='BYTE':
                current_loc=hex(int(current_loc,16)+1)
            elif df2['OPCODE'][i]=='RESW':
                current_loc=hex(int(current_loc,16)+(3*int(df2['ref'][i])))
            elif df2['OPCODE'][i]=='RESB':
                current_loc=hex(int(current_loc,16)+int(df2['ref'][i]))
            
            
        if df2['FORMAT_x'][i] in ['1','2']:
            current_loc=hex(int(current_loc,16)+(int(df2['FORMAT_x'][i])))
        elif df2['FORMAT_x'][i]=='3/4' and df2['plus'][i]=='1':
            current_loc=hex(int(current_loc,16)+4)
        else:
            current_loc=hex(int(current_loc,16)+3)
        df2['locctr'][i]=current_loc
        
    return df2
   
print('\n')
print('filling location counter column--------------------------> \n',fill_locctr(inst_set,hex(0)))
#--------------------------------------------------------------
#fill symbols table:
def get_symtab(df):
    df2=fill_locctr(df,hex(0))
    return df2[['sym','locctr']]

print('\n')        
print('Filling the symbols table up ---------------------------->\n',get_symtab(inst_set))

print('\n*************************************** END OF SIC/XE ASSEMBLER PASS 1 ****************************************')
"""