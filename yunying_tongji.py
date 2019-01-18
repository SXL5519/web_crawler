from datetime import datetime,date,timedelta

from db_file import DB

class test_tongji():
    """
    测试ajgs运营后台统计
    """
    def mon_sql(self,n,start_data,end_tata,field):
        """

        :param n:
        :param start_data:
        :param end_tata:
        :param field:
        :return: 相应时间的销售总额，退款总金额
        """
        sql_sale=[{'$match': {'$and': [{'payTime': {'$gte': start_data}},
                            {'payTime': {'$lte': end_tata}}]}},
                            {'$group': {'_id': '销售总额', 'total': {'$sum': '$'+field}}}]
        sql_refund=[{'$match':{'$and': [{"statusList.status":"FINISHED"},
                                        {'statusList.time': {'$gte': start_data}},
                                        {'statusList.time': {'$lte': end_tata}}]}},
                                        {'$group':{'_id':'退款总金额','total':{'$sum':'$'+field}}}]
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
            return date_start,date_end
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
        self.total_refund=0
        self.total_sales_three=0
        self.total_refund_three=0
        self.total_sales_balance=0
        self.total_refund_balance=0

        database=DB()
        db_total=database.connect_mongodb_all('tb_order',self.mon_sql('sale',self.get_data(n,nu)[0],self.get_data(n,nu)[1],'totalPrice'))
        if type(db_total)==None:
            self.total_sales=0
            print('查询无数据')
        else:
            for i_total in db_total:
                self.total_sales = float(str(i_total.get('total')))  ##支付总额
                print('支付总额%.2f'%self.total_sales)
        db_total_refund = database.connect_mongodb_all('tb_return_apply',self.mon_sql('refund',self.get_data(n,nu)[0],self.get_data(n,nu)[1],'confirmMoney'))
        if type(db_total_refund)==None:  #tuple(db_total_refund).count(db_total_refund)==0
            self.total_refund = 0
            print('查询无数据')
        else:
            for j_total in db_total_refund:
                self.total_refund=float(str(j_total.get('total')))  ##退款总金额
                print('退款总金额%.2f'%self.total_refund)

        sales_amount=self.total_sales-self.total_refund ##销售总额
        db_total_three = database.connect_mongodb_all('tb_order',self.mon_sql('sale',self.get_data(n,nu)[0],self.get_data(n,nu)[1],'thirdPayMoney'))
        if type(db_total_three)==None:
            self.total_sales_three=0
            print('查询无数据')
        else:
            for i_three in db_total_three:
                self.total_sales_three = float(str(i_three.get('total')))  ##第三方支付总额
                print('第三方支付总额%.2f'%self.total_sales_three)
        db_total_refund_three = database.connect_mongodb_all('tb_return_apply',self.mon_sql('refund',self.get_data(n,nu)[0],self.get_data(n,nu)[1],'confirmThirdMoney'))
        if type(db_total_refund_three)==None:
            self.total_refund_three=0
            print('查询无数据')
        else:
            for j_total_three in db_total_refund_three:
                self.total_refund_three = float(str(j_total_three.get('total')))  ##第三方退款总金额
                print('第三方退款总金额%.2f'%self.total_refund_three)
        sales_amount_three = self.total_sales_three - self.total_refund_three  ##第三方销售总额

        db_total_balance  = database.connect_mongodb_all('tb_order',self.mon_sql('sale',self.get_data(n,nu)[0],self.get_data(n,nu)[1],'deductionPrice'))
        if type(db_total_balance)==None:
            self.total_sales_balance=0
            print('查询无数据')
        else:
            for i_balance in db_total_balance:
                self.total_sales_balance = float(str(i_balance.get('total')))  ##余额支付总额
                print('余额支付总额%.2f'%self.total_sales_balance)

        db_total_refund_balance = database.connect_mongodb_all('tb_return_apply',self.mon_sql('refund',self.get_data(n,nu)[0],self.get_data(n,nu)[1],'deductionPrice'))
        if type(db_total_refund_balance)==None:
            self.total_refund_balance=0
            print('查询无数据')
        else:
            for j_total_balance in db_total_refund_balance:
                self.total_refund_balance = float(str(j_total_balance.get('total')))  ##余额退款总金额
                print('余额退款总金额%.2f'%self.total_refund_balance)
        sales_amount_balance = self.total_sales_balance - self.total_refund_balance  ##余额销售总额


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


