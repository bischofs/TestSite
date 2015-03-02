from django.db import models
import pandas as pd
import logging
#from Logger import *

#reate your models here.

class DataIO:

    def __init__(self, cycle, bench):

        #################################################################################################
        # Main channel reference, this key value pair is used to locate and check channels in the data  #
        #################################################################################################

        self.bench = bench 
        self.cycle = cycle
        self.mapDict = {} # Dictionary that maps species to channel name in uploaded file
        self.logDict = {} # key value pair for logging errors to be serialized and sent to client



    #######################################################
    # # @name load_data                                   #
    # # @desc Import csv file and create pandas DataFrame #
    # # @memberOf IO.DataIO                               #
    #######################################################

    def load_data(self,filename):

        self.filename = filename

        self.speciesData = pd.read_json("spec.json")
        self.data = pd.read_csv(filename)                                                   # Read Data into DataFrame
        self.meta_data = self.load_meta_data(self.data, filename)                           # Read Meta data
        self.check_channels()                                      # Check Units based on dictionary
        self.check_ranges()

        self.data = self.data.convert_objects(convert_numeric=True)                         # Convert all data to numeric
        self.data = self.data.dropna()                                                      # Drop NaN values from data
        self.convert_bar_to_kpa()
        self.check_ambient_conditions()


        # self.logger.info("Data Import successful - %s" % filename)



    #######################################################
    # # @name convert_bar_to_kpa                          #
    # # @desc converts bar to kpa for 1065 calculations   #
    # # @memberOf IO.DataIO                               #
    #######################################################


    def convert_bar_to_kpa(self):
        
        self.data.P_AMB = self.data.P_AMB * 100
        self.data.P_INLET = self.data.P_INLET * 100



    ########################################################################################
    # # @name check_analyzer_maximums                                                      #
    # # @desc Load json ranges and check imported data for out of range data (equipment)   #
    # # @memberOf IO.DataIO                                                                #
    ########################################################################################

    def check_analyzer_maximums(self):


        self.ranges = pd.read_json("ranges.json")
        
        boolean_cond = self.data.E_COHD > self.ranges.Measuring_Maximums.CO_HIGH_MAX
        if(boolean_cond.any()):
            self.logDict['error'] = "E_COHD above maximum equipment measuring range"
            raise Exception("E_COHD above maximum equipment measuring range")

        boolean_cond = self.data.E_COHD2 > self.ranges.Measuring_Maximums.CO_HIGH_MAX
        if(boolean_cond.any()):
            self.logDict['error'] = "E_COHD2 above maximum equipment measuring range"
            raise Exception("E_COHD2 above maximum equipment measuring range")

        boolean_cond = self.data.E_COHD < 0
        if(boolean_cond.any()):
            self.logDict['error'] = "E_COHD below 0"
            raise Exception("E_COHD below 0")

        boolean_cond = self.data.E_COHD2 < 0
        if(boolean_cond.any()):
            self.logDict['error'] = "E_COHD2 below 0"
            raise Exception("E_COHD2 below 0")




        

            # self.logger.info("Checking Data Ranges")


            # self.logger.error(e)

            #boolean_data = self.data.E_CO2D2 <  self.ranges.EngineOut_Max.CO2

            #if boolean_data.all()



    #####################################################################################
    # # @name _check_ambient_conditions                                                 #
    # # @desc using reference json file check data for required ambient conditions      #
    # # @memberOf IO.DataIO                                                             #
    #####################################################################################

    def check_ranges(self):
        
        for species in self.mapDict:

            max_value = self.speciesData.Species[species]['maximum_value']
            min_value = self.speciesData.Species[species]['minimum_value']

            boolean_cond = self.data[self.mapDict[species]] > max_value
            if(boolean_cond.any()):
                self.logDict['error'] = "%s is above required maximum of %s %s" % (self.mapDict[species], max_value, self.speciesData.Species[species]['unit'])
                raise Exception ("%s is above required maximum of %s %s" % (self.mapDict[species], max_value, self.speciesData.Species[species]['unit']))
            boolean_cond = self.data[self.mapDict[species]] < min_value
            if(boolean_cond.any()):
                self.logDict['error'] = "%s is below required minimum of %s %s" % (self.mapDict[species], min_value, self.speciesData.Species[species]['unit'])
                raise Exception ("%s is below required minimum of %s %s" % (self.mapDict[species], min_value, self.speciesData.Species[species]['unit']))


    #######################################################################
    # # @name _check_channels                                             #
    # # @desc using reference key value dict, check units of all channels #
    # # @memberOf IO.DataIO                                               #
    #######################################################################

    def check_channels(self):

        def check_channels_util(species, channel_names, multiple_benches, data, filename):
            
            for name in channel_names:
                if (multiple_benches == True ) and (self.bench == '2'):
                    if (name in data.columns) and ((name + "2") in data.columns):
                        self.mapDict[species] = name
                        break
                else:
                    if (name in data.columns):
                        self.mapDict[species] = name
                        break
            else:
               if (multiple_benches == True): 
                   channel_names.append(channel_names[0] + "2")   
                   raise Exception("Cannot find %s channel names %s in file %s" % (species.replace("_"," "), channel_names, filename))    
               else:
                   raise Exception("Cannot find %s channel %s in file %s" % (species.replace("_"," "), channel_names, filename))    
                   

        for species in self.speciesData.Species.items():

            if (species[1]['multiple_benches'] == True):
                check_channels_util(species[0], species[1]['channel_names'], True, self.data, self.filename)
            else:
                check_channels_util(species[0], species[1]['channel_names'], False, self.data, self.filename)
 


    #####################################################################################
    # # @name load_meta_data                                                            #
    # # @desc Look for certain channels in the header data( row 2), report if not found #
    # # @memberOf IO.DataIO                                                             #
    #####################################################################################

    def load_meta_data(self, data, filename):

        meta_data = data[:2]
        if 'proj' in meta_data.columns:
            self.logDict['info'] = "Meta-Data read from import file %s" % filename
            return meta_data
        else:
            self.logDict['warning'] = "Meta-Data missing in import file %s" % filename



