import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import {
  Table,
  TableBody,
  TableHeader,
  TableHeaderColumn,
  TableRow,
} from 'material-ui/Table';
import { Card, CardTitle, CardText } from 'material-ui/Card';
import {
  fetchUserInstallation,
  deleteInstallation,
  editInstallationName,
} from '../../../../../store/domain/installation/actions';
import InstallationListView from './InstallationListView';
import InstallatorsView from '../../../FirstTimeRun/components/InstallatorsView';

class ViewInstallation extends Component {
  renderTable() {
    const {
      installations,
      dispatchDeleteInstallation,
      editInstallation,
      user,
    } = this.props;

    if (!installations || !installations.list || installations.list.length === 0) {
      return <span className='label label-important'>No hay instalaciones registradas en el sistema.</span>;
    }
    return (
      <Table>
        <TableHeader displaySelectAll={false} adjustForCheckbox={false}>
          <TableRow>
            <TableHeaderColumn>Nombre</TableHeaderColumn>
            <TableHeaderColumn>Clave Publica</TableHeaderColumn>
            <TableHeaderColumn>Acciones</TableHeaderColumn>
          </TableRow>
        </TableHeader>
        <TableBody displayRowCheckbox={false} showRowHover>
          { Object.keys(installations.list).map(key => (
            <InstallationListView
              key={key}
              installation={installations.list[key]}
              deleteInstallation={dispatchDeleteInstallation}
              userId={user.id}
              editInstallation={editInstallation}
            />
          ))}
        </TableBody>
      </Table>
    );
  }

  render() {
    return (
      <div>
        <Card className='card-margins'>
          <CardTitle
            title='Mis Instalaciones'
          />
          <CardText>
            {this.renderTable()}
          </CardText>
        </Card>
        <Card className='card-margins'>
          <CardTitle
            title='Descargar Instalador'
          />
          <CardText>
            <InstallatorsView />
          </CardText>
        </Card>
      </div>
    );
  }
}

ViewInstallation.propTypes = {
  installations: PropTypes.shape({
    list: PropTypes.object,
    activeInstallation: PropTypes.number,
    activeLocation: PropTypes.number,
  }),
  user: PropTypes.shape({
    id: PropTypes.number,
  }),
  dispatchDeleteInstallation: PropTypes.func,
  editInstallation: PropTypes.func,
};

const mapStateToProps = store => ({
  user: store.account.user,
  installations: store.installations,
});

const mapDispatchToProps = dispatch => ({
  loadInstallations: userId => dispatch(fetchUserInstallation(userId)),
  dispatchDeleteInstallation: (userId, installationId) => dispatch(deleteInstallation(userId, installationId)),
  editInstallation: (userId, installationId, name) => dispatch(editInstallationName(userId, installationId, name)),
});

export default connect(
  mapStateToProps,
  mapDispatchToProps,
)(ViewInstallation);
