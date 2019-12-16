
import itertools

def get_visited_points(linepath):

    # Find visited points
    visited = []
    x = 0
    y = 0
    steps = 1
    for move in linepath:
        if move[0] == 'R':
            xdel = 1
            ydel = 0
        elif move[0] == 'U':
            xdel = 0
            ydel = 1
        elif move[0] == 'L':
            xdel = -1
            ydel = 0
        elif move[0] == 'D':
            xdel = 0
            ydel = -1
        else:
            print("What? {0}".format(move))

        length = move[1]
        while length > 0:
            x += xdel
            y += ydel
            visited.append((x, y, steps))
            steps += 1
            length -= 1
    
    visited.sort()
    min_list = visited.copy()
    for i in range(len(visited) - 1):
        if visited[i][0] == visited[i+1][0]:
            if visited[i][1] == visited[i+1][1]:
                print("Found repeated coord: {0}".format(visited[i]))
                print("Steps ", visited[i][2], " vs ", visited[i+1][2])
                min_list.remove(visited[i+1])
    return min_list

def get_intersection_points(path1, path2):

    intersections = []
    total_count = len(path1) * len(path2)
    current_comp = 0
    for a, b in itertools.product(path1, path2):
        if a[0] == b[0] and a[1] == b[1]:
            print()
            print("Found intersection at {0}".format(a))
            inter = (a[0], a[1], a[2], b[2])
            intersections.append(inter)

        current_comp += 1

        if current_comp % 10000 == 0:
            done = 100 * current_comp / total_count
            print(f"\r{done:.3f}% done",end='')

    return intersections

def man_dist(tup):

    return abs(tup[0]) + abs(tup[1])

def day3part1(filename):

    with open(filename, 'r') as infile:
        lines = infile.readlines()

    line1path = lines[0].rstrip().split(',')
    for i in range(len(line1path)):
        elem = line1path[i]
        line1path[i] = (elem[0], int(elem[1:]))
    line2path = lines[1].rstrip().split(',')
    for i in range(len(line2path)):
        elem = line2path[i]
        line2path[i] = (elem[0], int(elem[1:]))

    line1visited = get_visited_points(line1path)
    line2visited = get_visited_points(line2path)

    intersections = get_intersection_points(line1visited, line2visited)

    print(intersections)
    intersections.sort(key=lambda val: val[2] + val[3])
    print(intersections)

    dist = intersections[0][2] + intersections[0][3]
    print("Distance: {0}".format(dist))

if __name__ == "__main__":
    
    #filename = "testcase1.input"
    #filename = "testcase2.input"
    #filename = "testcase3.input"
    filename = "3.input"

    day3part1(filename)
