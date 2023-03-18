# Project Report: Distance-Vector Routing Protocol Implementation in Python
## Introduction
Our project is a robust implementation of the Distance-Vector Routing protocol in Python. The implementation uses a variety of concepts, including the Bellman-Ford algorithm, socket programming, and multi-threading, to create a scalable and efficient solution for network routing.

## How to Run


## Techniques and Methodology Used for Implementation
We have implemented our program in Python, leveraging the object-oriented paradigm to create two key classes that are used throughout the codebase: 'Neighbor' and 'Path'.

- 'Neighbor' refers to the link between any two nodes that are directly connected to each other.
- 'Path' refers to the link between any two nodes that may or may not be directly connected to each other. It is worth noting that every neighbor is a path, but not every path is necessarily a neighbor.

Our program comprises several threads, including both permanent and temporary threads. 
### The permanent threads include:
Listening: This thread listens for “Distance Vectors” sent by the neighbors and creates a temporary Bellman-Ford thread when an update is detected.
- Menu: This thread acts as the main interface for the program. The interface (menu) presents the user with four options:
  - To view the shortest paths to the other routers in the network.
  - To view the whole distance vector table.
  - To edit the link cost(s).
  - To quit the program.
- Timeout Checking: This thread determines whether a router is dead or not. After every second, it checks if all the neighbors are listening at their designated ports. If an exception is found, the router is considered to be dead.

### The temporary threads are as follows:
- Bellman-Ford: This thread executes the Bellman-Ford algorithm on the distance vectors it has received from the neighbors. It is started whenever an updated Distance Vector is received from a neighbor.
- SendDV: This thread sends the router’s Distance Vector to all the neighbors. It is created every time an update in the Distance Vector is detected.
To ensure that the program can cater for link cost changes and re-instantiation of routers, the routers send their link cost in addition to the Distance Vector to the neighbors so that the neighbors can appropriately update the link cost.

## Relevant Problems in Development and their Solutions
### Count-to-Infinity Problem
The network was unable to converge when link costs increased, or a router failed due to the count-to-infinity problem. To counter this issue, we used the technique of 'Split Horizon with Reverse Poisoning.'

### Count-to-Infinity Extended Problem
In some rare situations, this problem occurred in larger loops instead of just two routers. To resolve this, we did not execute the Bellman-Ford algorithm immediately after a router failure. Instead, we advertised the distance to the dead router as infinity first. This way, the neighbors of the router became aware that the path was outdated, and the path to the dead router got expired (set as infinity), thus resolving the router looping problem.

### Change in Link Costs
When link costs changed through a given interface, there was no way for the other neighbor to find out about the change. To make the cost of the link consistent in both directions, the router sends the updated link cost in addition to the Distance Vector to the concerned neighbor. The neighbor can then update the cost to the new value.

### Router Re-instantiation
Whenever a router is created, it sends its link cost in addition to the Distance Vector to all neighbors. When neighbors receive this packet, they change the link cost to this router from 'infinity' to the specified value.

## Conclusion
The project enabled us to apply theoretical concepts practically and provided us with a real-life networking issue to solve. We learned the intricacies of distance-vector routing protocols and their significance in modern networks.
