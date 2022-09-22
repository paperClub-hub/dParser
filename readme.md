

## dParser

- 关系解析: 基于ddparser进行了改写和重构，可以自定义行业领域词。

- 版本依赖：
    - paddlepaddle: >=2.0 (pip install paddlepaddle )
    - lac: >=2.1 (pip install lac )
    - networkx



- 使用：

~~~
from dparser import DDParser
from dparser.dextract import *

text = '三室一厅的毛坯房，108平米，装修预算40万，希望主卧独卫，客厅放L形沙发，厨房干湿分离，餐厅为红木餐桌。'

ddp_res = ddp.parse(text)
fine_info = FineGrainedInfo(ddp_res[0])
out = [tuple(filter(lambda i:i !=None, x[:-1][0])) for x in fine_info.parse()]


print(f"输入：{text}")
print("解析结果：")
for x in out:
    print(f" --- {x}")
~~~

- 示例：
~~~

输入：三室一厅的毛坯房，108平米，装修预算40万，希望主卧独卫，客厅放L形沙发，厨房干湿分离，餐厅为红木餐桌。

解析结果：
 --- ('三室一厅', '毛坯房')
 --- ('毛坯房', '108平米')
 --- ('装修', '预算')
 --- ('预算', '40万')
 --- ('希望', '独卫')
 --- ('主卧', '独卫')
 --- ('客厅', '放', '沙发')
 --- ('L形', '沙发')
 --- ('厨房', '分离')
 --- ('干湿', '分离')
 --- ('餐厅', '为', '木餐桌')
 --- ('红', '木餐桌')

~~~


