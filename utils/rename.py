import os


def rename(operate):
    os.chdir("../")

    for f in os.listdir("ts"):
        ord_name = f
        if ".ts" in f:
            new_name = f.replace(".ts", "")
        else:
            if operate == "r":
                new_name = ord_name + ".ts"
            else:
                new_name = ord_name
        os.rename(ord_name, new_name)
        print(f"{ord_name} to {new_name}")


if __name__ == "__main__":
    o = input("operate:")
    rename(o)
