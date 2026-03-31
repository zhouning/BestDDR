import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Tabs, Button, InputNumber, Select, Space, Spin, Table, Tag, Input,
  message, Typography, Card, Empty, Collapse, Segmented, Tooltip, Alert,
} from 'antd';
import {
  SaveOutlined, ThunderboltOutlined, PlusOutlined,
  CheckCircleFilled, CloseCircleFilled, FileExcelOutlined, FilePdfOutlined,
  ArrowLeftOutlined, InfoCircleOutlined,
} from '@ant-design/icons';
import {
  fetchPeriods, createPeriod, getPeriodData, upsertPeriodData,
  fetchScenarios, createScenario, getAssumptions, updateAssumptions,
  runForecast, getStatements, fetchLineItems, fetchTemplateDetail, fetchCompanies,
  getExportExcelUrl, getExportPdfUrl, downloadExport,
} from '../api';
import type {
  Company, PeriodResponse, FinancialDataItem, LineItemDef, Scenario,
  AssumptionYearItem, AssumptionItem, StatementsResponse, StatementResponse,
} from '../types/financial';

const { Title, Text } = Typography;

export default function CompanyDetail() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const companyId = Number(id);
  const navigate = useNavigate();
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanies()
      .then((companies) => setCompany(companies.find((c) => c.id === companyId) ?? null))
      .catch((err) => message.error(t('detail.history.loadFailed') + ': ' + (err as Error).message))
      .finally(() => setLoading(false));
  }, [companyId, t]);

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 80 }}><Spin size="large" /></div>;
  if (!company) return <Empty description={t('detail.companyNotFound')} />;

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')}>{t('back')}</Button>
        <Title level={3} style={{ margin: 0 }}>{company.name}</Title>
      </Space>

      <Tabs
        defaultActiveKey="history"
        items={[
          { key: 'history', label: t('detail.tabs.history'), children: <HistoryTab companyId={companyId} /> },
          { key: 'assumptions', label: t('detail.tabs.assumptions'), children: <AssumptionsTab companyId={companyId} templateId={company.industry_template_id} /> },
          { key: 'statements', label: t('detail.tabs.statements'), children: <StatementsTab companyId={companyId} /> },
          { key: 'export', label: t('detail.tabs.export'), children: <ExportTab companyId={companyId} /> },
        ]}
      />
    </>
  );
}

/* ── History Tab ─────────────────────────────────────── */

