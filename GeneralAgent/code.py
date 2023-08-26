# CodeWorkspace: 
# 代码工作空间，就是Agent的工作空间
# concept和action的串联物，相当于人的肌肉，受控于神经元，操作工具，完成任务

import pickle
import os
import io
import sys
import logging

class CodeBlock:
    def __init__(self, type, command, code, log, name=None, value=None):
        assert type in ['set', 'get', 'command']
        self.type = type        # 类型, ['set', 'get', 'command']
        self.command = command  # 命令
        self.code = code
        self.log = log            # 运行日志
        self.name = name    # 在set和get使用
        self.value = value     # 在set使用

    def __str__(self):
        if self.type == 'set':
            return f"# set: \n{self.name}={self.value}"
        if self.type == 'get':
            return f"# get: {self.name}"
        if self.type == 'command':
            return f"# command: {self.command} \n {self.code}"
        return f"{self.type} {self.command} {self.name} {self.value} {self.code} {self.log}"

init_code = """
import os
import sys
"""

class CodeWorkspace:
    def __init__(self, serialize_path=None):
        # serialize_path: 保存工作环境的地址
        self.locals = {}    # 本地变量，代码运行时的环境
        self.code_block_list = []       # 代码块列表
        self.serialize_path = serialize_path    # 序列化地址
        if serialize_path is None:
            print("Warning: serialize_path is None, CodeWorkspace will not be serialized")
        load_success = self._load()
        if load_success is False:
            # 初始化
            global init_code
            self._code_run('init', init_code)

    def _load(self):
        # 加载
        if self.serialize_path is not None and os.path.exists(self.serialize_path):
            with open(self.serialize_path, 'rb') as f:
                data = pickle.loads(f.read())
                self.locals = data['locals']
                self.code_block_list = data['code_block_list']
                return True
        else:
            return False

    def _save(self):
        # 保存，即序列化
        if self.serialize_path is not None:
            with open(self.serialize_path, 'wb') as f:
                data = {'locals': self.locals, 'code_block_list': self.code_block_list}
                f.write(pickle.dumps(data))

    def input(self, command):
        # 输入命令(string)，生成代码并执行
        retry_count = 3
        # 生成代码
        code = self._code_generate(command)
        # 检查&修复代码
        for index in range(retry_count):
            check_success = self._code_check(command, code)
            if check_success: break
            if index == retry_count - 1: return False
            code = self._code_fix(code, command=command)
        # 执行代码&修复代码
        for index in range(retry_count):
            run_success, sys_stdio = self._code_run(command, code)
            if run_success: break
            if index == retry_count - 1: return False
            code = self._code_fix(code, command=command, error=sys_stdio)
        return run_success

    def _code_generate(self, command):
        # 根据命令，生成执行的代码
        # TODO
        code = ''
        return code

    def _code_check(self, command, code):
        # TODO: 
        # 验证代码是否可以执行，有没有什么问题
        return True
    
    def _code_fix(self, code, command=None, error=None):
        # TODO: 
        # 根据command，修复代码
        return code
    
    def _code_run(self, command, code):
        # 运行代码
        # TODO: 获取运行日志
        old_locals_bin = pickle.dumps(self.locals)
        # 重定向输出
        output = io.StringIO()
        sys.stdout = output
        try:
            # 运行代码
            exec(code, self.locals)
            # 获取结果
            sys_stdout = output.getvalue()
            # 保存代码块
            code_block = CodeBlock(type='command', command=command, code=code, log=sys_stdout)
            self.code_block_list.append(code_block)
            # 保存现场
            self._save()
            return True, sys_stdout
        except Exception as e:
            # 异常情况，恢复环境
            self.locals = pickle.loads(old_locals_bin)
            logging.exception(e)
            sys_stdout = output.getvalue()
            return False, sys_stdout
        finally:
            sys.stdout = sys.__stdout__

    def get_variable(self, var_name):
        if var_name in self.locals:
            # 保存代码块
            code_block = CodeBlock(type='get', command=None, code=None, log=None, name=var_name)
            self.code_block_list.append(code_block)
            # 保存现场
            self._save()
            return self.locals[var_name]
        else:
            print("Variable not found")
            return None

    def set_variable(self, var_name, var_value):
        self.locals[var_name] = var_value
        # 保存代码块
        code_block = CodeBlock(type='set', command=None, code=None, log=None, name=var_name, value=var_value)
        self.code_block_list.append(code_block)
        # 保存现场
        self._save()


    def get_code_sheet(self):
        # 获取代码清单
        return '\n\n'.join([str(code_block) for code_block in self.code_block_list])