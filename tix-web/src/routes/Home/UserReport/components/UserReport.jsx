import React, { Component } from 'react';
import { connect } from 'react-redux';
import moment from 'moment';
import PropTypes from 'prop-types';
import { fetchAllReports } from '../../../../store/domain/report/actions';
import { fetchProviders } from '../../../../store/domain/provider/actions';
import DashboardChart from '../../../../components/Charts/DashboardChart';
import MonthlyReportTable from './MonthlyReportTable';

class UserReportView extends Component {

  componentWillMount() {
    this.props.fetchAllReports(this.props.user.id);
    this.props.fetchProviders(this.props.user.id);
  }

  setGraphData(report) {
    const data = {};
    data.fechas = report.dates;
    data.data = [
      {
        data: report.upUsage,
        name: 'Utilizacion Up',
      },
      {
        data: report.downUsage,
        name: 'Utilizacion Down',
      },
      {
        data: report.upQuality,
        name: 'Calidad Up',
      },
      {
        data: report.downQuality,
        name: 'Calidad Down',
      },
    ];
    return data;
  }

  renderGraph(provider, report) {
    const data = this.setGraphData(report);
    const {
      user,
    } = this.props;
    return (
      <DashboardChart key={provider} isp={provider} email={user.username} fechas={data.fechas} data={data.data} />
    );
  }
  render() {
    const {
      reports,
      providers,
    } = this.props;
    return (
      <div>
        <div>
          <MonthlyReportTable providers={providers} reports={reports} />
        </div>
        { reports.providerList && reports.providerList.map(provider =>
            this.renderGraph(providers[provider].name, reports.fullReport[provider])) }
      </div>
    );
  }
}

UserReportView.propTypes = {
  fetchAllReports: PropTypes.func,
  fetchProviders: PropTypes.func,
  user: PropTypes.shape({
    id: PropTypes.number,
  }),
  reports: PropTypes.shape({
    providerList: PropTypes.array,
  }),
  providers: PropTypes.shape({
    name: PropTypes.string,
  }),
};

const mapStateToProps = store => ({
  user: store.account.user,
  reports: store.reports,
  providers: store.providers,
});

const mapDispatchToProps = dispatch => ({
  fetchAllReports: userId => dispatch(fetchAllReports(userId, moment().subtract(30, 'days'), moment())),
  fetchProviders: userId => dispatch(fetchProviders(userId)),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(UserReportView);
