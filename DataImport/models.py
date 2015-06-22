from django.db import models
from Ebench.models import Ebench

import pandas as pd
import statsmodels.api as sm
import logging
import math
import itertools
import numpy as np

class DataHandler:

     def __init__(self):
         # need required channels for each file
          self.resultsLog = {'Regression': {},'Regression_bool': {}, 'Data Alignment': {}, 'Calculation': {}} 
          self.log = {}
          self.masterDict = {} 
          self.ebenches = Ebench.objects.all()
          self.allFilesLoaded = False

          self.CoHigh = True



     #Have to change ordering of load data so that excpetion causes file to not be saved to datahandler

          ######## HARD CODE EBENCH #########
          self.ebenchData = {}
          self.ebenchData['RFPF'] = 0.0133
          self.ebenchData['CH4_RF'] = 1.1
          self.ebenchData['Tchiller'] = 7
          self.ebenchData['Pchiller'] = 121.8418852
          self.ebenchData['xTHC[THC_FID]init'] = 1
          ###################################



     def import_test_data(self, numBenches, dataFile):
          self.testData = TestData(dataFile, numBenches) 
          self.testDataMapDict = self.testData.load_data(dataFile)
          self._all_files_loaded()          
         
     def import_pre_zero_span(self, dataFile):
          self.preZeroSpan = ZeroSpan(dataFile)
          self.zeroSpanMapDict = self.preZeroSpan.load_data(dataFile)
          self._all_files_loaded()
          
     def import_post_zero_span(self, dataFile):
          self.postZeroSpan = ZeroSpan(dataFile)
          self.zeroSpanMapDict = self.postZeroSpan.load_data(dataFile)
          self._all_files_loaded()
          
     def import_full_load(self, dataFile):
          self.fullLoad = FullLoad(dataFile)
          self.fullLoadMapDict = self.fullLoad.load_data(dataFile)
          self._all_files_loaded()

     def _all_files_loaded(self):
          
          self.attrs = ['fullLoad', 'postZeroSpan', 'preZeroSpan', 'testData']

          for attr in self.attrs:
               if not hasattr(self, attr):
                    break
          else:
               self.allFilesLoaded = True

          if(self.allFilesLoaded == True):
               self.files = [self.testData, self.preZeroSpan, self.postZeroSpan, self.fullLoad]
               #self._check_all_metadata()
               #self._check_time_stamps
               
               
     def _check_all_metadata(self):
          for x, y in itertools.combinations(self.files, 2):
               if not x.metaData.equals(y.metaData):
                    raise Exception("metadata in file %s does not match file %s" % (x.fileName, y.fileName))
                              


     #def _check_all_time_stamps:

     

     # def _corr_frequencies(self):
          

     # def _corr_time_stamps(self):


     # def _corr_fuel_data(self):



#load all files check each import if all files are uploaded



#Files must arrive in a certain order to check things
#Full load -> regression
#zero and spans can be in any order 

