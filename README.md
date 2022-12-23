# How to run the program

## In executable mode


## From python file

for now use this method

### `python3 assembler.py read test2.txt`
### `python3 assembler.py read test3.txt`
### `python3 assembler.py read test4.txt`

### `python3 assembler.py generate test2.txt`
### `python3 assembler.py generate test3.txt`
### `python3 assembler.py generate test4.txt`

Run these commnds in the same folder the program was extracted

## Flow of the program

### Reading the input file

### Storing the lines in class global variable list

### Iterating and modifying the global list variable 

- To remove comments ( symbole initialized to # and can be changed)
- To remove commas
- To remove spaces
- To obtain and update line info: line number,start and end adress {"0":[start_addres,end_address]}
- To replace labels start address

### Determining the instruction type

#### MIPS Instruction types
- R= 6 segments
- I= 4 segments
- J=2 segments  

#### R
Processing the opcode   
Convert register addresses to hex  
Convert string to hex  
Convert data to hex  

#### J

Processing the opcode   
Convert register addresses to hex  
Convert string to hex  
Convert data to hex  

### Save compile output to
` output.txt`