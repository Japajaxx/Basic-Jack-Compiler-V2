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
        lines_new.append(f"<tokens>\n")
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
                            lines_new.append(f"<stringConstant> {temp[1:-1]} </stringConstant>\n")
                            temp = ""
                            in_string = False
                        else:
                            if temp.strip():
                                if temp in keywords:
                                    lines_new.append(f"<keyword> {temp.strip()} </keyword>\n")
                                elif temp.isdigit():
                                    lines_new.append(f"<integerConstant> {temp.strip()} </integerConstant>\n")
                                elif temp in comp:
                                    lines_new.append(f"<symbol> {comp[temp]} </symbol>\n")
                                else:
                                    lines_new.append(f"<identifier> {temp.strip()} </identifier>\n")
                            temp = char
                            in_string = True
                    elif in_string:
                        temp += char
                    elif char in symbols:
                        if temp.strip():
                            if temp in keywords:
                                lines_new.append(f"<keyword> {temp.strip()} </keyword>\n")
                            elif temp.isdigit():
                                lines_new.append(f"<integerConstant> {temp.strip()} </integerConstant>\n")
                            elif temp in comp:
                                lines_new.append(f"<symbol> {comp[temp]} </symbol>\n")
                            else:
                                lines_new.append(f"<identifier> {temp.strip()} </identifier>\n")
                            temp = ""
                        lines_new.append(f"<symbol> {char} </symbol>\n")
                    elif char.isspace():
                        if temp.strip():
                            if temp in keywords:
                                lines_new.append(f"<keyword> {temp.strip()} </keyword>\n")
                            elif temp.isdigit():
                                lines_new.append(f"<integerConstant> {temp.strip()} </integerConstant>\n")
                            elif temp in comp:
                                lines_new.append(f"<symbol> {comp[temp]} </symbol>\n")
                            else:
                                lines_new.append(f"<identifier> {temp.strip()} </identifier>\n")
                            temp = ""
                    else:
                        temp += char
                if temp.strip() and not in_string:
                    if temp in keywords:
                        lines_new.append(f"<keyword> {temp.strip()} </keyword>\n")
                    elif temp.isdigit():
                        lines_new.append(f"<integerConstant> {temp.strip()} </integerConstant>\n")
                    elif temp in comp:
                        lines_new.append(f"<symbol> {comp[temp]} </symbol>\n")
                    else:
                        lines_new.append(f"<identifier> {temp.strip()} </identifier>\n")
        lines_new.append(f"</tokens>\n")

    file = open(file_path, 'r')
    lines = file.readlines()
    file.close()

    lines_new = []
    token()

    return lines_new
            

