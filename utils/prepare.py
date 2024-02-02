import os
import time

from utils.path import *


def tran_ui():
    ui_files = []
    for _ in os.listdir(ui_dir):
        if ".ui" not in _:
            continue
        if float(time.time()) - os.path.getmtime(f"{ui_dir}/{_}") > 60 * 10:
            continue
        ui_files.append(_)

    for ui_file in ui_files:
        ui_py_file = f"ui_{ui_file.replace('.ui', '.py')}"
        command = f'{str(uic_path)} {ui_dir}/{ui_file} -o {ui_dir}/{ui_py_file}'
        os.system(command)
        print(command)


def tran_qrc():
    # if float(time.time()) - os.path.getmtime("../res/resource.qrc") < 60 * 10:
    command = f"{rcc_path}  ../res/resource.qrc -o ../res/resource_rc.py"
    os.system(command)
    print(command)

    for py_file in os.listdir(ui_dir):
        if ".py" not in py_file:
            continue

        print(f"replaced {py_file}")
        with open(f"{ui_dir}/{py_file}", "r+", encoding="utf-8") as f:
            text = f.read()
            text = text.replace("import resource_rc", "import res.resource_rc")
        with open(f"{ui_dir}/{py_file}", "w", encoding="utf-8") as f:
            f.write(text)


def prepare():
    former_dir = os.path.abspath(".")
    os.chdir(os.path.dirname(__file__))

    tran_ui()
    tran_qrc()

    os.chdir(former_dir)


if __name__ == "__main__":
    prepare()
