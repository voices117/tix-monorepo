from datetime import datetime, timedelta, timezone
import logging
from functools import partial
from operator import attrgetter

from math import floor, sqrt, log as log_function

from processor import hurst


def observation_rtt_key_function(observation):
    return observation.final_timestamp - observation.initial_timestamp


def upstream_time_function(observation, phi_function):
    return (observation.reception_timestamp + phi_function(observation.day_timestamp)) \
            - observation.initial_timestamp


def downstream_time_function(observation, phi_function):
    return observation.final_timestamp - (observation.sent_timestamp + phi_function(observation.day_timestamp))


def divide_observations_into_minutes(observations):
    observations_per_minute = {}
    for observation in observations:
        observation_datetime = datetime.fromtimestamp(observation.day_timestamp, timezone.utc)
        observation_minute = observation_datetime.replace(second=0, microsecond=0).timestamp()
        if observation_minute not in observations_per_minute:
            observations_per_minute[observation_minute] = []
        observations_per_minute[observation_minute].append(observation)
    return observations_per_minute


class Bin:
    def __init__(self, data, characterization_function):
        self.data = list(data)
        self.characterization_function = characterization_function

    def update(self, new_data):
        self.data.extend(list(new_data))

    @property
    def max_value(self):
        return self.characterization_function(max(self.data, key=self.characterization_function))

    @property
    def min_value(self):
        return self.characterization_function(min(self.data, key=self.characterization_function))

    @property
    def width(self):
        return self.max_value - self.min_value

    @property
    def mid_value(self):
        return self.min_value + self.width // 2


class FixedSizeBinHistogram:
    DEFAULT_ALPHA = 0.5

    def __init__(self, data, characterization_function, alpha=DEFAULT_ALPHA):
        self.characterization_function = characterization_function
        self.alpha = alpha
        self.data = sorted(data, key=self.characterization_function)
        self.bins = list()
        self._generate_histogram()
        self.bins_probabilities, self.mode, self.threshold = self._generate_probabilities_mode_and_threshold()

    def _generate_histogram(self):
        bins_qty = int(floor(sqrt(len(self.data))))
        datapoints_per_bin = len(self.data) // bins_qty
        # Create a histogram with the same amount of observation in each bin
        threshold = 0
        for index in range(bins_qty):
            data_index = index * datapoints_per_bin
            threshold = data_index + datapoints_per_bin
            bin_data = self.data[data_index:threshold]
            bin_ = Bin(bin_data, self.characterization_function)
            self.bins.append(bin_)
        # If there still some observations left, we add them to the last bin
        if threshold < len(self.data):
            self.bins[-1].update(self.data[threshold:])

    def _generate_bins_probabilities(self):
        total_datapoints = sum([len(bin_.data) for bin_ in self.bins])
        total_width = self.bins[-1].max_value - self.bins[0].min_value
        probabilities = [(total_datapoints * total_width) / (len(bin_.data) * bin_.width)
                         for bin_ in self.bins]
        return list(probabilities)

    def _generate_probabilities_mode_and_threshold(self):
        probabilities = self._generate_bins_probabilities()
        representative_bins = 2 * int(sqrt(len(self.bins)))
        representative_probabilities = probabilities[:representative_bins]
        mode = max(representative_probabilities)
        mode_index = representative_probabilities.index(mode)
        mode_value = self.bins[mode_index].mid_value
        if representative_probabilities[0] == mode:
            threshold = self.bins[1].mid_value
        else:
            threshold = mode_value + self.alpha * self.bins[0].mid_value
        return probabilities, mode_value, threshold


