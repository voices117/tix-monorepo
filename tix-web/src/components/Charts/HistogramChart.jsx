import React, { Component } from 'react';
const ReactHighcharts = require('react-highcharts');

class DashboardChart extends Component {

  componentWillMount() {
    this.config = this.buildConfig(this.props);
  }

  componentWillReceiveProps(newProps) {
    this.config = this.buildConfig(newProps);
  }

  buildConfig(props) {
    return {
      chart: {
        type: 'column',
      },
      title: {
        text: props.title,
        x: -20, // center
      },
      xAxis: {
        categories:
          ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%'],
      },
      yAxis: {
        title: { text: 'Ocurrencias' },
      },
      plotOptions: {
        column: {
          groupPadding: 0,
          pointPadding: 0,
          borderWidth: 0,
          color: props.red ? '#E36262' : '#7cb5ec',
        },
      },
      series: [{
        name: props.description,
        data: props.data,
      }],
    };
  }

  render() {
    return (
      <ReactHighcharts config={this.config} />
    );
  }
}
export default DashboardChart;
