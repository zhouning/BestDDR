import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Form, Input, Button, Typography, Card, Alert, Space } from 'antd';
import { MailOutlined, LockOutlined, BarChartOutlined, GlobalOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const toggleLang = () => {
    const next = i18n.language === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(next);
    localStorage.setItem('lang', next);
  };

  const onFinish = async (values: { email: string; password: string }) => {
    setError('');
    setLoading(true);
    try {
      await login(values.email, values.password);
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('login.failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: 20,
      position: 'relative',
    }}>
      <Button
        icon={<GlobalOutlined />}
        onClick={toggleLang}
        style={{ position: 'absolute', top: 20, right: 20 }}
        ghost
      >
        {t('langSwitch')}
      </Button>

      <Card style={{ width: 420, boxShadow: '0 20px 60px rgba(0,0,0,0.15)' }}>
        <Space direction="vertical" size="middle" style={{ width: '100%', textAlign: 'center' }}>
          <BarChartOutlined style={{ fontSize: 40, color: '#1a73e8' }} />
          <Title level={3} style={{ margin: 0 }}>{t('appName')}</Title>
          <Text type="secondary">{t('login.title')}</Text>
        </Space>

        {error && <Alert message={error} type="error" showIcon style={{ marginTop: 16 }} />}

        <Form layout="vertical" onFinish={onFinish} style={{ marginTop: 24 }} size="large">
          <Form.Item name="email" rules={[
            { required: true, message: t('login.emailRequired') },
            { type: 'email', message: t('login.emailInvalid') },
          ]}>
            <Input prefix={<MailOutlined />} placeholder={t('login.email')} autoFocus />
          </Form.Item>
          <Form.Item name="password" rules={[
            { required: true, message: t('login.passwordRequired') },
            { min: 6, message: t('login.passwordMin') },
          ]}>
            <Input.Password prefix={<LockOutlined />} placeholder={t('login.password')} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              {t('login.submit')}
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">{t('login.noAccount')} </Text>
          <Link to="/register">{t('login.register')}</Link>
        </div>
      </Card>
    </div>
  );
}
