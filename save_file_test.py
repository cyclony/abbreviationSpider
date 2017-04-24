import sys
with open("text.txt",'a',encoding='utf-8') as f:
    str = ""
    while str != "exit":
        str = input("please input your key word: ")
        f.write(str+"\n")
        f.flush()
    sys.exit(0)

