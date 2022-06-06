import InstallationView from './components/Installations';
import ViewIntallation from './View/index';

// Sync route definition
export default () => ({
  path: 'installation',
  component : InstallationView,
  childRoutes : [
    ViewIntallation(),
  ],
});
