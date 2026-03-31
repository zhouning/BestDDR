"""
科目字典定义 — 按中国企业会计准则
Line item definitions following Chinese Accounting Standards (CAS)

Each tuple: (code, statement_type, name_cn, name_en, parent_code, sort_order, item_type, formula, indent, bold)
"""

LINE_ITEMS: list[tuple] = []

# ══════════════════════════════════════════════════════════════
# 利润表 (Income Statement)
# ══════════════════════════════════════════════════════════════

_IS = "IS"
_IN = "INPUT"
_CALC = "CALCULATED"
_SUB = "SUBTOTAL"

LINE_ITEMS += [
    # code, stmt, name_cn, name_en, parent, sort, type, formula, indent, bold
    ("IS_001", _IS, "一、营业收入", "Revenue", None, 100, _IN, None, 0, True),
    ("IS_002", _IS, "减：营业成本", "Cost of Revenue", None, 200, _IN, None, 1, False),
    ("IS_003", _IS, "税金及附加", "Tax and Surcharges", None, 300, _IN, None, 1, False),
    ("IS_004", _IS, "销售费用", "Selling Expenses", None, 400, _IN, None, 1, False),
    ("IS_005", _IS, "管理费用", "G&A Expenses", None, 500, _IN, None, 1, False),
    ("IS_006", _IS, "研发费用", "R&D Expenses", None, 600, _IN, None, 1, False),
    ("IS_007", _IS, "财务费用", "Finance Costs", None, 700, _IN, None, 1, False),
    ("IS_008", _IS, "其中：利息费用", "Interest Expense", "IS_007", 710, _IN, None, 2, False),
    ("IS_009", _IS, "利息收入", "Interest Income", "IS_007", 720, _IN, None, 2, False),
    ("IS_010", _IS, "加：其他收益", "Other Income", None, 800, _IN, None, 1, False),
    ("IS_011", _IS, "投资收益", "Investment Income", None, 900, _IN, None, 1, False),
    ("IS_012", _IS, "公允价值变动收益", "FV Change Gains", None, 1000, _IN, None, 1, False),
    ("IS_013", _IS, "信用减值损失", "Credit Impairment Loss", None, 1100, _IN, None, 1, False),
    ("IS_014", _IS, "资产减值损失", "Asset Impairment Loss", None, 1200, _IN, None, 1, False),
    ("IS_015", _IS, "资产处置收益", "Asset Disposal Gains", None, 1300, _IN, None, 1, False),
    (
        "IS_100",
        _IS,
        "二、营业利润",
        "Operating Profit",
        None,
        2000,
        _CALC,
        "IS_001 - IS_002 - IS_003 - IS_004 - IS_005 - IS_006 - IS_007 + IS_010 + IS_011 + IS_012 - IS_013 - IS_014 + IS_015",
        0,
        True,
    ),
    ("IS_101", _IS, "加：营业外收入", "Non-operating Income", None, 2100, _IN, None, 1, False),
    ("IS_102", _IS, "减：营业外支出", "Non-operating Expenses", None, 2200, _IN, None, 1, False),
    (
        "IS_200",
        _IS,
        "三、利润总额",
        "Total Profit",
        None,
        3000,
        _CALC,
        "IS_100 + IS_101 - IS_102",
        0,
        True,
    ),
    ("IS_201", _IS, "减：所得税费用", "Income Tax Expense", None, 3100, _IN, None, 1, False),
    (
        "IS_300",
        _IS,
        "四、净利润",
        "Net Profit",
        None,
        4000,
        _CALC,
        "IS_200 - IS_201",
        0,
        True,
    ),
]

# ══════════════════════════════════════════════════════════════
# 资产负债表 (Balance Sheet)
# ══════════════════════════════════════════════════════════════

_BS = "BS"

