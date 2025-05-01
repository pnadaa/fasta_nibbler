fasta_nibbler: Get a specified number of the first and last base pairs from fasta sequences  
  
A simple program that extracts the first and last number of base pairs from each sequence of a fasta file.  
  
Usage: python fasta_nibbler.py --type --input (--output) (--basepairs)  
  
-t, --type: Required.  
The type of output file:  
1: full sequence (same as input)  
2: 5' ends  
3: 3' ends  
4: 5' and 3' ends both in the same output file.  

-i, --input: Required. Name of the input filename, it cant take directories if the output is not written  
-o, --output: What would you like the output file to be named? Default: 3/5_prime_ends.fasta  
-bp, --basepairs: The number of base pairs to take from each end. Default = 300  
  
  
If you found this useful for your project, please cite this as:  
 
[![DOI](https://zenodo.org/badge/975677185.svg)](https://doi.org/10.5281/zenodo.15312728)