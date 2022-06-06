import React, { Component } from 'react';
import {List, ListItem, makeSelectable} from 'material-ui/List';
import Pencil from 'material-ui/svg-icons/content/create';
import Wrench from 'material-ui/svg-icons/action/build';
import Divider from 'material-ui/Divider';
import Subheader from 'material-ui/Subheader';
import PropTypes from 'prop-types';
import { Link } from 'react-router';
import LocationListView from './LocationList';
import './Sidebar.scss';

const SelectableList = makeSelectable(List);

class SidebarView extends Component {

  renderInstallations(installations, setActiveInstallation) {
    if (!installations.list) return [];
    return Object.keys(installations.list).map((key) => {
      const installation = installations.list[key];
      return (
        <LocationListView
          installation={installation}
          key={installation.id}
          active={installations.activeInstallation === installation.id}
          activeLocation={installations.activeLocation}
          setActiveInstallation={setActiveInstallation}
        />
      );
    });
  }

  renderAdminLink(user) {
    if (user.role === 'admin') {
      return (<ListItem
        primaryText={'Panel de Administracion'}
        containerElement={<Link to='/home/admin/users' />}
        value='/home/admin/users'
        nestedItems={[
          <ListItem
            primaryText={'Graficos de Utilización'}
            containerElement={<Link to='/home/admin/ispchart' />}
            value='/home/admin/ispchart'
          />,
        ]}
      />);
    }
    return <div />;
  }

  render() {
    const {
      installations,
      user,
      setActiveInstallation,
      downloadAdminReport,
      location
    } = this.props;
    return (
      <div>
        <SelectableList
          value={location.pathname}
        >
          <Subheader>Instalaciones</Subheader>
          {this.renderInstallations(installations, setActiveInstallation)}
          <Divider />
          <Subheader>Configuracion</Subheader>
          <ListItem
            primaryText={'Ver Instalaciones'}
            leftIcon={<Pencil />}
            containerElement={<Link to='/home/installation/view' />}
            value='/home/installation/view'
          />
          <ListItem
            primaryText={'Mi cuenta'}
            leftIcon={<Wrench />}
            containerElement={<Link to='/home/account' />}
            value='/home/account'
          />
          <ListItem
            primaryText={'Reporte de usuario'}
            leftIcon={<Pencil />}
            containerElement={<Link to='/home/userreport' />}
            value='/home/userreport'
          />
          {this.renderAdminLink(user, downloadAdminReport)}
        </SelectableList>
      </div>
    );
  }
}

SidebarView.propTypes = {
  user: PropTypes.shape({
    role: PropTypes.string.isRequired,
  }),
  installations: PropTypes.shape({
    list: PropTypes.object,
    activeInstallation: PropTypes.number,
    activeLocation: PropTypes.number,
  }),
  setActiveInstallation: PropTypes.func,
  downloadAdminReport: PropTypes.func,
};


export default SidebarView;

