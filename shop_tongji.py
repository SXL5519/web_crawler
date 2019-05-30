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
    def sql_s(self,start_data,end_tata,n,store_id,*orderStatus):
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
                             {"orders.supplier" :ObjectId(store_id)}]}}]
        #####销售金额（流水）
        sales_amount=[{'$match':{'$and':[{"orderTime":{'$gte':start_data}},
                        {"orderTime":{'$lte':end_tata}},
                        {"supplier" :store_id},
                        {"payTime":{'$ne':None}}]}},
                        {'$group':{'_id':'当日销售总额','total':{'$sum':'$totalPrice'},'transPrice':{'$sum':'$transPrice'}}}]

        #####销售总金额（所有）
        sales_amount_all=[{'$match':{'$and':[{"supplier" :ObjectId(store_id)},
                            {"payTime":{'$ne':None}}]}},
                            {'$group':{'_id':'销售总额','total':{'$sum':'$totalPrice'},'transPrice':{'$sum':'$transPrice'}}}]
        ###今日订单数量
        order_nu={'$and':[{"payTime":{'$ne':None}},
                {"orderTime":{'$gte':start_data}},{"orderTime":{'$lte':end_tata}},{"supplier" :ObjectId(store_id)}]}
        ###所有订单
        all_order_nu={'$and':[{"payTime":{'$ne':None}},{"supplier" :ObjectId(store_id)}]}

        ###今日发放红包
        red_page=[{'$lookup':{'from':"tb_red_packet",'localField':"_id",'foreignField': "adFeeRule",'as':"red_packet"}},{'$unwind': '$red_packet'},
                           {'$match':{'$and':[{"merchant" : ObjectId(store_id)},
                           {"red_packet.obtainTime":{'$gte': start_data}},
                           {"red_packet.obtainTime": {'$lte':end_tata}}]}},
                           {'$group':{'_id':'今日红包发放总额','sum_money':{'$sum':'$red_packet.money'}}}]

        #######粮票规则总余额
        remainMoney=[{'$match':{'$and':[{"merchant" :ObjectId(store_id)},{"isdelete" : False}]}},
                     {'$group':{'_id':'粮票总余额','total':{'$sum':'$remainMoney'}}}]
        ######今日待处理
        pending_order={'$and':[{"orderStatus" : orderStatus},{"supplier" : ObjectId(store_id)}]}
        ####待处理退款
        Pending_refund=[{'$lookup':{'from':"tb_order",'localField':"order",'foreignField': "_id",'as': "order"}},{'$unwind': '$order'},
                        {'$match':{'$and':[{"type" : "RETURN_MONEY"},{"status" : "WAIT_HANDLE"},
                        {'order.supplier':ObjectId(store_id)}]}},
                        {'$group':{'_id':'','number':{'$sum':1}}}]
        ###待处理退货
        Pending_return=[{'$lookup':{'from':"tb_order_detail",'localField':"orderDetail",'foreignField': "_id",'as': "orderDetail"}},{'$unwind': '$orderDetail'},
                        {'$lookup':{'from':"tb_order",'localField':"orderDetail.order",'foreignField': "_id",'as': "order"}},{'$unwind': '$order'},
                        {'$match':{'$and':[{"type" : "RETURN_GOODS"},{"status" : "WAIT_HANDLE"},{'order.supplier':ObjectId(store_id)}]}},
                        {'$group':{'_id':'','number':{'$sum':1}}}]

        ###待确认退货
        return_confirmed=[{'$lookup':{'from':"tb_order_detail",'localField':"orderDetail",'foreignField': "_id",'as': "orderDetail"}},{'$unwind':'$orderDetail'},
                            {'$lookup':{'from':"tb_order",'localField':"orderDetail.order",'foreignField': "_id",'as': "order"}},{'$unwind': '$order'},
                              {'$match':{'$and':[{'$or':[{"status" : "ACCEPTED"},]},{"type" :"RETURN_GOODS"},{'order.supplier':ObjectId(store_id)}]}},
                              {'$group':{'_id':'待确认退货订单数','number':{'$sum':1}}}]

        #####累计用户数
        shop_user=[{'$match':{'$and':[{'$or':[{"orderStatus":"ORDER_FINISH"},{"orderStatus":"ORDER_WAIT_DELIVER"},{"orderStatus":"ORDER_WAIT_RECEIVE"}]},
                   {"supplier" : ObjectId(store_id)}]}},{'$group':{"_id":'$customer'}},{'$count':'countNum'}]

        # shop_user=[{'$match':{'$and':[{"supplier" :ObjectId(store_id)}]}},{'$group':{"_id":'$customer'}},{'$count':'countNum'}]

        #####复购用户数
        more_user=[{'$match':{'$and':[{'$or':[{"orderStatus":"ORDER_FINISH"},{"orderStatus":"ORDER_WAIT_DELIVER"},{"orderStatus":"ORDER_WAIT_RECEIVE"}]},
                   {"supplier" : ObjectId(store_id)}]}},{'$group':{"_id":'$customer','number':{'$sum':1}}},
                   {'$match':{'number':{'$gt':1}}},{'$count':'countNum'}]

        ####新门客
        shop_new_user=[{'$match':{'$and':[{'$or':[{"orderStatus":"ORDER_FINISH"},{"orderStatus":"ORDER_WAIT_DELIVER"},{"orderStatus":"ORDER_WAIT_RECEIVE"}]},
                       {"supplier" : ObjectId(store_id)},{"orderTime":{'$gte': start_data}},{"orderTime": {'$lte': end_tata}}]}},
                       {'$group':{"_id":'$customer','number':{'$sum':1}}},{'$match':{'number':{'$lte':1}}},{'$count':'countNum'}]

        #####收藏店铺数
        collects_shop={'$and':[{"collection_id" : ObjectId(store_id)},{"type" : "MERCHANT"}]}

        ####商品上架
        shelf_true={'$and':[{"merchant" : ObjectId(store_id)},{"isDelete" : False},{"shelf" : True}]}

        ####商品下架
        shelf_false={'$and':[{"merchant" : ObjectId(store_id)},{"isDelete" : False},{"shelf" : False}]}

        ###全部商品
        all_goods={'$and':[{"merchant" : ObjectId(store_id)},{"isDelete" : False}]}

        ####库存紧张
        short_stock=[{'$lookup':{'from':"tb_goodsSku",'localField':"goodsSkus",'foreignField': "_id",'as': "goodssku"}},{'$unwind': '$goodssku'},
                       {'$match':{'$and':[{"merchant" : ObjectId(store_id)},{"isDelete" : False}
                       ]}},{'$addFields':{'cmpTo250': {'$cmp': [ "$goodssku.warnStock", "$goodssku.stock" ]}}}
                        ,{'$match':{'$or':[{"cmpTo250": 1},{"cmpTo250": 0}]}},{'$group': {'_id': '$_id', }},{'$count': 'countNum'}]

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
        if n==9:
            pending_order['$and'][0]['orderStatus']=orderStatus[0]###修改orderStatus传值
            return pending_order
        if n==10:
            return Pending_refund
        if n==11:
            return Pending_return
        if n==12:
            return shop_user
        if n==13:
            return more_user
        if n==14:
            return shop_new_user
        if n==15:
            return collects_shop
        if n==16:
            return shelf_true
        if n==17:
            return shelf_false
        if n==18:
            return all_goods
        if n==19:
            return short_stock
        if n==20:
            return return_confirmed

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
        # print(self.profit_s)
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
        # print(self.refund)
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
        # print(store_id)
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
        # print(order_nu)
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
        # print(order_nu)
        print('订单总数：%d' % order_nu)

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
        red_page = database.connect_mongodb_all('tb_adfee_rule', 2,
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

    def count_pending_order(self,n,nu,name,orderstation):
        """
        统计商家今日待处理订单
        :param n:
        :param nu:
        :param name:
        :param orderstation:订单状态
        :return:
        """
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        order_nu = database.connect_mongodb_all('tb_order', 3,
                                                self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 9,
                                                           store_id,orderstation))
        if orderstation=='ORDER_WAIT_PAY':
            print('待付款订单为：%d'%(order_nu))
        elif orderstation=='ORDER_WAIT_DELIVER':
            print('待发货订单为：%d' % (order_nu))
        elif orderstation=='ORDER_WAIT_RECEIVE':
            print('已发货订单为：%d' % (order_nu))
        elif orderstation=='ORDER_FINISH':
            print('已完成订单为：%d' % (order_nu))
    def count_pending_refund(self,n,nu,name):
        """
        统计商家待处理的退款单数量
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.pending_refund = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        refund = database.connect_mongodb_all('tb_return_apply', 2,
                                               self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 10,
                                                          store_id))
        for i in refund:
            self.pending_refund = int(str(i.get('number')))
        print('商家待处理退款单数量为：%d'%self.pending_refund)


    def count_pending_return(self,n,nu,name):
        """
        统计商家待处理的退货单数量
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.pending_refund = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        refund = database.connect_mongodb_all('tb_return_apply', 2,
                                              self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 11,
                                                         store_id))
        for i in refund:
            self.pending_refund = int(str(i.get('number')))
        print('商家待处理退货单数量为：%d' % self.pending_refund)

    def Shop_user(self,n,nu,name):
        """
        统计商家累计用户数
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.shop_user = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        shop_users = database.connect_mongodb_all('tb_order', 2,
                                              self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 12,
                                                         store_id))
        for i in shop_users:
            self.shop_user = int(str(i.get('countNum')))
        print('商家累计用户数：%d'%self.shop_user)


    def more_shop_user(self,n,nu,name):
        """
        统计商家复购用户数
        :param nu:
        :param name:
        :return:
        """
        self.more_shop_users = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        shop_users = database.connect_mongodb_all('tb_order', 2,
                                                  self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 13,
                                                             store_id))
        for i in shop_users:
            self.more_shop_users = int(str(i.get('countNum')))
        print('商家复购用户数：%d' % self.more_shop_users)
    def count_new_user(self,n,nu,name):
        """
        统计新门客
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.new_shop_user = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        new_shop_users = database.connect_mongodb_all('tb_order', 2,
                                                  self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 14,
                                                             store_id))
        for i in new_shop_users:
            self.new_shop_user = int(str(i.get('countNum')))
        print('%d天新用户数：%d' % (nu,self.new_shop_user))

    def count_collect_shop(self,n,nu,name):
        """
        统计店铺收藏数
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.collect_shop=0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        self.collect_shop = database.connect_mongodb_all('tb_collection', 3,
                                                self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 15,
                                                           store_id))
        print('店铺收藏总数：%d' % self.collect_shop)

    def count_goods_shelf_t(self,n,nu,name):
        """
        统计商品上架
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.shelf_t=0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        self.shelf_t = database.connect_mongodb_all('tb_goods', 3,
                                                    self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 16,
                                                               store_id))
        print('店铺商品上架数：%d' % self.shelf_t)

    def count_goods_shelf_f(self,n,nu,name):
        """
        统计商品下架
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.shelf_f=0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        self.shelf_f = database.connect_mongodb_all('tb_goods', 3,
                                                    self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 17,
                                                               store_id))
        print('店铺商品下架数：%d' % self.shelf_f)

    def count_goods_all(self,n,nu,name):
        """
        统计全部商品
        :param n:a
        :param nu:
        :param name:
        :return:
        """
        self.shelf_a=0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        self.shelf_a = database.connect_mongodb_all('tb_goods', 3,
                                                    self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 18,
                                                               store_id))
        print('店铺商品数：%d' % self.shelf_a)

    def count_short_stock(self,n,nu,name):
        """
        统计商家商品库存紧张数
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.short_stock_nu = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        short_stock_s = database.connect_mongodb_all('tb_goods', 2,
                                                      self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1],19,store_id))
        for i in short_stock_s:
            self.short_stock_nu = int(str(i.get('countNum')))
        print('商家库存紧张数：%d' % (self.short_stock_nu))

    def count_return_confirmed(self,n,nu,name):
        """
        统计待确认退货订单
        :param n:
        :param nu:
        :param name:
        :return:
        """
        self.return_confirmed = 0
        database = DB()
        tongji = test_tongji()
        store = database.connect_mongodb_all('tb_merchant', 1, self.select_shop_id(name))
        store_id = store.get('_id')
        refund = database.connect_mongodb_all('tb_return_apply', 2,
                                              self.sql_s(tongji.get_data(n, nu)[0], tongji.get_data(n, nu)[1], 20,
                                                         store_id))
        for i in refund:
            self.return_confirmed = int(str(i.get('number')))
        print('商家待确认退货单数量为：%d' % self.return_confirmed)


