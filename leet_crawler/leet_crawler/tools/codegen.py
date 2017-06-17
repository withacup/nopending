# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-13 12:30:58
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-16 17:02:02
from util.questionmeta import QuestionMeta
from tools.syntaxparser import SyntaxParser

'''
'''
DELI = ''
class CodeGenerator:
    def __init__(self, problem_id, l_type, total_testcases):    
        self.problem_id = str(problem_id)
        self.l_type = l_type
        self.qm = QuestionMeta()
        self.qm.load()
        self.JAVA = 'java'
        self.PYTHON = 'python'
        self.CPP = 'cpp'

        self.sp = SyntaxParser(self.problem_id, self.JAVA)
        self.total_testcases = total_testcases
        self.input_tree = self.sp.get_input_type()
        self.output_tree = self.sp.get_output_type()
        self.param_name_arr = self.sp.get_param_name()
        self.func_name = self.sp.get_func_name()
        self.param_arr = []
        # the problem may have no input parameter
        if self.param_name_arr:
            for i, child in enumerate(self.input_tree.get_root_child()):
                self.param_arr.append((self.param_name_arr[i], str(child)))

    def generate_variable(self, offset, end):
        if type(offset) is not int:
            raise TypeError('offset must be a int instead of {0}'.format(type(offset)))
        if self.l_type == self.CPP:
            return self.__gen_cpp_static(offset)
        if self.l_type == self.JAVA:
            return self.__gen_java_static(offset, end)
        if self.l_type == self.PYTHON:
            return self.__gen_py_static(offset)
        raise TypeError('Unsupported l_type: {0}'.format(self.l_type))

    def generate_function(self, boolean_value):
        # if self.l_type == 'cpp':
        #     return self.__gen_cpp_func()
        if self.l_type == 'java':
            return self.__gen_java_func(boolean_value)
        # if self.l_type == 'python':
        #     return self.__gen_py_func()
        raise TypeError('Unsupported l_type: {0}'.format(self.l_type))

    # boolean_value is needed to when return type is boolean(50% probability accepted)
    def __gen_java_func(self, boolean_value):
        self.boolean_value = boolean_value
        func_define = "{accessibility} {output_type} {func_name} ({param_list})"
        func_body = "{{{body}}};"

        # defination
        param_template = "{type} {name}"
        param_arr = []
        for p_name, p_type in self.param_arr:
            param_arr.append(param_template.format(type=p_type, name=p_name))

        func_define = func_define.format(accessibility='public', 
                                         output_type=str(self.output_tree.get_root().get_child_type()[0]), 
                                         func_name=self.func_name, 
                                         param_list=",".join(param_arr))

        # body
        func_body = func_body.format(body=self.__body(
                                         self.__printer(
                                            self.__printer_body(
                                                self.__formatter(
                                                    self.__sub_printer(
                                                        self.__recur_printer
                                                        ))))))
        util_func = 'void _encode_tree(TreeNode root, List<String> cache) {if (root == null) {cache.add("#"); return; } cache.add(Integer.toString(root.val)); _encode_tree(root.left, cache); _encode_tree(root.right, cache); }'
        return "".join([util_func, func_define, func_body])

    def __body(self, printer):
        body_template = "{limiter}{walker}{printer}{returner}"
        limiter_template = "if (_walker >= _home) {{{adder}}};"
        # adder_template = "_{num}Param.add({param_name});"
        # adder_template = "_{num}Param[_walker - _home] = {param_name};"
        # Becuase of some wired stuff in leetcode case runner, I need to initiate an array long enough to get all test cases
        adder_template = "_{num}Param.add({param_name});"
        adder = "".join([adder_template.format(num=i, param_name=self.param_name_arr[i], total_testcases=self.total_testcases) for i in range(len(self.param_name_arr))])
        limiter = limiter_template.format(adder=adder)
        walker = "_walker++;"
        returner_template = "{do_return} _{origin_func_name}({origin_params});"
          # if the return type of this solution is void, 
        # then we don't need to return any thing, just call the function is fine
        output_type_str = str(self.output_tree.get_root_child()[0])
        do_return = 'return'
        if output_type_str == 'void':
            do_return = ""
        returner = returner_template.format(do_return=do_return, origin_func_name=self.func_name, origin_params=",".join(self.param_name_arr))
        return body_template.format(do_return=do_return,
                                    limiter=limiter,
                                    walker=walker,
                                    printer=printer,
                                    returner=returner)

    def __printer(self, printer_body):
        printer_template = "if (_walker == _office) {{{print_body}}};"
        return printer_template.format(print_body=printer_body)

    def __printer_body(self, formatter):
        print_body_template = "for (int i = 0; i < _walker - _home; i++) {{{formatter}}};return {code_stopper};"
        output_type_str = str(self.output_tree.get_root_child()[0])
        code_stopper = 'null'
        if output_type_str in ['int', 'double', 'float', 'long', 'short']:
            code_stopper = '-1'
        type_cases = {
            'char': "'*'",
            'boolean': self.boolean_value,
            'void': '',
        }
        if output_type_str in type_cases:
            code_stopper = type_cases[output_type_str]
        return print_body_template.format(formatter=formatter, code_stopper=code_stopper)

    def __formatter(self, sub_printers):
        formatter_template = '{beginner}{sub_printers}{endder}'
        # beginner = 'System.out.println("---BEGIN:" + (i + _home + 1) + "---");'
        beginner = ''
        endder = 'System.out.println("---END:" + (i + _home + 1) + "---");'
        return formatter_template.format(beginner=beginner, endder=endder, sub_printers=sub_printers)

    def __sub_printer(self, recur_printer):
        pre_fix = "_"
        separator = "System.out.println();"
        # recur_printer_template = "System.out.print('[');for ({sub_type} {pre_fix}p: _{num}Param.get(i)) {{{recur_printer}}}System.out.print(']');{separator}"
        code_arr = []
        for num in range(len(self.param_name_arr)):
            _node = self.input_tree.get_root_child()[num]
            recur_printer_template = "System.out.print('[');for ({sub_type} {pre_fix}p: _{num}Param.get(i)) {{{recur_printer}}}System.out.print(']');{separator}"

            if _node.get_type() not in ['List', '[]', 'ListNode', 'TreeNode']:
                recur_printer_template = ''.join(['System.out.print("[");',
                                                    'System.out.print(_{num}Param.get(i));',
                                                    'System.out.print("]");', 
                                                    '{separator}'])
                code_arr.append(recur_printer_template.format(num=num, separator=separator))
            elif _node.get_type() == 'ListNode':
                recur_printer_template = ''.join(['System.out.print("[");',
                                                    'ListNode _{num}temp_node = _{num}Param.get(i); while(_{num}temp_node != null) {{'+ DELI +' System.out.print(_{num}temp_node.val + ","); '+ DELI +' _{num}temp_node = _{num}temp_node.next; }}',
                                                    'System.out.print("]");', 
                                                    '{separator}'])
                code_arr.append(recur_printer_template.format(num=num, separator=separator))
            elif _node.get_type() == 'TreeNode':
                recur_printer_template = ''.join(['System.out.print("[");',
                                                    'List<String> __cache = new ArrayList<String>(); _encode_tree(_{num}Param.get(i), __cache); System.out.print(__cache);',
                                                    'System.out.print("]");', 
                                                    '{separator}'])
                code_arr.append(recur_printer_template.format(num=num, separator=separator))
            else:
                code_arr.append(recur_printer_template.format(sub_type=str(_node.get_child_type()[0]),
                                                              pre_fix=pre_fix,
                                                              num=num,
                                                              recur_printer=recur_printer(_node.get_child_type()[0], pre_fix),
                                                              separator=separator)) 
        return ''.join(code_arr)

    def __recur_printer(self, param_node, pre_fix):
        recur_printer_template = 'System.out.print("["); for ({sub_type} {pre_son}p: {pre_dad}p) {{{sub_printer}}}; System.out.print("]");'
        return self.__java_recursive_printer(recur_printer_template, param_node, pre_fix)

    def __java_recursive_printer(self, recur_printer_template, param_node, pre_fix):
        if param_node.get_type() in ['List', '[]']:
            return recur_printer_template.format(sub_type=str(param_node.get_child_type()[0]),
                                                 pre_son=pre_fix + '_', 
                                                 pre_dad=pre_fix, 
                                                 sub_printer=self.__java_recursive_printer(recur_printer_template,
                                                                                           param_node.get_child_type()[0],
                                                                                           pre_fix + '_'))
        return DELI +'System.out.print({0}p);System.out.print(",");'.format(pre_fix)

    def __gen_java_static(self, offset, end):
        static_counter = "static int _home = {0};static int _walker = 0;static int _office = {1};".format(offset, end)
        static_cache_template = "static List<{param_type}> _{param_num}Param = new ArrayList<{param_type}>({fetching_length});"
        # static_cache_template = "static {param_type}[] _{param_num}Param = new {param_type}[{fetching_length}];"
        static_statement_arr = [static_counter]

        for i, child in enumerate(self.input_tree.get_root_child()):
            type_str = str(child)
            boxing = {
                'int': 'Integer',
                'double': 'Double',
                'float': 'Float',
                'char': 'Character',
                'boolean': 'Boolean',
                'long': 'Long',
                'short': 'Short',
            }

            if type_str in boxing:
                type_str = boxing[type_str]
            static_statement_arr.append(static_cache_template.format(param_type=type_str, 
                                                                     param_num=str(i), 
                                                                     fetching_length=self.total_testcases))

        static_statement = "".join(static_statement_arr)
        return static_statement

    def __gen_cpp_static(self, offset):
        raise NotImplementedError

    def __gen_py_static(self, offset):
        raise NotImplementedError
