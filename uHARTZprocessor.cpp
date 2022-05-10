/******************************************************************************

Author: Oscar A. B. Berg

Custom Processor
uHARTZ

16-Bit 2 Address Machine

MNC    OOOO   DISCRIPTION

RS     0000   DDDD = LSL/LSR/ROT/ASR XX:00/10/01/11 : IX : signed(number)
ADD    0001   DDDD = DDDD + AAAA for I=0; DDDD = DDDD + si(AAAA XXX) ONLY IF I=1
SUB    0010
AND    0011   DDDD = DDDD AND AAAA
NOT    0100   DDDD = NOT AAAA
LLI    1101   Load in DDDD = I AAAA XXX
LUI    1110   Load in DDDD = I AAAA XXX << 8
LD     0101   Load in DDDD = MEM[AAAA+si(XXX)] (AAAA as unsigned) for I=0; DDDD = MEM[us(AAAAXXX)]
ST     1111   Store DDDD in MEM[AAAA+si(XXX)] (AAAA as unsigned) for I=0; MEM[us(AAAAXXX)]
BRA    0110   PC = PC + si(DDDD AAAA XXX) I=0; for I=1 PC - ...
BEQ    0111   PC = PC + si(AAAA XXX) ONLY IF DDDD cc 0000
BNE    1000   
BGT    1001
BGE    1010
BLT    1011
BLE    1100

Format:
OOOO DDDD I AAAA XXX       --> I=1: AAAA XXXX => si7; I=0: OP2=AAAA; Destination Reg = DDDD {ADD,SUB,AND,NOT}
OOOO DDDD I AAAA XXX       --> LD/STM: MEM[AAAA+si(XXX)] = DDDD or MEM[si(AAAAXXX)] for I=1


linear Memory: 16-Bit Values

registers:

r0 - r14
r15 = PC


*******************************************************************************/

#include <iostream>
using namespace std;

class CPU {       
  public:             
    unsigned int registers[15]={0};      
    unsigned int PC=0;  
    unsigned int memory[1024]={0};
};

