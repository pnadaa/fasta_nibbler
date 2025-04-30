import argparse

# From stackoverflow: https://stackoverflow.com/questions/64980270/how-to-allow-only-positive-integer-using-argparse
def check_positive(value):
    """
    This function checks if the argparse input is a pos integer for the basepairs argument
    """
    try:
        value = int(value)
        if value <= 0:
            raise argparse.ArgumentTypeError("{} is not a positive integer".format(value))
    except ValueError:
        raise Exception("{} is not a positive integer".format(value))
    return value

def check_type(value):
    """
    This function checks if the argparse input is valid for the type argument
    """
    try:
        value = int(value)
        if (value <= 0 or value > 4):
            raise argparse.ArgumentTypeError("{} is not a valid option".format(value))
    except ValueError:
        raise Exception("{} is not a positive integer".format(value))
    return value


parser = argparse.ArgumentParser(
                    prog='First and last',
                    description='This program extracts the first and/or last base pairs from sequences of a fasta file and writes into another file',
                    epilog='Thank you for using! -Chris')
parser.add_argument("-t", "--type", required=True, type = check_type, help="The type of output file: 1: full sequence (same as input), 2: 5' ends, 3: 3' ends, 4: 5' and 3' ends both in the same output file.")
parser.add_argument("-i", "--input", required = True, help = "Name of the input filename, it cant take directories if the output is not written")
parser.add_argument("-o", "--output", required = False, help = "What would you like the output file to be named? Default: 3/5_prime_ends.fasta")
parser.add_argument("-bp", "--basepairs", type = check_positive, required = False, default = "300", help = "The number of base pairs to take from each end. Default = 300")

args = parser.parse_args()


"""
Loads the file and returns the data stored.
"""  
with open(f"{str(args.input)}", "r", encoding="utf-8") as file:
    data = []
    for line in file:
        data.append(line)
    file.close


#Transforms the data into an array for saving later
i = 0
sequenceArray = []
miniSequenceArray = []
for line in data:
    if line.startswith(">"):
        # Store the line with the sequence name and also the sequence on the next line
        seqName = data[i][1:]
        fullSequence = str(data[i + 1])
        # Select the 5' end 3' ends of the sequence on the next line. If the sequence is shorter than 300bp, use the whole sequence for both instead
        if len(fullSequence) > args.basepairs:
            five_prime_bp = f"{data[i+1][:args.basepairs]}\n"
            three_prime_bp = data[i+1][-(args.basepairs + 1):]
        else:
            five_prime_bp = fullSequence
            three_prime_bp = fullSequence
        # Save the sequence name and associated procesed sequences into an array for output
        miniSequenceArray = [seqName, fullSequence, five_prime_bp, three_prime_bp]
        sequenceArray.append(miniSequenceArray)
    i += 1


"""
Formatting the output name based on the args or based on the type of processing
"""

if args.output == None:
    if args.type == "1":
        output_file = f"fullSequence_{args.input}"
    elif args.type == "2":
        output_file = f"5prime_{args.input}"
    elif args.type == "3":
        output_file = f"3prime_{args.input}"
    elif args.type == "4":
        output_file = f"5and3prime_{args.input}"
    else:
        output_file = "output"
else:
    output_file = args.output


"""
Writes any content parsed into the file.
"""
with open(f"{output_file}", "w", encoding="utf-8") as file:
    i = 0
    for insetion_sequences in sequenceArray:
        if args.type == "1":
            file.write(f">fullseq_{sequenceArray[i][0]}")
            file.write(f"{sequenceArray[i][1]}")
        elif args.type == "2":
            file.write(f">5_prime_{sequenceArray[i][0]}")
            file.write(f"{sequenceArray[i][2]}")
        elif args.type == "3":
            file.write(f">3_prime_{sequenceArray[i][0]}")
            file.write(f"{sequenceArray[i][3]}")
        elif args.type == "4":
            file.write(f">5_prime_{sequenceArray[i][0]}")
            file.write(f"{sequenceArray[i][2]}")
            file.write(f">3_prime_{sequenceArray[i][0]}")
            file.write(f"{sequenceArray[i][3]}")
        i += 1
file.close