LINE_ITEMS += [
    # ── 流动资产 ──
    ("BS_A_000", _BS, "流动资产：", "Current Assets:", None, 100, _SUB, None, 0, True),
    ("BS_A_001", _BS, "货币资金", "Cash and Cash Equivalents", "BS_A_000", 110, _IN, None, 1, False),
    ("BS_A_002", _BS, "交易性金融资产", "Trading Financial Assets", "BS_A_000", 120, _IN, None, 1, False),
    ("BS_A_003", _BS, "应收票据", "Notes Receivable", "BS_A_000", 130, _IN, None, 1, False),
    ("BS_A_004", _BS, "应收账款", "Accounts Receivable", "BS_A_000", 140, _IN, None, 1, False),
    ("BS_A_005", _BS, "应收款项融资", "Receivables Financing", "BS_A_000", 150, _IN, None, 1, False),
    ("BS_A_006", _BS, "预付款项", "Prepayments", "BS_A_000", 160, _IN, None, 1, False),
    ("BS_A_007", _BS, "其他应收款", "Other Receivables", "BS_A_000", 170, _IN, None, 1, False),
    ("BS_A_008", _BS, "存货", "Inventory", "BS_A_000", 180, _IN, None, 1, False),
    ("BS_A_009", _BS, "合同资产", "Contract Assets", "BS_A_000", 190, _IN, None, 1, False),
    ("BS_A_010", _BS, "其他流动资产", "Other Current Assets", "BS_A_000", 200, _IN, None, 1, False),
    (
        "BS_A_100",
        _BS,
        "流动资产合计",
        "Total Current Assets",
        None,
        300,
        _CALC,
        "BS_A_001 + BS_A_002 + BS_A_003 + BS_A_004 + BS_A_005 + BS_A_006 + BS_A_007 + BS_A_008 + BS_A_009 + BS_A_010",
        0,
        True,
    ),
    # ── 非流动资产 ──
    ("BS_A_200", _BS, "非流动资产：", "Non-current Assets:", None, 400, _SUB, None, 0, True),
    ("BS_A_201", _BS, "长期股权投资", "Long-term Equity Investments", "BS_A_200", 410, _IN, None, 1, False),
    ("BS_A_202", _BS, "其他非流动金融资产", "Other Non-current Financial Assets", "BS_A_200", 420, _IN, None, 1, False),
    ("BS_A_203", _BS, "投资性房地产", "Investment Property", "BS_A_200", 430, _IN, None, 1, False),
    ("BS_A_204", _BS, "固定资产", "Property, Plant & Equipment", "BS_A_200", 440, _IN, None, 1, False),
    ("BS_A_205", _BS, "在建工程", "Construction in Progress", "BS_A_200", 450, _IN, None, 1, False),
    ("BS_A_206", _BS, "使用权资产", "Right-of-use Assets", "BS_A_200", 460, _IN, None, 1, False),
    ("BS_A_207", _BS, "无形资产", "Intangible Assets", "BS_A_200", 470, _IN, None, 1, False),
    ("BS_A_208", _BS, "商誉", "Goodwill", "BS_A_200", 480, _IN, None, 1, False),
    ("BS_A_209", _BS, "长期待摊费用", "Long-term Deferred Expenses", "BS_A_200", 490, _IN, None, 1, False),
    ("BS_A_210", _BS, "递延所得税资产", "Deferred Tax Assets", "BS_A_200", 500, _IN, None, 1, False),
    ("BS_A_211", _BS, "其他非流动资产", "Other Non-current Assets", "BS_A_200", 510, _IN, None, 1, False),
    (
        "BS_A_300",
        _BS,
        "非流动资产合计",
        "Total Non-current Assets",
        None,
        600,
        _CALC,
        "BS_A_201 + BS_A_202 + BS_A_203 + BS_A_204 + BS_A_205 + BS_A_206 + BS_A_207 + BS_A_208 + BS_A_209 + BS_A_210 + BS_A_211",
        0,
        True,
    ),
    (
        "BS_A_999",
        _BS,
        "资产总计",
        "Total Assets",
        None,
        700,
        _CALC,
        "BS_A_100 + BS_A_300",
        0,
        True,
    ),
    # ── 流动负债 ──
    ("BS_L_000", _BS, "流动负债：", "Current Liabilities:", None, 800, _SUB, None, 0, True),
    ("BS_L_001", _BS, "短期借款", "Short-term Borrowings", "BS_L_000", 810, _IN, None, 1, False),
    ("BS_L_002", _BS, "交易性金融负债", "Trading Financial Liabilities", "BS_L_000", 820, _IN, None, 1, False),
    ("BS_L_003", _BS, "应付票据", "Notes Payable", "BS_L_000", 830, _IN, None, 1, False),
    ("BS_L_004", _BS, "应付账款", "Accounts Payable", "BS_L_000", 840, _IN, None, 1, False),
    ("BS_L_005", _BS, "预收款项", "Advances from Customers", "BS_L_000", 850, _IN, None, 1, False),
    ("BS_L_006", _BS, "合同负债", "Contract Liabilities", "BS_L_000", 860, _IN, None, 1, False),
    ("BS_L_007", _BS, "应付职工薪酬", "Employee Benefits Payable", "BS_L_000", 870, _IN, None, 1, False),
    ("BS_L_008", _BS, "应交税费", "Taxes Payable", "BS_L_000", 880, _IN, None, 1, False),
    ("BS_L_009", _BS, "其他应付款", "Other Payables", "BS_L_000", 890, _IN, None, 1, False),
    ("BS_L_010", _BS, "一年内到期的非流动负债", "Non-current Liabilities Due Within 1 Year", "BS_L_000", 900, _IN, None, 1, False),
    ("BS_L_011", _BS, "其他流动负债", "Other Current Liabilities", "BS_L_000", 910, _IN, None, 1, False),
    (
        "BS_L_100",
        _BS,
        "流动负债合计",
        "Total Current Liabilities",
        None,
        1000,
        _CALC,
        "BS_L_001 + BS_L_002 + BS_L_003 + BS_L_004 + BS_L_005 + BS_L_006 + BS_L_007 + BS_L_008 + BS_L_009 + BS_L_010 + BS_L_011",
        0,
        True,
    ),
    # ── 非流动负债 ──
    ("BS_L_200", _BS, "非流动负债：", "Non-current Liabilities:", None, 1100, _SUB, None, 0, True),
    ("BS_L_201", _BS, "长期借款", "Long-term Borrowings", "BS_L_200", 1110, _IN, None, 1, False),
    ("BS_L_202", _BS, "应付债券", "Bonds Payable", "BS_L_200", 1120, _IN, None, 1, False),
    ("BS_L_203", _BS, "租赁负债", "Lease Liabilities", "BS_L_200", 1130, _IN, None, 1, False),
    ("BS_L_204", _BS, "长期应付款", "Long-term Payables", "BS_L_200", 1140, _IN, None, 1, False),
    ("BS_L_205", _BS, "预计负债", "Provisions", "BS_L_200", 1150, _IN, None, 1, False),
    ("BS_L_206", _BS, "递延收益", "Deferred Revenue", "BS_L_200", 1160, _IN, None, 1, False),
    ("BS_L_207", _BS, "递延所得税负债", "Deferred Tax Liabilities", "BS_L_200", 1170, _IN, None, 1, False),
    ("BS_L_208", _BS, "其他非流动负债", "Other Non-current Liabilities", "BS_L_200", 1180, _IN, None, 1, False),
    (
        "BS_L_300",
        _BS,
        "非流动负债合计",
        "Total Non-current Liabilities",
        None,
        1200,
        _CALC,
        "BS_L_201 + BS_L_202 + BS_L_203 + BS_L_204 + BS_L_205 + BS_L_206 + BS_L_207 + BS_L_208",
        0,
        True,
    ),
    (
        "BS_L_999",
        _BS,
        "负债合计",
        "Total Liabilities",
        None,
        1300,
        _CALC,
        "BS_L_100 + BS_L_300",
        0,
        True,
    ),
    # ── 所有者权益 ──
    ("BS_E_000", _BS, "所有者权益：", "Owner's Equity:", None, 1400, _SUB, None, 0, True),
    ("BS_E_001", _BS, "实收资本（股本）", "Paid-in Capital", "BS_E_000", 1410, _IN, None, 1, False),
    ("BS_E_002", _BS, "资本公积", "Capital Reserve", "BS_E_000", 1420, _IN, None, 1, False),
    ("BS_E_003", _BS, "其他综合收益", "Other Comprehensive Income", "BS_E_000", 1430, _IN, None, 1, False),
    ("BS_E_004", _BS, "盈余公积", "Surplus Reserve", "BS_E_000", 1440, _IN, None, 1, False),
    ("BS_E_005", _BS, "未分配利润", "Retained Earnings", "BS_E_000", 1450, _IN, None, 1, False),
    (
        "BS_E_100",
        _BS,
        "所有者权益合计",
        "Total Owner's Equity",
        None,
        1500,
        _CALC,
        "BS_E_001 + BS_E_002 + BS_E_003 + BS_E_004 + BS_E_005",
        0,
        True,
    ),
    (
        "BS_999",
        _BS,
        "负债和所有者权益总计",
        "Total Liabilities and Equity",
        None,
        1600,
        _CALC,
        "BS_L_999 + BS_E_100",
        0,
        True,
    ),
]