int main()
{
    cout<<"The HARTZ processor emulator by Oscar Berg\n";
    /// INIT CPU core
    CPU core;
    
    
    
    unsigned int opcode=0;
    unsigned int destination=0;
    unsigned int immCC;
    unsigned int opA;
    unsigned int offX;
    unsigned int ix;
    unsigned int code_word = 0;
    
    bool end_emulate = false;
    // READ CODE_WORD from binary file
    
    //code_word += 0b0001001010010001;  // 4753
    unsigned int ROM[5] = {
        0b1101000100000101,   // LLI r1 = #6
        0b1110000100000000,   // LUI 0 
        0b1101001000000110,
        0b1110001000000000,
        0b0010000100010000
    };
    while (!end_emulate) {
        code_word = ROM[core.PC];
        opcode = code_word << 16 >> 12+16;
        destination = code_word << 4+16 >> 12+16;
        immCC = code_word << 8+16 >> 15+16;
        opA = code_word << 9+16 >> 12+16;
        offX = code_word << 13+16 >> 13+16;
        switch(opcode) {
          case 0:
            ix = (offX >> 2) + (immCC << 1);
            if (offX << 30 >> 30 == 0) {
                //LSL
                core.registers[destination] = core.registers[opA] << ix+1;
            }else if (offX << 30 >> 30 == 2) {
                //LSR
                core.registers[destination] = core.registers[opA] >> ix+1;
            }else if (offX << 30 >> 30 == 1) {
                //ROT
                switch(ix){
                    case 0:
                    //ROT 1 left
                    if (core.registers[opA] >= 32768) {
                        core.registers[destination] = (core.registers[opA] << 1) + 1;
                    }else{
                        core.registers[destination] = (core.registers[opA] << 1);
                    }
                    break;
                    case 1:
                    //ROT 2 left
                    if (core.registers[opA] >= 32768) {
                        core.registers[destination] = (core.registers[opA] << 2) + 1;
                    }else{
                        core.registers[destination] = (core.registers[opA] << 2);
                    }
                    break;
                    case 2:
                    //ROT 1 right
                    if (core.registers[opA] % 2 == 1) {
                        core.registers[destination] = (core.registers[opA] >> 1) + (1<<15);
                    }else{
                        core.registers[destination] = (core.registers[opA] >> 1);
                    }
                    break;
                    case 3: 
                    //ROT 2 right
                    if (core.registers[opA] % 2 == 1) {
                        core.registers[destination] = (core.registers[opA] >> 2) + (1<<15);
                    }else{
                        core.registers[destination] = (core.registers[opA] >> 2);
                    }
                    break;
                }
            }else{
                //ASR
                core.registers[destination] = int(core.registers[opA]) >> 1;
            }
            break;
          case 1:
            //ADD
            if (immCC == 0) {
                core.registers[destination] += core.registers[opA];
            } else {
                core.registers[destination] += (opA << 3) + offX;
            }
            break;
          case 2:
            //SUB
            if (immCC == 0) {
                core.registers[destination] -= core.registers[opA];
            }else{
                core.registers[destination] -= (opA << 3) + offX;
            }
            break;
          case 3:
            //AND
            core.registers[destination] = core.registers[destination] & core.registers[opA];
            break;
          case 4:
            //NOT
            core.registers[destination] = ~core.registers[opA];
            break;
          case 5:
            //LD
            if (immCC == 0) {
                core.registers[destination] = core.memory[core.registers[opA] + offX];
            }else{
                core.registers[destination] = core.memory[opA << 3 + offX];
            }
            break;
          case 6:
            //BRA
            if (immCC == 0) {
                core.PC += (destination << 7) + (opA << 3) + offX;
            }else{
                core.PC -= (destination << 7) + (opA << 3) + offX;
            }
            break;
          case 7:
            //BEQ
            if (core.registers[destination] == 0) {
                if (immCC == 0) {
                    core.PC += (destination << 7) + (opA << 3) + offX;
                }else{
                    core.PC -= (destination << 7) + (opA << 3) + offX;
                }
            }
            break;
          case 8:
            //BNE
            if (core.registers[destination] != 0) {
                if (immCC == 0) {
                    core.PC += (destination << 7) + (opA << 3) + offX;
                }else{
                    core.PC -= (destination << 7) + (opA << 3) + offX;
                }
            }
            break;
          case 9:
            //BGT
            if (core.registers[destination] > 0) {
                if (immCC == 0) {
                    core.PC += (destination << 7) + (opA << 3) + offX;
                }else{
                    core.PC -= (destination << 7) + (opA << 3) + offX;
                }
            }
            break;
          case 10:
            //BGE
            if (core.registers[destination] >= 0) {
                if (immCC == 0) {
                    core.PC += (destination << 7) + (opA << 3) + offX;
                }else{
                    core.PC -= (destination << 7) + (opA << 3) + offX;
                }
            }
            break;
          case 11:
            //BLT
            if (core.registers[destination] < 0) {
                if (immCC == 0) {
                    core.PC += (destination << 7) + (opA << 3) + offX;
                }else{
                    core.PC -= (destination << 7) + (opA << 3) + offX;
                }
            }
            break;
          case 12:
            //BLE
            if (core.registers[destination] <= 0) {
                if (immCC == 0) {
                    core.PC += (destination << 7) + (opA << 3) + offX;
                }else{
                    core.PC -= (destination << 7) + (opA << 3) + offX;
                }
            }
            break;
          case 13:
            //LLI
            core.registers[destination] = (immCC << 7) + (opA << 3) + offX;
            break;
          case 14:
            //LUI
            core.registers[destination] += ((immCC << 7) + (opA << 3) + offX) << 8;
            break;
          case 15:
            //ST 
            if (immCC == 0) {
                core.memory[core.registers[opA]+offX] = core.registers[destination];
            }else{
                core.memory[opA<<3+offX] = core.registers[destination];
            }
            break;
          default:
            cout<<"ERROR: NO VALID CODE WORD!";
            end_emulate = true;
    }
    core.PC += 1;
        if (core.PC == (sizeof(ROM)/sizeof(*ROM))) {
            end_emulate = true;
        }
    }
    cout<<int(core.registers[1])<<"\n";    
    return 0;
}
