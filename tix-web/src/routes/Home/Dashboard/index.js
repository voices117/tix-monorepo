import DashboardView from './components/DashboardView';

// Sync route definition
export default () => ({
  path: 'report/:installationId/:providerId',
  component: DashboardView,
});
