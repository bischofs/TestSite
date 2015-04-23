from django.db import models
import pandas as pd
import statsmodels.api as sm
import logging
import math

 class RawDataHandler:

     def __init__(self):
         self._log = {}
         

     def _import_test_data(num_benches, data_file):
         
         _test_data_wrap = TestData(num_benches, self._log) 
         self._test_data, self._log, self.mapDict = _test_data_wrap.load_data(data_file)
         
    
#     def _pre_zero_span():

    
#     def _post_zero_span():


#     def _full_load():


#     def _data_container():

#Files must arrive in a certain order to check things
#Full load -> regression
#zero and spans can be in any order 




class TestData:

    ## CONSTRUCTOR ##

    def __init__(self, bench, log):
        self.bench = bench
        self.mapDict = {} # Dictionary that contains mapped species to channel name in uploaded file
        self.logDict = log # Dictionary for logging errors to be serialized and sent to client


    #######################################################
    # # @name load_data                                   #
    # # @desc Import csv file and create pandas DataFrame #
    # # @memberOf IO.DataIO                               #
    #######################################################

    def load_data(self,filename):

        self.filename = filename


        self.speciesData = pd.read_json("spec.json")
        self.data = pd.read_csv(filename)                                                   # Read Data into DataFrame
        self.meta_data = self._load_metadata(self.data, filename)                            # Read Meta data
        self._check_channels()                                                               # Check Units based on dictionary
        self._check_units()
        self.data = self.data.convert_objects(convert_numeric=True)                         # Convert all data to numeric
        self.data = self.data.dropna()                                                      # Drop NaN values from data
        self._check_ranges()

        self._convert_bar_to_kpa()


       
        return self.data, self.mapDict, self.logDict




    #######################################################
    # # @name convert_bar_to_kpa                          #
    # # @desc converts bar to kpa for 1065 calculations   #
    # # @memberOf IO.DataIO                               #
    #######################################################


    def _convert_bar_to_kpa(self): #FIX DIS
        
        self.data.P_AMB = self.data.P_AMB * 100
        self.data.P_INLET = self.data.P_INLET * 100



    #def check_cycle(self):
        





    ########################################################################################
    # # @name check_units                                                                  #
    # # @desc Load json ranges and check imported data for out of range data (equipment)   #
    # # @memberOf IO.DataIO                                                                #
    ########################################################################################

    def _check_units(self):

        for species in self.mapDict:

            unit = self.speciesData.Species[species]['unit']
            boolean_cond = self.data[self.mapDict[species]].str.contains(unit)
            if not (boolean_cond.any()):
                self.logDict['error'] = "%s units are not in %s" % (self.mapDict[species], unit)
                raise Exception("%s units are not in %s" % (self.mapDict[species], unit))


    #####################################################################################
    # # @name _check_ambient_conditions                                                 #
    # # @desc using reference json file check data for required ambient conditions      #
    # # @memberOf IO.DataIO                                                             #
    #####################################################################################

    def _check_ranges(self):
        
        for species in self.mapDict:

            max_value = self.speciesData.Species[species]['maximum_value']
            min_value = self.speciesData.Species[species]['minimum_value']

            boolean_cond = self.data[self.mapDict[species]] > float(max_value)
            if(boolean_cond.any()):
                self.logDict['error'] = "%s is above required maximum of %s %s" % (self.mapDict[species], str(max_value), self.speciesData.Species[species]['unit'])
                raise Exception ("%s is above required maximum of %s %s" % (self.mapDict[species], str(max_value), self.speciesData.Species[species]['unit']))
            boolean_cond = self.data[self.mapDict[species]] < float(min_value)
            if(boolean_cond.any()):
                self.logDict['error'] = "%s is below required minimum of %s %s" % (self.mapDict[species], str(min_value), self.speciesData.Species[species]['unit'])
                raise Exception ("%s is below required minimum of %s %s" % (self.mapDict[species], str(min_value), self.speciesData.Species[species]['unit']))


    #######################################################################
    # # @name _check_channels                                             #
    # # @desc using reference key value dict, check units of all channels #
    # # @memberOf IO.DataIO                                               #
    #######################################################################

    def _check_channels(self):

        def _check_channels_util(species, channel_names, multiple_benches, data, filename):
            
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
                _check_channels_util(species[0], species[1]['channel_names'], True, self.data, self.filename)
            else:
                _check_channels_util(species[0], species[1]['channel_names'], False, self.data, self.filename)
 


    #####################################################################################
    # # @name load_meta_data                                                            #
    # # @desc Look for certain channels in the header data( row 2), report if not found #
    # # @memberOf IO.DataIO                                                             #
    #####################################################################################

    def _load_metadata(self, data, filename):

        meta_data = data[:2]
        if 'proj' in meta_data.columns:
            self.logDict['info'] = "Meta-Data read from import file %s" % filename
            return meta_data
        else:
            self.logDict['warning'] = "Meta-Data missing in import file %s" % filename






