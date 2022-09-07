import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt


class SakayDBError(ValueError):

    def __init__(self, text=None):
        super().__init__(text)


class SakayDB():

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def add_trip(self, driver, pickup_datetime, dropoff_datetime,
                 passenger_count, pickup_loc_name, dropoff_loc_name,
                 trip_distance, fare_amount):
        '''
        Match `driver` to the existing `last_name`, `given_name`
        (case-insensitive) in `drivers.csv` and extract the corresponding
        `driver_id`. If `driver` is new, append `driver` to `drivers.csv`
        and assign last `driver_id` + 1 as `driver_id` or `1` if there is no
        `drivers.csv`. Match the location (pickup/dropoff) to the existing
        `loc_name` (case-insensitive) in `locations.csv` and extract the
        corresponding `location_id`. If the location is new, append the
        location to `locations.csv` and assign last `location_id` + 1 as
        `location_id` or `1` if there is no `locations.csv`. Add the trip data
        to the existing `trips.csv` or create `trips.csv` if it does not
        exist.

        Parameters
        ----------
        driver : str
            The name of the driver in the format of LAST NAME, GIVEN NAME.
        pickup_datetime : str
            The exact date and time of pick up in the format of
            "hh:mm:ss,DD-MM-YYYY".
        dropoff_datetime : str
            The exact date and time of drop off in the format of
            "hh:mm:ss,DD-MM-YYYY".
        passenger_count : int
            The number of passengers in the trip.
        pickup_loc_name : str
            The zone/location where the passenger was picked up.
        dropoff_loc_name : str
            The zone/location where the passenger was dropped off.
        trip_distance : float
            The distance of the trip in meters.
        fare_amount : float
            The amount due for the trip as paid by the passenger.

        Returns
        -------
        trip_id : int
            The `trip_id` of the successful trip entry in `trips.csv`.

        Raises
        ------
        SakayDBError
            If any of the Parameters is invalid.
            If trip is already in `trips.csv`.
        '''

        # Detecting if the inputs are valid otherwise raise an error
        try:
            driver_name = driver.strip().split(', ')
            if len(driver_name) != 2:
                raise SakayDBError('has invalid or incomplete information')
            pickup_datetime = pickup_datetime.strip()
            pickup_date = pd.to_datetime(pickup_datetime.strip(),
                                         format='%H:%M:%S,%d-%m-%Y')
            dropoff_datetime = dropoff_datetime.strip()
            dropoff_date = pd.to_datetime(dropoff_datetime.strip(),
                                          format='%H:%M:%S,%d-%m-%Y')
            pickup_loc_name = pickup_loc_name.strip()
            dropoff_loc_name = dropoff_loc_name.strip()
            passenger_count = int(passenger_count)
            trip_distance = float(trip_distance)
            fare_amount = float(fare_amount)
        except Exception:
            raise SakayDBError('has invalid or incomplete information')

        # Creating the directory path
        trip_dir = os.path.join(self.data_dir, 'trips.csv')
        driver_dir = os.path.join(self.data_dir, 'drivers.csv')
        loc_dir = os.path.join(self.data_dir, 'locations.csv')

        # Checks if the driver exists in database otherwise create new entry
        if os.path.exists(driver_dir):
            df_drivers = pd.read_csv(driver_dir)
            df_tripdriver = df_drivers[(df_drivers['last_name'].str.lower()
                                       == driver_name[0].lower())
                                       & (df_drivers['given_name'].str.lower()
                                       == driver_name[1].lower())]
            if df_tripdriver.shape[0] == 0:
                driver_id = df_drivers.loc[df_drivers.shape[0] - 1,
                                           'driver_id'] + 1
                df_drivers.loc[len(df_drivers)] = [driver_id,
                                                   driver_name[1].title(),
                                                   driver_name[0].title()]
            else:
                driver_id = df_tripdriver.iloc[0, 0]
        else:
            df_drivers = pd.DataFrame(columns=['driver_id',
                                               'given_name', 'last_name'])
            driver_id = 1
            df_drivers.loc[len(df_drivers)] = [driver_id,
                                               driver_name[1].title(),
                                               driver_name[0].title()]

        # Checks if the pickpup exists in database otherwise create new entry
        if os.path.exists(loc_dir):
            df_locs = pd.read_csv(loc_dir)
            df_pickup = df_locs[df_locs['loc_name'].str.lower()
                                == pickup_loc_name.lower()]
            if df_pickup.shape[0] == 0:
                pickup_id = df_locs.loc[df_locs.shape[0] - 1,
                                        'location_id'] + 1
                df_locs.loc[len(df_locs)] = [pickup_id,
                                             pickup_loc_name.title()]
            else:
                pickup_id = df_pickup.iloc[0, 0]
        else:
            df_locs = pd.DataFrame(columns=['location_id', 'loc_name'])
            pickup_id = 1
            df_locs.loc[len(df_locs)] = [pickup_id, pickup_loc_name.title()]

        # Checks if the dropoff exists in database otherwise create new entry
        if os.path.exists(loc_dir):
            df_locs = pd.read_csv(loc_dir)
            df_dropoff = df_locs[df_locs['loc_name'].str.lower()
                                 == dropoff_loc_name.lower()]
            if df_dropoff.shape[0] == 0:
                dropoff_id = df_locs.loc[df_locs.shape[0] - 1,
                                         'location_id'] + 1
                df_locs.loc[len(df_locs)] = [dropoff_id,
                                             dropoff_loc_name.title()]
            else:
                dropoff_id = df_dropoff.iloc[0, 0]
        else:
            df_locs = pd.DataFrame(columns=['location_id', 'loc_name'])
            dropoff_id = 1
            df_locs.loc[len(df_locs)] = [dropoff_id, dropoff_loc_name.title()]

        # Checks if the trip exists in database otherwise create new entry
        if os.path.exists(trip_dir):
            df_trips = pd.read_csv(trip_dir)
            df_trip = df_trips[(df_trips['driver_id'] == driver_id)
                               & (df_trips['pickup_datetime']
                                  == pickup_datetime)
                               & (df_trips['dropoff_datetime']
                                  == dropoff_datetime)
                               & (df_trips['passenger_count']
                                  == passenger_count)
                               & (df_trips['pickup_loc_id'] == pickup_id)
                               & (df_trips['dropoff_loc_id'] == dropoff_id)
                               & (np.isclose(df_trips['trip_distance'],
                                             trip_distance))
                               & (np.isclose(df_trips['fare_amount'],
                                             fare_amount))]
            if df_trip.shape[0] == 0:
                trip_id = df_trips.loc[df_trips.shape[0] - 1, 'trip_id'] + 1
                df_trips.loc[len(df_trips)] = [trip_id, driver_id,
                                               pickup_datetime,
                                               dropoff_datetime,
                                               passenger_count,
                                               pickup_id, dropoff_id,
                                               trip_distance, fare_amount]
            else:
                raise SakayDBError('is already in the database')
        else:
            df_trips = pd.DataFrame(columns=['trip_id', 'driver_id',
                                             'pickup_datetime',
                                             'dropoff_datetime',
                                             'passenger_count',
                                             'pickup_loc_id',
                                             'dropoff_loc_id',
                                             'trip_distance', 'fare_amount'])
            trip_id = 1
            df_trips.loc[len(df_trips)] = [trip_id, driver_id,
                                           pickup_datetime,
                                           dropoff_datetime, passenger_count,
                                           pickup_id, dropoff_id,
                                           trip_distance, fare_amount]

        # Updates csv files and returns trip_id
        df_drivers.to_csv(driver_dir, index=False)
        df_locs.to_csv(loc_dir, index=False)
        df_trips.to_csv(trip_dir, index=False)
        return trip_id

    def add_trips(self, trips):
        '''
        Accept a list of trips in dictionary format. Pass each dictionary to
        `add_trip` method.

        Parameters
        ----------
        trips: list of dictionary
            A list of dictionaries with the following key-value pairs.
                driver : str
                    The name of the driver in the format of LAST NAME,
                    GIVEN NAME.
                pickup_datetime : str
                    The exact date and time of pick up in the format of
                    "hh:mm:ss,DD-MM-YYYY".
                dropoff_datetime : str
                    The exact date and time of drop off in the format of
                    "hh:mm:ss,DD-MM-YYYY".
                passenger_count : int
                    The number of passengers in the trip.
                pickup_loc_name : str
                    The zone/location where the passenger was picked up.
                dropoff_loc_name : str
                    The zone/location where the passenger was dropped off.
                trip_distance : float
                    The distance of the trip in meters.
                fare_amount : float
                    The amount due for the trip as paid by the passenger.

        Returns
        -------
        trip_ids : list of int
            List of `trip_id`s that are successfully appended to `trips.csv`.

        Warnings
        --------
        SakayDBError
            A trip in `trips` is already existing in `trips.csv`.
            The trip entry is skipped.
            A trip in `trips` has invalid or incomplete information.
            The trip entry is skipped.

        See also
        --------
        add_trip : add trip to `trips.csv`.
        '''
        trip_ids = []
        for i, trip in enumerate(trips):
            try:
                trip_id = self.add_trip(trip['driver'],
                                        trip['pickup_datetime'],
                                        trip['dropoff_datetime'],
                                        trip['passenger_count'],
                                        trip['pickup_loc_name'],
                                        trip['dropoff_loc_name'],
                                        trip['trip_distance'],
                                        trip['fare_amount'])
                trip_ids.append(trip_id)
            except SakayDBError as error_text:
                print(f'Warning: trip index {i} {error_text}. Skipping...')
            except Exception:
                print(f'Warning: trip index {i}'
                      ' has invalid or incomplete information. Skipping...')
        return trip_ids

    def delete_trip(self, trip_id):
        '''
        Accept a `trip_id` and delete it from `trips.csv`. Update `trips.csv`
        to no longer include `trip_id`.

        Parameters
        ----------
        trip_id : int
            Integer assigned to a trip that will be deleted in `trips.csv`.

        Returns
        -------
        None

        Raises
        ------
        SakayDBError
            The `trip_id` does not exist in `trips.csv`.
            `trips.csv` is empty.
        '''
        trip_dir = os.path.join(self.data_dir, 'trips.csv')

        # Checks if the file exists otherwise raise an error
        if os.path.exists(trip_dir):
            df_trips = pd.read_csv(trip_dir)
            df_trip = df_trips[df_trips['trip_id'] == trip_id]

            if df_trip.shape[0] == 0:
                raise SakayDBError
            else:
                df_trips = df_trips[df_trips['trip_id'] != trip_id]
                df_trips.to_csv(trip_dir, index=False)
                return trip_id
        else:
            raise SakayDBError

    def search_trips(self, **kwargs):
        '''
        Filter `trips.csv` based on `**kwargs`. If the type of the value of
        `**kwargs` is either `str`, `int`, or `float` filter trips that match
        the value. If the value of `**kwargs` is a `tuple`, filter the trips
        that are within the range of the `tuple`.

        Parameters
        ----------
        **kwargs : dictionary
            Keyword arguments from the ff: `driver_id`, `pickup_datetime`,
            `dropoff_datetime`, `passenger_count`, `trip_distance`,
            `fare_amount` with value that may be single-value or tuple.

        Returns
        -------
        df_trips : pandas DataFrame (or list)
            Filtered dataframe that for all the passed search keys and values.
            If no file was loaded, returns an empty list.

        Raises
        ------
        SakayDBError
                If keyword is not a key from any of the above.
                If tuple range is not exactly two elements in length.
        '''
        valid_keys = ['driver_id', 'pickup_datetime', 'dropoff_datetime',
                      'passenger_count', 'trip_distance', 'fare_amount']
        date_keys = ['pickup_datetime', 'dropoff_datetime']
        float_keys = ['driver_id', 'passenger_count',
                      'trip_distance', 'fare_amount']

        # Checks if valid keyword argument
        keys = kwargs.keys()
        chk = any([True if key not in valid_keys else False for key in keys])
        if len(keys) == 0 or chk:
            raise SakayDBError

        # Checks if the database exists otherwise returns empty list
        trip_dir = os.path.join(self.data_dir, 'trips.csv')
        if os.path.exists(trip_dir):
            df_trips = pd.read_csv(trip_dir)
        else:
            return []

        # Keep a copy of string format datetime
        # Cast the other copy to a datetime format
        df_trips.insert(loc=4, column='pickup_string',
                        value=df_trips['pickup_datetime'])
        df_trips.insert(loc=5, column='dropoff_string',
                        value=df_trips['dropoff_datetime'])
        df_trips['pickup_datetime'] = \
            pd.to_datetime(df_trips['pickup_datetime'],
                           format='%H:%M:%S,%d-%m-%Y')
        df_trips['dropoff_datetime'] = \
            pd.to_datetime(df_trips['dropoff_datetime'],
                           format='%H:%M:%S,%d-%m-%Y')

        # For valid keys
        for key, value in kwargs.items():
            try:
                if type(value) is tuple:
                    if len(value) != 2:
                        raise SakayDBError

                    # Change value format to be aligned with valid format
                    value = list(value)
                    if key in float_keys:
                        if value[0] is not None:
                            value[0] = float(value[0])
                        if value[1] is not None:
                            value[1] = float(value[1])
                    if key in date_keys:
                        if value[0] is not None:
                            value[0] = \
                                pd.to_datetime(value[0],
                                               format='%H:%M:%S,%d-%m-%Y')
                        if value[1] is not None:
                            value[1] = \
                                pd.to_datetime(value[1],
                                               format='%H:%M:%S,%d-%m-%Y')

                    # Filter dataframe base on range
                    if (value[0] is not None) and (value[1] is None):
                        df_trips = df_trips[(df_trips[key] >= value[0])]
                    elif (value[0] is None) and (value[1] is not None):
                        df_trips = df_trips[(df_trips[key] <= value[1])]
                    elif (value[0] is not None) and (value[1] is not None):
                        df_trips = df_trips[(df_trips[key] >= value[0])
                                            & (df_trips[key] <= value[1])]
                else:
                    # Change value format to be aligned with valid format
                    if key in float_keys:
                        value = float(value)
                    if key in date_keys:
                        value = pd.to_datetime(value,
                                               format='%H:%M:%S,%d-%m-%Y')

                    # Filter dataframe base on exact
                    df_trips = df_trips[(df_trips[key] == value)]
            except Exception:
                raise SakayDBError

        # Revert to original datetime (string format)
        df_trips = df_trips.sort_values(list(keys))
        df_trips.drop(columns=date_keys, inplace=True)
        df_trips.rename(columns={'pickup_string': 'pickup_datetime',
                                 'dropoff_string': 'dropoff_datetime'},
                        inplace=True)
        return df_trips

    def export_data(self):
        '''
        Merge `trips.csv`, `drivers.csv`, `locations.csv`, and export a new
        DataFrame that include the following columns:
            driver_lastname : str
                Driver’s last name in title case.
            driver_givenname : str
                Driver’s given name in title case.
            pickup_datetime : str
                The exact date and time of pick up in the format of
                “hh:mm:ss,DD-MM-YYYY”.
            dropoff_datetime : str
                The exact date and time of drop off in the format of
                “hh:mm:ss,DD-MM-YYYY”.
            passenger_count : int
                The number of passengers in the trip.
            pickup_loc_name : str
                The zone/location where the passenger was picked up.
            dropoff_loc_name : str
                The zone/location where the passenger was dropped off.
            trip_distance : float
                The distance of the trip in meters.
            fare_amount : float
                The amount due for the trip as paid by the passenger.

        Parameters
        ----------
        None

        Returns
        -------
        df_trips : pandas DataFrame
            DataFrame with the columns mentioned above and sorted by trip_id.
        '''
        trip_dir = os.path.join(self.data_dir, 'trips.csv')
        driver_dir = os.path.join(self.data_dir, 'drivers.csv')
        loc_dir = os.path.join(self.data_dir, 'locations.csv')

        if (os.path.exists(trip_dir) and os.path.exists(driver_dir)
                and os.path.exists(loc_dir)):
            df_trips = pd.read_csv(trip_dir)
            df_drivers = pd.read_csv(driver_dir)
            df_locs = pd.read_csv(loc_dir)

            # Merging of dataframe to get all necessary columns
            df_trips = df_trips.merge(df_drivers, how='left', on='driver_id')
            df_trips = df_trips.merge(df_locs, how='left',
                                      left_on='pickup_loc_id',
                                      right_on='location_id')
            df_trips = df_trips.merge(df_locs, how='left',
                                      left_on='dropoff_loc_id',
                                      right_on='location_id')

            # Clean up the dataframe removing unnecessary columns
            df_trips.sort_values(by='trip_id', axis=0,
                                 ascending=True, inplace=True)
            df_trips.drop(columns=['driver_id', 'pickup_loc_id',
                                   'dropoff_loc_id', 'location_id_x',
                                   'location_id_y'], axis=1, inplace=True)
            df_trips.rename(columns={'given_name': 'driver_givenname',
                                     'last_name': 'driver_lastname',
                                     'loc_name_x': 'pickup_loc_name',
                                     'loc_name_y': 'dropoff_loc_name'},
                            inplace=True)
            df_trips = df_trips[['driver_lastname', 'driver_givenname',
                                 'pickup_datetime', 'dropoff_datetime',
                                 'passenger_count', 'pickup_loc_name',
                                 'dropoff_loc_name', 'trip_distance',
                                 'fare_amount']]
            df_trips = df_trips.astype({'driver_lastname': 'string',
                                        'driver_givenname': 'string',
                                        'pickup_datetime': 'string',
                                        'dropoff_datetime': 'string',
                                        'passenger_count': 'int',
                                        'pickup_loc_name': 'string',
                                        'dropoff_loc_name': 'string',
                                        'trip_distance': 'float',
                                        'fare_amount': 'float'})
            return df_trips
        else:
            return pd.DataFrame(columns=['driver_lastname',
                                         'driver_givenname',
                                         'pickup_datetime',
                                         'dropoff_datetime',
                                         'passenger_count',
                                         'pickup_loc_name',
                                         'dropoff_loc_name', 'trip_distance',
                                         'fare_amount'])

    def generate_statistics(self, stat):
        '''
        Generate a dictionary of statistics based on the `stat`.

        Parameters
        ----------
        stat : str
            Can either be 'trip', 'passenger', 'driver' or 'all'
            (case-sensitive).

        Returns
        -------
        tripdict_ave : dictionary
            If stat is 'trip', a trip dictionary with days of week as keys and
            values as the mean of trips for a specific day. If stat is
            'passenger', a passenger dictionary with unique passenger counts
            as keys and values as another dictionary with days of the week as
            keys and values as the mean of trips for a specific day. If stat
            is 'driver', a driver dictionary with the driver’s name as keys
            and values as another dictionary with days of the week as keys and
            values as the mean of trips for a specific day. If stat is 'all',
            a dictionary with trip, passenger and driver as keys and values as
            the corresponding stat dictionaries above. If no file was loaded,
            return empty dictionary.

        Raises
        ------
        SakayDBError
            If `stat` is invalid.
        '''

        def stat_trip():
            '''
            Returns a trip dictionary with days of week as keys and values as
            the mean of trips for a specific day.
            '''
            trip_dir = os.path.join(self.data_dir, 'trips.csv')
            if os.path.exists(trip_dir):
                df_trips = pd.read_csv(trip_dir)
                df_trips['pickup_datetime'] = \
                    pd.to_datetime(df_trips['pickup_datetime'],
                                   format='%H:%M:%S,%d-%m-%Y')
                df_trips['day_name'] = \
                    df_trips['pickup_datetime'].dt.day_name()
                df_tripcount = \
                    df_trips.groupby(['day_name',
                                      pd.Grouper(key='pickup_datetime',
                                                 freq='1D')])['trip_id']\
                    .count().reset_index()
                sr_tripave = \
                    df_tripcount.groupby('day_name')['trip_id'].mean()
                tripave_dict = sr_tripave.to_dict()
                return tripave_dict
            else:
                return {}

        def stat_passenger():
            '''
            Returns a passenger dictionary with unique passenger counts as
            keys and values as another dictionary with days of the week as
            keys and values as the mean of trips for a specific day.
            '''
            trip_dir = os.path.join(self.data_dir, 'trips.csv')
            if os.path.exists(trip_dir):
                df_trips = pd.read_csv(trip_dir)
                df_trips['pickup_datetime'] = \
                    pd.to_datetime(df_trips['pickup_datetime'],
                                   format='%H:%M:%S,%d-%m-%Y')
                df_trips['day_name'] = \
                    df_trips['pickup_datetime'].dt.day_name()
                df_tripcount = \
                    df_trips.groupby(['passenger_count', 'day_name',
                                      pd.Grouper(key='pickup_datetime',
                                                 freq='1D')])['trip_id']\
                    .count().reset_index()
                df_tripave = (df_tripcount
                              .groupby(['passenger_count', 'day_name'])
                              ['trip_id'].mean().reset_index())
                tripave_dict = df_tripave.groupby('passenger_count')\
                    .apply(lambda x: dict(zip(x['day_name'],
                                              x['trip_id']))).to_dict()
                return tripave_dict
            else:
                return {}

        def stat_driver():
            '''
            Returns a driver dictionary with the driver’s name as keys and
            values as another dictionary with days of the week as keys and
            values as the mean of trips for a specific day.
            '''
            trip_dir = os.path.join(self.data_dir, 'trips.csv')
            driver_dir = os.path.join(self.data_dir, 'drivers.csv')
            if os.path.exists(trip_dir) and os.path.exists(driver_dir):
                df_trips = pd.read_csv(trip_dir)
                df_drivers = pd.read_csv(driver_dir)
                df_trips['pickup_datetime'] = \
                    pd.to_datetime(df_trips['pickup_datetime'],
                                   format='%H:%M:%S,%d-%m-%Y')
                df_trips['day_name'] = \
                    df_trips['pickup_datetime'].dt.day_name()
                df_trips = df_trips.merge(df_drivers,
                                          how='left', on='driver_id')
                df_trips['full_name'] = \
                    df_trips['last_name'] + ', ' + df_trips['given_name']
                df_tripcount = \
                    df_trips.groupby(['full_name', 'day_name',
                                      pd.Grouper(key='pickup_datetime',
                                                 freq='1D')])['trip_id']\
                    .count().reset_index()
                df_tripave = (df_tripcount
                              .groupby(['full_name', 'day_name'])
                              ['trip_id'].mean().reset_index())
                tripave_dict = df_tripave.groupby('full_name')\
                    .apply(lambda x: dict(zip(x['day_name'],
                                              x['trip_id']))).to_dict()
                return tripave_dict
            else:
                return {}

        if stat == 'trip':
            return stat_trip()
        elif stat == 'passenger':
            return stat_passenger()
        elif stat == 'driver':
            return stat_driver()
        elif stat == 'all':
            return {'trip': stat_trip(),
                    'passenger': stat_passenger(), 'driver': stat_driver()}
        else:
            raise SakayDBError

    def plot_statistics(self, stat):
        '''
        Generate a plot based `stat`.

        Parameters
        ----------
        stat : str
            Can either be 'trip', 'passenger', or 'driver' (case-sensitive).

        Returns
        -------
        ax : matplotlib AxesSubplot
            AxesSubplot of a bar plot of the mean number of trips per day of
            week if `stat` is 'trip'.
        ax : matplotlib AxesSubplot
            AxesSubplot of a line plot with marker 'o' that shows the mean
            number of passengers per day and with each line representing the
            number of passengers if `stat` is 'passenger'.
        fig : matplotlib Figure
            Figure of a 7 by 1 grid that shows the top five drivers sorted
            according to the highest daily mean trip count per day of the week
            then lexicographically as a horizontal bar plot.

        Raises
        ------
        SakayDBError
            If `stat` is invalid.
            No reference csv file is found.
        '''
        if stat == 'trip':
            trip_dir = os.path.join(self.data_dir, 'trips.csv')
            if os.path.exists(trip_dir):
                stat_dict = self.generate_statistics(stat)
            else:
                raise SakayDBError

            # Creating dataframe from the dictionary
            sr_tripave = pd.Series(stat_dict, name='DateValue')
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                         'Friday', 'Saturday', 'Sunday']
            sr_tripave = sr_tripave.reindex(day_order)

            # Creating plot
            ax = sr_tripave.plot(kind='bar', figsize=(12, 8))
            ax.set(xlabel='Day of week', ylabel='Ave Trips',
                   title='Average trips per day')
            plt.show()

            return ax
        elif stat == 'passenger':
            trip_dir = os.path.join(self.data_dir, 'trips.csv')
            if os.path.exists(trip_dir):
                stat_dict = self.generate_statistics(stat)
            else:
                raise SakayDBError

            # Creating dataframe from the dictionary
            passenger_count = []
            daynames = []
            for passenger, dayname in stat_dict.items():
                passenger_count.append(passenger)
                daynames.append(pd.DataFrame.from_dict(dayname,
                                                       orient='index'))
            df = pd.concat(daynames, keys=passenger_count).reset_index()
            df.rename(columns={'level_1': 'day_name',
                               'level_0': 'passenger_count',
                               0: 'ave_trips'}, inplace=True)
            df = df.pivot(index='day_name',
                          columns='passenger_count', values='ave_trips')
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                         'Friday', 'Saturday', 'Sunday']
            df = df.reindex(day_order)

            # Creating plot
            ax = df.plot(kind='line', figsize=(12, 8), marker='o')
            ax.set(xlabel='Day of week', ylabel='Ave Trips')
            plt.show()

            return ax
        elif stat == 'driver':
            trip_dir = os.path.join(self.data_dir, 'trips.csv')
            driver_dir = os.path.join(self.data_dir, 'drivers.csv')
            if os.path.exists(trip_dir) and os.path.exists(driver_dir):
                stat_dict = self.generate_statistics(stat)
            else:
                raise SakayDBError

            # Creating dataframe from the dictionary
            drivers = []
            daynames = []
            for driver, dayname in stat_dict.items():
                drivers.append(driver)
                daynames.append(pd.DataFrame.from_dict(dayname,
                                                       orient='index'))
            df = pd.concat(daynames, keys=drivers).reset_index()
            df.rename(columns={'level_1': 'day_name',
                               'level_0': 'driver_name',
                               0: 'ave_trips'}, inplace=True)
            df = df.pivot(index='driver_name',
                          columns='day_name', values='ave_trips')
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                         'Friday', 'Saturday', 'Sunday']

            # Creating plot
            fig, ax = plt.subplots(nrows=7, sharex=True, figsize=(8, 25))
            for index, day in enumerate(day_order):
                df_day = (df[day].nlargest(5)
                          .reset_index()
                          .sort_values([day, 'driver_name'],
                                       ascending=[True, False]))
                df_day.plot(ax=ax[index], kind='barh', y=day,
                            x='driver_name', legend=True)
                ax[index].set(ylabel=None, xlabel='Ave Trips')
            plt.show()

            return fig
        else:
            raise SakayDBError

    def generate_odmatrix(self, date_range=None):
        '''
        Create a matrix that shows trip data on the origin and destination of
        passengers and show the daily mean trips that happened within the
        specified date_range.

        Parameters
        ----------
        date_range : tuple of length 2 (default None)
            A tuple with elements in datetime format and fetches trips basing
            on pickup_datetime.

        Returns
        -------
        df_od : pandas DataFrame
            A pandas DataFrame that has `pickup_loc_name` and
            `dropoff_loc_name` from the `trips.csv` as columns and rows,
            respectively. If no file was loaded, return empty DataFrame.

        Raises
        ------
        SakayDBError
            If `data_range` tuple is not exactly two elements in length.
        '''
        trip_dir = os.path.join(self.data_dir, 'trips.csv')
        loc_dir = os.path.join(self.data_dir, 'locations.csv')

        # Checking if the file exists
        if os.path.exists(trip_dir) and os.path.exists(loc_dir):
            df_trips = pd.read_csv(trip_dir)
            df_locs = pd.read_csv(loc_dir)
        else:
            return pd.DataFrame()

        # Merging and formatting of dataframes to get location names
        df_trips = df_trips.merge(df_locs, left_on='pickup_loc_id',
                                  right_on='location_id', how='left')
        df_trips = df_trips.merge(df_locs, left_on='dropoff_loc_id',
                                  right_on='location_id', how='left')
        df_trips.rename(columns={'loc_name_x': 'pickup_loc_name',
                                 'loc_name_y': 'dropoff_loc_name'},
                        inplace=True)
        df_trips = df_trips[['pickup_datetime',
                             'pickup_loc_name', 'dropoff_loc_name']]
        df_trips['pickup_datetime'] = \
            pd.to_datetime(df_trips['pickup_datetime'],
                           format='%H:%M:%S,%d-%m-%Y')

        # Filters data base on date_range
        if type(date_range) is tuple:
            if len(date_range) != 2:
                raise SakayDBError
            else:
                try:
                    if date_range[0] is not None and date_range[1] is None:
                        start = pd.to_datetime(date_range[0],
                                               format='%H:%M:%S,%d-%m-%Y')
                        df_trips = \
                            df_trips[df_trips['pickup_datetime'] >= start]
                    elif date_range[0] is None and date_range[1] is not None:
                        end = pd.to_datetime(date_range[1],
                                             format='%H:%M:%S,%d-%m-%Y')
                        df_trips = \
                            df_trips[df_trips['pickup_datetime'] <= end]
                    elif (date_range[0] is not None
                            and date_range[1] is not None):
                        start = pd.to_datetime(date_range[0],
                                               format='%H:%M:%S,%d-%m-%Y')
                        end = pd.to_datetime(date_range[1],
                                             format='%H:%M:%S,%d-%m-%Y')
                        df_trips = \
                            df_trips[(df_trips['pickup_datetime'] >= start)
                                     & (df_trips['pickup_datetime'] <= end)]
                    df_trips = df_trips.sort_values('pickup_datetime')
                except Exception:
                    raise SakayDBError
        elif date_range is None:
            pass
        else:
            raise SakayDBError

        # Calculating the average daily number of trips
        df_trips['pickup_datetime'] = df_trips['pickup_datetime'].dt.date
        df_trips['uniquedate'] = (df_trips
                                  .groupby(['pickup_loc_name',
                                            'dropoff_loc_name'])
                                  ['pickup_datetime'].transform('nunique'))
        df_uniqdates = df_trips.pivot_table(index='dropoff_loc_name',
                                            columns='pickup_loc_name',
                                            values='uniquedate',
                                            aggfunc='mean')
        df_od = pd.crosstab(index=df_trips['dropoff_loc_name'],
                            columns=df_trips['pickup_loc_name'])
        df_od = df_od / df_uniqdates
        df_od = df_od.fillna(0)

        return df_od
