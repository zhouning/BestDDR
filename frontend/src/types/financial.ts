export interface Company {
  id: number;
  name: string;
  industry_template_id: number;
  created_at: string;
}

export interface Template {
  id: number;
  code: string;
  name: string;
  description: string | null;
}

export interface TemplateDetail extends Template {
  default_assumptions: AssumptionItem[];
}

export interface AssumptionItem {
  param_key: string;
  display_name: string;
  category: string;
  param_value: number;
}

export interface AssumptionYearItem {
  year: number;
  param_key: string;
  param_value: number;
}

export interface FinancialDataItem {
  line_item_code: string;
  value: number;
  is_override?: boolean;
}

export interface PeriodDataResponse {
  year: number;
  period_type: string;
  data: FinancialDataItem[];
}

export interface PeriodResponse {
  id: number;
  year: number;
  period_type: string;
  scenario_id: number | null;
}

export interface Scenario {
  id: number;
  name: string;
  company_id: number;
}

export interface LineItemRow {
  code: string;
  name_cn: string;
  name_en: string;
  indent_level: number;
  is_bold: boolean;
  values: Record<number, number>;
  is_override: Record<number, boolean>;
}

export interface StatementResponse {
  statement_type: string;
  rows: LineItemRow[];
  years: number[];
  period_types: Record<number, string>;
}

export interface StatementsResponse {
  income_statement: StatementResponse;
  balance_sheet: StatementResponse;
  cash_flow: StatementResponse;
}

export interface LineItemDef {
  code: string;
  statement_type: string;
  name_cn: string;
  name_en: string;
  parent_code: string | null;
  sort_order: number;
  item_type: string;
  indent_level: number;
  is_bold: boolean;
}