def code(parsed_lines, filename):

    xml_file_T = open(filename + ("T.xml"), "a")

    for i in parsed_lines:
        xml_file_T.write(i)

    xml_file_T.close()

    xml_file = open(filename + (".xml"), "a")

    index = 0

    def classDec(index):
        xml_file.write("<class>\n")
        while parsed_lines[index] != "<symbol> { </symbol>\n":
            xml_file.write(parsed_lines[index])
            index += 1
        xml_file.write(parsed_lines[index])
        index += 1

        while parsed_lines[index] != "<symbol> } </symbol>\n":
            if parsed_lines[index] != "<keyword> static </keyword>\n" and parsed_lines[index] != "<keyword> field </keyword>\n":
                index = subroutineDec(index)
            else:
                index = classVarDec(index)
        xml_file.write(parsed_lines[index])
        index += 1

        xml_file.write("</class>\n")

        return index
    

    def classVarDec(index):
        xml_file.write("<classVarDec>\n")
        while parsed_lines[index] != "<symbol> ; </symbol>\n":
            xml_file.write(parsed_lines[index])
            index += 1
        xml_file.write(parsed_lines[index])
        index += 1
        xml_file.write("</classVarDec>\n")
        return index


    def subroutineDec(index):
        xml_file.write("<subroutineDec>\n")
        while parsed_lines[index] != "<symbol> ( </symbol>\n":
            xml_file.write(parsed_lines[index])
            index += 1
        xml_file.write(parsed_lines[index])
        index += 1

        index = parameterListDec(index)
        xml_file.write("<subroutineBody>\n")
        while parsed_lines[index] != "<symbol> } </symbol>\n":

            if parsed_lines[index] == "<keyword> var </keyword>\n":
                index = varDec(index)
            elif parsed_lines[index] == "<keyword> let </keyword>\n" or parsed_lines[index] == "<keyword> if </keyword>\n" or parsed_lines[index] == "<keyword> while </keyword>\n" or parsed_lines[index] == "<keyword> do </keyword>\n" or parsed_lines[index] == "<keyword> return </keyword>\n":
                index = statementDec(index)
            else:
                xml_file.write(parsed_lines[index])
                index += 1
        
        xml_file.write(parsed_lines[index])
        index += 1
        xml_file.write("</subroutineBody>\n")
        xml_file.write("</subroutineDec>\n")

        return index
    

    def parameterListDec(index):
        xml_file.write("<parameterList>\n")

        while parsed_lines[index] != "<symbol> ) </symbol>\n":
            xml_file.write(parsed_lines[index])
            index += 1

        xml_file.write("</parameterList>\n")
        xml_file.write(parsed_lines[index])
        index += 1

        return index

        
    def varDec(index):
        xml_file.write("<varDec>\n")
        while parsed_lines[index] != "<symbol> ; </symbol>\n":
            xml_file.write(parsed_lines[index])
            index += 1
        xml_file.write(parsed_lines[index])
        index += 1
        xml_file.write("</varDec>\n")

        return index


    def statementDec(index):
        xml_file.write("<statements>\n")

        while parsed_lines[index] == "<keyword> let </keyword>\n" or parsed_lines[index] == "<keyword> if </keyword>\n" or parsed_lines[index] == "<keyword> while </keyword>\n" or parsed_lines[index] == "<keyword> do </keyword>\n" or parsed_lines[index] == "<keyword> return </keyword>\n":
            if parsed_lines[index] == "<keyword> let </keyword>\n":
                index = letDec(index)
            if parsed_lines[index] == "<keyword> if </keyword>\n":
                index = ifDec(index)
            if parsed_lines[index] == "<keyword> while </keyword>\n":
                index = whileDec(index)
            if parsed_lines[index] == "<keyword> do </keyword>\n":
                index = doDec(index)
            if parsed_lines[index] == "<keyword> return </keyword>\n":
                index = returnDec(index)

        xml_file.write("</statements>\n")

        return index


    def ifDec(index):
        xml_file.write("<ifStatement>\n")
        while parsed_lines[index] != "<symbol> ( </symbol>\n":
            xml_file.write(parsed_lines[index])
            index += 1
        xml_file.write(parsed_lines[index])
        index += 1

        index = expressionDec(index, thing=False)

        while parsed_lines[index] != "<symbol> { </symbol>\n":
            xml_file.write(parsed_lines[index])
            index += 1
        xml_file.write(parsed_lines[index])
        index += 1

        index = statementDec(index)

        xml_file.write(parsed_lines[index])
        index += 1

        if parsed_lines[index] == "<keyword> else </keyword>\n":
            xml_file.write(parsed_lines[index])
            index += 1
            xml_file.write(parsed_lines[index])
            index += 1
            index = statementDec(index)
            xml_file.write(parsed_lines[index])
            index += 1

        xml_file.write("</ifStatement>\n")

        return index


    def doDec(index):
        xml_file.write("<doStatement>\n")
        while parsed_lines[index] != "<symbol> ; </symbol>\n":
            if parsed_lines[index] == "<symbol> ( </symbol>\n":
                index = expressionDecList(index)
            else:
                xml_file.write(parsed_lines[index])
                index += 1

        xml_file.write(parsed_lines[index])
        index += 1
        xml_file.write("</doStatement>\n")

        return index
    
    
    def returnDec(index):
        xml_file.write("<returnStatement>\n")
        xml_file.write(parsed_lines[index])
        index += 1
        while parsed_lines[index] != "<symbol> ; </symbol>\n":
            index = expressionDec(index, thing=False)
        xml_file.write(parsed_lines[index])
        index += 1

        xml_file.write("</returnStatement>\n")

        return index
    
    
    def expressionDecList(index):
        xml_file.write(parsed_lines[index])
        index += 1
        xml_file.write("<expressionList>\n")
        if parsed_lines[index] != "<symbol> ) </symbol>\n":
            index = expressionDec(index, thing=False)
        xml_file.write("</expressionList>\n")
        xml_file.write(parsed_lines[index])
        index += 1

        return index


    def expressionDec(index, thing):

        if not thing:
            xml_file.write("<expression>\n")
        while parsed_lines[index] not in ["<symbol> ) </symbol>\n", "<symbol> ; </symbol>\n", "<symbol> ] </symbol>\n"]:
            if parsed_lines[index] == "<symbol> ( </symbol>\n":
                if isExpressionList(index + 1):
                    index = expressionDecList(index)
                else:
                    xml_file.write("<term>\n")
                    xml_file.write(parsed_lines[index])
                    index += 1
                    index = expressionDec(index, thing=False)
                    xml_file.write(parsed_lines[index])
                    index += 1
                    xml_file.write("</term>\n")
            elif parsed_lines[index] in ["<symbol> - </symbol>\n", "<symbol> ~ </symbol>\n"] and parsed_lines[index - 1] == "<symbol> ( </symbol>\n":
                # Handle unary operators
                xml_file.write("<term>\n")
                xml_file.write(parsed_lines[index])
                index += 1
                index = expressionDec(index , thing=True)
                xml_file.write("</term>\n")
            elif parsed_lines[index + 1] == "<symbol> . </symbol>\n":
                xml_file.write("<term>\n")
                while parsed_lines[index] != "<symbol> ( </symbol>\n":
                    xml_file.write(parsed_lines[index])
                    index += 1
                index = expressionDecList(index)
                xml_file.write("</term>\n")
            elif parsed_lines[index + 1] == "<symbol> [ </symbol>\n":
                xml_file.write("<term>\n")
                xml_file.write(parsed_lines[index])
                index += 1
                xml_file.write(parsed_lines[index])
                index += 1
                index = expressionDec(index, thing=False)
                xml_file.write(parsed_lines[index])
                index += 1
                xml_file.write("</term>\n")
            elif parsed_lines[index] == "<symbol> , </symbol>\n":
                xml_file.write("</expression>\n")
                xml_file.write(parsed_lines[index])
                index += 1
                xml_file.write("<expression>\n")
            else:
                if parsed_lines[index].startswith("<symbol>"):
                    xml_file.write(parsed_lines[index])
                    index += 1
                else:
                    xml_file.write("<term>\n")
                    xml_file.write(parsed_lines[index])
                    index += 1
                    xml_file.write("</term>\n")
        if not thing:
            xml_file.write("</expression>\n")
        return index

    def isExpressionList(index):
        while parsed_lines[index] != "<symbol> ) </symbol>\n":
            if parsed_lines[index] == "<symbol> , </symbol>\n":
                return True
            index += 1
        return False


    def letDec(index):
        xml_file.write("<letStatement>\n")

        while parsed_lines[index] != "<symbol> ; </symbol>\n":
            if parsed_lines[index] == "<symbol> ( </symbol>\n" or parsed_lines[index] == "<symbol> [ </symbol>\n":
                xml_file.write(parsed_lines[index])
                index += 1
                index = expressionDec(index, thing=False)
                xml_file.write(parsed_lines[index])
                index += 1
            elif parsed_lines[index] == "<symbol> = </symbol>\n":
                xml_file.write(parsed_lines[index])
                index += 1
                index = expressionDec(index, thing=False)
            else:
                xml_file.write(parsed_lines[index])
                index += 1
        xml_file.write(parsed_lines[index])
        index += 1

        xml_file.write("</letStatement>\n")

        return index
    

    def whileDec(index):
        xml_file.write("<whileStatement>\n")
        xml_file.write(parsed_lines[index])
        index += 1

        while parsed_lines[index] == "<symbol> ( </symbol>\n" or parsed_lines[index] == "<symbol> { </symbol>\n":
            if parsed_lines[index] == "<symbol> ( </symbol>\n":
                xml_file.write(parsed_lines[index])
                index += 1
                index = expressionDec(index, thing=False)
                xml_file.write(parsed_lines[index])
                index += 1
            elif parsed_lines[index] == "<symbol> { </symbol>\n":
                xml_file.write(parsed_lines[index])
                index += 1
                index = statementDec(index)
                xml_file.write(parsed_lines[index])
                index += 1

        xml_file.write("</whileStatement>\n")

        return index


    while index < len(parsed_lines):
        if parsed_lines[index] == "<keyword> class </keyword>\n":
              index = classDec(index)
        else:
            index += 1

        

    xml_file.close()
        

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