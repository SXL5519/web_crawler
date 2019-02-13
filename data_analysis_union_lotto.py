"""
通过pandas分析CSV文件数据
"""
import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

"""
将CSV文件数据以ANSI的方式放到pandas的dataframe数据类型里
Pandas基于两种数据类型：series与dataframe;
series是一个一维的数据类型，其中每一个元素都有一个标签,标签可以是数字或者字符串
dataframe是一个二维的表结构,可以把它想象成一个series的字典项。
"""
##
df =pd.read_csv('./data_file/union_lotto.csv',header=0,encoding='ANSI')##header=0表示csv文件第一行为行名
print(df.head(3))###打印csv文件的前10行
print(df.tail(2))###打印CSV文件的后5行
##修改dataframe数据的列名
df.columns=['date','red_1','red_2','red_3','red_4','red_5','red_6','blue']
print(df.head(1))
print('行数'+str(len(df)))###打印csv文件数据行数，不计算列名行

pd.options.display.float_format='{:,.3f}'.format
print(df.describe())
# df.plot(x='date',title='双色球折线图')##画折线图
# plt.yticks(range(1,34))##改变折线图的X轴
# plt.xticks(range(1,34))##改变折线图的X轴
# plt.savefig('./data_file/'+str(int(time.time()))+'.png')##保存图片到指定路径
# # aa.plot(y='count',kind='bar')##画柱状图
# aa.plot.bar(y='count',title='柱状图')
# plt.savefig('./data_file/'+str(int(time.time()))+'.png')
# aa.to_csv('./data_file/union_lotto_1.csv')##保存到csv文件中
# plt.show()###直接显示图形，不保存图片

def pandas_data(path,n):
    df = pd.read_csv(path, header=0, encoding='ANSI')
    df_red = pd.Series(range(1, 34))
    # print((df_red.value_counts()-1).sort_index())
    if n ==0:
        df_red_1 = df.red_1.value_counts()
        df_red_2 = df.red_2.value_counts()
        df_red_3 = df.red_3.value_counts()
        df_red_4 = df.red_4.value_counts()
        df_red_5 = df.red_5.value_counts()
        df_red_6 = df.red_6.value_counts()
    else:
        df_red_1 = df.head(n).red_1.value_counts()
        df_red_2 = df.head(n).red_2.value_counts()
        df_red_3 = df.head(n).red_3.value_counts()
        df_red_4 = df.head(n).red_4.value_counts()
        df_red_5 = df.head(n).red_5.value_counts()
        df_red_6 = df.head(n).red_6.value_counts()
    df_red_1 = ((df_red.value_counts() - 1) + df_red_1).fillna(value=0)
    df_red_2 = ((df_red.value_counts() - 1) + df_red_2).fillna(value=0)
    df_red_3 = ((df_red.value_counts() - 1) + df_red_3).fillna(value=0)
    df_red_4 = ((df_red.value_counts() - 1) + df_red_4).fillna(value=0)
    df_red_5 = ((df_red.value_counts() - 1) + df_red_5).fillna(value=0)
    df_red_6 = ((df_red.value_counts() - 1) + df_red_6).fillna(value=0)
    df_red = (df_red_1 + df_red_2 + df_red_3 + df_red_4 + df_red_5 + df_red_6)
    dict_red__count = {'red': df_red.index, 'counts': df_red.values}
    df_red_count = pd.DataFrame(dict_red__count)
    df_red_count['counts']=df_red_count['counts'].astype(np.int64)###改变count列的数据类型为int
    # print(df_red_count)
    #df['列名'] = df['列名'].astype(np.int64)

    if n>0:
        n=str(n)
    else:
        n='所有'
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    df_red_count.plot(x='red', y='counts', title=n+'场折线图')#画折线图
    plt.xticks(range(1,len(df_red_count.red)+1))##改变折线图的X轴
    # plt.yticks(range(0,max(df_red_count.counts)+10,10))  ##改变折线图的y轴
    plt.savefig('./data_file/' + str(int(time.time())) + '.png')  ##保存图片到指定路径
    time.sleep(1)
    # df_red_count.plot(y='count',kind='bar')##画柱状图
    df_red_count.plot.bar(y='counts', title=n+'场柱状图')
    plt.savefig('./data_file/' + str(int(time.time())) + '.png')
    # plt.show()###直接显示图形，不保存图片
    # print(max(df_red_count.counts))
if __name__ == "__main__":
    pandas_data('./data_file/union_lotto.csv',100)

