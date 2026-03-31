import { Layout, Dropdown, Space, Typography, Button, theme } from 'antd';
import {
  UserOutlined, LogoutOutlined, QuestionCircleOutlined,
  BarChartOutlined, GlobalOutlined,
} from '@ant-design/icons';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import type { MenuProps } from 'antd';

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const { token: themeToken } = theme.useToken();

  const toggleLang = () => {
    const next = i18n.language === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(next);
    localStorage.setItem('lang', next);
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: user?.display_name || t('user'),
      disabled: true,
    },
    { type: 'divider' },
    {
      key: 'help',
      icon: <QuestionCircleOutlined />,
      label: t('menuHelp'),
      onClick: () => navigate('/help'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('logout'),
      danger: true,
      onClick: () => { logout(); navigate('/login'); },
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: '#fff', borderBottom: `1px solid ${themeToken.colorBorderSecondary}`,
          padding: '0 24px', position: 'sticky', top: 0, zIndex: 100,
          boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
        }}
      >
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <BarChartOutlined style={{ fontSize: 22, color: themeToken.colorPrimary }} />
          <Text strong style={{ fontSize: 17, color: themeToken.colorText }}>
            {t('appName')}
          </Text>
        </Link>

        <Space>
          <Button
            size="small"
            icon={<GlobalOutlined />}
            onClick={toggleLang}
          >
            {t('langSwitch')}
          </Button>
          <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
            <Space style={{ cursor: 'pointer', padding: '4px 8px', borderRadius: 6 }}>
              <UserOutlined />
              <Text>{user?.display_name}</Text>
            </Space>
          </Dropdown>
        </Space>
      </Header>

      <Content style={{ padding: '24px', maxWidth: 1400, margin: '0 auto', width: '100%' }}>
        <Outlet />
      </Content>

      <Footer style={{ textAlign: 'center', color: themeToken.colorTextSecondary, fontSize: 12 }}>
        {t('appName')} &copy; {new Date().getFullYear()}
      </Footer>
    </Layout>
  );
}
