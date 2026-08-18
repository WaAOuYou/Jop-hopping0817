# -*- coding: utf-8 -*-
"""
check_quiz_answers.py —— 自查测验参考答案
⚠️ 只在 D4 写完并计时结束后,或 D5 对答案时再看。先看等于没考。
每一题下面都标了它对应的 SQL,方便你对照自己的 SQL 直觉。
"""
import pandas as pd
import numpy as np

# ---------- 数据(与 check_quiz.py 一致) ----------
orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 102, 114],
    "user_id":  [1, 2, 1, 3, 4, 2, 5, 1, 4, 6, 2, 3, 2, 7],
    "date":     ["2026-01-03", "2026-01-05", "2026-01-09", "2026-01-12", "2026-01-15",
                 "2026-02-02", "2026-02-07", "2026-02-11", "2026-02-14", "2026-02-18",
                 "2026-02-22", "2026-02-25", "2026-01-05", "2026-02-28"],
    "region":   ["华东", "华南", "华东", "华北", "华南", "华东", "华北", "华南", "华东", "华北", "华南", "华北", "华南", "华东"],
    "category": ["手机", "家电", "手机", "服饰", "家电", "手机", "服饰", "家电", "手机", "服饰", "手机", "家电", "家电", "服饰"],
    "quantity": [2, 1, None, 3, 1, 2, 4, 1, 2, None, 1, 3, 1, 2],
    "price":    ["1999", "4599", "2699", "129", "1299", "2199", "99", "4599", "2699", "199", "1999", "1599", "4599", "299"],
})

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5, 7],
    "name":    ["Alice", "Bob", "Cathy", "David", "Eva", "Fiona"],
    "city":    ["上海", "广州", "北京", "深圳", "杭州", "上海"],
    "level":   ["VIP", "普通", "普通", "VIP", "普通", "普通"],
})

# ---------- Q1:看表(等价于 DESC / 空值巡检) ----------
print("Q1 形状:", orders.shape)            # (14, 7)
print("Q1 列名:", list(orders.columns))
print("Q1 缺失值:\n", orders.isna().sum())   # quantity 有 2 个缺失

# ---------- Q2:类型转换(等价于 CAST) ----------
orders["date"] = pd.to_datetime(orders["date"])
orders["price"] = orders["price"].astype(float)
print("Q2 dtypes:\n", orders.dtypes)

# ---------- Q3:计算列(等价于 SELECT ..., price*qty AS total) ----------
orders["total"] = orders["price"] * orders["quantity"]

# ---------- Q4:去重(等价于 SELECT DISTINCT,保留第一条) ----------
print("Q4 去重前行数:", len(orders))       # 14
orders = orders.drop_duplicates()          # 14 行 → 13 行(order_id=102 出现了两次,完全重复)
print("Q4 去重后行数:", len(orders))       # 13

# ---------- Q5:筛选 + 选列(等价于 WHERE region='华南' AND total>1000) ----------
south_high = orders[(orders["region"] == "华南") & (orders["total"] > 1000)]
print("Q5 华南高额订单:\n", south_high[["order_id", "total"]])   # 4 行

# ---------- Q6:按类别均价向下取整填充缺失(等价于 COALESCE + 窗口均值) ----------
avg_qty = orders.groupby("category")["quantity"].transform("mean").apply(np.floor)
orders["quantity"] = orders["quantity"].fillna(avg_qty)
print("Q6 填充后 quantity 缺失数:", orders["quantity"].isna().sum())   # 0

# ---------- Q7:分组聚合(等价于 GROUP BY region + 聚合函数) ----------
grp = orders.groupby("region").agg(
    订单数=("order_id", "count"),
    总金额=("total", "sum"),
    平均单价=("price", "mean"),
)
print("Q7 按地区:\n", grp)

# ---------- Q8:多列分组(等价于 GROUP BY region, category) ----------
reg_cat = orders.groupby(["region", "category"])["total"].sum()
reg_cat = reg_cat[reg_cat.notna()]
print("Q8 按地区×品类:\n", reg_cat)

# ---------- Q9:按月聚合(等价于 DATE_TRUNC('month', date)) ----------
orders["month"] = orders["date"].dt.to_period("M")
monthly = orders.groupby("month")["total"].sum()
print("Q9 每月金额:\n", monthly)

# ---------- Q10:左连接 + 城市统计 + 孤儿(等价于 LEFT JOIN + 查找不存在) ----------
merged = orders.merge(users, on="user_id", how="left")
city_stats = merged.groupby("city").agg(
    下单用户数=("user_id", "nunique"),   # 上海有 user 1 和 7,应 = 2(和 count 的区别就在这)
    订单总金额=("total", "sum"),
)
print("Q10 各城市:\n", city_stats)

orphan = orders[~orders["user_id"].isin(users["user_id"])]["user_id"].unique()
print("Q10 孤儿 user_id:", orphan)   # [6] —— user 6 在 users 表里不存在
