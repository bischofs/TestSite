from django.db import models
import pandas as pd
import logging
#from Logger import *

#reate your models here.

class DataIO:

    def __init__(self):

        self.speciesColumnDict = {"E_CH4W":"ppm","E_CH4W2":"ppm","E_CO2D":"%",
                                  "E_CO2D2":"%","E_COHD":"%","E_COHD2":"%",
                                  "E_COLD":"ppm","E_COLD2":"ppm","E_NOD":"ppm",
                                  "E_NOD2":"ppm","E_NOXD":"ppm","E_NOXD2":"ppm",
                                  "E_O2D":"%","E_O2D2":"%","E_THCW":"ppm","E_THCW2":"ppm"}

        logger = logging.getLogger('Evaluation_Log')
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler('eval.log')
        ch = logging.StreamHandler()
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)

        logger.info('Logger initialized')

        self.logDict = {} # key value pair for logging errrors to be serialized and sent to client

        self.logger = logging.getLogger("Evaluation_Log")
        self.logger.info("Beginning Data Import")

        # @name load_data
        # @desc Import csv file and create pandas DataFrame
        # @memberOf IO.DataIO

    def load_data(self,filename):

        self.data = pd.read_csv(filename) # Read Data into DataFrame
        self.meta_data = self.load_meta_data(self.data, filename) # Read Meta data
        self.check_units(self.data) #Check Units based on dictionary
        self.data = self.data.convert_objects(convert_numeric=True) # Convert all data to numeric
        self.data = self.data.dropna() # Drop NaN values from data
        self.logger.info("Data Import successful - %s" % filename)


        # @name check_analyzer_maximums
        # @desc Load json ranges and check imported data for out of range
        # The Ranges are loaded from configuration file for
        # @memberOf IO.DataIO


    def check_analyzer_maximums(self):

        try:
            self.ranges = pd.read_json("ranges.json")
            self.logger.info("Checking Data Ranges")
        except Exception as e:
            self.logger.error(e)

            #boolean_data = self.data.E_CO2D2 <  self.ranges.EngineOut_Max.CO2

            #if boolean_data.all()

        # @name _check_units
        # @desc Load json ranges and check imported data for out of range
        # The Ranges are loaded from configuration file for
        # @memberOf IO.DataIO


    def check_units(self, data):

        for species, unit in self.speciesColumnDict.items():
            self.check_units_util(data, species, unit)



        # @name _load_meta_data
        # @desc Load json ranges and check imported data for out of range
        # The Ranges are loaded from configuration file for
        # @memberOf IO.DataIO


    def load_meta_data(self, data, filename):

        meta_data = data[:2]
        if 'proj' in meta_data.columns:

            # self.logger.info("Meta-Data read from import file %s" % filename)

            self.logDict['info'] = "Meta-Data read from import file %s" % filename

            return meta_data
        else:
            self.logDict['warning'] = "Meta-Data missing in import file %s" % filename

            # self.logger.warning("Meta-Data missing in import file %s" % filename)



        #### UTILITY METHODS

    def check_units_util(self, data, species, unit):

        try:
            boolean = data[species].str.contains(unit)
            if not(boolean.any()):
                self.logger.warning("%s units are not in %s" % (species,unit))
        except Exception as e:
                self.logger.error("Cannot find %s in data" % e)


