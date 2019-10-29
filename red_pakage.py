from db_file import DB
from yunying_tongji import test_tongji
from bson.objectid import ObjectId


class redpacket():
    """红包池运营后台促销统计"""

    def  total_amount(self):
        """
        普奖奖池总额
        :return:
        """
        self.total_money=0  ###所有规则总额
        self.del_total_money=0  ###删除规则剩余金额
        sum=[{'$group':{'_id':'金额总额','total':{'$sum':"$money"}}}]
        del_sum=[{'$match':{"isDelete" :True}},{'$group':{'_id':'删除规则总额','total':{'$sum':"$remainMoney"}}}]

        database = DB()
        ol=database.connect_mongodb_all('tb_redpond', 2,sum)
        print(ol)
        for i in ol:
            self.total_money=float(str(i.get('total')))##
            print(self.total_amount)
        del_ol=database.connect_mongodb_all('tb_redpond', 2,del_sum)
        for j in del_ol:
            self.del_total_money=float(str(j.get('total')))

        total=self.total_money-self.del_total_money
        print('普奖奖池总额：%.2f'%total)


if __name__ == "__main__":

    a=redpacket()
    a.total_amount()