class Data:

     def __init__(self, dataFile):
          
          self.mapDict = {}
          self.logDict = {}

          self.dataFile = dataFile
          self.fileName = dataFile.name
          self.fileType = self.__class__.__name__


     def load_data(self, dataFile):


          self.speciesData = pd.read_json("spec.json")
          self.data = pd.read_csv(dataFile, encoding='windows-1258')
          self.metaData, self.data = self._load_metadata(self.data)

          self.data = self.data.dropna(how="all",axis=(1))
          self._check_units()
          self.data = self.data.convert_objects(convert_numeric=True)       # Convert all data to numeric
          self.data = self.data.dropna()
          self.data.index = range(0,len(self.data))
          self._check_channels()


          return self.mapDict


     def _check_channels_util(self, species, channelNames, multipleBenches, data, fileName):
            
          for name in channelNames:
               if name in data.columns:
                    self.mapDict[species] = name
                    break
               # if (multipleBenches == True ) and (self.numBenches == '2'):
               #      if (name in data.columns) and ((name + "2") in data.columns):
               #           self.mapDict[species] = name
               #           break
               # else:
          else:
               raise Exception("Cannot find %s channel %s in file %s" % (species.replace("_"," "), channelNames, fileName))
               # if (multipleBenches == True):
               #     channelNames.append(channelNames[0] + "2")
               #     raise Exception("Cannot find %s channel names %s in file %s" % (species.replace("_"," "), channelNames, fileName))
               # else:
              
                   

     def _check_channels(self):          
          
          for species in self.speciesData.Species.items():

               if species[1]['files'].__contains__(self.fileType) and species[1]['header_data'] == False:
                    if (species[1]['multiple_benches'] == True):
                         self._check_channels_util(species[0], species[1]['channel_names'], True, self.data, self.fileName)
                    else:
                         self._check_channels_util(species[0], species[1]['channel_names'], False, self.data, self.fileName)
                         
               elif species[1]['header_data'] == True:
                    self._check_channels_util(species[0], species[1]['channel_names'], False, self.metaData, self.fileName)
    

     def _check_units(self):

          for species in self.mapDict:
               unit = self.speciesData.Species[species]['unit']
               if self.speciesData.Species[species]['header_data'] == False: 
                    booleanCond = self.data[self.mapDict[species]].str.contains(unit)
                    if not (booleanCond.any()):
                         self.logDict['error'] = "%s units are not in %s" % (self.mapDict[species], unit)
                         raise Exception("%s units are not in %s" % (self.mapDict[species], unit))




     def _load_metadata(self, data):

          metaData = data[:1]
          data.columns = data.loc[1].values
          data = data[2:]

          for channel in self.speciesData.Species.items():
              if channel[1]['header_data'] == True:
                    for channelName in channel[1]['channel_names']:
                         if channelName in metaData.columns:
                              self.logDict['info'] = "Meta-Data read from import file %s" % self.fileName
                             
                         else:
                              self.logDict['warning'] = "Meta-Data missing in import file %s" % self.fileName
                              raise Exception("Cannot find %s channel in header data of file %s" % (channelName, self.fileName))

          return metaData, data




class FullLoad(Data):

     def __init__(self, dataFile):
          super().__init__(dataFile)


class ZeroSpan(Data):

     def __init__(self, dataFile):
          super().__init__(dataFile)


