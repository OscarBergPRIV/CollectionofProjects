library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use ieee.NUMERIC_STD.all;
library work;
use work.package_types.all;

architecture behav of alu is
signal out_temp : std_logic_vector (N downto 0);
begin
   process(x,y,func_sel,shift_number)
   begin
    case(func_sel) is
     when ADD_N => 
      ALU_Result <= unsigned('0' & x)+unsigned('0' & y); 
     when SUB_n =>
      ALU_Result <= unsigned('0' & x)-unsigned('0' & y);
     when MUL_n => 
      ALU_Result <= std_logic_vector(to_unsigned((to_integer(unsigned('0' & x)) * to_integer(unsigned('0' & y))),N));
     when DIV_n => 
      ALU_Result <= std_logic_vector(to_unsigned(to_integer(unsigned('0' & x)) / to_integer(unsigned('0' & y)),N));
     when LSR_n => 
      ALU_Result <= '0' & (std_logic_vector(unsigned(x) srl shift_number));
     when LSR_n =>
       ALU_Result <= '0' & (std_logic_vector(unsigned(x) sll shift_number));
     when ASR_n => 
       ALU_Result => '0' & (std_logic_vector(signed(x) / (2**shift_number)));
     when AND_n =>
       ALU_Result <= '0' & (x and y);
     when NAND_n => 
       ALU_Result <= '0' & (x nand y);
     when NOT_n =>
       ALU_RESULT <= '0' & (not x)
     when NOR_n =>
       ALU_Result <= '0' & (x nor y);
     when XOR_n => 
       ALU_Result <= '0' & (x xor y);
     when XNOR_n => 
       ALU_Result <= '0' & (x xnor y);
     when OR_n => 
       ALU_Result <= '0' & (x or y);
     when ROTR_n =>
        ALU_Result <= '0' & (std_logic_vector(unsigned(x) ror shift_number));
     when ROTL_n => 
       ALU_Result => '0' & (std_logic_vector(unsigned(x) rol shift_number));
     when others => 
       ALU_Result <= '0' & x; 
    end case;
   end process;
 output <= out_temp(N-2 downto 0); 
 carry_out <= out_temp(N-1);
end behav;
