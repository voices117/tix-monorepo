import CoreLayoutView from '../layouts/CoreLayout/CoreLayout';
import Landing from './Landing';
import AboutRoute from './About';
import HomeRoute from './Home';
import RegisterRoute from './Register';
import RecoverRoute from './Recover';

export const createRoutes = () => ({
  path        : '/',
  component   : CoreLayoutView,
  indexRoute  : Landing,
  childRoutes : [
    AboutRoute(),
    HomeRoute(),
    RegisterRoute(),
    RecoverRoute(),
  ],
});

export default createRoutes;
