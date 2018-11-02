from RuleParser import RuleParser

# 用词典可以快速匹配到
poet_names = {'李白':1,'李白冰':2,'杜甫':3}
poetry_names = {'将进酒':1,'沁园春':2}
poetry_sentences = {'黄河之水天上来':1,'海上升明月':2}

# 外部库查找实现
def hook_lib_method_impl(match_string,lib_name,params):
    #print("hook_lib_method_impl 库中查找，库名："+lib_name+" 查找句子："+match_string)
    # 传递参数测试
    assert(params=='HELLO')
    # 返回的关键词数组
    matched_strings = []
    current_database = None
    if lib_name == '诗人':
        current_database = poet_names
    elif lib_name == '诗名':
        current_database = poetry_names
    elif lib_name == '诗句':
        current_database = poetry_sentences
    else:
        # print("hook_lib_method_impl 未找到库，库名："+lib_name+" 查找句子："+match_string)
        return matched_strings

    for i in range(len(match_string)):
        search_string = match_string[:i+1]
        if search_string in current_database:
            # print("hook_lib_method_impl 匹配到库："+lib_name+" 关键词："+search_string+" match_string:"+match_string)
            matched_strings.append(search_string)
    
    # print("hook_lib_method_impl 库："+lib_name+" 全部匹配到的关键词："+str(matched_strings))
    return matched_strings


def test_sentence(rule_parser,sentence):
    success,keywords,keywords_pos,lib_names,nodes_path = rule_parser.match(sentence)
    if success:
        print("\n=================================================================")
        print("句子："+sentence)
        print("关键词："+str(keywords)+" \n关联库："+str(lib_names)+" \n位置："+str(keywords_pos))
        path_trace = ''
        for node in nodes_path:
            if path_trace == '':
                path_trace = str(node)
            else:
                path_trace += "-->"+str(node)
        print("节点路径："+path_trace)
        print("=================================================================\n")
    else:
        print("\n=================================================================")
        print("匹配失败:"+sentence)
        print("=================================================================\n")

if __name__ == '__main__':
    # 创建一个实例
    rule_parser = RuleParser()
    # 自定义词库匹配查询
    rule_parser.set_match_lib_hook(hook_lib_method_impl,"HELLO")
    # 解析规则
    rule = "#sys.任意文本##诗人#[的]#诗名#的(介绍|说明|#歌曲#)[啊|哦|#呵呵#|额]"
    print("解析规则："+rule)
    rule_parser.parse(rule)

    # 默认关闭，设为True打开
    rule_parser.set_debug(False)
    
    # 测试句子
    test_sentence(rule_parser,'李白的将进酒的介绍哦')
    test_sentence(rule_parser,'李白将进酒的介绍')
    test_sentence(rule_parser,'我请问李白冰将进酒的介绍')
    
    # ”李白是谁“不能命中
    test_sentence(rule_parser,'李白是谁')
    # 重置新规则
    rule = "#诗人#是谁"
    print("解析规则："+rule)
    rule_parser.parse(rule)
    # ”李白是谁“命中
    test_sentence(rule_parser,'李白是谁')

    # 加入内置数字测试
    rule = "[请问]#sys.数字#个人是什么字"
    print("解析规则："+rule)
    rule_parser.parse(rule)
    test_sentence(rule_parser,'三个人是什么字')
    test_sentence(rule_parser,'请问三个人是什么字')
    test_sentence(rule_parser,'请问十二个人是什么字')