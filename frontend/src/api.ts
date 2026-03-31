import type {
  AssumptionYearItem,
  Company,
  FinancialDataItem,
  LineItemDef,
  PeriodDataResponse,
  PeriodResponse,
  Scenario,
  StatementsResponse,
  Template,
  TemplateDetail,
} from './types/financial';

const JSON_HEADERS = { 'Content-Type': 'application/json' };

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

function mergeHeaders(...objs: Record<string, string>[]): Record<string, string> {
  return Object.assign({}, ...objs);
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ── Companies ──────────────────────────────────────────

export async function fetchCompanies(): Promise<Company[]> {
  const res = await fetch('/api/companies/', { headers: authHeaders() });
  return handleResponse<Company[]>(res);
}

export async function createCompany(name: string, templateId: number): Promise<Company> {
  const res = await fetch('/api/companies/', {
    method: 'POST',
    headers: mergeHeaders(JSON_HEADERS, authHeaders()),
    body: JSON.stringify({ name, industry_template_id: templateId }),
  });
  return handleResponse<Company>(res);
}

export async function deleteCompany(id: number): Promise<void> {
  const res = await fetch(`/api/companies/${id}`, { method: 'DELETE', headers: authHeaders() });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
}

// ── Templates ──────────────────────────────────────────

export async function fetchTemplates(): Promise<Template[]> {
  const res = await fetch('/api/templates/', { headers: authHeaders() });
  return handleResponse<Template[]>(res);
}

export async function fetchTemplateDetail(id: number): Promise<TemplateDetail> {
  const res = await fetch(`/api/templates/${id}`, { headers: authHeaders() });
  return handleResponse<TemplateDetail>(res);
}

// ── Line Items ─────────────────────────────────────────

export async function fetchLineItems(statementType?: string): Promise<LineItemDef[]> {
  const url = statementType
    ? `/api/line-items/?statement_type=${statementType}`
    : '/api/line-items/';
  const res = await fetch(url, { headers: authHeaders() });
  return handleResponse<LineItemDef[]>(res);
}

// ── Periods ────────────────────────────────────────────

export async function fetchPeriods(companyId: number): Promise<PeriodResponse[]> {
  const res = await fetch(`/api/companies/${companyId}/periods/`, { headers: authHeaders() });
  return handleResponse<PeriodResponse[]>(res);
}

export async function createPeriod(companyId: number, year: number): Promise<PeriodResponse> {
  const res = await fetch(`/api/companies/${companyId}/periods/`, {
    method: 'POST',
    headers: mergeHeaders(JSON_HEADERS, authHeaders()),
    body: JSON.stringify({ year }),
  });
  return handleResponse<PeriodResponse>(res);
}

export async function getPeriodData(companyId: number, year: number): Promise<PeriodDataResponse> {
  const res = await fetch(`/api/companies/${companyId}/periods/${year}/data`, { headers: authHeaders() });
  return handleResponse<PeriodDataResponse>(res);
}

export async function upsertPeriodData(
  companyId: number,
  year: number,
  items: FinancialDataItem[],
): Promise<PeriodDataResponse> {
  const res = await fetch(`/api/companies/${companyId}/periods/${year}/data`, {
    method: 'PUT',
    headers: mergeHeaders(JSON_HEADERS, authHeaders()),
    body: JSON.stringify({ items }),
  });
  return handleResponse<PeriodDataResponse>(res);
}

// ── Scenarios ──────────────────────────────────────────

export async function fetchScenarios(companyId: number): Promise<Scenario[]> {
  const res = await fetch(`/api/companies/${companyId}/scenarios/`, { headers: authHeaders() });
  return handleResponse<Scenario[]>(res);
}

export async function createScenario(companyId: number, name: string): Promise<Scenario> {
  const res = await fetch(`/api/companies/${companyId}/scenarios/`, {
    method: 'POST',
    headers: mergeHeaders(JSON_HEADERS, authHeaders()),
    body: JSON.stringify({ name }),
  });
  return handleResponse<Scenario>(res);
}

// ── Assumptions ────────────────────────────────────────

export async function getAssumptions(
  companyId: number,
  scenarioId: number,
): Promise<AssumptionYearItem[]> {
  const res = await fetch(
    `/api/companies/${companyId}/scenarios/${scenarioId}/assumptions`,
    { headers: authHeaders() },
  );
  return handleResponse<AssumptionYearItem[]>(res);
}

export async function updateAssumptions(
  companyId: number,
  scenarioId: number,
  assumptions: AssumptionYearItem[],
): Promise<AssumptionYearItem[]> {
  const res = await fetch(
    `/api/companies/${companyId}/scenarios/${scenarioId}/assumptions`,
    {
      method: 'PUT',
      headers: mergeHeaders(JSON_HEADERS, authHeaders()),
      body: JSON.stringify({ assumptions }),
    },
  );
  return handleResponse<AssumptionYearItem[]>(res);
}

// ── Forecast ───────────────────────────────────────────

export async function runForecast(
  companyId: number,
  scenarioId: number,
  forecastYears: number[],
): Promise<{ status: string; forecast_years: number[] }> {
  const res = await fetch(
    `/api/companies/${companyId}/scenarios/${scenarioId}/forecast`,
    {
      method: 'POST',
      headers: mergeHeaders(JSON_HEADERS, authHeaders()),
      body: JSON.stringify({ forecast_years: forecastYears }),
    },
  );
  return handleResponse<{ status: string; forecast_years: number[] }>(res);
}

// ── Statements ─────────────────────────────────────────

export async function getStatements(
  companyId: number,
  scenarioId: number,
): Promise<StatementsResponse> {
  const res = await fetch(
    `/api/companies/${companyId}/scenarios/${scenarioId}/statements`,
    { headers: authHeaders() },
  );
  return handleResponse<StatementsResponse>(res);
}

// ── Export ─────────────────────────────────────────────

export function getExportExcelUrl(companyId: number, scenarioId: number): string {
  return `/api/companies/${companyId}/scenarios/${scenarioId}/export/excel`;
}

export function getExportPdfUrl(companyId: number, scenarioId: number): string {
  return `/api/companies/${companyId}/scenarios/${scenarioId}/export/pdf`;
}

export async function downloadExport(url: string, filename: string): Promise<void> {
  const res = await fetch(url, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Export failed: ${res.status}`);
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
