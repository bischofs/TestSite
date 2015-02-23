from django.db import models
import pandas as pd
import logging
#from Logger import *

#reate your models here.

class DataIO:

    def __init__(self):

        #################################################################################################
        # Main channel reference, this key value pair is used to locate and check channels in the data  #
        #################################################################################################

        self.speciesColumnDict = {"E_CH4W":"ppm","E_CH4W2":"ppm","E_CO2D":"%",
                                  "E_CO2D2":"%","E_COHD":"%","E_COHD2":"%",
                                  "E_COLD":"ppm","E_COLD2":"ppm","E_NOD":"ppm",
                                  "E_NOD2":"ppm","E_NOXD":"ppm","E_NOXD2":"ppm",
                                  "E_O2D":"%","E_O2D2":"%","E_THCW":"ppm","E_THCW2":"ppm",
                                  "T_AMB": "°C","P_AMB":"bar","T_INLET":"°C","P_INLET":"bar",
                                  "E_NOXW":"ppm","E_NOXW2":"ppm","E_NOW":"ppm","E_NOW2":"ppm",
                                  "E_COHW":"%","E_COHW2":"%","E_CO2W":"ppm","E_CO2W2":"ppm",
                                  "M_RELHUM":"%","M_FRAIRW":"Kg/hr","M_FRFUEL":"Kg/hr","C_BHP":"bhp",
                                  "C_TRQENG":"Nm","C_SPDDYN":"rpm","UDPi_SpeedDemand":"rpm","UDPi_TorqueDemand":"Nm",
                                  "UDPi_Throttle":"%"}

        self.logDict = {} # key value pair for logging errors to be serialized and sent to client



    #######################################################
    # # @name load_data                                   #
    # # @desc Import csv file and create pandas DataFrame #
    # # @memberOf IO.DataIO                               #
    #######################################################

    def load_data(self,filename):

        self.data = pd.read_csv(filename)                                                   # Read Data into DataFrame
        self.meta_data = self.load_meta_data(self.data, filename)                           # Read Meta data
        self.check_channels(self.data)                                                         # Check Units based on dictionary
        self.data = self.data.convert_objects(convert_numeric=True)                         # Convert all data to numeric
        self.data = self.data.dropna()                                                      # Drop NaN values from data
        self.check_ambient_conditions()


        # self.logger.info("Data Import successful - %s" % filename)





    ########################################################################################
    # # @name check_analyzer_maximums                                                      #
    # # @desc Load json ranges and check imported data for out of range data ( equipement) #
    # # @memberOf IO.DataIO                                                                #
    ########################################################################################

    def check_analyzer_maximums(self):


           self.ranges = pd.read_json("ranges.json")
            # self.logger.info("Checking Data Ranges")


            # self.logger.error(e)

            #boolean_data = self.data.E_CO2D2 <  self.ranges.EngineOut_Max.CO2

            #if boolean_data.all()



    #####################################################################################
    # # @name _check_ambient_conditions                                                 #
    # # @desc using reference json file check data for required ambient conditions      #
    # # @memberOf IO.DataIO                                                             #
    #####################################################################################

    def check_ambient_conditions(self):


        self.cond = pd.read_json("ambient.json")

        boolean_cond = self.data.T_AMB > self.cond.Ambient_Conditions.T_AMB_MAX
        if (boolean_cond.any()):
            self.logDict['error'] = "T_AMB out of range"

        boolean_cond = self.data.T_AMB < self.cond.Ambient_Conditions.T_AMB_MIN
        if (boolean_cond.any()):
            self.logDict['error'] = "T_AMB out of range"




    #######################################################################
    # # @name _check_channels                                                #
    # # @desc using reference key value dict, check units of all channels #
    # # @memberOf IO.DataIO                                               #
    #######################################################################

    def check_channels(self, data):

        for species, unit in self.speciesColumnDict.items():
            self.check_units_util(data, species, unit)



    #####################################################################################
    # # @name load_meta_data                                                            #
    # # @desc Look for certain channels in the header data( row 2), report if not found #
    # # @memberOf IO.DataIO                                                             #
    #####################################################################################

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

        # try:
        boolean = data[species].str.contains(unit)
        if not(boolean.any()):
            self.logDict['warning'] = "%s units are not in %s" % (species, unit)
        # except Exception as e:
            self.logDict['error'] = "Cannot find %s in data" % e

