library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use ieee.NUMERIC_STD.all;
library work;
use work.package_types.all;

---------------------------
------- 16 Bit ALU --------
---------------------------

entity alu is
  generic ( 
     constant N: positive := 16  -- bit width / default: 16 bit operand
    );
  
  Port (
    x, y     : in  STD_LOGIC_VECTOR(N downto 0);     -- Operands
    func_sel  : in  function_select;                  -- selects numerical (ADD, SUB, MUL ...) or logical (AND, NAND, ...) Operation Mode | Defined in Package
    shift_number: in natural;
    output   : out  STD_LOGIC_VECTOR(N downto 0);    -- Output
    carry_out : out std_logic      
    );
end alu; 