class CycleValidation:
    

    def __init__(self, data, mapDict):
        
        self.data = data
        self.mapDict = mapDict

        com_power = (self.data[self.mapDict['Commanded_Torque']] * self.data[self.mapDict['Commanded_Speed']] / 9.5488) / 1000
        self.data['Commanded_Power'] = com_power

        self.dataDict = {'Speed': [self.mapDict['Commanded_Speed'], self.mapDict['Engine_Speed']],
                         'Torque': [self.mapDict['Commanded_Torque'], self.mapDict['Engine_Torque']],
                         'Power': ["Commanded_Power", self.mapDict['Engine_Power']]}
        
        self._pre_regression_filter()
        self._regression()


        
    def _pre_regression_filter(self):


        curbidle = 600

        indeces = self.data[(self.data[self.mapDict['Commanded_Throttle']] == 0) & (self.data[self.mapDict['Commanded_Torque']] < 0)].index

        self.data = self.data.drop(indeces)
            
        
        indeces = self.data[(self.data[self.mapDict['Commanded_Throttle']] == 0) & (self.data[self.mapDict['Commanded_Speed']] == curbidle) &
                            ((self.data[self.mapDict['Commanded_Torque']] - (0.02 * self.data[self.mapDict['Commanded_Torque']].max())) < self.data[self.mapDict['Engine_Torque']] ) & 
                            ((self.data[self.mapDict['Commanded_Torque']] + (0.02 * self.data[self.mapDict['Commanded_Torque']].max())) > self.data[self.mapDict['Engine_Torque']] )].index

        self.data = self.data.drop(indeces)

        #'Torque': [self.mapDict['Commanded_Torque'], self.mapDict['Engine_Torque']],

        #indeces = self.data


        
        
        

    def _regression(self):
        
        self.reg_results = { 'Speed': { 'slope': " ", 'intercept': " ", 'standard_error': " ", 'rsquared': " " },
                             'Torque': { 'slope': " ", 'intercept': " ", 'standard_error': " ", 'rsquared': " " },
                             'Power': { 'slope': " ", 'intercept': " ", 'standard_error': " ", 'rsquared': " " }}
        
        for channel in self.dataDict.items():
           self._regression_util(channel[0], channel[1][0], channel[1][1])
 


    def _regression_util(self, channel, X, Y):

        ymean = self.data[Y].mean()
        xmean = self.data[X].mean()

        # -- Regression Slope -- EPA 1065.602-9 
        numerator, denominator = 0.0, 0.0
        for x, y in zip(self.data[X], self.data[Y]):
            numerator = numerator + ((x - xmean) * (y - ymean))

        for x, y in zip(self.data[X], self.data[Y]):
            denominator = denominator + ((y - ymean) ** 2)
                
        slope = numerator / denominator 


        # -- Regression Intercept -- EPA 1065.602-10 
        intercept = (xmean - (slope * ymean))
            

        # -- Regression Standard Error of Estimate -- EPA 1065.602-11 
        sumat = 0.0
        for x, y in zip(self.data[X], self.data[Y]):
            sumat = sumat + ((x - intercept - (slope * y)) ** 2)
            
        see = sumat / (self.data[X].size - 2)
        standerror = math.sqrt(see)

        # -- Regression Coefficient of determination -- EPA 1065.602-12
        numerator, denominator = 0.0, 0.0
        for x, y in zip(self.data[X], self.data[Y]):
            numerator = numerator + ((x - intercept - (slope * y)) ** 2)

        for x, y in zip(self.data[X], self.data[Y]):
            denominator = denominator + ((x - ymean) ** 2)
                
        r2 = 1 - (numerator / denominator)


        self.reg_results[channel]['slope'] = slope
        self.reg_results[channel]['intercept'] = intercept
        self.reg_results[channel]['standard_error'] = standerror
        self.reg_results[channel]['rsquared'] = r2
            

            






    
    




         


