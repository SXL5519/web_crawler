from db_file import DB
from yunying_tongji import test_tongji
from bson.objectid import ObjectId

class test_shop_tongji():
    """
    测试商家后台首页数据统计
    """
    def select_shop_id(self,storeName):
        """
        查询商家ID
        :return:
        """
        store_id={"storeName" : storeName}
        return store_id
    def sql_s(self,start_data,end_tata,n,store_id):
        """
        所需要的sql集
        :return: 相应的sql
        """
        ###商家在相应时间有效订单（未排除退货订单）（tb_order_detail）
        profit=[{'$lookup':{'from': "tb_order",'localField': "order",'foreignField': "_id",'as': "orders"}},{'$unwind': '$orders'},
                             {'$match':{'$and':[{'$or':[{"orders.orderStatus": "ORDER_FINISH"},
                             {"orders.orderStatus": "ORDER_WAIT_DELIVER"},
                             {"orders.orderStatus": "ORDER_WAIT_RECEIVE"}]}, {"orders.orderTime":
                             {'$gte': start_data}},{"orders.orderTime": {'$lte': end_tata}},
                             {"orders.supplier":ObjectId("5b4edd8d0b06ca10e99ec625")}]}}]

        ####商家在相应时间内退货成功数据（tb_return_apply）
        refund=[{'$lookup': {'from': "tb_order_detail",'localField': "orderDetail",'foreignField': "_id",'as': "orderDetail"}},
                             {'$unwind': '$orderDetail'},{'$lookup': {'from': "tb_order",'localField': "orderDetail.order",'foreignField': "_id",'as': "orders"}},
                             {'$unwind': '$orders'},{'$match': {'$and':[
                             {'orders.orderTime': {'$gte': start_data}},
                             {'orders.orderTime': {'$lte': end_tata}},{'statusList.status': "FINISHED"},
                             {'statusList.time': {'$gte': start_data}},
                             {'statusList.time': {'$lte': end_tata}},
                             {"orders.supplier" :ObjectId("5b4edd8d0b06ca10e99ec625")}]}}]
            #####销售金额（流水）
        sales_amount=[{'$match':{'$and':[{"orderTime":{'$gte':start_data}},{"orderTime":{'$lte':end_tata}},
                      {"supplier" :ObjectId(store_id)}]}},
                      {'$group':{'_id':'销售总额','total':{'$sum':'$totalPrice'},'transPrice':{'$sum':'$transPrice'}}}]

        #####销售总金额（所有）
        sales_amount_all=[{'$match':{"supplier" :ObjectId(store_id)}},
                      {'$group':{'_id':'销售总额','total':{'$sum':'$totalPrice'},'transPrice':{'$sum':'$transPrice'}}}]
        ###今日订单数量
        order_nu={'$and':[{'$or':[{"orderStatus":"ORDER_FINISH"},
                {"orderStatus":"ORDER_WAIT_DELIVER"},{"orderStatus":"ORDER_WAIT_RECEIVE"}]},
                {"orderTime":{'$gte':start_data}},{"orderTime":{'$lte':end_tata}},{"supplier" :ObjectId(store_id)}]}
        ###所有订单
        all_order_nu={'$and':[{'$or':[{"orderStatus":"ORDER_FINISH"},
                {"orderStatus":"ORDER_WAIT_DELIVER"},{"orderStatus":"ORDER_WAIT_RECEIVE"}]},{"supplier" :ObjectId(store_id)}]}

        ###今日发放红包
        red_page=[{'$lookup':{'from': "tb_order_detail",'localField': "orderDetail",'foreignField': "_id",'as': "orderDetail"}},{'$unwind': '$orderDetail'},
                             {'$lookup':{'from': "tb_order",'localField': "orderDetail.order",'foreignField': "_id",'as': "order"}},{'$unwind': '$order'},
                             {'$match':{'$and':[{'$or':[{"status": "ACCOUNTED"},{"status": "FROZEN_ING"},{"status": "WAIT_SHARE"}]},
                             {"obtainTime":{'$gte': start_data}},{"obtainTime": {'$lte': end_tata}},{"order.supplier" :ObjectId(store_id)}]}},
                             {'$group':{'_id':'销售总额','sum_money':{'$sum':'$money'}}}]

        #######粮票规则总余额
        remainMoney=[{'$match':{'$and':[{"merchant" :ObjectId(store_id)},{"isdelete" : False}]}},
                     {'$group':{'_id':'粮票总余额','total':{'$sum':'$remainMoney'}}}]
        if n==1:
            return profit
        if n==2:
            return refund
        if n==3:
            return sales_amount
        if n==4:
            return sales_amount_all
        if n==5:
            return order_nu
        if n==6:
            return all_order_nu
        if n==7:
            return red_page
        if n==8:
            return remainMoney
    def execute_sql(self,n,nu,name):
        self.profit_s = 0##总利润
        self.refund=0##退货利润
        self.transPrice=0#运费
        self.isReturnTransFee=''###是否退运费
        database = DB()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        tongji =test_tongji()
        db_profit = database.connect_mongodb_all('tb_order_detail',2,
                                                self.sql_s( tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1],1,store_id))

        for i in db_profit:
            costPrice=float(str(i.get('costPrice')))##成本价
            totalPrice=float(str(i.get('totalPrice')))###售价
            count=int(i.get('count'))
            self.profit_s=self.profit_s+count*(totalPrice-costPrice)
        print(self.profit_s)
        db_refund=database.connect_mongodb_all('tb_return_apply',2,
                                                self.sql_s( tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1],2,store_id))
        for j in db_refund:
            refund_costPrice=float(str(j.get('orderDetail').get('costPrice')))
            refund_totalPrice=float(str(j.get('orderDetail').get('totalPrice')))
            refund_count=int(j.get('orderDetail').get('count'))
            self.transPrice = float(str(j.get('orders').get('transPrice')))
            self.isReturnTransFee=str(j.get('isReturnTransFee'))

            if self.isReturnTransFee == 'true':
                self.refund = self.refund + refund_count * (refund_totalPrice - refund_costPrice)
            else: ##单类商品退货后的利润-运费
                self.refund = self.refund + refund_count * (refund_totalPrice - refund_costPrice)-self.transPrice
        profit = self.profit_s - abs(self.refund) ###利润
        print(self.refund)
        print('运费：%.2f'%self.transPrice)
        print('利润为:%.2f'%profit)
    def count_sales_amount(self,n,nu,name):
        """
        统计销售总额
        :return:
        """
        self.total=0
        self.transPrice=0
        database = DB()
        tongji = test_tongji()
        store=database.connect_mongodb_all('tb_merchant',1,self.select_shop_id(name))
        store_id=store.get('_id')
        sales_amount = database.connect_mongodb_all('tb_order',2,
                                                 self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 3,store_id))
        for i in sales_amount:
            self.total=float(str(i.get('total')))##订单总额
            self.transPrice=float(str(i.get('transPrice')))###运费总额
        sales_amounts=self.total+self.transPrice
        print('%d天销售总额：%.2f'%(nu,sales_amounts))

    def count_sales_amount_all(self,n,nu,name):
        """
        统计所有的销售额
        :return:
        """
        self.total = 0
        self.transPrice = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        sales_amount_all=database.connect_mongodb_all('tb_order',2,
                                                 self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 4,store_id))
        for i in sales_amount_all:
            self.total=float(str(i.get('total')))##订单总额
            self.transPrice=float(str(i.get('transPrice')))###运费总额
        sales_amounts_all=self.total+self.transPrice
        print('累计销售额：%.2f'%sales_amounts_all)

    def count_order_nu(self,n,nu,name):
        """
        统计订单总数
        :return:
        """
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        order_nu = database.connect_mongodb_all('tb_order', 3,
                                                        self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1],5, store_id))
        print(order_nu)
        print('%d天订单数：%d'%(nu,order_nu))

    def count_all_order_nu(self,n,nu,name):
        """
        统计所有订单数
        :param n:
        :param nu:
        :return:
        """
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        order_nu = database.connect_mongodb_all('tb_order', 3,
                                                self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 6,
                                                           store_id))
        print(order_nu)
        print('%d天订单数：%d' % (nu, order_nu))

    def count_red_page_nu(self,n,nu,name):
        """
        统计当天发放的所有红包金额
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.red_page_nu=0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        red_page = database.connect_mongodb_all('tb_red_packet', 2,
                                                        self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1],7, store_id))
        for i in red_page:
            self.red_page_nu=float(str(i.get('sum_money')))
        print('%d天发放红包：%.2f'%(nu,self.red_page_nu))

    def count_remainMoney(self,n,nu,name):
        """
        统计商家粮票规则剩余总金额
        :param nu:
        :param name:
        :return:
        """
        self.remainMoneys = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        rMoneys = database.connect_mongodb_all('view_adfee', 2,
                                                self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 8,
                                                           store_id))
        for i in rMoneys:
            self.remainMoneys = float(str(i.get('total')))
        print('规则剩余红包金额：%.2f' % (self.remainMoneys))

    def store_money(self,name):
        """
        统计商家钱包余额
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.store_moneys=0
        database = DB()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        self.store_moneys=float(str(store.get('money')))
        print('商家余额为:%.2f'%(self.store_moneys))

if __name__ == "__main__":
    name='惠宜家艾家（恒大中央公园店）'
    a=test_shop_tongji()
    # a.execute_sql(1,10)
    ####今日销售额
    a.count_sales_amount(0,1,name)
    ####商家累计销售总额
    a.count_sales_amount_all(0,1,name)
    ####今日商家订单数
    a.count_order_nu(0,1,name)
    ###统计商家所有订单数
    a.count_all_order_nu(0,1,name)
    ###今日商家发放红包金额
    a.count_red_page_nu(0,1,name)
    ###商家粮票规则剩余红包金额
    a.count_remainMoney(0,1,name)
    #####商家余额
    a.store_money(name)