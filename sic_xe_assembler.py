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



def createLocctr(inst_set,sicxe,firstloc=0):
    # Add column of + sign for format 4
    #trim + sign from opcode to be able to merge successfully 
    inst_set['signal'] = inst_set.apply(lambda row:int(bool(re.findall('[+]',row.OPCODE))), axis = 1)
    inst_set['OPCODE'] = inst_set['OPCODE'].str.replace('+','')
    
    
    
    #merge the two dataframes
    inst_set1= pd.merge(sicxe,inst_set,on='OPCODE', how='right', copy='True')
    
    #add LOCCTR col.
    inst_set1['LOCCTR'] = inst_set1.apply(lambda row: row.FORMAT, axis = 1)
    current_loc=firstloc
    inst_set1['LOCCTR'][0]=current_loc
    inst_set1=inst_set1.fillna(0)
 
    
    
    for i in range(len(inst_set1)):
    #assure type of data =string
       inst_set1['OPCODEVAL'][i]=str(inst_set1['OPCODEVAL'][i])
       inst_set1['OPERAND'][i]=str(inst_set1['OPERAND'][i])
       increment=0
       if inst_set1['OPCODEVAL'][i]!='nan' :
           inst_set1['OPCODEVAL'][i]=hex(int(inst_set1['OPCODEVAL'][i],16))
       
           
       if  inst_set1['FORMAT'][i] in ['1','2']:
           increment=int(inst_set1['FORMAT'][i])
           inst_set1['FORMAT'][i]=increment
           
       elif  inst_set1['FORMAT'][i]=='3/4':
           increment=3
           inst_set1['FORMAT'][i]=increment
           if inst_set1['signal'][i]:
               increment=4
               inst_set1['FORMAT'][i]=increment
       elif inst_set1['FORMAT'][i]==0:
           if inst_set1['OPCODE'][i]=='RESW':
               increment= 3* int(inst_set1['OPERAND'][i]) 
               
           elif inst_set1['OPCODE'][i]=='RESB':
               increment=int(inst_set1['OPERAND'][i])
               
           elif inst_set1['OPCODE'][i]=='WORD':
               increment=3
           elif inst_set1['OPCODE'][i]=='BYTE' :
               increment=1
           elif inst_set1['OPCODE'][i]=='BASE':
               increment=0
    
       current_loc = increment+current_loc
       

           
       inst_set1['LOCCTR'][i+1]=current_loc
    #OPTIONAL FOR THE CASE OF FILE IMPORTED ONLY !!!
    for n in ['P', 'X', 'F', 'C']:
        del inst_set1[n]
    
    #Adding nixpbe flags and '+' signal column
    for flag in ['n','i','x','p','b','e']:
        inst_set1[flag]=inst_set1.apply(lambda row: row.signal*0, axis = 1)
    inst_set1=inst_set1[['FORMAT','REF','OPCODE','OPCODEVAL','OPERAND','signal','n','i','x','p','b','e','LOCCTR']]
    
    #binary representation:
    #{0:08b}'.format(6)
           
    
    return inst_set1

#.................................................................................

def get_symtab(inst_set):
    df=pd.DataFrame()
    df=inst_set[['REF','LOCCTR']]
    return df
    
      

          
print('\n*************************************** END OF SIC/XE ASSEMBLER PASS 1 ****************************************')
 #PASS 2........................................................................................
