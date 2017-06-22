# 这是一个失败了的项目

## OVERVIEW

我最近学了一下scrapy，想写个爬虫之类的练练手，加上一直接触的网站就是leetcode，就有了写一个关于leetcode的项目的念头。

这个项目的意图很简单，做一个单机版的leetcode，希望支持的功能（只针对无锁题目）：

* 有所有leetcode.com的test case，能够在本地验证用户算法的正确性，和leetcode具有同样的功能。支持cpp，java，python三种语言。
 
* 有新题目出现的时候，可以通过简单的命令实现全自动的本地更新，也就是得到新题的内容以及test case。

* 其他的一些服务性质的功能，比如和用户已经提交过的leetcode代码同步，还有从本地直接向lc提交代码并取得返回结果。

##APPROACH

普遍情况来说，lc每次都会生成一个Solution的instance，然后调用它的算法入口，输入case，判断输出。

**方案一：**

	提交错误答案，lc会返回错误的case以及正确结果，那么我只需要把正确结果记录下来，每次针对case返回结果即可。但是这个做法只在脑子里存活了十几秒就被否决了，
	第一，submit的次数会过多，不道德，并且几千个case就是几万秒，太久了；
	第二，output有时候会非常大，如果每次都以string的形式把output给submit过去，可能会超过lc的输入字符上限（猜测）；
	第三，有些题目的case并不是可以做比较的，比如有些设计题就不行

**方案二（使用）：**

	利用静态变量，在方程被调用的时候一边计数一边记录输入的case（TreeNode就serialize一下），当计数到最后一个case的时候，print出当前记录的所有的case，抛出错误答案，迫使程序停下来，lc服务器会返回std_out，也就是print出的case。
	这个方案是我使用的方案，但是最后我发现这个方案也不能解决所有的问题。
	
既然需要记录case，那么我就需要能够通过所有case的solution，这个solution从哪里来？我google了几个小时之后表示并没有人提供完整的答案，lc一周更新3-5道题，没有人可以提供稳定的正确解。所以最终确定的路线是：

**scrapy爬到题目 ---> 去leetcode的discuss区域爬取solution ---> 验证正确的solution，生成记录的case的代码，插入到正确的solution里面 ---> 提交solution，获得case**

## IMPLEMENTATION

本来我以为大概也就是个小的python的程序，结果发现要实现的逻辑远远超过我的想象。

### solutions_spider.py
第一个实现的文件是solutions_spider.py，这是在scrapy框架下运行的一个爬虫，它先会在lc首页弄到所有question的meta data，meta里面会有每一道题的id、name、url，在question对应的url里面可以找到它的description，已经所有语言的default code，也就是平时在leetcode.com上面看到的```class Solution {} ```初始化代码。
我通过抓包看到了一些lc的api，在不登陆的情况下可以得到的信息：题目的介绍，题目的discuss里面的topics。这两个信息是爬虫所需要得到的。

### questionmeta.py 
这个文件是用来维持得到的meta信息的，因为meta信息在几乎在任何一个module里面都会用到，所以在这里把它封装一下。

### questioncontent.py
这个文件用来维持question的description和default code，最麻烦的事情是处理编码问题，也可能是我对python的编码处理包不熟悉，写起来很麻烦，从web上弄来的字符串编码总是很蛋疼。

### questionsolutionservice.py
从讨论区得到topic之后，可以分析topic里面的post得到\<code\>tag里面的代码，简单的根据pl分类，大概判断一下答案code是否可用，这些全是hard code进去的，主要也是用来维持data，提供接口给其他的文件使用。里面的方法基本上都是static或者class方法，因为我不想把几百个文件一次性加载到内存里（其实就是强迫症，这几百个文件也没多大）。

### user.py
经过抓包得到了lc关于提交代码的api，提交代码的过程大概是：向题目对应的url提交post请求，如果没有cookie之类的错误，lc会返回对应的submission\_id，拿到这个id就可以反复的check submission的结果，结果会以status\_code的形式描述，大概分成wrong answer，time limit exeeded，runtime error，accepted等结果。User类的instance可以维持一个session，可以模拟用户登录或者提交代码、查看结果。

### usermanager.py
用来封装User instance的行为，因为lc在服务器端会检查同一个lc账号的提交次数，11s之内重复提交很大概率会被驳回，而且提交的代码也是需要其他的module管理的，所以封装user的行为很重要。因为question有500+，在这里我申请了十个账号多线程提交从discuss里面爬下来的代码，manager也有责任控制多个user的提交行为。

### verifiedsolutionservice.py
这个文件里的类是用来维持通过user提交成功的代码的，我写到这里的时候已经有点烦了，加上之前没有写文档，接口名字写的乱七八糟，同时它也维持modified\_code，也就是插入了爬取case代码的solution，可能是我写的最垃圾的类了。

### codegen.py
这个文件的类是用来生成对应id的题目的test case爬取代码的，它被VerifiedSolutionService直接使用，这个类我写了一个下午，最后惊奇的发现我的代码很像lisp，突然领悟了functional的魅力，下面是核心代码：

```
func_body = 
	func_body.format(self.__body(
                        self.__printer(
                            self.__printer_body(
                                self.__formatter(
                                    self.__sub_printer(
                                        self.__recur_printer
                                                        ))))))
```
我只实现了java的生成器，生成的代码可以把input按照一定的格式print到stdout里面，经过解析就可以实现自动输入case。

### syntaxparser.py
语法分析器用来分析default code的代码，分析出input 和 output type，以及input的变量名，从而可以交给CodeGenerator来生成目标代码，type都是以树的形式记录的，因为lc上输入的数据结构比较有限，所以TypeTree也就不是很难写，也就处理了一点情况，甚至可以同时处理java和cpp的type，python不存在type，也就没有对应的TypeTree。

## ISSUES
* 以上的代码写完之后，基本可以拿到90%题目的test case，但是依旧没有办法实现完全的自动化。
最大的问题就是design的题目，lc在做design题目的测试的时候，对每个case它都会生成一个你的solution的object，然后按照一定的顺序调用你写的方法，这个顺序是因case而异的，无法确定，也就意味着我不知道该什么时候抛出错误使程序停止，这个是我程序无法完成的原因。

* 还有就是只有一个方法的类我可以确定test case一定会以这个方法为入口来跑case，但是多个方法这就不明确了，我的CodeGenerator支持对多个方法的类的每个方法都插入监视代码，但是不支持记录每个方程的调用顺序，记录调用顺序不是不可解，改动codegen.py即可。

* 最后一点，我的codegen只支持java，虽然几乎每一道lc的题目都可以在discuss里面找到java解，但是这并不确定，如果同时再支持cpp和python解那么就基本可以确定能够拿到答案了，但是再支持另外两种语言还需要很大的工作量，更不要说最后还需要实现自动输入case、自动验证用户代码的正确性，工作量非常大，这个虽然没有第一个issue严重，但是它的工作量也足够让我这种菜狗停止敲代码了。


 
