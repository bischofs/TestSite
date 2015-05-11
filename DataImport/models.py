from django.db import models
import pandas as pd
import statsmodels.api as sm
import logging
import math

class RawDataHandler:

     def __init__(self):
         # need required channels for each file
         self.log = {}
         
     def import_test_data(self, num_benches, dataFile):
         testData = TestData(dataFile) 
         self.testData, self.mapDict, self.log = testData.load_data(data_file)
             
     def import_pre_zero_span(self, data_file):
          self.preZeroSpan = pd.read_csv(data_file)

     def import_post_zero_span(self, data_file):
          self.postZeroSpan = pd.read_csv(data_file)

     def import_full_load(self, data_file):
          fullLoadWrap = FullLoad()
          self.fullLoad = fullLoadWrap.load_data(data_file)
          


#Files must arrive in a certain order to check things
#Full load -> regression
#zero and spans can be in any order 

class Data:

     def __init__(self, fileName, data, num_benches):
          self.data = data
          self.fileName = fileName
          self.fileType = self.__class__.__name__
          self.speciesData = pd.read_json("spec.json")
          


     def _check_channels_util(species, channelNames, multipleBenches, data, fileName):
            
          for name in channelNames:
               if (multipleBenches == True ) and (self.bench == '2'):
                    if (name in data.columns) and ((name + "2") in data.columns):
                         self.mapDict[species] = name
                         break
                    else:
                         if (name in data.columns):
                              self.mapDict[species] = name
                              break
            else:
               if (multipleBenches == True): 
                   channelNames.append(channelNames[0] + "2")   
                   raise Exception("Cannot find %s channel names %s in file %s" % (species.replace("_"," "), channelNames, filename))    
               else:
                   raise Exception("Cannot find %s channel %s in file %s" % (species.replace("_"," "), channelNames, filename))    
                   



     def check_channels(self):
          
          for species in self.speciesData.Species.items():
               if species[1]['files'].__contains__(self.fileType):
                    if (species[1]['multiple_benches'] == True):
                         self._check_channels_util(species[0], species[1]['channel_names'], True, self.data, self.fileName)
                    else:
                         self._check_channels_util(species[0], species[1]['channel_names'], False, self.data, self.fileName)



     # def load_meta_data():
     #      metaData = data[:2]
     #      if 'proj' in metaData.columns:
     #           self.logDict['info'] = "Meta-Data read from import file %s" % filename
     #           return metaData
     #      else:
     #           self.logDict['warning'] = "Meta-Data missing in import file %s" % filename
            

     # def check_cycle():
     #      self.stuff = 1



class TestData(Data):

     ## CONSTRUCTOR ##
     
     def __init__(self, bench, log):
          self.bench = bench
          self.mapDict = {} # Dictionary that contains mapped species to channel name in uploaded file
          self.logDict = log # Dictionary for logging errors to be serialized and sent to client


     def load_data(self,filename):

        self.filename = filename

        self.speciesData = pd.read_json("spec.json")
        self.data = pd.read_csv(filename)                                 # Read Data into DataFrame
        self.metaData = self._load_metadata(self.data, filename)          # Read Meta data
        self._check_channels()                                            # Check Units based on dictionary
        self._check_units()
        self.data = self.data.convert_objects(convert_numeric=True)       # Convert all data to numeric
        self.data = self.data.dropna()                                    # Drop NaN values from data
        self._check_ranges()
        self._convert_bar_to_kpa()
       
        return self.data, self.mapDict, self.logDict


     def _convert_bar_to_kpa(self): #FIX DIS
        
        self.data.P_AMB = self.data.P_AMB * 100
        self.data.P_INLET = self.data.P_INLET * 100


     def _check_units(self):

        for species in self.mapDict:

            unit = self.speciesData.Species[species]['unit']
            booleanCond = self.data[self.mapDict[species]].str.contains(unit)
            if not (booleanCond.any()):
                self.logDict['error'] = "%s units are not in %s" % (self.mapDict[species], unit)
                raise Exception("%s units are not in %s" % (self.mapDict[species], unit))


     def _check_ranges(self):
        
        for species in self.mapDict:

            maxValue = self.speciesData.Species[species]['maximum_value']
            minValue = self.speciesData.Species[species]['minimum_value']

            booleanCond = self.data[self.mapDict[species]] > float(maxValue)
            if(booleanCond.any()):
                self.logDict['error'] = "%s is above required maximum of %s %s" % (self.mapDict[species], str(maxValue), self.speciesData.Species[species]['unit'])
                raise Exception ("%s is above required maximum of %s %s" % (self.mapDict[species], str(maxValue), self.speciesData.Species[species]['unit']))
            booleanCond = self.data[self.mapDict[species]] < float(minValue)
            if(booleanCond.any()):
                self.logDict['error'] = "%s is below required minimum of %s %s" % (self.mapDict[species], str(minValue), self.speciesData.Species[species]['unit'])
                raise Exception ("%s is below required minimum of %s %s" % (self.mapDict[species], str(minValue), self.speciesData.Species[species]['unit']))


     def _check_channels(self):

        def _check_channels_util(species, channelNames, multipleBenches, data, filename):
            
            for name in channelNames:
                if (multipleBenches == True ) and (self.bench == '2'):
                    if (name in data.columns) and ((name + "2") in data.columns):
                        self.mapDict[species] = name
                        break
                else:
                    if (name in data.columns):
                        self.mapDict[species] = name
                        break
            else:
               if (multipleBenches == True): 
                   channelNames.append(channelNames[0] + "2")   
                   raise Exception("Cannot find %s channel names %s in file %s" % (species.replace("_"," "), channelNames, filename))    
               else:
                   raise Exception("Cannot find %s channel %s in file %s" % (species.replace("_"," "), channelNames, filename))    
                   

        for species in self.speciesData.Species.items():
            if (species[1]['multiple_benches'] == True):
                _check_channels_util(species[0], species[1]['channel_names'], True, self.data, self.filename)
            else:
                _check_channels_util(species[0], species[1]['channel_names'], False, self.data, self.filename)
 

     def _load_metadata(self, data, filename):

        metaData = data[:2]
        if 'proj' in metaData.columns:
            self.logDict['info'] = "Meta-Data read from import file %s" % filename
            return metaData
        else:
            self.logDict['warning'] = "Meta-Data missing in import file %s" % filename


class FullLoad(Data):

     def load_data(self, dataFile):
          self.data = pd.read_csv(dataFile)
          self.metaData = self.load_meta_data()

     

class CycleValidator:
    

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
            

            






    
    




         