class ClockFixer:
    UPSTREAM_SERIALIZATION_TIME = 15 * (10 ** 3)  # 15 micro
    DOWNSTREAM_SERIALIZATION_TIME = 15 * (10 ** 3)  # 15 micro

    def __init__(self, observations, tau):
        self.observations = sorted(observations,
                                   key=lambda o: o.day_timestamp)

    def _between_obs(self, day_timestamp):
        obs = tuple()
        if day_timestamp < self.observations[0].day_timestamp:
            obs = (None, self.observations[0])
        elif self.observations[-1].day_timestamp <= day_timestamp:
            obs = (self.observations[-1], None)
        else:
            for index in range(len(self.observations) - 1):
                if self.observations[index].day_timestamp <= day_timestamp < self.observations[index + 1].day_timestamp:
                    obs = (self.observations[index], self.observations[index + 1])
                    break
        return obs

    def _calculate_observation_phi(self, observation):
        if observation is None:
            return None
        return (observation.initial_timestamp - observation.reception_timestamp +
                ((observation.reception_timestamp - observation.initial_timestamp) +
                 (observation.final_timestamp - observation.sent_timestamp)) / 2)

    def _base_phi_function(self, x):
        obs_before, obs_after = self._between_obs(x)
        phi_before = self._calculate_observation_phi(obs_before)
        phi_after = self._calculate_observation_phi(obs_after)
        slope = 0
        if phi_before is not None and phi_after is not None:
            slope = (phi_before - phi_after) / (obs_before.day_timestamp - obs_after.day_timestamp)
        intercept = 0
        if phi_before is None:
            intercept = phi_after - obs_after.day_timestamp * slope
        else:
            intercept = phi_before - obs_before.day_timestamp * slope
        return x * slope + intercept

    @property
    def phi_function(self):
        return self._base_phi_function


class UsageCalculator:
    def __init__(self, observations, clock_fixer):
        self.observations = observations
        self.clock_fixer = clock_fixer
        self.upstream_time_key_function = partial(upstream_time_function,
                                                  phi_function=self.clock_fixer.phi_function)
        self.downstream_time_key_function = partial(downstream_time_function,
                                                    phi_function=self.clock_fixer.phi_function)
        self.upstream_histogram = FixedSizeBinHistogram(observations, self.upstream_time_key_function)
        self.downstream_histogram = FixedSizeBinHistogram(observations, self.downstream_time_key_function)
        self.upstream_usage, self.downstream_usage = self._calculate_usage()

    def _calculate_usage(self):
        upstream_over_threshold = 0
        downstream_over_threshold = 0
        upstream_over_mode = 0
        downstream_over_mode = 0
        for observation in self.observations:
            upstream_time = self.upstream_time_key_function(observation)
            downstream_time = self.downstream_time_key_function(observation)
            if upstream_time > self.upstream_histogram.threshold:
                upstream_over_threshold += 1
            if downstream_time > self.downstream_histogram.threshold:
                downstream_over_threshold += 1
            if upstream_time > self.upstream_histogram.mode:
                upstream_over_mode += 1
            if downstream_time > self.downstream_histogram.mode:
                downstream_over_mode += 1
        upstream_usage = upstream_over_threshold / upstream_over_mode
        downstream_usage = downstream_over_threshold / downstream_over_mode
        return upstream_usage, downstream_usage


class HurstCalculator:
    @staticmethod
    def calculate_effective_hurst(hurst_values):
        return (hurst_values['wavelet'] + hurst_values['rs']) / 2

    @staticmethod
    def hurst_values(data):
        wavelet_hurst = hurst.wavelet(data)
        rs_hurst = hurst.rs(data)
        return {
            'wavelet': wavelet_hurst,
            'rs': rs_hurst
        }

    def __init__(self, observations, clock_fixer):
        self.observations = observations
        self.capped_observations = self._cap_observations()
        self.clock_fixer = clock_fixer
        self.upstream_times, self.downstream_times = self._calculate_times()
        self.upstream_values = self.hurst_values(self.upstream_times)
        self.downstream_values = self.hurst_values(self.downstream_times)

    def _calculate_desired_length(self):
        return int(2 ** floor(log_function(len(self.observations), 2)))

    def _cap_observations(self):
        desired_length = self._calculate_desired_length()
        capped_observations = self.observations[-desired_length:]
        return capped_observations

    def _calculate_times(self):
        upstream_times = []
        downstream_times = []
        for observation in self.capped_observations:
            upstream_time = upstream_time_function(observation, self.clock_fixer.phi_function)
            downstream_time = downstream_time_function(observation, self.clock_fixer.phi_function)
            upstream_times.append(upstream_time)
            downstream_times.append(downstream_time)
        return upstream_times, downstream_times


