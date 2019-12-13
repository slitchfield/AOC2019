

def calc_fuel(module_mass):
    if int(module_mass / 3) - 2 <= 0:
        return 0
    return int(module_mass / 3) - 2 + calc_fuel(int(module_mass / 3) - 2)
 
if __name__ == "__main__":
    with open("1.input", 'r') as infile:
        lines = infile.readlines()[:-1]
    
    acc = 0
    for line in lines:
        acc += calc_fuel(int(line.rstrip()))
    print(lines)
    print("Acc: {0}".format(acc))
