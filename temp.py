while True:
    input_str = input("Enter instrument tokens to add (comma-separated) or 'exit' to quit: ")
    stringsplit = input_str.split()
    print(f'Command is : {stringsplit[0]}')
    print(f'Tokens : {stringsplit[1]}')