# ══════════════════════════════════════════════════════════════
# 现金流量表 (Cash Flow Statement) — 间接法
# ══════════════════════════════════════════════════════════════

_CF = "CF"

LINE_ITEMS += [
    # ── 经营活动 ──
    ("CF_O_000", _CF, "一、经营活动产生的现金流量：", "Cash Flows from Operating Activities:", None, 100, _SUB, None, 0, True),
    ("CF_O_001", _CF, "净利润", "Net Profit", "CF_O_000", 110, _IN, None, 1, False),
    ("CF_O_002", _CF, "加：资产减值准备", "Asset Impairment Provisions", "CF_O_000", 120, _IN, None, 1, False),
    ("CF_O_003", _CF, "固定资产折旧", "Depreciation of PPE", "CF_O_000", 130, _IN, None, 1, False),
    ("CF_O_004", _CF, "无形资产摊销", "Amortization of Intangibles", "CF_O_000", 140, _IN, None, 1, False),
    ("CF_O_005", _CF, "长期待摊费用摊销", "Amortization of Long-term Deferred Exp.", "CF_O_000", 150, _IN, None, 1, False),
    ("CF_O_006", _CF, "处置固定资产损失", "Loss on Disposal of PPE", "CF_O_000", 160, _IN, None, 1, False),
    ("CF_O_007", _CF, "公允价值变动损失", "Loss on FV Changes", "CF_O_000", 170, _IN, None, 1, False),
    ("CF_O_008", _CF, "财务费用", "Finance Costs", "CF_O_000", 180, _IN, None, 1, False),
    ("CF_O_009", _CF, "投资损失", "Investment Losses", "CF_O_000", 190, _IN, None, 1, False),
    ("CF_O_010", _CF, "递延所得税变动", "Change in Deferred Tax", "CF_O_000", 200, _IN, None, 1, False),
    ("CF_O_011", _CF, "存货的减少", "Decrease in Inventory", "CF_O_000", 210, _IN, None, 1, False),
    ("CF_O_012", _CF, "经营性应收项目的减少", "Decrease in Operating Receivables", "CF_O_000", 220, _IN, None, 1, False),
    ("CF_O_013", _CF, "经营性应付项目的增加", "Increase in Operating Payables", "CF_O_000", 230, _IN, None, 1, False),
    ("CF_O_014", _CF, "其他", "Others", "CF_O_000", 240, _IN, None, 1, False),
    (
        "CF_O_100",
        _CF,
        "经营活动产生的现金流量净额",
        "Net Cash from Operating Activities",
        None,
        300,
        _CALC,
        "CF_O_001 + CF_O_002 + CF_O_003 + CF_O_004 + CF_O_005 + CF_O_006 + CF_O_007 + CF_O_008 + CF_O_009 + CF_O_010 + CF_O_011 + CF_O_012 + CF_O_013 + CF_O_014",
        0,
        True,
    ),
    # ── 投资活动 ──
    ("CF_I_000", _CF, "二、投资活动产生的现金流量：", "Cash Flows from Investing Activities:", None, 400, _SUB, None, 0, True),
    ("CF_I_001", _CF, "收回投资收到的现金", "Cash from Investment Recovery", "CF_I_000", 410, _IN, None, 1, False),
    ("CF_I_002", _CF, "取得投资收益收到的现金", "Cash from Investment Income", "CF_I_000", 420, _IN, None, 1, False),
    ("CF_I_003", _CF, "处置固定资产收到的现金", "Cash from Disposal of PPE", "CF_I_000", 430, _IN, None, 1, False),
    ("CF_I_004", _CF, "购建固定资产支付的现金", "Cash Paid for PPE", "CF_I_000", 440, _IN, None, 1, False),
    ("CF_I_005", _CF, "投资支付的现金", "Cash Paid for Investments", "CF_I_000", 450, _IN, None, 1, False),
    ("CF_I_006", _CF, "其他投资活动现金流", "Other Investing Cash Flows", "CF_I_000", 460, _IN, None, 1, False),
    (
        "CF_I_100",
        _CF,
        "投资活动产生的现金流量净额",
        "Net Cash from Investing Activities",
        None,
        500,
        _CALC,
        "CF_I_001 + CF_I_002 + CF_I_003 - CF_I_004 - CF_I_005 + CF_I_006",
        0,
        True,
    ),
    # ── 筹资活动 ──
    ("CF_F_000", _CF, "三、筹资活动产生的现金流量：", "Cash Flows from Financing Activities:", None, 600, _SUB, None, 0, True),
    ("CF_F_001", _CF, "吸收投资收到的现金", "Cash from Equity Financing", "CF_F_000", 610, _IN, None, 1, False),
    ("CF_F_002", _CF, "取得借款收到的现金", "Cash from Borrowings", "CF_F_000", 620, _IN, None, 1, False),
    ("CF_F_003", _CF, "偿还债务支付的现金", "Cash Paid for Debt Repayment", "CF_F_000", 630, _IN, None, 1, False),
    ("CF_F_004", _CF, "分配股利、利润或偿付利息支付的现金", "Cash Paid for Dividends and Interest", "CF_F_000", 640, _IN, None, 1, False),
    ("CF_F_005", _CF, "其他筹资活动现金流", "Other Financing Cash Flows", "CF_F_000", 650, _IN, None, 1, False),
    (
        "CF_F_100",
        _CF,
        "筹资活动产生的现金流量净额",
        "Net Cash from Financing Activities",
        None,
        700,
        _CALC,
        "CF_F_001 + CF_F_002 - CF_F_003 - CF_F_004 + CF_F_005",
        0,
        True,
    ),
    # ── 汇总 ──
    (
        "CF_900",
        _CF,
        "四、现金及现金等价物净增加额",
        "Net Increase in Cash",
        None,
        800,
        _CALC,
        "CF_O_100 + CF_I_100 + CF_F_100",
        0,
        True,
    ),
    ("CF_901", _CF, "加：期初现金及现金等价物余额", "Opening Cash Balance", None, 810, _IN, None, 1, False),
    (
        "CF_999",
        _CF,
        "五、期末现金及现金等价物余额",
        "Closing Cash Balance",
        None,
        900,
        _CALC,
        "CF_900 + CF_901",
        0,
        True,
    ),
]