class QualityCalculator:
    DEFAULT_CONGESTION_THRESHOLD = 0.5
    DEFAULT_HURST_CONGESTION_THRESHOLD = 0.7

    def __init__(self, observations, hurst_calcultor, clock_fixer,
                 congestion_threshold=DEFAULT_CONGESTION_THRESHOLD,
                 hurst_congestion_threshold=DEFAULT_HURST_CONGESTION_THRESHOLD):
        self.observations = observations
        self.hurst_calculator = hurst_calcultor
        self.clock_fixer = clock_fixer
        self.congestion_threshold = congestion_threshold
        self.hurst_congestion_threshold = hurst_congestion_threshold
        self.observations_per_minute = divide_observations_into_minutes(self.observations)
        self.upstream_congestion, self.downstream_congestion = self._calculate_congestion()
        self.upstream_quality = \
            (len(self.observations_per_minute) - self.upstream_congestion) / len(self.observations_per_minute)
        self.downstream_quality = \
            (len(self.observations_per_minute) - self.downstream_congestion) / len(self.observations_per_minute)

    def _calculate_congestion(self):
        upstream_congestion = 0
        downstream_congestion = 0
        effective_upstream_hurst = HurstCalculator.calculate_effective_hurst(self.hurst_calculator.upstream_values)
        effective_downstream_hurst = HurstCalculator.calculate_effective_hurst(self.hurst_calculator.downstream_values)
        obspm_items = list(self.observations_per_minute.items())
        for minute, m_observations in obspm_items:
            if len(m_observations) < 30:
                self.observations_per_minute.pop(minute, None)
        for minute, m_observations in self.observations_per_minute.items():
            minute_usage_calculator = UsageCalculator(m_observations, self.clock_fixer)
            if minute_usage_calculator.upstream_usage < self.congestion_threshold \
                    and effective_upstream_hurst > self.hurst_congestion_threshold:
                upstream_congestion += 1
            if minute_usage_calculator.downstream_usage < self.congestion_threshold \
                    and effective_downstream_hurst > self.hurst_congestion_threshold:
                downstream_congestion += 1
        return upstream_congestion, downstream_congestion


class Analyzer:
    MEANINGFUL_OBSERVATIONS_DELTA = timedelta(minutes=10)

    CONGESTION_THRESHOLD = 0.5
    HURST_CONGESTION_THRESHOLD = 0.7

    def __init__(self, observations_set):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.observations = [observation for observation in observations_set if observation.type_identifier == b'S']
        self.meaningful_observations = self.calculate_meaningful_observations()
        self.rtt_histogram = FixedSizeBinHistogram(data=self.observations,
                                                   characterization_function=observation_rtt_key_function)
        self.clock_fixer = ClockFixer(self.rtt_histogram.bins[0].data, tau=self.rtt_histogram.mode)
        self.usage_calculator = UsageCalculator(self.meaningful_observations, self.clock_fixer)
        self.hurst_calculator = HurstCalculator(self.meaningful_observations, self.clock_fixer)
        self.quality_calculator = QualityCalculator(self.meaningful_observations,
                                                    self.hurst_calculator,
                                                    self.clock_fixer)

    def calculate_meaningful_observations(self):
        sorted_observations = sorted(self.observations, key=attrgetter('day_timestamp'))
        first_observation = sorted_observations[0]
        last_observation = sorted_observations[-1]
        observations_delta = timedelta(seconds=(last_observation.day_timestamp - first_observation.day_timestamp))
        if observations_delta < self.MEANINGFUL_OBSERVATIONS_DELTA:
            raise ValueError('Meaningful observations time delta is lower than expected. '
                             'Expected {}, got {}'.format(self.MEANINGFUL_OBSERVATIONS_DELTA, observations_delta))
        meaningful_threshold_timestamp = last_observation.day_timestamp \
                                         - self.MEANINGFUL_OBSERVATIONS_DELTA.total_seconds()
        meaningful_observations = [observation for observation in self.observations
                                   if observation.day_timestamp > meaningful_threshold_timestamp]
        return meaningful_observations

    def get_results(self):
        logger = self.logger.getChild('get_results')
        results = {
            'timestamp': self.meaningful_observations[-1].day_timestamp,
            'upstream': {
                'usage': self.usage_calculator.upstream_usage,
                'quality': self.quality_calculator.upstream_quality,
                'hurst': self.hurst_calculator.upstream_values
            },
            'downstream': {
                'usage': self.usage_calculator.downstream_usage,
                'quality': self.quality_calculator.downstream_quality,
                'hurst': self.hurst_calculator.downstream_values
            }
        }
        logger.debug(results)
        return results
