import React, { Component } from 'react';
import { connect } from 'react-redux';
import { push } from 'react-router-redux';
import R from 'ramda';
import PropTypes from 'prop-types';
import { fetchCurrentUser } from '../../../store/domain/account/actions';
import { fetchUserInstallation, setActiveInstallation } from '../../../store/domain/installation/actions';
import { fetchReports, downloadAdminReport } from '../../../store/domain/report/actions';
import SidebarView from '../../../components/Sidebar/SidebarView';

class HomeView extends Component {

  componentWillMount() {
    if (!this.props.user) {
      this.props.redirectRoot();
    }
  }

  componentDidMount() {
    this.props.loadUserData();
    const id = R.path(['user', 'id'], this.props);
    this.id = id;
    if (id) this.props.loadInstallations(this.props.user.id);
  }

  componentWillReceiveProps(nextProps) {
    if (this.id !== nextProps.user.id) {
      this.id = nextProps.user.id;
      nextProps.loadInstallations(nextProps.user.id);
      if (nextProps.installations && nextProps.installations.list) {
        console.log(Object.keys(nextProps.installations.list).length);
      }
    } else if (nextProps.location.pathname === '/home' && nextProps.installations && nextProps.installations.list &&
      Object.keys(nextProps.installations.list).length > 0) {
      nextProps.redirectToReport(Object.keys(nextProps.installations.list)[0], 0);
    } else if ((nextProps.location.pathname === '/home' ||  nextProps.location.pathname.includes('report')) &&
      !nextProps.location.pathname.includes('firstrun') && nextProps.installations && nextProps.installations.list &&
      Object.keys(nextProps.installations.list).length === 0) {
      nextProps.redirectToFirstTimeRun();
    } else if(nextProps.location.pathname.includes('firstrun') && nextProps.installations && nextProps.installations.list &&
      Object.keys(nextProps.installations.list).length > 0){
      nextProps.redirectHome();
    } else if (nextProps.params.installationId && nextProps.installations && nextProps.installations.list &&
      !Object.keys(nextProps.installations.list).includes(nextProps.params.installationId)) {
      nextProps.redirectToReport(Object.keys(nextProps.installations.list)[0], 0);
    }
  }

  render() {
    const {
      installations,
      loadReports,
      user,
      children,
      setActiveInstallationFunc,
      downloadAdminReportFunc,
    } = this.props;
    if(!user){
      return <div />;
    }
    return (
      <div className='container-fluid'>
        <div className='row'>
          <div className='col-md-3'>
            <SidebarView
              installations={installations}
              loadReports={loadReports}
              user={user}
              setActiveInstallation={setActiveInstallationFunc}
              downloadAdminReport={downloadAdminReportFunc}
              location={location}
            />
          </div>
          <div className='col-md-9'>
            {children}
          </div>
        </div>
      </div>
    );
  }
}

HomeView.propTypes = {
  loadUserData: PropTypes.func,
  loadInstallations: PropTypes.func,
  loadReports: PropTypes.func,
  redirectToReport: PropTypes.func,
  redirectHome: PropTypes.func,
  redirectToFirstTimeRun: PropTypes.func,
  setActiveInstallationFunc: PropTypes.func,
  downloadAdminReportFunc: PropTypes.func,
  redirectRoot: PropTypes.func,
  user: PropTypes.shape({
    id: PropTypes.number,
  }),
  children: PropTypes.node,
  installations: PropTypes.shape({
    list: PropTypes.object,
    activeInstallation: PropTypes.number,
    activeLocation: PropTypes.number,
  }),
  params: PropTypes.shape({
    installationId: PropTypes.string,
  }),
  location: PropTypes.shape({
    pathname: PropTypes.string,
  }),
};


const mapStateToProps = store => ({
  user: store.account.user,
  installations: R.pathOr({}, ['installations'], store),
});

const mapDispatchToProps = dispatch => ({
  loadUserData: () => dispatch(fetchCurrentUser()),
  loadInstallations: userId => dispatch(fetchUserInstallation(userId)),
  loadReports: userId => dispatch(fetchReports(userId)),
  redirectToReport: (installationId, providerId) => dispatch(push(`/home/report/${installationId}/${providerId}`)),
  redirectHome: () => dispatch(push('/home')),
  redirectToFirstTimeRun: () => dispatch(push('/home/report/firstrun')),
  setActiveInstallationFunc: (installationId, locationId) =>
    dispatch(setActiveInstallation(installationId, locationId)),
  downloadAdminReportFunc: () => dispatch(downloadAdminReport()),
  redirectRoot: () => dispatch(push('/')),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(HomeView);
