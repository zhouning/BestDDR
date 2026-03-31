import { Typography, Collapse, Table, Card, Anchor, Divider, Tag, Steps, Alert } from 'antd';
import {
  RocketOutlined, BarChartOutlined, SettingOutlined,
  QuestionCircleOutlined, BookOutlined,
  CheckCircleOutlined, ThunderboltOutlined, BankOutlined,
  EditOutlined, FundOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { Title, Paragraph, Text } = Typography;

export default function HelpPage() {
  const { t } = useTranslation();

  const paramKeys = [
    'revenueGrowth', 'grossMargin', 'sellingRatio', 'adminRatio', 'rndRatio',
    'dso', 'dio', 'dpo', 'capex', 'depreciation', 'taxRate', 'dividendRatio', 'interestRate',
  ];

  const glossaryKeys = [
    'dso', 'dio', 'dpo', 'grossMargin', 'capex', 'ebit',
    'indirect', 'workingCapital', 'retainedEarnings', 'debtPlug',
  ];

  const faqKeys = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6'] as const;

  return (
    <div style={{ display: 'flex', gap: 24 }}>
      <div style={{ width: 200, flexShrink: 0 }}>
        <Anchor
          offsetTop={80}
          items={[
            { key: 'quick-start', href: '#quick-start', title: t('help.quickStart') },
            { key: 'features', href: '#features', title: t('help.features') },
            { key: 'three-statements', href: '#three-statements', title: t('help.threeStatements') },
            { key: 'glossary', href: '#glossary', title: t('help.glossary') },
            { key: 'faq', href: '#faq', title: t('help.faq') },
          ]}
        />
      </div>

      <div style={{ flex: 1, maxWidth: 900 }}>
        <Title level={2}><BookOutlined /> {t('help.title')}</Title>
        <Paragraph type="secondary">{t('help.description')}</Paragraph>

        {/* Quick Start */}
        <div id="quick-start">
          <Divider />
          <Title level={3}><RocketOutlined /> {t('help.quickStart')}</Title>
          <Paragraph>{t('help.quickStartDesc')}</Paragraph>
          <Steps
            direction="vertical"
            current={-1}
            items={[
              { title: t('help.steps.createCompany'), icon: <BankOutlined />, description: t('help.steps.createCompanyDesc') },
              { title: t('help.steps.enterData'), icon: <EditOutlined />, description: t('help.steps.enterDataDesc') },
              { title: t('help.steps.setAssumptions'), icon: <SettingOutlined />, description: t('help.steps.setAssumptionsDesc') },
              { title: t('help.steps.runForecast'), icon: <ThunderboltOutlined />, description: t('help.steps.runForecastDesc') },
              { title: t('help.steps.viewResults'), icon: <FundOutlined />, description: t('help.steps.viewResultsDesc') },
            ]}
          />
        </div>

        {/* Features */}
        <div id="features">
          <Divider />
          <Title level={3}><BarChartOutlined /> {t('help.features')}</Title>
          <Collapse
            defaultActiveKey={['historical']}
            items={[
              {
                key: 'historical',
                label: <Text strong>{t('help.sections.historicalEntry')}</Text>,
                children: (
                  <div>
                    <Paragraph>{t('help.sections.historicalEntryDesc')}</Paragraph>
                    <ul>
                      <li><Tag color="blue">IS</Tag> <strong>{t('help.sections.isLabel')}</strong> — {t('help.sections.isDesc')}</li>
                      <li><Tag color="green">BS</Tag> <strong>{t('help.sections.bsLabel')}</strong> — {t('help.sections.bsDesc')}</li>
                      <li><Tag color="orange">CF</Tag> <strong>{t('help.sections.cfLabel')}</strong> — {t('help.sections.cfDesc')}</li>
                    </ul>
                    <Alert type="info" showIcon message={t('help.sections.historicalTip')} />
                  </div>
                ),
              },
              {
                key: 'assumptions',
                label: <Text strong>{t('help.sections.assumptionParams')}</Text>,
                children: (
                  <div>
                    <Paragraph>{t('help.sections.assumptionParamsDesc')}</Paragraph>
                    <Table
                      size="small"
                      pagination={false}
                      dataSource={paramKeys.map(k => ({
                        key: k,
                        name: t(`help.params.${k}`),
                        desc: t(`help.params.${k}Desc`),
                      }))}
                      columns={[
                        { title: t('detail.assumptions.parameter'), dataIndex: 'name', width: 220 },
                        { title: t('help.description') ? '' : '', dataIndex: 'desc' },
                      ]}
                    />
                  </div>
                ),
              },
              {
                key: 'forecast',
                label: <Text strong>{t('help.sections.forecastEngine')}</Text>,
                children: (
                  <div>
                    <Paragraph>{t('help.sections.forecastEngineDesc')}</Paragraph>
                    <ol>
                      <li>{t('help.sections.engineStep1')}</li>
                      <li>{t('help.sections.engineStep2')}</li>
                      <li>{t('help.sections.engineStep3')}</li>
                      <li>{t('help.sections.engineStep4')}</li>
                      <li>{t('help.sections.engineStep5')}</li>
                    </ol>
                    <Alert type="info" showIcon message={t('help.sections.engineTip')} />
                  </div>
                ),
              },
              {
                key: 'scenarios',
                label: <Text strong>{t('help.sections.multiScenario')}</Text>,
                children: <Paragraph>{t('help.sections.multiScenarioDesc')}</Paragraph>,
              },
            ]}
          />
        </div>

        {/* Three Statements */}
        <div id="three-statements">
          <Divider />
          <Title level={3}><FundOutlined /> {t('help.threeStatements')}</Title>
          <Card size="small" style={{ fontFamily: 'monospace', fontSize: 13, whiteSpace: 'pre-line', lineHeight: 1.8 }}>
{`Income Statement (IS)        Balance Sheet (BS)          Cash Flow (CF)
─────────────────────        ────────────────────        ───────────────────
Revenue                      Assets:                     Net Profit
- COGS                         Cash ← CF closing cash      + Depreciation
- Expenses                     AR ← DSO × Revenue          + WC changes
- Interest ← from debt         Inventory ← DIO × COGS     = Operating CF
= Net Profit ──────────→       Fixed Assets                - CapEx
                               ...                         = Investing CF
         │                   Liabilities:                   ± Debt changes
         │                     Debt (auto-balance plug)     - Dividends
         └──→ Retained         AP ← DPO × COGS             = Financing CF
              Earnings       Equity:                        ─────────────
                               Retained Earnings ←──┘      = Net Cash Change
              Assets ≡ Liabilities + Equity                 + Opening Cash
                                                           = Closing Cash → BS`}
          </Card>
        </div>

        {/* Glossary */}
        <div id="glossary">
          <Divider />
          <Title level={3}><BookOutlined /> {t('help.glossary')}</Title>
          <Table
            size="small"
            pagination={false}
            dataSource={glossaryKeys.map((k, i) => ({
              key: String(i),
              term: t(`help.glossaryItems.${k}.term`),
              def: t(`help.glossaryItems.${k}.def`),
            }))}
            columns={[
              { title: 'Term', dataIndex: 'term', width: 280 },
              { title: 'Definition', dataIndex: 'def' },
            ]}
          />
        </div>

        {/* FAQ */}
        <div id="faq">
          <Divider />
          <Title level={3}><QuestionCircleOutlined /> {t('help.faq')}</Title>
          <Collapse
            items={faqKeys.map((k, i) => ({
              key: String(i),
              label: t(`help.faqItems.${k}`),
              children: <Paragraph>{t(`help.faqItems.a${k.slice(1)}`)}</Paragraph>,
            }))}
          />
        </div>

        <Divider />
        <Paragraph type="secondary" style={{ textAlign: 'center' }}>
          <CheckCircleOutlined /> {t('help.footer')}
        </Paragraph>
      </div>
    </div>
  );
}
