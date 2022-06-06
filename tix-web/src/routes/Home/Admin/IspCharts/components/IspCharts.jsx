import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import R from 'ramda';
import { Card, CardTitle, CardText } from 'material-ui/Card';
import moment from 'moment';
import { CSVLink } from 'react-csv';
import { fetchAdminReports } from '../../../../../store/domain/report/actions';
import HistogramChart from '../../../../../components/Charts/HistogramChart';
import FiltersForm from './FiltersForm';
import { fetchProviders } from '../../../../../store/domain/provider/actions';

class AdminView extends Component {

  componentWillMount() {
    this.props.fetchProviders(this.props.user.id);
    this.setState({ version: 0 });
    this.filterReports = this.filterReports.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.reports && this.state.version !== nextProps.reports.version) {
      this.calculateQuartils(nextProps.reports);
    }
  }

  calculateQuartils(measures) {
    const filters = this.state.filters;
    this.upUsageQuartils = new Array(10).fill(0);
    this.downUsageQuartils = new Array(10).fill(0);
    this.upQualityQuartils = new Array(10).fill(0);
    this.downQualityQuartils = new Array(10).fill(0);
    measures.forEach((measure) => {
      const date = moment(measure.timestamp);
      if ((filters.dayOfWeek && (date.day() === filters.dayOfWeek - 1 || filters.dayOfWeek === 0)) ||
        (filters.startTime && date.hour() >= filters.startTime && filters.endTime && date.hour() <= filters.endTime) ||
        (!filters.endTime && filters.startTime && date.hour() >= filters.startTime) ||
        (!filters.startTime && filters.endTime && date.hour() <= filters.endTime) ||
        (!filters.dayOfWeek && !filters.startTime && !filters.endTime)) {
        this.assignQuartils(this.upUsageQuartils, measure.upUsage);
        this.assignQuartils(this.downUsageQuartils, measure.downUsage);
        this.assignQuartils(this.upQualityQuartils, measure.upQuality);
        this.assignQuartils(this.downQualityQuartils, measure.downQuality);
      }
    });
  }

  assignQuartils(quartilsArray, value) {
    let w = 0;
    for (let i = 0.101; i < 1.1; i += 0.1) {
      if (value <= i) {
        quartilsArray[w] += 1;
        return;
      }
      w++;
    }
  }

  filterReports(data) {
    this.state.filters = data;
    this.props.fetchAdminReports(data.isp,
      moment(data.startDate).format('YYYY-MM-DD'), moment(data.endDate).format('YYYY-MM-DD'));
  }

  renderHistograms() {
    if (!this.upUsageQuartils) {
      return <div />;
    }
    return (
      <Card className='card-margins'>
        <CardTitle
          title='Reporte para ISP: '
          subtitle='Histogramas para los rangos de fechas definidos en los filtros'
        />
        <CardText>
          <div className='row'>
            <div className='col-md-6'>
              <HistogramChart
                data={this.upUsageQuartils}
                description='Utilization Subida'
                title='Histograma Utilization Subida'
              />
            </div>
            <div className='col-md-6'>
              <HistogramChart
                data={this.downUsageQuartils}
                description='Utilization Bajada'
                red
                title='Histograma Utilization Bajada'
              />
            </div>
          </div>
          <div className='row'>
            <div className='col-md-6'>
              <HistogramChart
                data={this.upQualityQuartils}
                description='Calidad Subida'
                title='Histograma Calidad Subida'
              />
            </div>
            <div className='col-md-6'>
              <HistogramChart
                data={this.downQualityQuartils}
                description='Calidad Bajada'
                red
                title='Histograma Calidad Bajada'
              />
            </div>
          </div>
        </CardText>
      </Card>
    );
  }

  renderCsvDownload() {
    const {
      providers,
      provider,
    } = this.props;
    if (!this.upUsageQuartils) {
      return <div />;
    }
    return (
      <Card className='card-margins'>
        <CardTitle
          title='Descarga de CSV'
          subtitle='Descargar los datos RAW para analisis'
        />
        <CardText>
          <CSVLink data={this.props.reports} separator={','} filename={`reporte-${providers[provider].name}.csv`}>
            Descargar
          </CSVLink>
        </CardText>
      </Card>
    );
  }

  render() {
    const {
      providers,
    } = this.props;
    return (
      <div>
        <FiltersForm providers={providers} onSubmit={this.filterReports} />
        {this.renderCsvDownload()}
        {this.renderHistograms()}
      </div>

    );
  }
}

AdminView.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number,
  }),
  reports: PropTypes.shape({
    version: PropTypes.number,
    upUsage: PropTypes.number,
    downUsage: PropTypes.number,
    upQuality: PropTypes.number,
    downQuality: PropTypes.number,
  }),
  providers: PropTypes.shape({
    name: PropTypes.string,
  }),
  provider: PropTypes.string,
  fetchProviders: PropTypes.func,
  fetchAdminReports: PropTypes.func,
};

const mapStateToProps = store => ({
  user: store.account.user,
  reports: R.path(['reports', 'adminReport'], store),
  provider: store.reports.provider,
  version: store.reports.version,
  providers: store.providers,
});

const mapDispatchToProps = dispatch => ({
  fetchAdminReports: (isp, startDate, endDate) => dispatch(fetchAdminReports(isp, startDate, endDate)),
  fetchProviders: userId => dispatch(fetchProviders(userId)),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(AdminView);
