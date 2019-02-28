def convert_to_map(input_string):
    input_map = {}
    for i in range(len(input_string)):
        if(i % 2 == 0):
            continue
        try:
            input_map[input_string[i]] = input_string[i + 1]
        except:
            print("Invalid arguments")
    return input_map
