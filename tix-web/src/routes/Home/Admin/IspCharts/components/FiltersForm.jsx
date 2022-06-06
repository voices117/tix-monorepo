import React, { Component } from 'react';
import { Field, reduxForm } from 'redux-form';
import PropTypes from 'prop-types';
import MenuItem from 'material-ui/MenuItem';
import {
  DatePicker,
  TextField,
  SelectField,
} from 'redux-form-material-ui';
import RaisedButton from 'material-ui/RaisedButton';
import { Card, CardTitle, CardText } from 'material-ui/Card';

const required = value => value ? undefined : 'Requerido';

class FiltersForm extends Component {

  render() {
    const { handleSubmit, providers } = this.props;
    if (Object.keys(providers).length === 0) {
      return <span>wait</span>;
    }
    return (
      <Card className='card-margins'>
        <CardTitle
          title='Filtros de reporte'
        />
        <CardText>
          <form onSubmit={handleSubmit}>
            <div className='row'>
              <div className='col-md-4'>
                <Field name='startDate' component={DatePicker} floatingLabelText='Fecha Inicio' validate={[required]} />
                <Field component={DatePicker} floatingLabelText={'Fecha Fin'} name='endDate' validate={[required]} />
              </div>
              <div className='col-md-4'>
                <Field name='dayOfWeek' component={SelectField} floatingLabelText='Dia de la semana' >
                  <MenuItem value='0' primaryText='Todos' />
                  <MenuItem value='1' primaryText='Lunes' />
                  <MenuItem value='2' primaryText='Martes' />
                  <MenuItem value='3' primaryText='Miercoles' />
                  <MenuItem value='4' primaryText='Jueves' />
                  <MenuItem value='5' primaryText='Viernes' />
                  <MenuItem value='6' primaryText='Sabado' />
                  <MenuItem value='7' primaryText='Domingo' />
                </Field>
                <Field name='isp' component={SelectField} floatingLabelText='ISP' validate={[required]}>
                  {Object.keys(providers).map(key =>
                    <MenuItem key={key} value={providers[key].id} primaryText={providers[key].name} />)}
                </Field>
              </div>
              <div className='col-md-4'>
                <Field name='startTime' component={TextField} floatingLabelText='Hora Inicio' />
                <Field component={TextField} floatingLabelText={'Hora Final'} name='endTime' />
              </div>
            </div>
            <RaisedButton className='settings-button-margin' label='Filtrar' type='submit' />
          </form>
        </CardText>
      </Card>
    );
  }
}

FiltersForm.propTypes = {
  handleSubmit: PropTypes.func,
  providers: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
  }),
};

const FiltersFormView = reduxForm({
  form: 'usernameForm',
})(FiltersForm);

export default FiltersFormView;
