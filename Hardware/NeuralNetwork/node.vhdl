library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use ieee.NUMERIC_STD.all;
library work;

------------------------------------------------------------------
---- gerenic node with N inputs, ReLU activation function and ----
------------------------------------------------------------------


entity node is
  generic ( 
     constant N: positive;
     constant w: real(N-1 downto 0);
    constant b: real
    );
  
  Port (
    x     : in  integer(N-1 downto 0);                     -- input vector
    output   : out  rel                                    -- output value
    );
end node; 
