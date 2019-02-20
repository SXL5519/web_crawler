from datetime import datetime,date,timedelta

from db_file import DB

class test_tongji():
    """
    测试ajgs运营后台统计
    """
    def mon_sql(self,n,start_data,end_tata):
        """

        :param n:
        :param start_data:
        :param end_tata:
        :param field:
        :return: 相应时间的销售总额，退款总金额
        """
        ###销售金额查询
        # sql_sale=[{'$match': {'$and':[{'$or':[{"orderStatus": "ORDER_FINISH"},
        #                      {"orderStatus": "ORDER_WAIT_DELIVER"},
        #                      {"orderStatus": "ORDER_WAIT_RECEIVE"}]}, {"orderTime":
        #                      {'$gte': start_data}},{"orderTime": {'$lte': end_tata}}]}},
        #                      {'$group': {'_id': '','sumGoodsPay': {'$sum': "$totalPrice"},
        #                      'sumTransPay': {'$sum': "$transPrice"}, 'sumDeductionPay': {'$sum': "$deductionPrice"},
        #                      'sumThirdPay': {'$sum': "$realPay"}}}]

        sql_sale=[{'$match':{'$and':[{"orderTime":{'$gte':start_data}},
                        {"orderTime":{'$lte':end_tata}},
                        {"payTime":{'$ne':None}}]}},
                        {'$group': {'_id': '', 'sumGoodsPay': {'$sum': "$totalPrice"},
                                                'sumTransPay': {'$sum': "$transPrice"},
                                                'sumDeductionPay': {'$sum': "$deductionPrice"},
                                                'sumThirdPay': {'$sum': "$realPay"}}}]


