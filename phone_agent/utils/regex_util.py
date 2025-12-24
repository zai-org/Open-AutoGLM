import re

def escape_inner_quotes(expr: str) -> str:
    """
    解析指令字符串，转义 value 内部嵌套的、未转义的双引号。
    使用正向断言确保只匹配真正的结构化引号。
    """
    def repl(match):
        key = match.group(1)
        val = match.group(2)
        # 核心修复：把 value 内部「前面没有斜杠」的双引号加上斜杠
        # 比如：把 [输入了""] 变成 [输入了\"\"]
        fixed_val = re.sub(r'(?<!\\)"', r'\\"', val)
        return f'{key}="{fixed_val}"'

    # 优化后的正则表达式：
    # (\w+)\s*=\s* : 匹配 key 和等号
    # "([\s\S]*?)" : 匹配 value（非贪婪模式）
    # (?=\s*[,)])   : 【重要】正向肯定断言，要求引号后面必须紧跟逗号或右括号
    pattern = re.compile(r'(\w+)\s*=\s*"([\s\S]*?)"(?=\s*[,)])', re.DOTALL)
    return pattern.sub(repl, expr)