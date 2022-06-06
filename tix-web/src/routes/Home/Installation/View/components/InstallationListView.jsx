import React, { Component } from 'react';
import PropTypes from 'prop-types';
import IconButton from 'material-ui/IconButton';
import Pencil from 'material-ui/svg-icons/content/create';
import Delete from 'material-ui/svg-icons/action/delete';
import {
  TableRow,
  TableRowColumn,
} from 'material-ui/Table';
import InstallationNameForm from './InstallationNameForm';

class InstallationListView extends Component {

  componentWillMount() {
    const {
      installation,
      userId,
    } = this.props;
    this.setState({ editInstallatio: false });
    this.editInstallation = this.editInstallation.bind(this);
    this.toggleEditInstallation = this.toggleEditInstallation.bind(this, installation);
    this.deleteInstallation = this.deleteInstallation.bind(this, installation.id, userId);
  }

  deleteInstallation(installationId, userId) {
    this.props.deleteInstallation(userId, installationId);

  }

  toggleEditInstallation() {
    this.setState({ editInstallation: !this.state.editInstallation });
  }

  editInstallation(result) {
    const {
      editInstallation,
      installation,
      userId,
    } = this.props;
    editInstallation(userId, installation.id, result.installationName).then(() => this.toggleEditInstallation());
  }

  renderInstallationName() {
    if (this.state.editInstallation) {
      return (
        <InstallationNameForm
          onSubmit={this.editInstallation}
          installation={this.props.installation}
          toggleEditInstallation={this.toggleEditInstallation}
        />
      );
    }
    return this.props.installation.name;
  }

  render() {
    const {
      installation
    } = this.props;

    return (
      <TableRow key={installation.id}>
        <TableRowColumn>{this.renderInstallationName()}</TableRowColumn>
        <TableRowColumn>{installation.publickey}</TableRowColumn>
        <TableRowColumn>
          <IconButton onTouchTap={this.toggleEditInstallation} >
            <Pencil />
          </IconButton>
          <IconButton onTouchTap={this.deleteInstallation}>
            <Delete />
          </IconButton>
        </TableRowColumn>
      </TableRow>
    );
  }
}

InstallationListView.propTypes = {
  installation: PropTypes.shape({
    name: PropTypes.string,
  }),
  userId: PropTypes.number,
  editInstallation: PropTypes.func,
  deleteInstallation: PropTypes.func,
}

export default InstallationListView;
