import typeToReducer from 'type-to-reducer';
import moment from 'moment';
import { FETCH_REPORTS, FETCH_ALL_REPORTS, FETCH_ADMIN_REPORTS } from '../actions';
import { LOGOUT_USER } from '../../account/actions';

let version = 0;

export default typeToReducer({
  [FETCH_REPORTS]: {
    FULFILLED: (state, action) => {
      const upUsage = [];
      const downUsage = [];
      const upQuality = [];
      const downQuality = [];
      const dates = [];
      let lastDate = null;
      action.payload.forEach((measure) => {
        if (lastDate) {
          if (moment(measure.timestamp).isAfter(lastDate.add(25, 'minutes'))) {
            upUsage.push(null);
            downUsage.push(null);
            upQuality.push(null);
            downQuality.push(null);
            dates.push(lastDate.add(25, 'minutes'));
            lastDate = moment(measure.timestamp);
          }
        } else {
          lastDate = moment(measure.timestamp);
        }
        upUsage.push(Math.floor(measure.upUsage * 100));
        downUsage.push(Math.floor(measure.downUsage * 100));
        upQuality.push(Math.floor(measure.upQuality * 100));
        downQuality.push(Math.floor(measure.downQuality * 100));
        dates.push(measure.timestamp);
      });
      return {
        dates,
        upUsage,
        downUsage,
        upQuality,
        downQuality,
      };
    },
  },
  [FETCH_ALL_REPORTS]: {
    FULFILLED: (state, action) => {
      const report = [];
      const providerList = [];
      let lastDate = null;
      action.payload.forEach((measure) => {
        if (!report[measure.provider_id]) {
          report[measure.provider_id] = {};
          report[measure.provider_id].upUsage = [];
          report[measure.provider_id].downUsage = [];
          report[measure.provider_id].upQuality = [];
          report[measure.provider_id].downQuality = [];
          report[measure.provider_id].dates = [];
          providerList.push(measure.provider_id);
        }
        if (lastDate) {
          if (moment(measure.timestamp).isAfter(lastDate.add(25, 'minutes'))) {
            report[measure.provider_id].upUsage.push(null);
            report[measure.provider_id].downUsage.push(null);
            report[measure.provider_id].upQuality.push(null);
            report[measure.provider_id].downQuality.push(null);
            report[measure.provider_id].dates.push(lastDate.add(25, 'minutes'));
            lastDate = moment(measure.timestamp);
          }
        } else {
          lastDate = moment(measure.timestamp);
        }
        report[measure.provider_id].upUsage.push(Math.floor(measure.upUsage * 100));
        report[measure.provider_id].downUsage.push(Math.floor(measure.downUsage * 100));
        report[measure.provider_id].upQuality.push(Math.floor(measure.upQuality * 100));
        report[measure.provider_id].downQuality.push(Math.floor(measure.downQuality * 100));
        report[measure.provider_id].dates.push(measure.timestamp);
      });
      providerList.forEach((providerId) => {
        report[providerId].upUsageMedian =
          report[providerId].upUsage[Math.round(report[providerId].upUsage.length / 2)];
        report[providerId].downUsageMedian =
          report[providerId].downUsage[Math.round(report[providerId].downUsage.length / 2)];
        report[providerId].upQualityMedian =
          report[providerId].upQuality[Math.round(report[providerId].upQuality.length / 2)];
        report[providerId].downQualityMedian =
          report[providerId].downQuality[Math.round(report[providerId].downQuality.length / 2)];
      });
      return {
        providerList,
        fullReport: report,
      };
    },
  },
  [FETCH_ADMIN_REPORTS]: {
    FULFILLED: (state, action) => {
      version += 1;
      return {
        version,
        provider: 1,
        adminReport: action.payload,
      };
    },
  },
  [LOGOUT_USER]: () => ({}),
}, {});
