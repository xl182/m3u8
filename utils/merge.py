def merge_files(name):
    import os
    with open("../ts/" + name + ".ts", "wb") as l_f:
        file_list = os.listdir("../store/" + name)
        file_list.sort(key=lambda x: int(x.replace(".ts", "")) if ".ts" in x else 0)
        for file in file_list:
            if ".ts" in file:
                with open("../store/" + name + '/' + file, "rb") as s_f:
                    l_f.write(s_f.read())
                print(file)
    print("decoded ok")


if __name__ == "__main__":
    name = str(input("dir name:"))
    merge_files(name)
