# -*- coding: utf-8 -*-

from macd_split import *


class inject:

    def __init__(self, minute, day):
        self.day = day
        self.minute = minute
        self.min_boduan = minute.boduan
        self.day_boduan = day.boduan
        self.min_boduan_list = []
        self.min_close = minute.close
        self.day_close = day.close
        self.situation = pd.DataFrame({})
        self.misplace_point = pd.DataFrame({})
        self.zuji_situation = pd.DataFrame({})
        self.tupo_situation = pd.DataFrame({})
        self.zujiplustupo = pd.DataFrame({})
        self.now_situation = pd.DataFrame({})

    def mapping(self):
        df_day = self.day_boduan
        df_min = self.min_boduan
        mapping_num = []
        mapping_table = []
        location = 0
        for i in range(len(df_day)):

            start = df_day.ix[i].start_date
            end = df_day.ix[i].end_date
            mapping_df = df_min[
                (df_min.start_date >= start) & (
                    df_min.end_date <= end)].copy()

            if not mapping_df.empty:
                a = mapping_df.index[0]
                b = mapping_df.index[-1]
                location = b
                if df_min.ix[b].bd_type == df_day.ix[i].bd_type and df_min.ix[
                        a].bd_type != df_day.ix[i].bd_type:
                    mapping_df = df_min.ix[a - 1:b].copy()

                if df_min.ix[a].bd_type == df_day.ix[i].bd_type and df_min.ix[
                        b].bd_type != df_day.ix[i].bd_type:
                    mapping_df = df_min.ix[a:b + 1].copy()
                    location = b + 1
                if df_min.ix[a].bd_type != df_day.ix[i].bd_type and df_min.ix[
                        b].bd_type != df_day.ix[i].bd_type:
                    mapping_df = df_min.ix[a - 1:b + 1].copy()
                    location = b + 1

            else:
                if not mapping_table:
                    mapping_table.append(df_min.ix[0])
                else:
                    mapping_table.append(df_min.ix[location + 1])
                location += 1

                mapping_num.append(1)
                continue

            if df_day.ix[i].bd_type == "decline":
                for j in list(mapping_df.index[:-2]):
                    if j not in mapping_df.index:
                        continue
                    bd = mapping_df.ix[j]
                    if bd.bd_type == "decline":
                        if bd.end_price > mapping_df.end_price.ix[:j].min():
                            bdp2 = mapping_df.ix[j + 2]
                            mapping_df = mapping_df.drop(j)
                            mapping_df = mapping_df.drop(j + 1)
                            mapping_df = mapping_df.drop(j + 2)
                            mapping_df.ix[j] = {
                                'start_point': bd.start_point,
                                'end_point': bdp2.end_point,
                                'start_date': bd.start_date,
                                'end_date': bdp2.end_date,
                                'start_price': bd.start_price,
                                'end_price': bdp2.end_price,
                                'comfirmpoint': bd.comfirmpoint,
                                'prevtime': bd.prevtime,
                                'aftertime': bdp2.end_point - bd.comfirmpoint,
                                'timedelta': bdp2.end_point - bd.start_point,
                                'bd_type': 'decline',
                                'comfirm_date': bd.comfirm_date,
                                'comfirm_price': bd.comfirm_price,
                                'returns': bdp2.end_price / bd.start_price - 1,
                                'prevreturns': bd.comfirm_price / bd.start_price - 1,
                                'afterreturns': bdp2.end_price / bd.comfirm_price - 1,
                                'continue_ratio': (
                                    bd.comfirm_price / bd.start_price - 1) / (
                                    bdp2.end_price / bd.comfirm_price - 1)}

                            mapping_df = mapping_df.sort_index()

            elif df_day.ix[i].bd_type == "raise":
                for j in list(mapping_df.index[:-2]):
                    if j not in mapping_df.index:
                        continue
                    bd = mapping_df.ix[j]
                    if bd.bd_type == "raise":
                        if bd.end_price < mapping_df.end_price.ix[:j].max():
                            bdp2 = mapping_df.ix[j + 2]
                            mapping_df = mapping_df.drop(j)
                            mapping_df = mapping_df.drop(j + 1)
                            mapping_df = mapping_df.drop(j + 2)
                            mapping_df.ix[j] = {
                                'start_point': bd.start_point,
                                'end_point': bdp2.end_point,
                                'start_date': bd.start_date,
                                'end_date': bdp2.end_date,
                                'start_price': bd.start_price,
                                'end_price': bdp2.end_price,
                                'comfirmpoint': bd.comfirmpoint,
                                'prevtime': bd.prevtime,
                                'aftertime': bdp2.end_point - bd.comfirmpoint,
                                'timedelta': bdp2.end_point - bd.start_point,
                                'bd_type': 'raise',
                                'comfirm_date': bd.comfirm_date,
                                'comfirm_price': bd.comfirm_price,
                                'returns': bdp2.end_price / bd.start_price - 1,
                                'prevreturns': bd.comfirm_price / bd.start_price - 1,
                                'afterreturns': bdp2.end_price / bd.comfirm_price - 1,
                                'continue_ratio': (
                                    bd.comfirm_price / bd.start_price - 1) / (
                                    bdp2.end_price / bd.comfirm_price - 1)}

                            mapping_df = mapping_df.sort_index()

            mapping_table.append(mapping_df)
            mapping_num.append(mapping_df.shape[0])
        df_day['total_num'] = mapping_num
        self.day_boduan = df_day
        a = self.day
        a.boduan = df_day
        self.day = a
        self.min_boduan_list = mapping_table

    def comfirm_num(self):
        day_boduan = self.day_boduan
        min_boduan_list = self.min_boduan_list
        res = []
        for i in range(day_boduan.shape[0]):
            df = min_boduan_list[i]
            if len(df.shape) == 1:
                res.append(1)
                continue

            day_point = day_boduan.ix[i]
            day_comfirm_date = day_point.comfirm_date
            flag = True
            j = 0
            while flag and j < df.shape[0]:

                if df.iloc[j].start_date < day_comfirm_date < df.iloc[
                        j].end_date:
                    flag = False
                j += 1
            bd_type = day_point.bd_type
            if bd_type != df.iloc[j - 1].bd_type:
                j -= 1
            res.append(j)

        day_boduan['comfirm_num'] = res
        self.day_boduan = day_boduan
        a = self.day
        a.boduan = day_boduan
        self.day = a

    def day_situation(self):
        min_boduan = self.min_boduan
        day_boduan = self.day_boduan
        mapping_table = self.min_boduan_list
        start = day_boduan.start_date.iloc[0]
        today = datetime.date.today()
        days = w.tdays(start, today).Data[0]
        days = map(lambda x: str(x).split(' ')[0], days)
        df = pd.DataFrame(
            columns=[
                'future_day_situation',
                'now_day_situation',
                'future_day_start',
                'future_day_end',
                'now_day_start',
                'future_minute_situation',
                'now_minute_situation',
                'future_min_start',
                'future_min_end',
                'now_min_start',
                'future_min_duannum',
                'now_min_duannum'],
            index=days)

        for i in range(1, day_boduan.shape[0]):
            duan = day_boduan.iloc[i]
            start_date = str(duan.start_date)
            end_date = str(duan.end_date)
            comfirm_date = str(duan.comfirm_date)
            prev_start_date = day_boduan.iloc[i - 1].start_date
            situation = duan.bd_type
            situation_inverse = 'raise' if situation == 'decline' else 'decline'
            df['future_day_situation'].ix[start_date:end_date] = situation
            df['now_day_situation'].ix[start_date:comfirm_date] = situation_inverse
            df['now_day_situation'].ix[comfirm_date:end_date] = situation
            df['future_day_start'].ix[start_date:end_date] = start_date
            df['future_day_end'].ix[start_date:end_date] = end_date
            df['now_day_start'].ix[start_date:comfirm_date] = prev_start_date
            df['now_day_start'].ix[comfirm_date:end_date] = start_date
            table = mapping_table[i]
            prev_table = mapping_table[i - 1]
            if len(table.shape) == 1:
                num = 1
            else:
                num = table.shape[0]
            for j in range(num):
                if len(table.shape) == 1:
                    min_start_date = str(table.start_date)
                    min_end_date = str(table.end_date)
                    min_comfirm_date = str(table.comfirm_date)
                else:
                    min_duan = table.iloc[j]
                    min_start_date = str(min_duan.start_date)
                    min_end_date = str(min_duan.end_date)
                    min_comfirm_date = str(min_duan.comfirm_date)

                df['future_min_duannum'].ix[min_start_date:min_end_date] = j + 1
                if len(prev_table.shape) == 1:
                    length = 1
                else:
                    length = prev_table.shape[0]
                df['now_min_duannum'].ix[min(start_date, min_start_date):comfirm_date].ix[min_start_date:min_comfirm_date] = length + j
                df['now_min_duannum'].ix[min(start_date, min_start_date): comfirm_date].ix[min_comfirm_date:min_end_date] = length + j + 1
                df['now_min_duannum'].ix[comfirm_date: max(end_date, min_end_date)].ix[min_start_date:min_comfirm_date] = j
                df['now_min_duannum'].ix[comfirm_date: max(end_date, min_end_date)].ix[min_comfirm_date:min_end_date] = j + 1

        for i in range(1, min_boduan.shape[0]):
            duan = min_boduan.iloc[i]
            start_date = str(duan.start_date)
            end_date = str(duan.end_date)
            comfirm_date = str(duan.comfirm_date)
            prev_start_date = min_boduan.iloc[i - 1].start_date
            situation = duan.bd_type
            situation_inverse = 'raise' if situation == 'decline' else 'decline'
            df['future_minute_situation'].ix[start_date:end_date] = situation
            df['now_minute_situation'].ix[start_date:comfirm_date] = situation_inverse
            df['now_minute_situation'].ix[comfirm_date:end_date] = situation
            df['future_min_start'].ix[start_date:end_date] = start_date
            df['future_min_end'].ix[start_date:end_date] = end_date
            df['now_min_start'].ix[start_date:comfirm_date] = prev_start_date
            df['now_min_start'].ix[comfirm_date:end_date] = start_date

        end_day = self.day_boduan.end_date.iloc[-1]
        end_min = self.min_boduan.end_date.iloc[-1]
        day_date, day_type = self.day.now_situation()
        min_date, min_type = self.minute.now_situation()

        df['future_day_situation'].ix[end_day:day_date] = day_type
        df['now_day_situation'].ix[end_day:day_date] = "raise" if day_type == "decline" else "decline"
        df['future_day_start'].ix[end_day:day_date] = end_day
        self.now_situation = df

    def misplace(self):
        min_boduan = self.min_boduan
        day_boduan = self.day_boduan
        min_close = self.min_close
        day_close = self.day_close
        misplace_point = []
        point_type = []
        day_comfirm = []
        misplace_success = []
        for i in range(min_boduan.shape[0] - 2):
            n1 = min_boduan.iloc[i]
            n3 = min_boduan.iloc[i + 2]
            bd_type = n1.bd_type
            temp = day_boduan[day_boduan.bd_type == bd_type]
            temp = temp[temp.start_date < n1.end_date]
            if temp.empty:
                continue

            if temp.index[-1] >= day_boduan.shape[0] - 1:
                break
            A = temp.iloc[-1].comfirm_date
            e = self.minute.comfirm_point_list[i + 3]
            a = n1.start_date
            c = n3.start_date
            b = n1.end_date
            d = n3.end_date
            Pb = min_close.ix[b]
            Pd = min_close.ix[d]
            Ae = day_close.ix[A:e]
            if Ae.empty:
                continue
            B1 = Ae.idxmin()
            B2 = Ae.idxmax()
            if Pb > Pd:
                if temp.iloc[-1].bd_type == "decline" and a <= B1 <= c:
                    misplace_point.append(e)
                    point_type.append("deline_after")
                    day_comfirm.append(
                        day_boduan.iloc[temp.index[-1] + 1].comfirm_date)
                    premin = min_close.ix[A:e].min()
                    nowmin = min_close.ix[e:day_boduan.iloc[
                        temp.index[-1] + 1].comfirm_date].min()
                    if nowmin < premin:
                        misplace_success.append(1)
                    else:
                        misplace_success.append(0)

                if temp.iloc[-1].bd_type == "raise" and c <= B2 <= e:
                    misplace_point.append(e)
                    point_type.append("raise_prev")
                    day_comfirm.append(
                        day_boduan.iloc[temp.index[-1] + 1].comfirm_date)
                    premax = min_close.ix[A:e].max()
                    nowmax = min_close.ix[e:day_boduan.iloc[
                        temp.index[-1] + 1].comfirm_date].max()
                    if nowmax > premax:
                        misplace_success.append(1)
                    else:
                        misplace_success.append(0)

            if Pb < Pd:
                if temp.iloc[-1].bd_type == "decline" and c <= B1 <= e:

                    misplace_point.append(e)
                    point_type.append("deline_prev")
                    day_comfirm.append(
                        day_boduan.iloc[temp.index[-1] + 1].comfirm_date)
                    premin = min_close.ix[A:e].min()
                    nowmin = min_close.ix[e:day_boduan.iloc[
                        temp.index[-1] + 1].comfirm_date].min()
                    if nowmin < premin:
                        misplace_success.append(1)
                    else:
                        misplace_success.append(0)

                if temp.iloc[-1].bd_type == "raise" and a <= B2 <= c:
                    misplace_point.append(e)
                    point_type.append("raise_after")
                    day_comfirm.append(
                        day_boduan.iloc[temp.index[-1] + 1].comfirm_date)
                    premax = min_close.ix[A:e].max()
                    nowmax = min_close.ix[e:day_boduan.iloc[
                        temp.index[-1] + 1].comfirm_date].max()
                    if nowmax > premax:
                        misplace_success.append(1)
                    else:
                        misplace_success.append(0)
        df = pd.DataFrame({'miplace_date': misplace_point,
                           'type': point_type,
                           'day_comfirm': day_comfirm,
                           'misplace_success': misplace_success})
        self.misplace_point = df

    def restrict(self):
        min_boduan = self.min_boduan
        day_boduan = self.day_boduan
        min_close = self.min_close
        day_close = self.day_close
        min_boduan_list = []
        zuji = []
        zuji_success = []
        zuji_boduan = []
        zuji_day = []
        zuji_type = []
        zuji_price = []
        zuji_false = []
        zuji_false_price = []
        tupo = []
        tupo_success = []
        tupo_boduan = []
        tupo_day = []
        tupo_type = []
        tupo_price = []
        tupo_false = []
        tupo_false_price = []
        zt = []
        zt_boduan = []
        zt_day = []
        zt_success = []
        zt_type = []
        zt_price = []
        zt_false = []
        zt_false_price = []
        for i in range(day_boduan.shape[0] - 1):
            start_date = day_boduan.iloc[i].comfirm_date
            comfirm_date = day_boduan.iloc[i + 1].comfirm_date
            mapping_df = min_boduan[
                (min_boduan.start_date >= start_date) & (
                    min_boduan.comfirm_date <= comfirm_date)]
            if not mapping_df.empty:
                a = mapping_df.index[0]
                b = mapping_df.index[-1]
            else:
                continue
            if min_boduan.ix[a].bd_type != day_boduan.iloc[i].bd_type:
                mapping_df = min_boduan.ix[a - 1:b]
            min_boduan_list.append(mapping_df)
            if day_boduan.iloc[i].bd_type == "raise":
                flag = True
                j = 0

                while flag and j < mapping_df.shape[0] - 2:
                    if mapping_df.iloc[
                            j + 2].end_price < mapping_df.iloc[j].end_price:
                        if j + 3 < mapping_df.shape[0]:
                            zuji.append(mapping_df.iloc[j + 3].comfirm_date)
                            zuji_boduan.append(i + 1)
                            zuji_day.append(
                                day_boduan.iloc[
                                    i + 1].comfirm_date)
                            zuji_type.append("decline")
                            zuji_price.append(
                                min_close.ix[
                                    mapping_df.iloc[
                                        j + 3].comfirm_date])
                            premax = day_close.ix[
                                day_boduan.iloc[i].comfirm_date:mapping_df.iloc[
                                    j + 3].comfirm_date].max()
                            nowmax = day_close.ix[
                                mapping_df.iloc[
                                    j +
                                    3].comfirm_date:day_boduan.iloc[
                                    i +
                                    1].comfirm_date].max()
                            price_boduan = day_close.ix[
                                mapping_df.iloc[
                                    j +
                                    3].comfirm_date:day_boduan.iloc[
                                    i +
                                    1].comfirm_date]
                            if nowmax > premax:
                                zuji_success.append(0)
                                f = price_boduan[
                                    price_boduan > premax].index[0]
                                zuji_false.append(f)
                                zuji_false_price.append(min_close.ix[f])

                            else:
                                zuji_success.append(1)
                                zuji_false.append(
                                    mapping_df.iloc[j + 3].comfirm_date)
                                zuji_false_price.append(
                                    min_close.ix[mapping_df.iloc[j + 3].comfirm_date])
                                flag = False
                    j += 2

                flag = True
                j = 0

                while flag and j < mapping_df.shape[0] - 4:
                    avalue = mapping_df.iloc[j + 3].end_price
                    five = mapping_df.iloc[j + 4]
                    five_price = min_close.ix[
                        five.comfirm_date:day_boduan.iloc[
                            i + 1].comfirm_date]
                    c = five_price[five_price < avalue]

                    if not c.empty:
                        tupo.append(c.index[0])
                        tupo_boduan.append(i + 1)
                        tupo_day.append(day_boduan.iloc[i + 1].comfirm_date)
                        tupo_type.append("decline")
                        tupo_price.append(min_close.ix[c.index[0]])
                        premax = day_close.ix[
                            day_boduan.iloc[i].comfirm_date:c.index[0]].max()
                        nowmax = day_close.ix[
                            c.index[0]:day_boduan.iloc[
                                i + 1].comfirm_date].max()
                        price_boduan = day_close.ix[
                            c.index[0]:day_boduan.iloc[
                                i + 1].comfirm_date]
                        if nowmax > premax:
                            tupo_success.append(0)
                            f = price_boduan[price_boduan > premax].index[0]
                            tupo_false.append(f)
                            tupo_false_price.append(min_close.ix[f])
                        else:
                            tupo_success.append(1)
                            tupo_false.append(tupo[-1])
                            tupo_false_price.append(min_close.ix[tupo[-1]])
                            flag = False
                    j += 2

                flag = True
                j = 0

                while flag and j < mapping_df.shape[0] - 3:
                    a = mapping_df.iloc[j].end_price
                    b = mapping_df.iloc[j + 1].end_price
                    c = mapping_df.iloc[j + 2].end_price
                    append = False
                    if a > c:
                        d = mapping_df.iloc[j + 3]
                        if d.comfirm_price < b:
                            zt.append(d.comfirm_date)
                            zt_boduan.append(i + 1)
                            zt_day.append(day_boduan.iloc[i + 1].comfirm_date)

                            append = True
                        else:
                            d_price = min_close.ix[
                                d.comfirm_date:day_boduan.iloc[
                                    i + 1].comfirm_date]
                            d_price = d_price[d_price < b]
                            if not d_price.empty:
                                zt.append(d_price.index[0])
                                zt_boduan.append(i + 1)
                                zt_day.append(
                                    day_boduan.iloc[
                                        i + 1].comfirm_date)

                                append = True

                        if append:
                            zt_type.append("decline")
                            zt_price.append(min_close.ix[zt[-1]])
                            price_boduan = day_close.ix[
                                zt[-1]:day_boduan.iloc[i + 1].comfirm_date]
                            premax = day_close.ix[day_boduan.iloc[
                                i].comfirm_date:zt[-1]].max()
                            nowmax = day_close.ix[
                                zt[-1]:day_boduan.iloc[i + 1].comfirm_date].max()
                            if premax >= nowmax:
                                zt_success.append(1)
                                zt_false.append(zt[-1])
                                zt_false_price.append(zt_price[-1])
                                flag = False
                            else:
                                zt_success.append(0)
                                f = price_boduan[
                                    price_boduan > premax].index[0]
                                zt_false.append(f)
                                zt_false_price.append(min_close.ix[f])
                    j += 2

            if day_boduan.iloc[i].bd_type == "decline":
                flag = True
                j = 0
                while flag and j < mapping_df.shape[0] - 2:
                    if mapping_df.iloc[
                            j + 2].end_price > mapping_df.iloc[j].end_price:
                        if j + 3 < mapping_df.shape[0]:
                            zuji_boduan.append(i + 1)
                            zuji.append(mapping_df.iloc[j + 3].comfirm_date)
                            zuji_day.append(
                                day_boduan.iloc[
                                    i + 1].comfirm_date)
                            zuji_type.append("raise")
                            zuji_price.append(
                                min_close.ix[
                                    mapping_df.iloc[
                                        j + 3].comfirm_date])
                            premin = day_close.ix[
                                day_boduan.iloc[i].comfirm_date:mapping_df.iloc[
                                    j + 3].comfirm_date].min()
                            nowmin = day_close.ix[
                                mapping_df.iloc[
                                    j +
                                    3].comfirm_date:day_boduan.iloc[
                                    i +
                                    1].comfirm_date].min()
                            price_boduan = day_close.ix[
                                mapping_df.iloc[
                                    j +
                                    3].comfirm_date:day_boduan.iloc[
                                    i +
                                    1].comfirm_date]
                            if nowmin < premin:
                                zuji_success.append(0)
                                f = price_boduan[
                                    price_boduan < premin].index[0]
                                zuji_false.append(f)
                                zuji_false_price.append(min_close.ix[f])

                            else:
                                zuji_success.append(1)
                                zuji_false.append(
                                    mapping_df.iloc[j + 3].comfirm_date)
                                zuji_false_price.append(
                                    min_close.ix[mapping_df.iloc[j + 3].comfirm_date])
                                flag = False
                    j += 2

                flag = True
                j = 0

                while flag and j < mapping_df.shape[0] - 4:
                    avalue = mapping_df.iloc[j + 3].end_price
                    five = mapping_df.iloc[j + 4]
                    five_price = min_close.ix[
                        five.comfirm_date:day_boduan.iloc[
                            i + 1].comfirm_date]
                    c = five_price[five_price > avalue]

                    if not c.empty:
                        tupo.append(c.index[0])
                        tupo_boduan.append(i + 1)
                        tupo_day.append(day_boduan.iloc[i + 1].comfirm_date)
                        tupo_type.append("raise")
                        tupo_price.append(min_close.ix[c.index[0]])
                        premax = day_close.ix[
                            day_boduan.iloc[i].comfirm_date:c.index[0]].min()
                        nowmax = day_close.ix[
                            c.index[0]:day_boduan.iloc[
                                i + 1].comfirm_date].min()
                        price_boduan = day_close.ix[
                            c.index[0]:day_boduan.iloc[
                                i + 1].comfirm_date]
                        if nowmax < premax:
                            tupo_success.append(0)
                            f = price_boduan[price_boduan < premax].index[0]
                            tupo_false.append(f)
                            tupo_false_price.append(min_close.ix[f])
                        else:
                            tupo_success.append(1)
                            tupo_false.append(tupo[-1])
                            tupo_false_price.append(min_close.ix[tupo[-1]])
                            flag = False
                    j += 2

                flag = True
                j = 0
                while flag and j < mapping_df.shape[0] - 3:
                    a = mapping_df.iloc[j].end_price
                    b = mapping_df.iloc[j + 1].end_price
                    c = mapping_df.iloc[j + 2].end_price
                    append = False
                    if a < c:
                        d = mapping_df.iloc[j + 3]
                        if d.comfirm_price > b:
                            zt.append(d.comfirm_date)
                            zt_boduan.append(i + 1)
                            zt_day.append(day_boduan.iloc[i + 1].comfirm_date)

                            append = True
                        else:
                            d_price = min_close.ix[
                                d.comfirm_date:day_boduan.iloc[
                                    i + 1].comfirm_date]
                            d_price = d_price[d_price > b]
                            if not d_price.empty:
                                zt.append(d_price.index[0])
                                zt_boduan.append(i + 1)
                                zt_day.append(
                                    day_boduan.iloc[
                                        i + 1].comfirm_date)

                                append = True

                        if append:
                            print zt[-1]
                            zt_type.append("raise")
                            zt_price.append(min_close.ix[zt[-1]])
                            price_boduan = day_close.ix[
                                zt[-1]:day_boduan.iloc[i + 1].comfirm_date]
                            premax = day_close.ix[day_boduan.iloc[
                                i].comfirm_date:zt[-1]].min()
                            nowmax = day_close.ix[
                                zt[-1]:day_boduan.iloc[i + 1].comfirm_date].min()
                            print premax, nowmax
                            if premax <= nowmax:
                                zt_success.append(1)
                                zt_false.append(zt[-1])
                                zt_false_price.append(zt_price[-1])
                                flag = False
                            else:
                                zt_success.append(0)
                                f = price_boduan[
                                    price_boduan < premax].index[0]
                                zt_false.append(f)
                                zt_false_price.append(min_close.ix[f])
                    j += 2

        zuji_situation = pd.DataFrame({'judge_date': zuji,
                                       'day_comfirm': zuji_day,
                                       'boduan_num': zuji_boduan,
                                       'success': zuji_success,
                                       'bd_type': zuji_type,
                                       'judge_price': zuji_price,
                                       'false_date': zuji_false,
                                       'false_price': zuji_false_price})

        tupo_situation = pd.DataFrame({'judge_date': tupo,
                                       'day_comfirm': tupo_day,
                                       'boduan_num': tupo_boduan,
                                       'success': tupo_success,
                                       'bd_type': tupo_type,
                                       'judge_price': tupo_price,
                                       'false_date': tupo_false,
                                       'false_price': tupo_false_price})

        zt_situation = pd.DataFrame({'judge_date': zt,
                                     'day_comfirm': zt_day,
                                     'boduan_num': zt_boduan,
                                     'success': zt_success,
                                     'bd_type': zt_type,
                                     'judge_price': zt_price,
                                     'false_date': zt_false,
                                     'false_price': zt_false_price})

        zuji_situation['boduan_start'] = zuji_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].start_date, axis=1)
        zuji_situation['boduan_end'] = zuji_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].end_date, axis=1)
        zuji_situation['comfirm_price'] = zuji_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].comfirm_price, axis=1)

        tupo_situation['boduan_start'] = tupo_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].start_date, axis=1)
        tupo_situation['boduan_end'] = tupo_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].end_date, axis=1)
        tupo_situation['comfirm_price'] = tupo_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].comfirm_price, axis=1)

        zt_situation['boduan_start'] = zt_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].start_date, axis=1)
        zt_situation['boduan_end'] = zt_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].end_date, axis=1)
        zt_situation['comfirm_price'] = zt_situation.apply(
            lambda x: day_boduan.iloc[x.boduan_num].comfirm_price, axis=1)

        def get_returns(row):
            if row.success == 1:
                return (
                    row.comfirm_price - row.judge_price) / row.judge_price if row.bd_type == "raise" else - (
                    row.comfirm_price - row.judge_price) / row.judge_price

            else:
                return row.false_price / row.judge_price - \
                    1 if row.bd_type == "raise" else - row.false_price / row.judge_price + 1

        zuji_situation['returns'] = zuji_situation.apply(
            lambda x: get_returns(x), axis=1)
        tupo_situation['returns'] = tupo_situation.apply(
            lambda x: get_returns(x), axis=1)
        zt_situation['returns'] = zt_situation.apply(
            lambda x: get_returns(x), axis=1)

        self.zuji_situation = zuji_situation
        self.tupo_situation = tupo_situation
        self.zujiplustupo = zt_situation

    def trade(self, situation):
        in_tupo_buy = False
        in_tupo_sell = False
        day_boduan = self.day_boduan
        min_boduan = self.min_boduan
        min_close = self.min_close
        day_close = self.day_close
        now_situation = self.now_situation
        duan_buy_date = []
        duan_sell_date = []
        for i in range(1, now_situation.shape[0]):
            today = now_situation.iloc[i]
            yesterday = now_situation.iloc[i - 1]
            if today.now_min_duannum == 8 and yesterday.now_min_duannum == 7:
                if today.now_day_situation == "decline":
                    duan_buy_date.append(now_situation.index[i])
                else:
                    duan_sell_date.append(now_situation.index[i])

        duan_buy = False
        duan_sell = False
        buy_date = day_boduan[
            day_boduan.bd_type == "raise"].comfirm_date.tolist()
        sell_date = day_boduan[
            day_boduan.bd_type == "decline"].comfirm_date.tolist()
        situation_date_buy = situation[
            situation.bd_type == "raise"].judge_date.tolist()
        situation_date_sell = situation[
            situation.bd_type == "decline"].judge_date.tolist()

        stream = []
        cash = 1.0
        p = 0.0
        for date in min_close.index:
            price_today = min_close.ix[date]

            if date in buy_date and cash > 0:
                p += cash / price_today
                cash = 0
                in_tupo_sell = False
                duan_sell = False
                print "buy in %s" % date

            if date in sell_date and p > 0:
                cash += p * price_today
                p = 0
                in_tupo_buy = False
                duan_buy = False
                print "sell in %s" % date

            if date in situation_date_buy and cash > 0:
                p += cash / price_today
                cash = 0
                in_tupo_buy = True
                duan_sell = False
                buyday = date
                print "situation_buy in %s" % date

            if date in situation_date_sell and p > 0:
                cash += p * price_today
                p = 0
                in_tupo_sell = True
                duan_buy = False
                sellday = date
                print "situation_sell in %s" % date

            if date in duan_buy_date and cash > 0:
                p += cash / price_today
                cash = 0
                duan_buy = True
                in_tupo_sell = False
                duan_buyday = date
                print "duan_buy in %s" % date

            if date in duan_sell_date and p > 0:
                cash += p * price_today
                p = 0
                duan_sell = True
                in_tupo_buy = False
                duan_sellday = date
                print "duan_sell in %s" % date

            if in_tupo_buy and p > 0:
                temp = day_boduan[day_boduan.comfirm_date < buyday]
                if not temp.empty:
                    precomfirm_date = temp.iloc[-1].comfirm_date
                    if price_today < day_close.ix[precomfirm_date:date].min():
                        cash += p * price_today
                        p = 0
                        in_tupo_buy = False

            if in_tupo_sell and cash > 0:
                temp = day_boduan[day_boduan.comfirm_date < sellday]
                if not temp.empty:
                    precomfirm_date = temp.iloc[-1].comfirm_date
                    if price_today > day_close.ix[precomfirm_date:date].max():
                        p += cash / price_today
                        cash = 0
                        in_tupo_sell = False

            if duan_buy and p > 0:
                temp = min_boduan[min_boduan.end_date < duan_buyday]
                if not temp.empty:
                    if price_today < temp.iloc[-1].end_price:
                        cash += p * price_today
                        p = 0
                        duan_buy = False

            if duan_sell and p > 0:
                temp = min_boduan[min_boduan.end_date < duan_sellday]
                if not temp.empty:
                    if price_today > temp.iloc[-1].end_price:
                        p += cash / price_today
                        cash = 0
                        duan_sell = False

            stream.append(cash + p * price_today)
        df = pd.DataFrame({'strategy': stream,
                           'benchmark': min_close.values},
                          index=min_close.index)

        df = df / df.iloc[0]
        return df

    def run(self):
        self.mapping()
        self.comfirm_num()
        self.misplace()
        self.restrict()
        self.day_situation()

