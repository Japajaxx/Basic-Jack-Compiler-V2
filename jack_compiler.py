#Call with "python jack_compiler.py <filename>"

import sys
import os


symbols = [";",
           ",",
           "{{".format(),
           "}}".format(),
           "(",
           ")",
           "[",
           "]",
           "=",
           ".",
           "+",
           "-",
           "*",
           "/",
           "|",
           "~"]

keywords = ["class",
            "method",
            "function",
            "void",
            "static",
            "boolean",
            "field",
            "constructor",
            "var",
            "int",
            "char",
            "let",
            "if",
            "else",
            "while",
            "do",
            "true",
            "false",
            "null",
            "this",
            "return"]

comp = {"<": "&lt;",
        ">": "&gt;",
        "&": "&amp;"}

def parser(file_path):

    def token():
        for i in lines:
            if i[0] != "\n" and i[0] != "/" and i != "	\n" and i[0] != "*":
                if "//" in i:
                    i = i.split("//")[0]

                if "/**" in i:
                    i = i.split("/**")[0]

                if "*" in i:
                    i= i.strip()
                    if i[0] == "*":
                        continue


                i = i.replace("	", "")
                temp = ""
                in_string = False
                for char in i:
                    if char == '"':
                        if in_string:
                            temp += char
                            lines_new.append(f"{temp[1:-1]}")
                            temp = ""
                            in_string = False
                        else:
                            if temp.strip():
                                if temp in keywords:
                                    lines_new.append(f"{temp.strip()}")
                                elif temp.isdigit():
                                    lines_new.append(f"{temp.strip()}")
                                elif temp in comp:
                                    lines_new.append(f"{comp[temp]}")
                                else:
                                    lines_new.append(f"{temp.strip()}")
                            temp = char
                            in_string = True
                    elif in_string:
                        temp += char
                    elif char in symbols:
                        if temp.strip():
                            if temp in keywords:
                                lines_new.append(f"{temp.strip()}")
                            elif temp.isdigit():
                                lines_new.append(f"{temp.strip()}")
                            elif temp in comp:
                                lines_new.append(f"{comp[temp]}")
                            else:
                                lines_new.append(f"{temp.strip()}")
                            temp = ""
                        lines_new.append(f"{char}")
                    elif char.isspace():
                        if temp.strip():
                            if temp in keywords:
                                lines_new.append(f"{temp.strip()}")
                            elif temp.isdigit():
                                lines_new.append(f"{temp.strip()}")
                            elif temp in comp:
                                lines_new.append(f"{comp[temp]}")
                            else:
                                lines_new.append(f"{temp.strip()}")
                            temp = ""
                    else:
                        temp += char
                if temp.strip() and not in_string:
                    if temp in keywords:
                        lines_new.append(f"{temp.strip()}")
                    elif temp.isdigit():
                        lines_new.append(f"{temp.strip()}")
                    elif temp in comp:
                        lines_new.append(f"{comp[temp]}")
                    else:
                        lines_new.append(f"{temp.strip()}")

    file = open(file_path, 'r')
    lines = file.readlines()
    file.close()

    lines_new = []
    token()

    return lines_new
            

def code(parsed_lines, filename):

    xml_file_T = open(filename + ("T.xml"), "a")

    for i in parsed_lines:
        xml_file_T.write(i + "\n")

    xml_file_T.close()

    vm_file = open(filename + (".vm"), "a")

    

    def compileClass(index):
        index += 1
        className = parsed_lines[index]
        index += 1
        if parsed_lines[index].startswith("{"):
            index += 1
            index = compileSubroutine(index, className)

        return index


    def compileSubroutine(index, className):
        constructType = parsed_lines[index]
        index += 1
        constructValType = parsed_lines[index]
        index += 1
        constructName = parsed_lines[index]
        index += 2

        funcInputNumber = 0

        while not parsed_lines[index].startswith(")"):
            if not parsed_lines[index].startswith(","):
                funcInputNumber += 1
            index += 1
        index += 2

        vm_file.write(f"{constructType} {className}.{constructName} {funcInputNumber}\n")

        index = compileSubroutineBody(index)

        return index
    

    def compileSubroutineBody(index):

        if not(parsed_lines[index].startswith("var")):
            index = compileStatements(index)


    def compileStatements(index):
        while parsed_lines[index] in ["let","if","while","do","return"]:
            if parsed_lines[index].startswith("do"):
                index += 1
                index = compileDo(index)

    
    def compileDo(index):
        if parsed_lines[index].startswith("Output"):
            index += 2
            if parsed_lines[index].startswith("printInt"):
                index += 1
                printInt(index)

    def printInt(index):
        while not parsed_lines[index].startswith(")"):
            
            
            index += 1

        return index


    index = 0

    while index < len(parsed_lines):
        if parsed_lines[index].startswith("class"):
            index = compileClass(index)
        else:
            index += 1


    vm_file.close()
        

def hack_assembler():
    if len(sys.argv) != 2:
        print("Usage: python jack_compiler.py <folder_path>")
        return
    
    folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".jack"):
            file_path = os.path.join(folder_path, filename)
            parsed_lines = parser(file_path)
            code(parsed_lines, os.path.splitext(file_path)[0])

hack_assembler()