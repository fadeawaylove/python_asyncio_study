# coding=utf-8
# 自动提交合并代码
import os


class gitScript(object):
    def __init__(self):
        self.current_branch = self.getCurBranchName()

    def run(self, commit):
        os.system("git commit -am '{}'".format(commit))
        os.system("git push origin {}".format(self.current_branch))
        os.system("git checkout develop")

        os.system("git pull origin develop")

        os.system("git merge {}".format(self.current_branch))

        os.system(":")
        os.system("q\n")

        os.system("git push origin develop")
        os.system("git checkout {}".format(self.current_branch))


    def getCurBranchName(self):
        for line in os.popen("git branch"):
            if line.startswith("*"):
                return line[1:]





if __name__ == "__main__":
    g = gitScript()
    g.run("test")
    print(g.current_branch)
