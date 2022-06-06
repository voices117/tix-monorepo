import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Highstock from 'highcharts/highstock';
import ReactHighcharts from 'react-highcharts';
import moment from 'moment';
import { Card, CardTitle, CardText } from 'material-ui/Card';

const Charts = ReactHighcharts.withHighcharts(Highstock);

class DashboardChart extends Component {

  componentWillMount() {
    this.config = this.buildConfig();
  }

  componentWillReceiveProps(newProps) {
    this.config = this.buildConfig(newProps);
  }

  buildConfig(props) {
    const datesLength = props && props.fechas ? props.fechas.length :
      (this.props && this.props.fechas ? this.props.fechas.length : 0);
    const dates = props ? props.fechas : this.props.fechas;
    return {
      chart: {
        marginRight: 130,
        marginBottom: 40,
      },
      title: {
        text: '',
        x: -20, // center
      },
      xAxis: {
        type: 'datetime',
        categories: dates ? dates.map(date => moment(date).format()) : [],
        tickInterval: 6,
        labels: {
          enabled: true,
          formatter() {
            if (this.value <= 0) {
              return '';
            }
            const date = moment(this.value);
            return `${date.date() < 10 ? '0' : ''}${date.date()}/${date.month() < 10 ? '0' : ''}${date.month() + 1
            } <br> ${date.hour() < 10 ? '0' : ''}${date.hour()}:${date.minute() < 10 ? '0' : ''}${date.minute()}`;
          },
        },
        min: datesLength < 50 ? 0 : datesLength - 50,
        max: datesLength,
      },
      yAxis: {
        title: {
          text: '% de utilizacion',
        },
        plotLines: [{
          value: 0,
          width: 1,
          color: '#808080',
        }],
        min: 0,
        max: 100,
      },
      tooltip: {
        shared: true,
        valueSuffix: '%',
        crosshairs: true,
      },
      legend: {
        layout: 'vertical',
        align: 'right',
        verticalAlign: 'top',
        x: -10,
        y: 100,
        borderWidth: 0,
      },
      scrollbar: {
        enabled: true,
      },
      series: props ? props.data : this.props.data,
      plotOptions: {
        series: {
          cursor: 'pointer',
          turboThreshold: 0,
          marker: {
            lineWidth: 1,
          },
        },
      },
    };
  }

  renderGraph() {
    if (!this.props.data || !this.props.fechas || this.props.fechas.length === 0) {
      return <span>No hay reportes para mostrar</span>;
    }
    return <Charts config={this.config} />;
  }


  render() {
    const {
      isp,
      email,
    } = this.props;
    return (
      <Card className='card-margins'>
        <CardTitle
          title={`Porcentaje de utilizacion de ancho de banda en ${isp}`}
          subtitle={`Grafico general para ${email}`}
        />
        <CardText>
          {this.renderGraph()}
        </CardText>
      </Card>
    );
  }
}

DashboardChart.propTypes = {
  fechas: PropTypes.array,
  isp: PropTypes.string,
  email: PropTypes.string,
  data: PropTypes.array,
};

export default DashboardChart;
