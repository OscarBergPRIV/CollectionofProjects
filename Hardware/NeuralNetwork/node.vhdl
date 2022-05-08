library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use ieee.NUMERIC_STD.all;
library work;
use work.package_types.all;
------------------------------------------------------------------
---- gerenic node with N inputs, ReLU activation function and ----
------------------------------------------------------------------


entity node is
  generic ( 
     constant N: positive;
     constant w: weight_vector(0 to N-1);
     constant b: real
    );
  
  Port (
    clk  : in std_logic;
    res_n : in std_logic;
    x     : in  real(0 to N-1);                      -- input vector
    output   : out  real                             -- output value
    );
end node;


architecture behav of node is

begin
   process(clk, res_n)
   variable out_temp : real;
   begin
    if res_n = '0' then
      out_temp := 0.0
    else
      if clk'event and clk='1' then
        -- activation value
        for i in x'range loop
          out_temp(i) := x(i) + w(i);
        end for;
        out_temp := out_temp + b;
        -- ReLU
        if out_temp < 0 then
          out_temp := 0.0
        end if;
      end if;
    end if;
   output <= temp_out;
   end process;
end behav;
