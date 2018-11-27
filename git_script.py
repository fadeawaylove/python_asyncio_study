# coding=utf-8
# 自动提交合并代码
import os
import sys

class gitScript(object):
    def __init__(self):
        self.current_branch = self.getCurBranchName()

    def run(self, commit):
        os.system("git commit -am '{}'".format(commit))
        os.system("git push origin {}".format(self.current_branch))
        os.system("git checkout develop")

        os.system("git pull origin develop")
        # os.system(":")
        # os.system("q\n")

        os.system("git merge {}".format(self.current_branch))
        # os.system(":")
        # os.system("q\n")

        os.system("git push origin develop")
        os.system("git checkout {}".format(self.current_branch))


    def getCurBranchName(self):
        for line in os.popen("git branch"):
            if line.startswith("*"):
                return line[1:]

# 呵呵呵
if __name__ == "__main__":
    # 要先获取当前路径
    current_path = os.getcwd()
    print(current_path)

    # commit = sys.argv[-1]
    commit = raw_input("message:")
    gitScript().run(commit)
