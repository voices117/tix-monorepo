import React from 'react';
import PropTypes from 'prop-types';
import FolderOpen from 'material-ui/svg-icons/file/folder-open';
import FolderClose from 'material-ui/svg-icons/file/folder';
import { ListItem } from 'material-ui/List';
import './Sidebar.scss';


const renderFolders = (providers, id, setActiveInstallation) => {
  const providerItems = [];
  providerItems.push(
    <ListItem
      key={`ListItem${id}-0`}
      primaryText={'General'}
      onTouchTap={() => setActiveInstallation(id, 0)}
      value={`/home/report/${id}/0`}
    />);
  return providerItems.concat(providers.map(provider => (<ListItem
    key={`ListItem${id}-${provider.id}`}
    primaryText={provider.name}
    onTouchTap={() => setActiveInstallation(id, provider.id)}
    value={`/home/report/${id}/${provider.id}`}
  />)));
};

export const LocationList = props => (
  <ListItem
    primaryText={props.installation.name}
    leftIcon={props.active ? <FolderOpen /> : <FolderClose />}
    open={props.active}
    onTouchTap={() => props.setActiveInstallation(props.installation.id, 0)}
    value={`/home/report/${props.installation.id}`}
    nestedItems={
        renderFolders(props.installation.providers, props.installation.id, props.setActiveInstallation)
      }
  />
);

LocationList.propTypes = {
  installation: PropTypes.shape({
    name: PropTypes.string,
    id: PropTypes.number,
    providers: PropTypes.array,
  }),
  active: PropTypes.bool,
  setActiveInstallation: PropTypes.func,
};

export default LocationList;