if __name__ == "__main__":
    # name='惠宜家艾家（恒大中央公园店）'
    # name = '西门艾家'
    name='理工艾家'
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
    ###商家待付款
    a.count_pending_order(0,1,name,'ORDER_WAIT_PAY')
    ###商家待发货
    a.count_pending_order(0, 1, name, 'ORDER_WAIT_DELIVER')
    ###商家已发货
    a.count_pending_order(0, 1, name, 'ORDER_WAIT_RECEIVE')
    ###商家已完成
    a.count_pending_order(0, 1, name, 'ORDER_FINISH')
    ###商家待处理的退款订单
    a.count_pending_refund(0, 1, name)
    ###商家待处理的退货订单
    a.count_pending_return(0, 1, name)
    ####商家待确认的退货订单
    a.count_return_confirmed(0,1,name)
    ###商家累计用户数
    a.Shop_user(0,1,name)
    ###商家复购用户数
    a.more_shop_user(0,1,name)
    ###商家新门客
    a.count_new_user(0,1,name)
    ###店铺收藏总数
    a.count_collect_shop(0,1,name)
    ###商品上架
    a.count_goods_shelf_t(0,1,name)
    ###商品下架
    a.count_goods_shelf_f(0,1,name)
    ##店铺商品数
    a.count_goods_all(0,1,name)
    ###库存紧张
    a.count_short_stock(0,1,name)
    ###第几天的销售额
    a.count_sales_amount(0,29,name)
    ###近几天的销售额
    a.count_sales_amount(1, 7, name)
    ###近几天的销售额
    a.count_sales_amount(1, 15, name)
    ###近几天的销售额
    a.count_sales_amount(1, 30, name)
    ###近几天的销售额
    a.count_sales_amount(1, 90, name)