function HistoryTab({ companyId }: { companyId: number }) {
  const { t } = useTranslation();
  const [periods, setPeriods] = useState<PeriodResponse[]>([]);
  const [lineItems, setLineItems] = useState<LineItemDef[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [data, setData] = useState<Record<string, number>>({});
  const [newYear, setNewYear] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [loadingData, setLoadingData] = useState(false);

  const loadPeriods = useCallback(async () => {
    try {
      const [p, li] = await Promise.all([fetchPeriods(companyId), fetchLineItems()]);
      setPeriods(p.filter((pr) => pr.period_type === 'HISTORICAL'));
      setLineItems(li);
    } catch (err) {
      message.error(t('detail.history.loadFailed') + ': ' + (err as Error).message);
    }
  }, [companyId, t]);

  useEffect(() => { void loadPeriods(); }, [loadPeriods]);

  async function handleAddYear() {
    if (!newYear || newYear < 1900 || newYear > 2100) return;
    try {
      await createPeriod(companyId, newYear);
      message.success(t('detail.history.yearAdded', { year: newYear }));
      setNewYear(null);
      await loadPeriods();
      await handleSelectYear(newYear);
    } catch (err) {
      message.error(t('detail.history.failed') + ': ' + (err as Error).message);
    }
  }

  async function handleSelectYear(year: number) {
    setSelectedYear(year);
    setLoadingData(true);
    try {
      const res = await getPeriodData(companyId, year);
      const map: Record<string, number> = {};
      for (const item of res.data) map[item.line_item_code] = item.value;
      setData(map);
    } catch (err) {
      message.error(t('detail.history.failed') + ': ' + (err as Error).message);
    } finally {
      setLoadingData(false);
    }
  }

  async function handleSave() {
    if (selectedYear === null) return;
    setSaving(true);
    try {
      const items: FinancialDataItem[] = Object.entries(data)
        .filter(([, v]) => v !== 0)
        .map(([code, value]) => ({ line_item_code: code, value }));
      await upsertPeriodData(companyId, selectedYear, items);
      message.success(t('detail.history.dataSaved'));
    } catch (err) {
      message.error(t('detail.history.saveFailed') + ': ' + (err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  const groups = [
    { type: 'IS', label: t('detail.history.incomeStatement') },
    { type: 'BS', label: t('detail.history.balanceSheet') },
    { type: 'CF', label: t('detail.history.cashFlow') },
  ];

  return (
    <>
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space>
          <InputNumber
            value={newYear}
            onChange={(v) => setNewYear(v)}
            placeholder={t('detail.history.yearPlaceholder')}
            min={1900} max={2100}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => void handleAddYear()}>
            {t('detail.history.addYear')}
          </Button>
          {periods.length > 0 && (
            <Segmented
              value={selectedYear ?? undefined}
              options={periods.map((p) => ({ label: String(p.year), value: p.year }))}
              onChange={(v) => void handleSelectYear(v as number)}
            />
          )}
        </Space>
      </Card>

      {loadingData && <div style={{ textAlign: 'center', padding: 40 }}><Spin /></div>}

      {selectedYear !== null && !loadingData && (
        <>
          <Collapse
            defaultActiveKey={['IS']}
            items={groups.map((g) => ({
              key: g.type,
              label: <Text strong>{g.label}</Text>,
              children: (
                <Table
                  size="small"
                  pagination={false}
                  dataSource={lineItems.filter((li) => li.statement_type === g.type)}
                  rowKey="code"
                  columns={[
                    {
                      title: t('detail.history.lineItem'),
                      dataIndex: 'name_cn',
                      render: (_, li) => (
                        <span style={{ paddingLeft: li.indent_level * 20, fontWeight: li.is_bold ? 600 : 400 }}>
                          {li.name_cn}
                          <Text type="secondary" style={{ fontSize: 11, marginLeft: 6 }}>{li.code}</Text>
                        </span>
                      ),
                    },
                    {
                      title: `${selectedYear}`,
                      width: 180,
                      render: (_, li) => (
                        <InputNumber
                          size="small"
                          style={{ width: '100%' }}
                          value={data[li.code] ?? undefined}
                          onChange={(v) => setData((prev) => ({ ...prev, [li.code]: v ?? 0 }))}
                          formatter={(v) => v ? Number(v).toLocaleString() : ''}
                          parser={(v) => Number((v || '').replace(/,/g, '')) as 0}
                        />
                      ),
                    },
                  ]}
                />
              ),
            }))}
          />
          <div style={{ marginTop: 16, textAlign: 'right' }}>
            <Button type="primary" icon={<SaveOutlined />} loading={saving} onClick={() => void handleSave()}>
              {t('detail.history.saveData')}
            </Button>
          </div>
        </>
      )}
    </>
  );
}

/* ── Assumptions Tab ─────────────────────────────────── */

function AssumptionsTab({ companyId, templateId }: { companyId: number; templateId: number }) {
  const { t } = useTranslation();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<number | null>(null);
  const [newName, setNewName] = useState('');
  const [templateAssumptions, setTemplateAssumptions] = useState<AssumptionItem[]>([]);
  const [values, setValues] = useState<Record<string, number>>({});
  const [forecastYears, setForecastYears] = useState<number[]>([]);
  const [yearsInput, setYearsInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [forecasting, setForecasting] = useState(false);

  const loadScenarios = useCallback(async (autoSelect = false) => {
    const s = await fetchScenarios(companyId);
    setScenarios(s);
    if (autoSelect && s.length > 0) { await handleSelect(s[0].id); }
  }, [companyId]);

  useEffect(() => { void loadScenarios(true).catch(() => {}); }, [loadScenarios]);
  useEffect(() => {
    fetchTemplateDetail(templateId).then((t) => setTemplateAssumptions(t.default_assumptions)).catch(() => {});
  }, [templateId]);

  async function handleCreate() {
    if (!newName.trim()) return;
    try {
      const s = await createScenario(companyId, newName.trim());
      setNewName('');
      await loadScenarios();
      await handleSelect(s.id);
    } catch (err) { message.error((err as Error).message); }
  }

  async function handleSelect(sid: number) {
    setSelectedScenario(sid);
    try {
      const assumptions = await getAssumptions(companyId, sid);
      const v: Record<string, number> = {};
      const yrs = new Set<number>();
      for (const a of assumptions) { v[`${a.year}-${a.param_key}`] = a.param_value; yrs.add(a.year); }
      setValues(v);
      const sorted = Array.from(yrs).sort((a, b) => a - b);
      setForecastYears(sorted);
      setYearsInput(sorted.join(', '));
    } catch (err) { message.error((err as Error).message); }
  }

  function applyYears() {
    const years = yearsInput.split(/[,\s]+/).map((s) => parseInt(s, 10)).filter((n) => !isNaN(n)).sort((a, b) => a - b);
    setForecastYears(years);
    const nv = { ...values };
    for (const y of years) for (const ta of templateAssumptions) { const k = `${y}-${ta.param_key}`; if (!(k in nv)) nv[k] = ta.param_value; }
    setValues(nv);
  }

  async function handleSave() {
    if (!selectedScenario) return;
    setSaving(true);
    try {
      const items: AssumptionYearItem[] = [];
      for (const y of forecastYears) for (const ta of templateAssumptions) items.push({ year: y, param_key: ta.param_key, param_value: values[`${y}-${ta.param_key}`] ?? ta.param_value });
      await updateAssumptions(companyId, selectedScenario, items);
      message.success(t('detail.assumptions.assumptionsSaved'));
    } catch (err) { message.error((err as Error).message); } finally { setSaving(false); }
  }

  async function handleForecast() {
    if (!selectedScenario || forecastYears.length === 0) { message.warning(t('detail.assumptions.selectScenarioFirst')); return; }
    setForecasting(true);
    try {
      await runForecast(companyId, selectedScenario, forecastYears);
      message.success(t('detail.assumptions.forecastComplete'));
    } catch (err) { message.error((err as Error).message); } finally { setForecasting(false); }
  }

  const categories = new Map<string, AssumptionItem[]>();
  for (const ta of templateAssumptions) { const l = categories.get(ta.category) ?? []; l.push(ta); categories.set(ta.category, l); }
  const catLabels: Record<string, string> = { IS: t('detail.history.incomeStatement'), BS: t('detail.history.balanceSheet'), CF: t('detail.history.cashFlow') };

  return (
    <>
      <Card size="small" title={t('detail.assumptions.scenarioMgmt')} style={{ marginBottom: 16 }}>
        <Space>
          <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder={t('detail.assumptions.scenarioName')} style={{ width: 200 }}
            onPressEnter={() => void handleCreate()} />
          <Button type="primary" onClick={() => void handleCreate()}>{t('create')}</Button>
        </Space>
        {scenarios.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <Segmented
              value={selectedScenario ?? undefined}
              options={scenarios.map((s) => ({ label: s.name, value: s.id }))}
              onChange={(v) => void handleSelect(v as number)}
            />
          </div>
        )}
      </Card>

      {selectedScenario && (
        <>
          <Card size="small" title={t('detail.assumptions.forecastYears')} style={{ marginBottom: 16 }}>
            <Space>
              <Input value={yearsInput} onChange={(e) => setYearsInput(e.target.value)} placeholder={t('detail.assumptions.yearsPlaceholder')} style={{ width: 200 }} />
              <Button onClick={applyYears}>{t('apply')}</Button>
            </Space>
          </Card>

          {forecastYears.length > 0 && (
            <>
              <Collapse defaultActiveKey={['IS']} items={Array.from(categories.entries()).map(([cat, items]) => ({
                key: cat,
                label: <Text strong>{catLabels[cat] ?? cat}</Text>,
                children: (
                  <Table size="small" pagination={false} dataSource={items} rowKey="param_key"
                    columns={[
                      {
                        title: t('detail.assumptions.parameter'), dataIndex: 'display_name', width: 200,
                        render: (name: string, item: AssumptionItem) => (
                          <Tooltip title={item.param_key}><span>{name}</span></Tooltip>
                        ),
                      },
                      ...forecastYears.map((y) => ({
                        title: String(y), key: String(y), width: 120,
                        render: (_: unknown, item: AssumptionItem) => {
                          const k = `${y}-${item.param_key}`;
                          return <InputNumber size="small" style={{ width: '100%' }} value={values[k] ?? item.param_value}
                            onChange={(v) => setValues((prev) => ({ ...prev, [k]: v ?? 0 }))} />;
                        },
                      })),
                    ]}
                  />
                ),
              }))} />

              <div style={{ marginTop: 16, textAlign: 'right' }}>
                <Space>
                  <Button icon={<SaveOutlined />} loading={saving} onClick={() => void handleSave()}>{t('save')}</Button>
                  <Button type="primary" icon={<ThunderboltOutlined />} loading={forecasting} onClick={() => void handleForecast()}>
                    {t('detail.assumptions.runForecast')}
                  </Button>
                </Space>
              </div>
            </>
          )}
        </>
      )}
    </>
  );
}

/* ── Statements Tab ──────────────────────────────────── */

function StatementsTab({ companyId }: { companyId: number }) {
  const { t } = useTranslation();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<number | null>(null);
  const [statements, setStatements] = useState<StatementsResponse | null>(null);
  const [subTab, setSubTab] = useState<'IS' | 'BS' | 'CF'>('IS');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchScenarios(companyId).then((list) => {
      setScenarios(list);
      if (list.length > 0) { handleSelect(list[0].id); }
    }).catch(() => {});
  }, [companyId]);

  async function handleSelect(sid: number) {
    setSelectedScenario(sid);
    setLoading(true);
    try { setStatements(await getStatements(companyId, sid)); } catch { setStatements(null); } finally { setLoading(false); }
  }

  function fmt(v: number): string {
    if (v === 0) return '-';
    const s = Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    return v < 0 ? `(${s})` : s;
  }

  const stmtMap: Record<string, StatementResponse | undefined> = {
    IS: statements?.income_statement,
    BS: statements?.balance_sheet,
    CF: statements?.cash_flow,
  };
  const stmt = stmtMap[subTab];

  return (
    <>
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Text type="secondary">{t('detail.statements.scenario')}:</Text>
          {scenarios.length === 0 ? (
            <Text type="secondary">{t('detail.statements.noScenarios')}</Text>
          ) : (
            <Segmented
              value={selectedScenario ?? undefined}
              options={scenarios.map((s) => ({ label: s.name, value: s.id }))}
              onChange={(v) => void handleSelect(v as number)}
            />
          )}
        </Space>
      </Card>

      {loading && <div style={{ textAlign: 'center', padding: 40 }}><Spin /></div>}

      {statements && !loading && (
        <>
          <Segmented
            value={subTab}
            options={[
              { label: t('detail.statements.incomeStatement'), value: 'IS' },
              { label: t('detail.statements.balanceSheet'), value: 'BS' },
              { label: t('detail.statements.cashFlow'), value: 'CF' },
            ]}
            onChange={(v) => setSubTab(v as 'IS' | 'BS' | 'CF')}
            style={{ marginBottom: 16 }}
          />

          {subTab === 'BS' && stmt && (
            <div style={{ marginBottom: 12 }}>
              {(() => {
                const totA = stmt.rows.find(r => r.code === 'BS_A_999');
                const totLE = stmt.rows.find(r => r.code === 'BS_999');
                if (!totA || !totLE) return null;
                const lastYear = stmt.years[stmt.years.length - 1];
                const diff = Math.abs((totA.values[lastYear] ?? 0) - (totLE.values[lastYear] ?? 0));
                const balanced = diff < 0.01;
                return balanced
                  ? <Tag icon={<CheckCircleFilled />} color="success">{t('detail.statements.balanced', { year: lastYear })}</Tag>
                  : <Tag icon={<CloseCircleFilled />} color="error">{t('detail.statements.imbalanced', { diff: fmt(diff), year: lastYear })}</Tag>;
              })()}
            </div>
          )}

          {stmt && stmt.rows.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, fontFamily: 'monospace' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e8e8e8' }}>
                    <th style={{ textAlign: 'left', padding: '8px 12px', minWidth: 240, position: 'sticky', left: 0, background: '#fff', zIndex: 1 }}>{t('detail.statements.lineItem')}</th>
                    {stmt.years.map((y) => (
                      <th key={y} style={{
                        textAlign: 'right', padding: '8px 12px', minWidth: 110,
                        background: stmt.period_types[y] === 'HISTORICAL' ? '#f9f9f9' : '#e8f4fd',
                      }}>
                        {y}
                        <div style={{ fontSize: 10, fontWeight: 400, color: '#999' }}>
                          {stmt.period_types[y] === 'HISTORICAL' ? t('detail.statements.actual') : t('detail.statements.forecast')}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {stmt.rows.map((row) => (
                    <tr key={row.code} style={{
                      borderBottom: '1px solid #f0f0f0',
                      fontWeight: row.is_bold ? 600 : 400,
                      background: row.is_bold ? '#fafafa' : undefined,
                    }}>
                      <td style={{
                        padding: '6px 12px', paddingLeft: 12 + row.indent_level * 20,
                        position: 'sticky', left: 0, background: row.is_bold ? '#fafafa' : '#fff', zIndex: 1,
                      }}>
                        {row.name_cn}
                      </td>
                      {stmt.years.map((y) => {
                        const val = row.values[y] ?? 0;
                        const isH = stmt.period_types[y] === 'HISTORICAL';
                        return (
                          <td key={y} style={{
                            textAlign: 'right', padding: '6px 12px',
                            background: isH ? '#f9f9f9' : '#e8f4fd',
                            color: val < 0 ? '#cf1322' : undefined,
                          }}>
                            {row.is_override[y] && <Tooltip title={t('detail.statements.overridden')}><InfoCircleOutlined style={{ marginRight: 4, color: '#faad14' }} /></Tooltip>}
                            {fmt(val)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <Empty description={t('detail.statements.noData')} />
          )}
        </>
      )}
    </>
  );
}

/* ── Export Tab ───────────────────────────────────────── */

function ExportTab({ companyId }: { companyId: number }) {
  const { t } = useTranslation();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<number | null>(null);
  const [exporting, setExporting] = useState<string | null>(null);

  useEffect(() => {
    fetchScenarios(companyId).then((list) => {
      setScenarios(list);
      if (list.length > 0) { setSelectedScenario(list[0].id); }
    }).catch(() => {});
  }, [companyId]);

  async function handleExport(type: 'excel' | 'pdf') {
    if (!selectedScenario) { message.warning(t('detail.export.selectFirst')); return; }
    setExporting(type);
    try {
      const url = type === 'excel'
        ? getExportExcelUrl(companyId, selectedScenario)
        : getExportPdfUrl(companyId, selectedScenario);
      const ext = type === 'excel' ? 'xlsx' : 'html';
      const name = scenarios.find(s => s.id === selectedScenario)?.name || 'forecast';
      await downloadExport(url, `forecast_${name}.${ext}`);
      message.success(type === 'excel' ? t('detail.export.excelSuccess') : t('detail.export.pdfSuccess'));
    } catch (err) {
      message.error(t('detail.export.exportFailed') + ': ' + (err as Error).message);
    } finally {
      setExporting(null);
    }
  }

  return (
    <Card>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Text strong style={{ display: 'block', marginBottom: 8 }}>{t('detail.export.selectScenario')}</Text>
          {scenarios.length === 0 ? (
            <Text type="secondary">{t('detail.export.noScenarios')}</Text>
          ) : (
            <Select
              style={{ width: 300 }}
              placeholder={t('detail.export.selectPlaceholder')}
              value={selectedScenario}
              onChange={setSelectedScenario}
              options={scenarios.map(s => ({ label: s.name, value: s.id }))}
            />
          )}
        </div>

        <Space>
          <Button
            type="primary"
            icon={<FileExcelOutlined />}
            size="large"
            disabled={!selectedScenario}
            loading={exporting === 'excel'}
            onClick={() => void handleExport('excel')}
          >
            {t('detail.export.exportExcel')}
          </Button>
          <Button
            icon={<FilePdfOutlined />}
            size="large"
            disabled={!selectedScenario}
            loading={exporting === 'pdf'}
            onClick={() => void handleExport('pdf')}
          >
            {t('detail.export.exportPdf')}
          </Button>
        </Space>

        <Alert
          type="info"
          showIcon
          message={t('detail.export.exportInfo')}
        />
      </Space>
    </Card>
  );
}
