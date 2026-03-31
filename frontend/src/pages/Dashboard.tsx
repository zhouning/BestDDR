import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card, Row, Col, Button, Modal, Form, Input, Select, Empty, Spin,
  Typography, Space, Popconfirm, message, Tag,
} from 'antd';
import {
  PlusOutlined, BankOutlined, DeleteOutlined,
  CalendarOutlined, RightOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { fetchCompanies, createCompany, deleteCompany, fetchTemplates } from '../api';
import type { Company, Template } from '../types/financial';

const { Title, Text } = Typography;

export default function Dashboard() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form] = Form.useForm();

  async function loadData() {
    try {
      const [c, tp] = await Promise.all([fetchCompanies(), fetchTemplates()]);
      setCompanies(c);
      setTemplates(tp);
    } catch (err) {
      message.error(t('dashboard.loadFailed') + (err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void loadData(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCreate(values: { name: string; templateId: number }) {
    setCreating(true);
    try {
      await createCompany(values.name, values.templateId);
      message.success(t('dashboard.createSuccess'));
      setModalOpen(false);
      form.resetFields();
      await loadData();
    } catch (err) {
      message.error(t('dashboard.createFailed') + (err as Error).message);
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteCompany(id);
      message.success(t('dashboard.deleteSuccess'));
      await loadData();
    } catch (err) {
      message.error(t('dashboard.deleteFailed') + (err as Error).message);
    }
  }

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 80 }}><Spin size="large" /></div>;

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>{t('dashboard.title')}</Title>
        <Button type="primary" icon={<PlusOutlined />} size="large" onClick={() => {
          form.setFieldsValue({ templateId: templates[0]?.id });
          setModalOpen(true);
        }}>{t('dashboard.newCompany')}</Button>
      </div>

      {companies.length === 0 ? (
        <Card>
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={t('dashboard.noCompanies')}>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => {
              form.setFieldsValue({ templateId: templates[0]?.id });
              setModalOpen(true);
            }}>{t('dashboard.createFirst')}</Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {companies.map((c) => (
            <Col key={c.id} xs={24} sm={12} lg={8} xl={6}>
              <Card hoverable onClick={() => navigate(`/companies/${c.id}`)} styles={{ body: { padding: 20 } }}
                actions={[
                  <Popconfirm key="delete" title={t('dashboard.deleteConfirm')} description={t('dashboard.deleteDesc')}
                    onConfirm={(e) => { e?.stopPropagation(); void handleDelete(c.id); }}
                    onCancel={(e) => e?.stopPropagation()} okText={t('delete')} okType="danger">
                    <DeleteOutlined onClick={(e) => e.stopPropagation()} style={{ color: '#999' }} />
                  </Popconfirm>,
                  <RightOutlined key="open" />,
                ]}>
                <Space direction="vertical" size={4} style={{ width: '100%' }}>
                  <Space>
                    <BankOutlined style={{ fontSize: 18, color: '#1a73e8' }} />
                    <Text strong style={{ fontSize: 15 }}>{c.name}</Text>
                  </Space>
                  <Tag color="blue" style={{ margin: 0 }}>
                    {templates.find(tp => tp.id === c.industry_template_id)?.name || t('dashboard.template')}
                  </Tag>
                  <Space size={4}>
                    <CalendarOutlined style={{ fontSize: 12, color: '#999' }} />
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {new Date(c.created_at).toLocaleDateString('zh-CN')}
                    </Text>
                  </Space>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal title={t('dashboard.modalTitle')} open={modalOpen} onCancel={() => setModalOpen(false)} footer={null} destroyOnClose>
        <Form form={form} layout="vertical" onFinish={handleCreate} style={{ marginTop: 16 }}>
          <Form.Item name="name" label={t('dashboard.companyName')} rules={[{ required: true, message: t('dashboard.companyNameRequired') }]}>
            <Input placeholder={t('dashboard.companyNamePlaceholder')} autoFocus />
          </Form.Item>
          <Form.Item name="templateId" label={t('dashboard.industryTemplate')} rules={[{ required: true, message: t('dashboard.templateRequired') }]}>
            <Select>
              {templates.map(tp => (
                <Select.Option key={tp.id} value={tp.id}>{tp.name}{tp.description ? ` - ${tp.description}` : ''}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setModalOpen(false)}>{t('cancel')}</Button>
              <Button type="primary" htmlType="submit" loading={creating}>{t('create')}</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