# ══════════════════════════════════════════════════════════════
# Default assumptions for 通用模板 (General Template)
# ══════════════════════════════════════════════════════════════

DEFAULT_ASSUMPTIONS = [
    # (param_key, display_name, category, default_value)
    # ── Income Statement ──
    ("revenue_growth_rate", "营收增长率 (%)", "IS", 10.0),
    ("gross_margin", "毛利率 (%)", "IS", 40.0),
    ("selling_expense_ratio", "销售费用率 (%)", "IS", 8.0),
    ("admin_expense_ratio", "管理费用率 (%)", "IS", 5.0),
    ("rnd_expense_ratio", "研发费用率 (%)", "IS", 3.0),
    ("tax_surcharge_ratio", "税金及附加占比 (%)", "IS", 1.5),
    ("effective_tax_rate", "有效所得税率 (%)", "IS", 25.0),
    # ── Balance Sheet ──
    ("dso_days", "应收账款周转天数", "BS", 60.0),
    ("dio_days", "存货周转天数", "BS", 45.0),
    ("dpo_days", "应付账款周转天数", "BS", 30.0),
    ("capex_ratio", "资本开支占营收比 (%)", "BS", 5.0),
    ("depreciation_rate", "固定资产折旧率 (%)", "BS", 10.0),
    ("amortization_rate", "无形资产摊销率 (%)", "BS", 10.0),
    ("prepayment_ratio", "预付款占营收比 (%)", "BS", 2.0),
    ("contract_liability_ratio", "合同负债占营收比 (%)", "BS", 3.0),
    # ── Cash / Financing ──
    ("dividend_payout_ratio", "分红比例 (%)", "CF", 30.0),
    ("surplus_reserve_ratio", "盈余公积提取比例 (%)", "CF", 10.0),
    ("interest_rate", "借款利率 (%)", "CF", 4.5),
    ("short_term_debt", "短期借款 (万元)", "CF", 0.0),
    ("long_term_debt", "长期借款 (万元)", "CF", 0.0),
    ("new_equity", "新增股本 (万元)", "CF", 0.0),
]
