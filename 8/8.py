

def run_test(lines):
    
    width  = 25
    height = 6

    layer_size = width * height

    image = list(lines[0])
    image = [int(x) for x in image]

    assert(len(image) % layer_size == 0)

    # Separate into layers
    print(f"Separating Layers")
    raw_layers = []
    for i in range(int(len(image) / layer_size)):
        off = i * layer_size
        raw_layers.append(image[off:off+layer_size])
        print(raw_layers)

    assert(len(raw_layers[0]) % height == 0)
    assert(len(raw_layers[0]) % width  == 0)

    print(f"Separating Rows")
    # Separate the rows
    new_image = []
    for l in range(len(raw_layers)):
        new_image.append([])
        layer = raw_layers[l]
        for i in range(int(len(layer) / width)):
            print(f"i: {i}")
            off = i * width
            new_image[l].append(layer[off:off+width])
    
    black = 0
    white = 1
    trans = 2

    final_image = new_image[0]
    for r in range(height):
        for c in range(width):
            # Iterate through layers until we find a non-transparent
            for l in range(len(raw_layers)):
                if new_image[l][r][c] != trans:
                    final_image[r][c] = new_image[l][r][c]
                    break
            
    print("Final Message:")
    for r in range(height):
        for c in range(width):
            if final_image[r][c] == black:
                print("#",end='')
            elif final_image[r][c] == white:
                print(" ",end='')
            else:
                print("UNKNOWN COLOR: {final_image[r][c]}")
        print()
            
    """
    print(f"Finding Layer with fewest 0's")
    min_count = layer_size + 1
    min_ones  = 0
    min_twos  = 0
    min_layer = None
    for layer in new_image:
        zero_count = 0
        one_count  = 0
        two_count  = 0
        for row in layer:
            zero_count += row.count(0)
            one_count  += row.count(1)
            two_count  += row.count(2)

        if zero_count < min_count:
            min_count = zero_count
            min_layer = layer
            min_ones  = one_count
            min_twos  = two_count

    # Presumably, we have the minimum layer
    print(min_layer)
    print(one_count)
    print(two_count)
    print(min_ones * min_twos)
    """

if __name__ == "__main__":
    
    filename = "8.input"
    #filename = "testcase1.input"

    with open(filename, 'r') as infile:
        lines = infile.readlines()
    
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    
    run_test(lines)