class TestData(Data):

     def __init__(self, dataFile, numBenches):
          super().__init__(dataFile)
          self.numBenches = numBenches



     # def load_data(self,filename):

     #    self.filename = filename

     #    self.speciesData = pd.read_json("spec.json")
     #    self.data = pd.read_csv(filename)                                 # Read Data into DataFrame
     #    self.metaData = self._load_metadata(self.data, filename)          # Read Meta data
     #    self._check_channels()                                            # Check Units based on dictionary
     #    self._check_units()
     #    self.data = self.data.convert_objects(convert_numeric=True)       # Convert all data to numeric
     #    self.data = self.data.dropna()                                    # Drop NaN values from data
     #    self._check_ranges()
     #    self._convert_bar_to_kpa()
       
     #    return self.data, self.mapDict, self.logDict


     # def _convert_bar_to_kpa(self): #FIX DIS
        
     #    self.data.P_AMB = self.data.P_AMB * 100
     #    self.data.P_INLET = self.data.P_INLET * 100


     # def _check_units(self):

     #    for species in self.mapDict:

     #        unit = self.speciesData.Species[species]['unit']
     #        booleanCond = self.data[self.mapDict[species]].str.contains(unit)
     #        if not (booleanCond.any()):
     #            self.logDict['error'] = "%s units are not in %s" % (self.mapDict[species], unit)
     #            raise Exception("%s units are not in %s" % (self.mapDict[species], unit))


     # def _check_ranges(self):
        
     #    for species in self.mapDict:

     #        maxValue = self.speciesData.Species[species]['maximum_value']
     #        minValue = self.speciesData.Species[species]['minimum_value']

     #        booleanCond = self.data[self.mapDict[species]] > float(maxValue)
     #        if(booleanCond.any()):
     #            self.logDict['error'] = "%s is above required maximum of %s %s" % (self.mapDict[species], str(maxValue), self.speciesData.Species[species]['unit'])
     #            raise Exception ("%s is above required maximum of %s %s" % (self.mapDict[species], str(maxValue), self.speciesData.Species[species]['unit']))
     #        booleanCond = self.data[self.mapDict[species]] < float(minValue)
     #        if(booleanCond.any()):
     #            self.logDict['error'] = "%s is below required minimum of %s %s" % (self.mapDict[species], str(minValue), self.speciesData.Species[species]['unit'])
     #            raise Exception ("%s is below required minimum of %s %s" % (self.mapDict[species], str(minValue), self.speciesData.Species[species]['unit']))


     # def _check_channels(self):

     #    def _check_channels_util(species, channelNames, multipleBenches, data, filename):
            
     #        for name in channelNames:
     #            if (multipleBenches == True ) and (self.bench == '2'):
     #                if (name in data.columns) and ((name + "2") in data.columns):
     #                    self.mapDict[species] = name
     #                    break
     #            else:
     #                if (name in data.columns):
     #                    self.mapDict[species] = name
     #                    break
     #        else:
     #           if (multipleBenches == True): 
     #               channelNames.append(channelNames[0] + "2")   
     #               raise Exception("Cannot find %s channel names %s in file %s" % (species.replace("_"," "), channelNames, filename))    
     #           else:
     #               raise Exception("Cannot find %s channel %s in file %s" % (species.replace("_"," "), channelNames, filename))    
                   

     #    for species in self.speciesData.Species.items():
     #        if (species[1]['multiple_benches'] == True):
     #            _check_channels_util(species[0], species[1]['channel_names'], True, self.data, self.filename)
     #        else:
     #            _check_channels_util(species[0], species[1]['channel_names'], False, self.data, self.filename)
 

     # def _load_metadata(self, data, filename):

     #    metaData = data[:2]
     #    if 'proj' in metaData.columns:
     #        self.logDict['info'] = "Meta-Data read from import file %s" % filename
     #        return metaData
     #    else:
     #        self.logDict['warning'] = "Meta-Data missing in import file %s" % filename


