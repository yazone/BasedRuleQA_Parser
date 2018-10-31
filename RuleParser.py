
TOKEN_TYPE_SELECT_LIB = 'LIB'
TOKEN_TYPE_SELECT_FULL = 'FULL'

class RuleNode:
    def __init__(self,value,token_type=TOKEN_TYPE_SELECT_FULL):
        self.parent = []
        self.children = []
        self.value = value
        self.rule_type = token_type
        #print("value is :"+self.value+" type is :"+token_type)
        
    def add_children(self,node):
        self.children.append(node)

    def set_childrens(self,nodes):
        self.children = nodes

    def get_childrens(self):
        return self.children

    def get_value(self):
        return self.value

    def get_type(self):
        return self.rule_type

    def __str__(self):
        return str(self.value)+"("+self.rule_type+")"

class RuleGraph:
    def __init__(self):
        self.root_node = RuleNode('Root')

    def add_children_node(self,parent_node,node):
        if parent_node == None:
            self.root_node.add_children(node)
        else:
            parent_node.add_children(node)
            print(parent_node.get_childrens())
        print(str(parent_node)+"==>"+str(node))

    def get_childrens(self,parent_node):
        return parent_node.get_childrens()

    def set_childrens(self,current_node,children_nodes):
        current_node.set_childrens(children_nodes)

    def get_root_node(self):
        return self.root_node

    def travel(self,parent_node):
        if parent_node == None:
            parent_node = self.root_node.get_childrens()[0]
        
        print(parent_node)
        #print(parent_node.get_childrens())
        childrens = parent_node.get_childrens()
        for children in childrens:
            ret = self.travel(children)
            if ret == True:
                return True

        return False
        
        
