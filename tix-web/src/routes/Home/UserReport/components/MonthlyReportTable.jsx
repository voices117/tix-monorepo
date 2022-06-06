import React, { Component } from 'react';
import PropTypes from 'prop-types';
import {
  Table,
  TableBody,
  TableHeader,
  TableHeaderColumn,
  TableRow,
  TableRowColumn,
} from 'material-ui/Table';
import { Card, CardTitle, CardText } from 'material-ui/Card';

class MonthlyReportTable extends Component {

  renderTableValues(providers, reports) {
    return reports.providerList.map(provider =>
      (<TableRow key={`providerList${provider}`}>
        <TableRowColumn>{providers[provider].name}</TableRowColumn>
        <TableRowColumn>{Math.floor(reports.fullReport[provider].upQualityMedian)}%</TableRowColumn>
        <TableRowColumn>{Math.floor(reports.fullReport[provider].downQualityMedian)}%</TableRowColumn>
        <TableRowColumn>{Math.floor(reports.fullReport[provider].upUsageMedian)}%</TableRowColumn>
        <TableRowColumn>{Math.floor(reports.fullReport[provider].downUsageMedian)}%</TableRowColumn>
      </TableRow>),
    );
  }

  renderTable() {
    const {
      providers,
      reports,
    } = this.props;
    if (!reports.providerList || reports.providerList.length === 0 || !providers) {
      return <span> No hay información para mostrar</span>;
    }

    return (
      <Table>
        <TableHeader displaySelectAll={false} adjustForCheckbox={false}>
          <TableRow>
            <TableHeaderColumn>ISP</TableHeaderColumn>
            <TableHeaderColumn>Calidad Subida</TableHeaderColumn>
            <TableHeaderColumn>Calidad Bajada</TableHeaderColumn>
            <TableHeaderColumn>Utilizacion Subida</TableHeaderColumn>
            <TableHeaderColumn>Utilizacion Bajada</TableHeaderColumn>
          </TableRow>
        </TableHeader>
        <TableBody displayRowCheckbox={false} showRowHover>
          {this.renderTableValues(providers, reports)}
        </TableBody>
      </Table>
    );
  }

  render() {
    return (
      <Card className='card-margins'>
        <CardTitle
          title='Tabla de medianas mensuales'
          subtitle={`Esta tabla muestra las medianas mensuales de cada uno de los parámetros estudiados para
            cada uno de los proveedores de internet que utilizó el usuario.`}
        />
        <CardText>
          {this.renderTable()}
        </CardText>
      </Card>
    );
  }
}

MonthlyReportTable.propTypes = {
  providers: PropTypes.shape({
    name: PropTypes.string,
  }),
  reports: PropTypes.shape({
    providerList: PropTypes.array,
    fullReport: PropTypes.arrayOf(PropTypes.shape({
      upQualityMedian: PropTypes.number,
      downQualityMedian: PropTypes.number,
      upUsageMedian: PropTypes.number,
      downUsageMedian: PropTypes.number,
    })),
  }),
};

export default MonthlyReportTable;
