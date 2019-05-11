
inflow_data = []
inflow_file = "steadyflow.txt"

try:

    with open(inflow_file, "r") as ofile:
        for line in ofile:
            values = line.strip().split()
            time=float(values[0]) 
            flow=float(values[1])
            print(values[0])
            print(values[1])
    #__with open(inflow_file, "r") as ofile

except Exception as e:
    print(str(e))

