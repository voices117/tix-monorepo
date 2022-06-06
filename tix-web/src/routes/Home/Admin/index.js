import AdminView from './components/Admin';
import IpsCharts from './IspCharts/index';
import UserAdminView from './UserAdminView/index';

// Sync route definition
export default () => ({
  path: 'admin',
  component : AdminView,
  childRoutes: [
    IpsCharts(),
    UserAdminView(),
  ],
});
