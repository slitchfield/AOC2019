

def num_to_list(number):

    list_digits = []
    
    # Known to be 6 digits

    list_digits.append(int(number / 100000))
    list_digits.append(int(number / 10000) % 10)
    list_digits.append(int(number / 1000)  % 10)
    list_digits.append(int(number / 100)   % 10)
    list_digits.append(int(number / 10)    % 10)
    list_digits.append(int(number)         % 10)
    
    return list_digits

def list_to_num(digit_list):
    
    pass

def check_for_exactly_doubles(digit_list):
    
    # Get a set of present digits
    digit_set = set(digit_list)

    for elem in digit_set:
        if digit_list.count(elem) == 2:
            return True

def check_for_doubles(digit_list):

    if digit_list[1] == digit_list[0]:
        return True
    if digit_list[2] == digit_list[1]:
        return True
    if digit_list[3] == digit_list[2]:
        return True
    if digit_list[4] == digit_list[3]:
        return True
    if digit_list[5] == digit_list[4]:
        return True
    
    return False

def check_for_incr(digit_list):
    
    if digit_list[1] < digit_list[0]:
        return False
    if digit_list[2] < digit_list[1]:
        return False
    if digit_list[3] < digit_list[2]:
        return False
    if digit_list[4] < digit_list[3]:
        return False
    if digit_list[5] < digit_list[4]:
        return False

    return True

def evaluate_possibilities(minimum, maximum):

    num_passwords = 0

    for i in range(minimum, maximum):

        num_list = num_to_list(i)
        #if check_for_doubles(num_list) and check_for_incr(num_list):
        if check_for_exactly_doubles(num_list) and check_for_incr(num_list):
            num_passwords += 1
            print(f"Found Candidate: {num_list}")

    print(f"Num Passwords: {num_passwords}")

if __name__ == "__main__":
    evaluate_possibilities(264793, 803935)