#Adding addressing mode :

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
#Filling n,i,x,p,b,e,disp1,disp2,address columns
def fill_address(inst_set):
    #for format 1,2 
    inst_set['R1']=inst_set.apply(lambda row: row.e*0, axis = 1)
    inst_set['R2']=inst_set.apply(lambda row: row.e*0, axis = 1)
    inst_set['ADD']=inst_set.apply(lambda row: row.e*0, axis = 1)
    
    #call symtab:
    symtab=get_symtab(inst_set)
    #handle format 3 and 4:
    operand_switcher={
        '@':'n',
        '#':'i',
        'X':'x',
        }
    
    #referances-table 
    Ref=get_symtab(inst_set)
    
    #iterate on inst_set and fill '+' col, nixpbe cols, and disp/ADD cols 
    for i in range(len(inst_set)):
       
        #is + found ? then e=1
        if inst_set['signal'][i]:
            inst_set['e'][i]=1
       
        #adjust nixpbe for flags
        for sign in operand_switcher:
            s=operand_switcher[sign]
            if inst_set['FORMAT'][i] in [3,4]:
           
                #handle n,i,x
                if re.search(sign,str(inst_set['OPERAND'][i])):
                    inst_set[s][i]=1
                    inst_set['OPERAND'][i]=inst_set['OPERAND'][i].replace(sign,'').replace(',','')
            
            #handle p,b ???  
            #fill address for formats 3/4:
        
        
                    
                    
                
 
        #handle simple mode
        if inst_set['n'][i]==0 and inst_set['i'][i]==0 and inst_set['FORMAT'][i] in [3,4]:
            inst_set['n'][i]=1
            inst_set['i'][i]=1
        
            
            
        # handle format 2 and 1  and fill displacement columns:
        if inst_set['FORMAT'][i]==2:
            
            for operand in inst_set['OPERAND'].split(','):
                format_row=inst_set.loc(inst_set['REF']==operand)
                inst_set['R1']=format_row[0]
                if format_row[1]:
                    inst_set['R2']=format_row[1]
        
        #fill adds for formmats 3 and 4
        elif inst_set['FORMAT'][i] in [3,4]:
            operand=str(inst_set['OPERAND'][i])
            if operand in ['null']:
                operand=0
                inst_set['ADD'][i]=0
            elif operand.isdigit() :
                inst_set['ADD'][i]=int(str(operand))
            else:
                for j in range(len(symtab['REF'])):
                    if symtab['REF'][j] == operand:
                        inst_set['ADD'][i]=symtab['LOCCTR'][j]
    
    #handle p,b flags for formats 3 and 4
    
    inst_set['p']=inst_set.apply(lambda row: int(row.ADD<2047 and row.ADD>-2048 and row.FORMAT==3), axis = 1)
    inst_set['b']=inst_set.apply(lambda row: int(row.ADD<4095 and row.ADD>0 and row.FORMAT==3 and row.p==0), axis = 1)
   
    
    return inst_set

#.............................................................................................
def setToBinary(inst_set):
    inst_set['OPCODEVAL']=inst_set.apply(lambda row: int(row.OPCODEVAL,16), axis = 1)
    inst_set['OPCODEVAL']=inst_set.apply(lambda row: format(row.OPCODEVAL,'08b') if row.FORMAT in [1,2] else format(row.OPCODEVAL,'06b'), axis = 1)
    inst_set['ADD']=inst_set.apply(lambda row:format(row.ADD,'020b') if row.FORMAT==4 else format(row.ADD,'012b'), axis = 1)
    inst_set['R1']=inst_set.apply(lambda row: format(row.R1,'04b'), axis = 1)
    inst_set['R2']=inst_set.apply(lambda row: format(row.R2,'04b'), axis = 1)
    #inst_set['OPCODEVAL']=inst_set.to_numeric(inst_set['OPCODEVAL'])
    return inst_set
    
#.......................................................................................   
print('\n add mode table \n',add_mode)
print(add_mode['FLAGS'][1].split())

print('--------------------------------------------------------------------------------------') 



print("\n","Set of input instructions modified","\n")
input_set1=createLocctr(input_set, sicxe_inst)
input_set2=fill_address(input_set1)
print(fill_address(input_set1))

print('Get sym-table\n')
symtab=get_symtab(input_set1)
print(symtab)
print('to numeric data-------------------------------------------') 
print(setToBinary(input_set2))
#data['column'].apply(lambda element: format(int(element), 'b'))