class RuleParser:
    def __init__(self):
        self.rule_graph = RuleGraph()
        self.keywords = []
        self.keywords_postion = []
        self.lib_names = []
        self.nodes_path = []
        self.match_lib_hook = None
        self.match_lib_hook_parms = None
        self.DEBUG_FLAG = False

    def set_debug(self,flag):
        self.DEBUG_FLAG = flag

    """
        设置外部库查询函数
    """
    def set_match_lib_hook(self,hook_method,hook_params):
        self.match_lib_hook = hook_method
        self.match_lib_hook_parms = hook_params

    """
        内置知识库实现
    """
    def hook_lib_default(self,match_string,lib_name):
        if self.DEBUG_FLAG:
            print("hook_lib_default 库中查找，库名："+lib_name+" 查找实体："+match_string)
        
        matched_strings = []

        if lib_name == 'sys.任意文本':
            matched_strings.append('')
            for i in range(len(match_string)):
                search_string = match_string[:i+1]
                matched_strings.append(search_string)
        
        if self.DEBUG_FLAG:
            print("匹配到的词典："+str(matched_strings))
        return matched_strings

    """
        匹配库
    """
    def match_lib(self,match_string,lib_name):
        if lib_name.startswith('sys.'):
            return self.hook_lib_default(match_string,lib_name)
        
        if self.match_lib_hook != None:
            return self.match_lib_hook(match_string,lib_name,self.match_lib_hook_parms)

    def travel(self):
        self.rule_graph.travel(None)
    
    # 解析规则
    def parse(self,question_rule):
        self.keywords = []
        self.keywords_postion = []
        self.lib_names = []
        self.nodes_path = []

        token_tmp_setence = ''
        token_sharp_start_flag = False
        token_parentheses_count = 0
        token_bracket_count = 0
        current_nodes = [self.rule_graph.get_root_node()]

        for i in range(len(question_rule)):
            token = question_rule[i]
            # 开始子句
            if token_parentheses_count > 0:
                if token == ')':
                    token_parentheses_count -= 1
                    if token_parentheses_count == 0:
                        sub_tokens = token_tmp_setence.split('|')
                        token_tmp_setence = ''
                        rule_nodes = []
                        
                        for sub_token in sub_tokens:
                            rule_node = None
                            if sub_token.startswith('#'):
                                rule_node = RuleNode(sub_token[1:-1],TOKEN_TYPE_SELECT_LIB)
                            else:
                                rule_node = RuleNode(sub_token,TOKEN_TYPE_SELECT_FULL)
                            rule_nodes.append(rule_node)

                        for current_node in current_nodes:
                            # current_node.set_childrens(rule_nodes)
                            self.rule_graph.set_childrens(current_node,rule_nodes)
                        
                        current_nodes = rule_nodes
                        continue
            elif token_bracket_count > 0:
                if token == ']':
                    token_bracket_count -= 1
                    if token_bracket_count == 0:
                        sub_tokens = token_tmp_setence.split('|')
                        token_tmp_setence = ''
                        rule_nodes = []
                        rule_node = RuleNode('',TOKEN_TYPE_SELECT_FULL)
                        rule_nodes.append(rule_node)
                        for sub_token in sub_tokens:
                            rule_node = None
                            if sub_token.startswith('#'):
                                rule_node = RuleNode(sub_token[1:-1],TOKEN_TYPE_SELECT_LIB)
                            else:
                                rule_node = RuleNode(sub_token,TOKEN_TYPE_SELECT_FULL)
                            rule_nodes.append(rule_node)
                        for current_node in current_nodes:
                            # current_node.set_childrens(rule_nodes)
                            self.rule_graph.set_childrens(current_node,rule_nodes)
                        current_nodes = rule_nodes
                        continue
            else:
                if token == '#':
                    if token_sharp_start_flag == True: # ‘#’结束
                        token_sharp_start_flag = False
                        rule_node = RuleNode(token_tmp_setence,TOKEN_TYPE_SELECT_LIB)
                        token_tmp_setence = ''
                        rule_nodes = [rule_node]
                        for current_node in current_nodes:
                            # current_node.set_childrens(rule_nodes)
                            self.rule_graph.set_childrens(current_node,rule_nodes)
                        current_nodes = rule_nodes
                    else: # ‘#’开始
                        token_sharp_start_flag = True
                        if len(token_tmp_setence) > 0:
                            rule_node = RuleNode(token_tmp_setence,TOKEN_TYPE_SELECT_FULL)
                            token_tmp_setence = ''
                            rule_nodes = [rule_node]
                            for current_node in current_nodes:
                                # current_node.set_childrens(rule_nodes)
                                self.rule_graph.set_childrens(current_node,rule_nodes)
                            current_nodes = rule_nodes
                    continue

                if token == '}':
                    token_sharp_start_flag = False
                    rule_node = RuleNode(token_tmp_setence,TOKEN_TYPE_SELECT_LIB)
                    token_tmp_setence = ''
                    rule_nodes = [rule_node]
                    for current_node in current_nodes:
                        # current_node.set_childrens(rule_nodes)
                        self.rule_graph.set_childrens(current_node,rule_nodes)
                    current_nodes = rule_nodes
                    continue

                if token == '{':
                    if len(token_tmp_setence) > 0:
                        rule_node = RuleNode(token_tmp_setence,TOKEN_TYPE_SELECT_FULL)
                        token_tmp_setence = ''
                        rule_nodes = [rule_node]
                        for current_node in current_nodes:
                            # current_node.set_childrens(rule_nodes)
                            self.rule_graph.set_childrens(current_node,rule_nodes)
                        current_nodes = rule_nodes
                    continue

                if token == '(':
                    token_parentheses_count += 1
                    if len(token_tmp_setence) > 0:
                        rule_node = RuleNode(token_tmp_setence,TOKEN_TYPE_SELECT_FULL)
                        token_tmp_setence = ''
                        rule_nodes = [rule_node]
                        for current_node in current_nodes:
                            # current_node.set_childrens(rule_nodes)
                            self.rule_graph.set_childrens(current_node,rule_nodes)
                        current_nodes = rule_nodes
                    continue

                if token == '[':
                    token_bracket_count += 1
                    if len(token_tmp_setence) > 0:
                        rule_node = RuleNode(token_tmp_setence,TOKEN_TYPE_SELECT_FULL)
                        token_tmp_setence = ''
                        rule_nodes = [rule_node]
                        for current_node in current_nodes:
                            # current_node.set_childrens(rule_nodes)
                            self.rule_graph.set_childrens(current_node,rule_nodes)
                        current_nodes = rule_nodes
                    continue
                
            token_tmp_setence = token_tmp_setence + token
            
            if i == len(question_rule) - 1:
                rule_node = RuleNode(token_tmp_setence,TOKEN_TYPE_SELECT_FULL)
                token_tmp_setence = ''
                rule_nodes = [rule_node]
                for current_node in current_nodes:
                    # current_node.set_childrens(rule_nodes)
                    self.rule_graph.set_childrens(current_node,rule_nodes)
                current_nodes = rule_nodes
        

    """
        处理文本类型节点
    """
    def real_match_process_fulltext(self,current_node,match_string,match_string_start_pos):
        # 当前节点信息
        current_node_value = current_node.get_value()
        current_node_type = current_node.get_type()
        if self.DEBUG_FLAG:
            print("real_match_process_fulltext 当前节点，值："+current_node_value+" 类型："+current_node_type)

        # 没匹配到节点文本，返回匹配失败，同时删除该节点路径记录
        if not match_string.startswith(current_node_value):
            node_pop = self.nodes_path.pop()
            if self.DEBUG_FLAG:
                print("real_match_process_fulltext 文本未匹配，节点路径，弹出:"+str(node_pop))
            return False

        # 接下来匹配的字符串
        current_node_value_len = len(current_node_value)
        next_match_string_start_pos = match_string_start_pos + current_node_value_len
        next_match_string = match_string[current_node_value_len:]
        # 获取子节点
        childrens = current_node.get_childrens()

        # 如果接下来的匹配的字符串为空（全部匹配完成）并且子节点匹配完成了，返回匹配成功
        if next_match_string == '' and len(childrens) == 0:
            if self.DEBUG_FLAG:
                print("real_match_process_fulltext 文本与节点完全匹配了")
            return True
        
        if self.DEBUG_FLAG:
            print("real_match_process_fulltext 需要匹配子句："+next_match_string + "子节点数："+str(len(childrens)))
        
        # 匹配文本与子节点，深度优先递归
        for children in childrens:
            ret = self.real_match(children,next_match_string,next_match_string_start_pos)
            if ret == True:
                if self.DEBUG_FLAG:
                    print("real_match_process_fulltext 子句匹配成功："+next_match_string)
                match_string_start_pos = next_match_string_start_pos
                return True

        if self.DEBUG_FLAG:
            print("real_match_process_fulltext 子句匹配失败："+next_match_string)

        # 没有一个子节点匹配到了文本
        node_pop = self.nodes_path.pop()
        if self.DEBUG_FLAG:
            print("real_match_process_fulltext 节点路径，弹出:"+str(node_pop))
        
        return False

    """
        处理库类型节点
    """
    def real_match_process_lib(self,current_node,match_string,match_string_start_pos):
        # 当前节点信息
        current_node_value = current_node.get_value()
        current_node_type = current_node.get_type()
        if self.DEBUG_FLAG:
            print("real_match_process_lib 当前节点，值："+current_node_value+" 类型："+current_node_type + "匹配文本："+match_string)

        # 匹配词库
        matched_strings =self.match_lib(match_string,current_node_value)
        if self.DEBUG_FLAG:
            print("real_match_process_lib 匹配到的词库数组："+str(matched_strings))

        # 没有匹配到词典
        if len(matched_strings) == 0:
            if self.DEBUG_FLAG:
                print("real_match_process_lib 句子没有匹配到词典："+match_string)
            node_pop = self.nodes_path.pop()
            if self.DEBUG_FLAG:
                print("real_match_process_lib 节点路径，弹出:"+str(node_pop))
            return False

        # 遍历匹配到的词库数组，对每一条进行下一个节点的分析
        for matched_string in matched_strings:
            if self.DEBUG_FLAG:
                print("real_match_process_lib 处理知识库词条："+matched_string+ " 匹配语句："+match_string)
            # 作为关键词记录，作为抽取关键词
            self.keywords.append(matched_string)
            matched_string_len = len(matched_string)
            self.keywords_postion.append((match_string_start_pos,matched_string_len))
            # 记录当前库名，作为抽取库
            self.lib_names.append(current_node_value)
            # 下一个需要处理的字句
            next_match_string_start_pos = match_string_start_pos + matched_string_len
            next_match_string = match_string[matched_string_len:]
            # 获取子节点
            childrens = current_node.get_childrens()
            
            # 如果接下来的匹配的字符串为空（全部匹配完成）并且子节点匹配完成了，返回匹配成功
            if next_match_string == '' and len(childrens) == 0:
                if self.DEBUG_FLAG:
                    print("real_match_process_lib 文本与节点完全匹配了")
                return True
            
            # 匹配文本与子节点，深度优先递归
            for children in childrens:
                ret = self.real_match(children,next_match_string,next_match_string_start_pos)
                if ret == True:
                    if self.DEBUG_FLAG:
                        print("real_match_process_lib 子句匹配成功："+next_match_string)
                    match_string_start_pos = next_match_string_start_pos
                    return True
            
            # 当前词条无法进行下一个节点，需要弹出关键词以及知识库名称，不做记录
            keyword = self.keywords.pop()
            lib_name = self.lib_names.pop()
            self.keywords_postion.pop()
            if self.DEBUG_FLAG:
                print("pop出关键词："+keyword+" keywords:"+str(self.keywords) + " pop出库名："+lib_name+" lib:"+str(self.lib_names))

        # 没有一个子节点匹配到了文本
        node_pop = self.nodes_path.pop()
        if self.DEBUG_FLAG:
            print("real_match_process_lib 节点路径，弹出:"+str(node_pop))
        
        return False
        
    
    """
        匹配文本与节点
    """
    def real_match(self,current_node,match_string,match_string_start_pos):
        # 默认从Root节点的子节点开始
        if current_node == None:
            root_childrens = self.rule_graph.get_root_node().get_childrens()
            if len(root_childrens) == 0:
                if self.DEBUG_FLAG:
                    print("real_match ROOT节点没有子节点")
                return False
            current_node = self.rule_graph.get_root_node().get_childrens()[0]
        
        # 当前节点信息
        current_node_value = current_node.get_value()
        current_node_type = current_node.get_type()
        if self.DEBUG_FLAG:
            print("real_match 当前节点，值："+current_node_value+" 类型："+current_node_type)

        # 记录节点路径
        self.nodes_path.append(current_node)
        if self.DEBUG_FLAG:
            print("real_match 节点路径，添加:"+str(current_node))

        # 处理节点
        if current_node_type == TOKEN_TYPE_SELECT_FULL: # 处理全匹配字段
            return self.real_match_process_fulltext(current_node,match_string,match_string_start_pos)
        elif current_node_type == TOKEN_TYPE_SELECT_LIB: # 处理库中查找字段
            return self.real_match_process_lib(current_node,match_string,match_string_start_pos)

        return False

    """
        匹配字符串
    """
    def match(self,match_string):
        self.match_string_start_pos = 0
        self.keywords = []
        self.keywords_postion = []
        self.lib_names = []
        self.nodes_path = []
        ret = self.real_match(None,match_string,0)
        return ret,self.keywords,self.keywords_postion,self.lib_names,self.nodes_path