##退款金额查询
        sql_refund=[{'$lookup': {'from': "tb_order_detail",'localField': "orderDetail",'foreignField': "_id",'as': "orderDetail"}},
                             {'$unwind': '$orderDetail'},{'$lookup': {'from': "tb_order",'localField': "orderDetail.order",'foreignField': "_id",'as': "order"}},
                             {'$unwind': '$order'},{'$match': {'$and':[{'order.orderStatus': "ORDER_FINISH"},{'order.orderTime': {'$gte': start_data}},
                             {'order.orderTime': {'$lte': end_tata}},{'statusList.status': "FINISHED"},{'statusList.time': {'$gte': start_data}},
                             {'statusList.time': {'$lte': end_tata}}]}},{'$group': {'_id': '', 'sumGoodsPay': {'$sum': "$confirmMoney"},
                             'thirdPayMoney': {'$sum': "$thirdPayMoney"},'deductionPrice': {'$sum': "$deductionPrice"}}}]

        if n=='sale':
            return sql_sale
        if n=='refund':
            return sql_refund

    def get_data(self,n,nu):
        """
        开始时间，结束时间
        :param n: 0 为只返回当天时间段,1为结束时间为今天
        :param nu: 当前时间需要减少的天数
        :return:开始时间，结束时间
        """
        if n==0:
            date_start = datetime.strptime((date.today() + timedelta(days=-nu)).strftime("%Y-%m-%d")
                                           + ' 16:00:00','%Y-%m-%d %H:%M:%S')
            date_end = datetime.strptime((date.today() + timedelta(days=-nu+1)).strftime("%Y-%m-%d")
                                         + ' 15:59:59','%Y-%m-%d %H:%M:%S')
            # return date_start,date_end
        else:
            date_start = datetime.strptime((date.today() + timedelta(days=-nu)).strftime("%Y-%m-%d")
                                           + ' 16:00:00', '%Y-%m-%d %H:%M:%S')
            date_end = datetime.strptime((date.today()).strftime("%Y-%m-%d")
                                         + ' 15:59:59', '%Y-%m-%d %H:%M:%S')
        return date_start,date_end



    def sale(self,n,nu):
        """
        测试销售额
        :param n:0为只返回当天时间段
        :param nu: 当前时间需要减少的天数
        :param time: 查询时间
        :return: 相应的金额
        """
        self.total_sales = 0   ##销售总额
        self.total_refund=0  ###退款总金额
        self.total_sales_three=0##第三方支付总额
        self.total_refund_three=0##第三方退款总金额
        self.total_sales_balance=0##余额支付总额
        self.total_refund_balance=0###余额退款总金额
        self.total_Trans_sales=0###运费总额

        database=DB()
        db_total=database.connect_mongodb_all('tb_order',2,self.mon_sql('sale',self.get_data(n,nu)[0],self.get_data(n,nu)[1]))
        if type(db_total)==None:
            self.total_sales=0
            print('查询无数据')
        else:
            for i_total in db_total:
                self.total_sales = float(str(i_total.get('sumGoodsPay')))  ##商品总额
                self.total_Trans_sales = float(str(i_total.get('sumTransPay')))  ##运费总额
                # print('商品总额%.2f'%self.total_sales)
                # print('运费总额%.2f' % self.total_sales)
        db_total_refund = database.connect_mongodb_all('tb_return_apply',2,self.mon_sql('refund',self.get_data(n,nu)[0],self.get_data(n,nu)[1],))
        if type(db_total_refund)==None:  #tuple(db_total_refund).count(db_total_refund)==0
            self.total_refund = 0
            print('查询无数据')
        else:
            for j_total in db_total_refund:
                self.total_refund=float(str(j_total.get('sumGoodsPay')))  ##退款总金额
                # print('退款总金额%.2f'%self.total_refund)

        sales_amount=self.total_sales+self.total_Trans_sales
                     # -self.total_refund ##销售总额
        db_total_three = database.connect_mongodb_all('tb_order',2,self.mon_sql('sale',self.get_data(n,nu)[0],self.get_data(n,nu)[1]))
        if type(db_total_three)==None:
            self.total_sales_three=0
            print('查询无数据')
        else:
            for i_three in db_total_three:
                self.total_sales_three = float(str(i_three.get('sumThirdPay')))  ##第三方支付总额
                # print('第三方支付总额%.2f'%self.total_sales_three)
        db_total_refund_three = database.connect_mongodb_all('tb_return_apply',2,self.mon_sql('refund',self.get_data(n,nu)[0],self.get_data(n,nu)[1]))
        if type(db_total_refund_three)==None:
            self.total_refund_three=0
            print('查询无数据')
        else:
            for j_total_three in db_total_refund_three:
                self.total_refund_three = float(str(j_total_three.get('thirdPayMoney')))  ##第三方退款总金额
                # print('第三方退款总金额%.2f'%self.total_refund_three)
        sales_amount_three = self.total_sales_three
                             # - self.total_refund_three  ##第三方销售总额

        db_total_balance  = database.connect_mongodb_all('tb_order',2,self.mon_sql('sale',self.get_data(n,nu)[0],self.get_data(n,nu)[1]))
        if type(db_total_balance)==None:
            self.total_sales_balance=0
            print('查询无数据')
        else:
            for i_balance in db_total_balance:
                self.total_sales_balance = float(str(i_balance.get('sumDeductionPay')))  ##余额支付总额
                # print('余额支付总额%.2f'%self.total_sales_balance)

        db_total_refund_balance = database.connect_mongodb_all('tb_return_apply',2,self.mon_sql('refund',self.get_data(n,nu)[0],self.get_data(n,nu)[1]))
        if type(db_total_refund_balance)==None:
            self.total_refund_balance=0
            print('查询无数据')
        else:
            for j_total_balance in db_total_refund_balance:
                self.total_refund_balance = float(str(j_total_balance.get('deductionPrice')))  ##余额退款总金额
                # print('余额退款总金额%.2f'%self.total_refund_balance)
        sales_amount_balance = self.total_sales_balance
                               # - self.total_refund_balance  ##余额销售总额


        if nu==1:
            print('今日销售总额%.2f'%sales_amount)
            print('今日第三方销售总额%.2f' % sales_amount_three)
            print('今日余额销售总额%.2f' % sales_amount_balance)
        elif nu==2:
            print('昨日销售总额%.2f' % sales_amount)
            print('昨日第三方销售总额%.2f' % sales_amount_three)
            print('昨日余额销售总额%.2f' % sales_amount_balance)
        elif nu==7:
            print('近7天销售总额%.2f' % sales_amount)
            print('近7天第三方销售总额%.2f' % sales_amount_three)
            print('近7天余额销售总额%.2f' % sales_amount_balance)

if __name__ == "__main__":
    a=test_tongji()
    print('今日##########################################')
    a.sale(0,1)
    print('昨日##########################################')
    a.sale(0,2)
    print('近七天########################################')
    a.sale(1,7)


