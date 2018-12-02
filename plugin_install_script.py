# coding=utf-8
import os
import re



def install_script(command,file_name):
	# 1.读取文件中的插件名
	with open(file_name, "r") as f:
		content = f.read()
	# print(content)

	# 2.正则获取插件名
	script_list = re.findall("[\w\d-]+.*\n", content)
	# print("script_list:{}".format(script_list))

	# 3.命令行执行这个
	for script_name in script_list:
		print("now installing {}".format(script_name),)
		os.system(command + " " + script_name)
		print("----"*10)

if __name__ == "__main__":
	f_name = raw_input("请输入文件名:")
	command = raw_input("请输入命令:")
	# apm install
	install_script(command, f_name)
