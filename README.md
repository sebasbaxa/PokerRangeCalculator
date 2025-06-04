# PokerRangeCalculator
A tool to find the win rate of a range against another range

# How it works
Runs simulations with each hero's hand (the range whose win rate will be shown in the output) against random hands from the villain range (the number of simulations run can be adjusted in the Simulation tab). The output will show the win rate of each hero hand (not including splits).

# Some limitations
Because the win rate is found through random simulation, variance plays a large role in the output. This can be reduced by increasing the number of simulations per hand (which can be adjusted in the simulations tab). However, the runtime can become long for large hero ranges, so it is recommended to keep the simulation number small for large hero ranges and increase the number for smaller hero ranges. 
