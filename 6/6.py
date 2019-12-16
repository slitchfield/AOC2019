

class Body:

    def __init__(self, label="", parent=None, depth=0):
        self.label = label
        self.parent = parent
        self.children = []
        self.depth = depth

    def get_parent(self):
        return self.parent

    def add_child(self, body):
        self.children.append(body)

    def insert(self, center_label="", outer_label="", depth=0):
        print(f"(In {self.label}): Inserting {center_label}){outer_label}")
        if self.label != center_label:
            for child in self.children:
                child.insert(center_label, outer_label, depth+1)
        elif self.label == center_label:
            print(f"\tIn {self.label}: Found match! Inserting {outer_label} at depth={depth}")
            newnode = Body(outer_label, self, depth)
            self.add_child(newnode)

    def accumulate(self):
        res = 0
        if self.children:
            for child in self.children:
                res += child.accumulate()

        return res + self.depth

    def can_reach_y(self):
        
        reach = False
        for child in self.children:
            if child.label == 'YOU':
                return True

            if child.can_reach_y():
                return True

        return reach
    
    def can_reach_s(self):
        
        reach = False
        for child in self.children:
            if child.label == 'SAN':
                return True

            if child.can_reach_s():
                return True

        return reach

    def can_reach_ys(self):
        
        print(f"\t\tCan {self.label} reach YS?")
        
        reach_y = False
        reach_s = False
        for child in self.children:
            if child.label == 'YOU':
                print(f"\t\t\tYOU direct child")
                reach_y = True
            if child.label == 'SAN':
                print(f"\t\t\tSAN direct child")
                reach_s = True

            if child.can_reach_y():
                print(f"\t\t\tHave child that can reach y")
                reach_y = True
            if child.can_reach_s():
                print(f"\t\t\tHave child that can reach s")
                reach_s = True

        if reach_y and reach_s:
            print(f"\t\t\tCan reach both")
            return True
        else:
            print(f"\t\t\tCannot reach both")
            return False

    def find_y_depth(self):
       
        #print("Am I, {self.label}, Y?")
        if self.label == 'YOU':
            #print(f"Yes, at depth {self.depth}")
            return self.depth
        else:
            depth = -1
            for child in self.children:
                depth = child.find_y_depth()
                if depth > 0:
                    return depth
             
            return -1
    
    def find_s_depth(self):
       
        #print("Am I, {self.label}, S?")
        if self.label == 'SAN':
            #print(f"Yes, at depth {self.depth}")
            return self.depth
        else:
            depth = -1
            for child in self.children:
                depth = child.find_s_depth()
                if depth > 0:
                    return depth
             
            return -1

def run_test(lines):

    root = None

    seen_nodes = ['COM']

    temp_list = lines.copy()

    i = 0
    while len(temp_list) > 0:
        cur = temp_list[i]
        [center, outer] = cur.split(')')
        if center in seen_nodes or center == 'COM':
            print(f"Found seen center! {center}")

            seen_nodes.append(outer)
            if center == 'COM' and root == None:
                root = Body('COM', None, 0)
                root.insert('COM', outer, 1)
                seen_nodes.append(outer)
            else:
                root.insert(center, outer, 1)
            temp_list.remove(cur)
            i = 0
        else:
            i = (i + 1) % len(temp_list)
    #print(root.accumulate())

    max_common_depth = 0
    max_common_node = None
    you_depth = 0
    san_depth = 0

    done = False
    cur = root
    while not done:
        reach_ys = False
        print(f"In {cur.label}")
        for child in cur.children:
            print(f"\tEvaluating {child.label}")
            if child.can_reach_ys():
                print(f"\t\tCan reach YS!")
                max_common_depth = child.depth
                max_common_node = child
                cur = child
                reach_ys = True
                break
        if reach_ys == False:
            done = True


    print(f"Common Node {max_common_node.label} at {max_common_depth}")
    y_depth = root.find_y_depth()
    print(f"Y at depth of {y_depth}")
    s_depth = root.find_s_depth()
    print(f"S at depth of {s_depth}")
    distance = y_depth + s_depth - 2*(max_common_depth + 1)
    print(f"Transfers reqd: {distance}")
             

if __name__ == "__main__":

    filename = "6.input"
    #filename = "testcase1.input"

    with open(filename, 'r') as infile:
        lines = infile.readlines()
    
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    
    run_test(lines)
