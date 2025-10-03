# probability-stream-06-joannafarris
Plan and draft a custom streaming data project. 

# P6: Probability Stream

This project simulates dice rolls as a continuous data stream using a Python generator.  
The consumer reads each event, updates running counts, and calculates live proportions for all six faces.  
A Matplotlib animation displays an updating bar chart that shows how the distribution of rolls converges toward the expected probability of 1/6 per face.  

The goal is to demonstrate streaming analytics concepts in a simple but meaningful way.  
Future extensions could include bias detection (flagging when one face appears too often early on) or adding a coin flip stream for comparison.  