class CycleValidator:
    

    def __init__(self, Testdata, Mapdict, Fullload, Warmidle, Filter_bool):

        self.data = Testdata.data
        self.data_full = Fullload.data
        self.data_full.index = range(0,len(self.data_full))
        self.data.index = range(0,len(self.data))
        self.mapDict = Mapdict

        ##### Define Variables #####     
        self.Throttle = self.data[self.mapDict['Commanded_Throttle']]
        self.Torque_Demand = self.data[self.mapDict['Commanded_Torque']]
        self.Torque_Engine = self.data[self.mapDict['Engine_Torque']] 
        self.Speed_Demand = self.data[self.mapDict['Commanded_Throttle']]
        self.Speed_Engine = self.data[self.mapDict['Engine_Speed']]
        self.Power_Demand = (self.data[self.mapDict['Commanded_Torque']] * self.data[self.mapDict['Commanded_Speed']] / 9.5488) / 1000
        self.Power_Engine = self.data[self.mapDict['Engine_Power']]
        self.data = None

        ##### Maximum of Speed, Torque, Power and warm idle #####
        self.Speed_Max = np.nanmax(self.data_full[self.mapDict['Engine_Speed']])[0]
        self.Torque_Max = np.nanmax(self.data_full[self.mapDict['Engine_Torque']])[0]
        self.Power_Max = np.nanmax(self.data_full[self.mapDict['Engine_Power']])[0]
        self.Warm_Idle = Warmidle[0]
        self.data_full = None

        ##### Index of Maximum and Minimum Throttle #####
        self.Index_Min = np.where([self.Throttle==np.nanmin(self.Throttle)[0]])[1]
        self.Index_Max = np.where([self.Throttle==np.nanmax(self.Throttle)[0]])[1]


        ##### Drop Lists #####
        self.Torque_Drop = []
        self.Speed_Drop = []
        self.Power_Drop = []

        self.dataDict = {'Torque': ['Torque_Demand', 'Torque_Engine'],
                         'Power': ['Power_Demand', 'Power_Engine'], 
                         'Speed': ['Speed_Demand', 'Speed_Engine']}
        if Filter_bool:
          self._pre_regression_filter()        
        self._regression()
        self._regression_validation()
        
    def _pre_regression_filter(self):

        for i in self.Index_Min:
            ##### Check Minimum Throttle ##### -- Table 1 EPA 1065.514
            if self.Torque_Demand[i]<0:
                self.Torque_Drop.append(i)
                self.Power_Drop.append(i)
                self.Torque_Below_Zero = True # Used to show the User that negative Torque during motoring is omitted                    
                
            if (self.Torque_Demand[i]==0) & (self.Speed_Demand[i]==0) & ((self.Torque_Engine[i]-0.02*self.Torque_Max)<self.Torque_Engine[i]) & (self.Torque_Engine[i]<(self.Torque_Engine[i]+0.02*self.Torque_Max)):
                self.Speed_Drop.append(i)
                self.Power_Drop.append(i)
                
            if (self.Speed_Engine[i]>self.Speed_Demand[i]) & (self.Speed_Engine[i]<self.Speed_Demand[i]*1.02):
                self.Speed_Drop.append(i)
                self.Power_Drop.append(i)
                
            if (self.Torque_Engine[i]>self.Torque_Demand[i]) & ((self.Torque_Engine[i]<(self.Torque_Engine[i]+0.02*self.Torque_Max)) | (self.Torque_Engine[i]<(self.Torque_Engine[i]-0.02*self.Torque_Max))):
                self.Torque_Drop.append(i)
                self.Power_Drop.append(i)
            
        for i in self.Index_Max:
            ##### Check Maximum Throttle ##### -- Table 1 EPA 1065.514
            if (self.Speed_Engine[i]<self.Speed_Demand[i]) & (self.Speed_Engine[i]>self.Speed_Demand[i]*0.98):
                self.Speed_Drop.append(i)
                self.Power_Drop.append(i)
                
            if (self.Torque_Engine[i]<self.Torque_Demand[i]) & (self.Torque_Engine[i]>(self.Torque_Engine[i]-0.02*self.Torque_Max)):
                self.Torque_Drop.append(i)
                self.Power_Drop.append(i)            

        ##### Omitting the Data #####
        self.Speed_Engine = self.Speed_Engine.drop(self.Speed_Drop)
        self.Speed_Demand = self.Speed_Demand.drop(self.Speed_Drop)
        self.Torque_Engine = self.Torque_Engine.drop(self.Torque_Drop)
        self.Torque_Demand = self.Torque_Demand.drop(self.Torque_Drop)
        self.Power_Engine = self.Power_Engine.drop(self.Power_Drop)
        self.Power_Demand = self.Power_Demand.drop(self.Power_Drop)            

        ##### Reindexing the data #####
        self.Torque_Engine.index = range(0,len(self.Torque_Engine))
        self.Torque_Demand.index = range(0,len(self.Torque_Demand))
        self.Speed_Engine.index = range(0,len(self.Speed_Engine))
        self.Speed_Demand.index = range(0,len(self.Speed_Demand))
        self.Power_Engine.index = range(0,len(self.Power_Engine))
        self.Power_Demand.index = range(0,len(self.Power_Demand))

        ##### Cleaning Variables #####
        self.Throttle, self.Index_Min = None, None
        self.Torque_Drop, self.Speed_Drop, self.Power_Drop = None, None, None
       

    def _regression(self):
        
        self.reg_results = {'Torque': { 'slope': " ", 'intercept': " ", 'standard_error': " ", 'rsquared': " " },
                            'Power': { 'slope': " ", 'intercept': " ", 'standard_error': " ", 'rsquared': " " }, 
                            'Speed': { 'slope': " ", 'intercept': " ", 'standard_error': " ", 'rsquared': " " }}
        
        for channel in self.dataDict.items():
           self._regression_util(channel[0], channel[1][0], channel[1][1])
 

    def _regression_util(self, channel, X, Y):

        ymean = vars(self)[Y].mean()
        xmean = vars(self)[X].mean()

        # -- Regression Slope -- EPA 1065.602-9 
        numerator, denominator = 0.0, 0.0
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            numerator = numerator + ((x - xmean) * (y - ymean))
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            denominator = denominator + ((y - ymean) ** 2)
                
        slope = numerator / denominator 

        # -- Regression Intercept -- EPA 1065.602-10 
        intercept = (xmean - (slope * ymean))

        # -- Regression Standard Error of Estimate -- EPA 1065.602-11 
        sumat = 0.0
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            sumat = sumat + ((x - intercept - (slope * y)) ** 2)
        see = sumat / (vars(self)[X].size - 2)
        standerror = math.sqrt(see)

        # -- Regression Coefficient of determination -- EPA 1065.602-12
        numerator, denominator = 0.0, 0.0
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            numerator = numerator + ((x - intercept - (slope * y)) ** 2)
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            denominator = denominator + ((x - ymean) ** 2)
                
        r2 = 1 - (numerator / denominator)

        self.reg_results[channel]['slope'] = round(slope,2)
        self.reg_results[channel]['intercept'] = round(intercept,2)
        self.reg_results[channel]['standard_error'] = round(standerror,2)
        self.reg_results[channel]['rsquared'] = round(r2,2)


    def _regression_validation(self):

        self.reg_results_bool = {'Torque': { 'slope': False, 'intercept': False, 'standard_error': False, 'rsquared': False }, 
                                  'Power': { 'slope': False, 'intercept': False, 'standard_error': False, 'rsquared': False },
                                  'Speed': { 'slope': False, 'intercept': False, 'standard_error': False, 'rsquared': False }}

        # Cycle-validation criteria for operation over specified duty cycles -- EPA 1065.514 - Table 2
        for parameter in self.reg_results:

            ###### Statistical Criteria for Speed #####
            if parameter == 'Speed':

                # Slope
                if (self.reg_results[parameter]['slope'] <= 1.03) & (self.reg_results[parameter]['slope'] >= 0.95):
                    self.reg_results_bool[parameter]['slope'] = True

                # Intercept
                if (self.reg_results[parameter]['intercept'] <= 0.1*float(self.Warm_Idle)):
                    self.reg_results_bool[parameter]['intercept'] = True

                # Standard error
                if self.reg_results[parameter]['standard_error'] <= 0.05*self.Speed_Max:
                    self.reg_results_bool[parameter]['standard_error'] = True

                # Coefficient of determination
                if self.reg_results[parameter]['rsquared'] >= 0.97:
                    self.reg_results_bool[parameter]['rsquared'] = True

            ###### Statistical Criteria for Torque #####
            if parameter == 'Torque':

                # Slope
                if (self.reg_results[parameter]['slope'] <= 1.03) & (self.reg_results[parameter]['slope'] >= 0.83):
                    self.reg_results_bool[parameter]['slope'] = True
                # Intercept
                if (self.reg_results[parameter]['intercept'] <= 0.02*self.Torque_Max):
                    self.reg_results_bool[parameter]['intercept'] = True

                # Standard error
                if self.reg_results[parameter]['standard_error'] <= 0.1*self.Torque_Max:
                    self.reg_results_bool[parameter]['standard_error'] = True

                # Coefficient of determination
                if self.reg_results[parameter]['rsquared'] >= 0.85:
                    self.reg_results_bool[parameter]['rsquared'] = True

            ###### Statistical Criteria for Power #####
            if parameter == 'Power':

                # Slope
                if (self.reg_results[parameter]['slope'] <= 1.03) & (self.reg_results[parameter]['slope'] >= 0.83):
                    self.reg_results_bool[parameter]['slope'] = True

                # Intercept
                if (self.reg_results[parameter]['intercept'] <= 0.02*self.Power_Max):
                    self.reg_results_bool[parameter]['intercept'] = True

                # Standard error
                if self.reg_results[parameter]['standard_error'] <= 0.1*self.Power_Max:
                    self.reg_results_bool[parameter]['standard_error'] = True

                # Coefficient of determination
                if self.reg_results[parameter]['rsquared'] >= 0.91:
                    self.reg_results_bool[parameter]['rsquared'] = True






