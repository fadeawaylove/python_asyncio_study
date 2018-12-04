# coding=utf-8
import os


def getCurBranchName():
        for line in os.popen("git branch"):
            if line.startswith("*"):
                return line[1:]


if __name__ == "__main__":
    cur_branch = getCurBranchName()
    print("当前分支:{}".format(cur_branch))
    os.system("git pull origin " + cur_branch)



