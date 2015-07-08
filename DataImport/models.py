from django.db import models
from Ebench.models import Ebench

import pandas as pd
import statsmodels.api as sm
import logging
import math
import itertools
import numpy as np
import datetime
import time as time

class DataHandler:

  def __init__(self):

    self.resultsLog = {'Regression': {},'Regression_bool': {}, 'Data Alignment': {}, 'Calculation': {}, 'Report':{}}
    self.fileDict = {'FULL': 'fullLoad', 'PRE':'preZeroSpan','MAIN':'testData','POST':'postZeroSpan'}
    self.CyclesData = pd.read_json("cycles.json").Cycles
    self.speciesData = pd.read_json("spec.json")
    self.ebenches = Ebench.objects.all()
    self.masterDict = {}
    self.masterMetaData = pd.DataFrame()
    self.masterFileName = None    
    self.allFilesLoaded = False
    self.CoHigh = None    
    self.CycleAttr = {}
    self.log = {}

  def import_data(self, dataFile):        

    self._clear_all_files_loaded()
    RawData = pd.read_csv(dataFile, encoding='windows-1258')
    File = RawData[:1]['CycleState1065'][0] # Reads the filetype out of header page

    if File == 'FULL':
      fileType = FullLoad(dataFile)

    elif File == 'PRE':
      fileType = ZeroSpan(dataFile)

    elif File == 'MAIN':
      self.CycleAttr = self._load_cycle_attr(self.CycleAttr, RawData[:1], self.CyclesData)
      fileType = TestData(dataFile, self.CycleAttr['CycleType'])

    elif File == 'POST':
      fileType = ZeroSpan(dataFile)

    [masterDict, masterMetaData, masterFileName, CoHigh] = fileType.load_data(RawData, self.masterMetaData, self.masterFileName, self.masterDict, self.speciesData)  
    setattr(self, self.fileDict[File], fileType)
    self._set_variables(masterDict, masterMetaData, masterFileName, CoHigh, fileType)

    if File == 'MAIN':
      self.ebenchData = self._load_ebench(self.ebenches[int(self.CycleAttr['EbenchNum'])-1].history, self.testData.TimeStamp)

    self._check_files_loaded()


  def _set_variables(self, masterDict, masterMetaData, masterFileName, CoHigh, fileType):

    if fileType.fileType == 'ZeroSpan' or fileType.fileType == 'TestData':
      self.masterDict.update(masterDict)
    if self.masterMetaData.empty:
      self.masterMetaData = masterMetaData
    if (self.masterFileName == None):
      self.masterFileName = masterFileName
    if CoHigh != None:
      self.CoHigh = CoHigh   


  def _clear_all_files_loaded(self):

  ##### Clears all Data and resets the Datahandler when 5th file is uploaded #####
    if(self.allFilesLoaded == True):
      del self.testData, self.preZeroSpan, self.postZeroSpan, self.fullLoad
      self.__init__()


  def _check_files_loaded(self):        

    ##### Checks whether all files are uploaded #####
    attrs = ['fullLoad', 'postZeroSpan', 'preZeroSpan', 'testData']        

    for attr in attrs:
      if not hasattr(self, attr):
        self.allFilesLoaded = False
        break
    else:
      self.allFilesLoaded = True
      self.masterDict = self.testData.mapDict
      self.masterDict.update(self.preZeroSpan.mapDict)
      
      
  def _load_cycle_attr(self, CycleAttr, MetaData, CyclesData):

    Cycle = MetaData['CycleType1065'][0]
    CycleAttr['Cycle'] = Cycle
    CycleAttr['EbenchNum'] = MetaData['EbenchID']
    CycleAttr['Name'] = CyclesData[Cycle]['Name']    
    CycleAttr['Engine'] = CyclesData[Cycle]['Engine']
    CycleAttr['CycleType'] = CyclesData[Cycle]['CycleType']
    CycleAttr['Fuel'] = CyclesData[Cycle]['Fuel']
    CycleAttr['FactorMult'] = CyclesData[Cycle]['NOxFactorMult']
    CycleAttr['FactorAdd'] = CyclesData[Cycle]['NOxFactorAdd']

    # Clear Variables
    Cycle, MetaData, CyclesData = None, None, None

    return CycleAttr     


  def _load_ebench(self, Ebenches, TimeStamp):

    ############### HARD CODED TIMESTAMP #######################
    TimeStamp = time.time()
    ############################################################

    ebenchData = {}    
    for EbenchSet in Ebenches.values():
      if EbenchSet['history_date'].timestamp() < TimeStamp :

        ebenchData['RFPF'] = EbenchSet['CH4_Penetration_Factor']
        ebenchData['CH4_RF'] = EbenchSet['CH4_Response_Factor']
        ebenchData['Tchiller'] = EbenchSet['Thermal_Chiller_Dewpoint']
        ebenchData['Pchiller'] = EbenchSet['Thermal_Absolute_Pressure']
        ebenchData['xTHC[THC_FID]init'] = EbenchSet['THC_Initial_Contamination']
        ebenchData['Bottle_Concentration_CO2'] = EbenchSet['Bottle_Concentration_CO2']
        ebenchData['Bottle_Concentration_COH'] = EbenchSet['Bottle_Concentration_COH']
        ebenchData['Bottle_Concentration_COL'] = EbenchSet['Bottle_Concentration_COL']
        ebenchData['Bottle_Concentration_NOX'] = EbenchSet['Bottle_Concentration_NOX']
        ebenchData['Bottle_Concentration_THC'] = EbenchSet['Bottle_Concentration_THC']
        ebenchData['Bottle_Concentration_NMHC'] =  EbenchSet['Bottle_Concentration_NMHC']
        break

    return ebenchData    



class Data:

  def __init__(self, dataFile):
      
    self.mapDict = {}
    self.logDict = {}
    self.CycelAttr = {}

    self.dataFile = dataFile
    self.fileName = dataFile.name
    self.fileType = self.__class__.__name__


  def load_data(self, RawData, masterMetaData, masterFileName, masterDict, speciesData):

    ##### Load Spec-File, Metadata, Data, Units #####
    self.speciesData = speciesData
    self.data = RawData
    [self.metaData, masterMetaData, masterFileName] = self._load_metadata(self.data, self.fileName, masterMetaData, masterFileName)
    [self.data, self.units] = self._load_data_units(self.data)

    ##### Perform Checks on Data #####
    self._check_metadata(self.metaData, self.fileName, masterMetaData, masterFileName) 
    self._check_channels()
    self._check_units()
    
    CoHigh = self._check_ranges()

    return self.mapDict, masterMetaData, masterFileName, CoHigh


  def _load_metadata(self, data, FileName, masterMetaData, masterFileName):

    metaData = data[:1]     

    for channel in self.speciesData.Species.items():
      if channel[1]['header_data'] == True:
        for channelName in channel[1]['channel_names']:
          if channelName in metaData.columns:
            self.logDict['info'] = "Meta-Data read from import file %s" % self.fileName
                     
          else:
            self.logDict['warning'] = "Meta-Data missing in import file %s" % self.fileName
            raise Exception("Cannot find %s channel in header data of file %s" % (channelName, self.fileName))

    if masterFileName == None:

      masterMetaData = metaData
      masterFileName = FileName                

    return metaData, masterMetaData, masterFileName  


  def _load_data_units(self, RawData):

      self.data.columns = RawData.loc[1].values
      self.data = RawData[2:]
      units = RawData[2:3]
      self.data = self.data.dropna(how="all",axis=(1))
      self.data = (self.data.convert_objects(convert_numeric=True)).dropna() # Convert and drop NA
      self.data.index = range(0,len(self.data))

      # Clear Variables
      RawData = None

      return self.data, units


  def _check_metadata(self, MetaData, FileName, masterMetaData, masterFileName):

    SkipList = ['N_TR','no_run','Comment1','Comment2','Proj#', 'N_TQ', 'CycleCondition1065','CycleState1065', 'N_FLAG2'] # Remove CycleCondition later e.g COS = Coldstart

    ##### Compare Metadata with Master-MetaData #####
    for x, y, z in zip(masterMetaData.values[0],MetaData.values[0],MetaData):
      if (not x == y) and (z not in SkipList):
        raise Exception("%s in file %s is not the same as in file %s" % (z, FileName, masterFileName))              
               

  def _check_units(self):

    for species in self.mapDict:
      unit = self.speciesData.Species[species]['unit']
      if self.speciesData.Species[species]['header_data'] == False:
        booleanCond = self.units[self.mapDict[species]].str.contains(unit)

        if not (booleanCond.any()):
          self.logDict['error'] = "%s units are not in %s" % (self.mapDict[species], unit)          
          raise Exception("%s units are not in %s" % (self.mapDict[species], unit))


  def _check_channels(self):
      
    for species in self.speciesData.Species.items():
      if species[1]['files'].__contains__(self.fileType) and species[1]['header_data'] == False:
        if (species[1]['multiple_benches'] == True):
          self._check_channels_util(species[0], species[1]['channel_names'], True, self.data, self.fileName)
        else:
          self._check_channels_util(species[0], species[1]['channel_names'], False, self.data, self.fileName)                   
      elif species[1]['header_data'] == True:
          self._check_channels_util(species[0], species[1]['channel_names'], False, self.metaData, self.fileName)

    # Clear Variables
    species = None


  def _check_channels_util(self, species, channelNames, multipleBenches, data, fileName):   

    ##### For Loop through all entries of of mapDict        
    for name in channelNames:
      if name in data.columns:
        self.mapDict[species] = name
        break
    else:
        raise Exception("Cannot find %s channel %s in file %s" % (species.replace("_"," "), channelNames, fileName))   

    # Clear Variables
    name = None


  def _check_ranges(self):

    CoHigh = None
        
    for species in self.mapDict:       

      ##### Read Max/Min-Vaues from json-file #####
      maxValue = self.speciesData.Species[species]['maximum_value']
      minValue = self.speciesData.Species[species]['minimum_value']

      ##### Load Values from Data #####
      if self.speciesData.Species[species]['header_data'] == False:
        source = self.data
        maxCompare = np.nanmax(source[self.mapDict[species]])[0]
        minCompare = np.nanmin(source[self.mapDict[species]])[0]

      ##### Load Values from Metadata #####
      else:
        source = self.metaData
        maxCompare = float(source[self.mapDict[species]][0])
        minCompare = float(source[self.mapDict[species]][0])

      ##### Check whether maximum out of Range #####
      if (maxCompare > float(maxValue)) == True:
        self._output_out_of_range(species, maxValue, 'above required maximum')       

      ##### Check whether minimum out of Range #####
      if (minCompare < float(minValue)) == True:
        if species == 'Carbon_Monoxide_Low_Dry':
          CoHigh = True
        else:
          self._output_out_of_range(species, minValue, 'below required minimum')

    return CoHigh


  def _output_out_of_range(self, species, Value, ErrorString):   

    self.logDict['error'] = "%s is %s of %s %s" % (self.mapDict[species], ErrorString, str(Value), self.speciesData.Species[species]['unit'])
    raise Exception ("%s is %s of %s %s" % (self.mapDict[species], ErrorString, str(Value), self.speciesData.Species[species]['unit']))



class FullLoad(Data):

  def __init__(self, dataFile):
    super().__init__(dataFile)


  def load_data(self, dataFile, masterMetaData, masterFileName, masterDict, speciesData):

    [_, masterMetaData, masterFileName, _] = super().load_data(dataFile, masterMetaData, masterFileName, masterDict, speciesData)          
    return _, masterMetaData, masterFileName, _


  def _check_channels_util(self, species, channelNames, multipleBenches, data, fileName):  
    ##### For Loop through all entries of of mapDict        
    for name in channelNames:
      if name in data.columns:
        break
    else:
        raise Exception("Cannot find %s channel %s in file %s" % (species.replace("_"," "), channelNames, fileName))   

    # Clear Variables
    name = None        



class ZeroSpan(Data):

  def __init__(self, dataFile):
    super().__init__(dataFile)

  def load_data(self, dataFile, masterMetaData, masterFileName, masterDict, speciesData):

    [mapDict, masterMetaData, masterFileName, _] = super().load_data(dataFile, masterMetaData, masterFileName, masterDict, speciesData)   
    return mapDict, masterMetaData, masterFileName, _

  def _check_channels_util(self, species, channelNames, multipleBenches, data, fileName):

    ##### For Loop through all entries of of mapDict     
    for name in channelNames:
      if name in data.columns:
        if multipleBenches == True:
          BenchChannel = self._set_bench_channel(data, name)
        else:
          BenchChannel = ''
        
        self.mapDict[species] = name + BenchChannel
        break
    else:
        raise Exception("Cannot find %s channel %s in file %s" % (species.replace("_"," "), channelNames, fileName))   

    # Clear Variables
    name = None


  def _set_bench_channel(self, data, name):

    MaxPctChange = np.nanmax(data[name].pct_change())[0]
    if MaxPctChange > 0.5:
      return ''
    else:
      return '2'    



class TestData(Data):

  def __init__(self, dataFile, CycleType):
    super().__init__(dataFile)
    self.CycleType = CycleType


  def load_data(self, dataFile, masterMetaData, masterFileName, masterDict, speciesData):

    [_, masterMetaData, masterFileName, CoHigh] = super().load_data(dataFile, masterMetaData, masterFileName, masterDict, speciesData)
    self.TimeStamp = time.mktime(datetime.datetime.strptime(self.data['Date'][0] + ' ' + self.data['Time'][0], "%m/%d/%Y %H:%M:%S.%f").timetuple())

    return _, masterMetaData, masterFileName, CoHigh


  def _load_data_units(self, RawData):

    [data, units] = super()._load_data_units(RawData)

    if self.CycleType == 'Steady':
      data = self._load_steady_state(data)

    return data, units


  def _load_steady_state(self, Data): 

    Torque71_6 = max(Data['N_CERTTRQ'])
    Data = Data[Data['N_CERTMODE'].isin(pd.Series(Data['N_CERTMODE'].astype(int)).unique())]
    Data = Data[Data['N_CERTMODE']>0]
    Data['UDPi_TorqueDemand'] = Data['N_CERTTRQ']
    Data['UDPi_TorqueDemand'][Data['N_CERTMODE'] == 1] = Torque71_6/0.716
    Data['UDPi_SpeedDemand'] = Data['N_CERTSPD']
    Data.index = range(0,len(Data))

    return Data


  def _check_ranges(self):
    
    CoHigh = super()._check_ranges()

    if CoHigh == None:
      CoHigh = False

    return CoHigh



class CycleValidator:
    

    def __init__(self, Testdata, Mapdict, Fullload, Warmidle, filterChoice):

        ##### Load Data #####
        self.FilterChoice = filterChoice     
        self.data = Testdata.data
        self.data_full = Fullload.data
        self.data_full.index = range(0,len(self.data_full))
        self.data.index = range(0,len(self.data))
        self.mapDict = Mapdict

        ##### Define Variables #####     
        self.Throttle = self.data[self.mapDict['Commanded_Throttle']]
        self.Torque_Demand = self.data[self.mapDict['Commanded_Torque']]
        self.Torque_Engine = self.data[self.mapDict['Engine_Torque']] 
        self.Speed_Demand = self.data[self.mapDict['Commanded_Speed']]
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

        if (self.FilterChoice != 0):
          self._pre_regression_filter(self.FilterChoice)        
        self._regression()
        self._regression_validation()
        
    def _pre_regression_filter(self, FilterChoice):

        for i in self.Index_Min:
            ##### Check Minimum Throttle ##### -- Table 1 EPA 1065.514
            if (self.Torque_Demand[i])<0 and (FilterChoice == 1):
                self.Torque_Drop.append(i)
                self.Power_Drop.append(i)                  
                
            if (self.Torque_Demand[i]==0) and (self.Speed_Demand[i]==0) and ((self.Torque_Engine[i]-0.02*self.Torque_Max)<self.Torque_Engine[i]) and (self.Torque_Engine[i]<(self.Torque_Engine[i]+0.02*self.Torque_Max)) and (FilterChoice == 2):
                self.Speed_Drop.append(i)
                self.Power_Drop.append(i)
                
            if (self.Torque_Engine[i]>self.Torque_Demand[i]) and ((self.Torque_Engine[i]<(self.Torque_Engine[i]+0.02*self.Torque_Max)) | (self.Torque_Engine[i]<(self.Torque_Engine[i]-0.02*self.Torque_Max))) and (FilterChoice == 3):
                self.Torque_Drop.append(i)
                self.Power_Drop.append(i)
                
            if (self.Speed_Engine[i]>self.Speed_Demand[i]) and (self.Speed_Engine[i]<self.Speed_Demand[i]*1.02) and (FilterChoice == 4):
                self.Speed_Drop.append(i)
                self.Power_Drop.append(i)
            
        for j in self.Index_Max:
            ##### Check Maximum Throttle ##### -- Table 1 EPA 1065.514                
            if (self.Torque_Engine[j]<self.Torque_Demand[j]) and (self.Torque_Engine[j]>(self.Torque_Engine[j]-0.02*self.Torque_Max)) and (FilterChoice == 5):
                self.Torque_Drop.append(j)
                self.Power_Drop.append(j)

            if (self.Speed_Engine[j]<self.Speed_Demand[j]) and (self.Speed_Engine[j]>self.Speed_Demand[j]*0.98) and (FilterChoice == 6):
                self.Speed_Drop.append(j)
                self.Power_Drop.append(j)                    

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
        
        self.reg_results = {'Torque': { 'Slope': " ", 'Intercept': " ", 'Standard Error': " ", 'Rsquared': " " },
                            'Power': { 'Slope': " ", 'Intercept': " ", 'Standard Error': " ", 'Rsquared': " " }, 
                            'Speed': { 'Slope': " ", 'Intercept': " ", 'Standard Error': " ", 'Rsquared': " " }}
        
        for channel in self.dataDict.items():

          self._regression_util(channel[0], channel[1][1], channel[1][0])
 

    def _regression_util(self, channel, X, Y):

        ymean = vars(self)[Y].mean()
        xmean = vars(self)[X].mean()

        # -- Regression Slope -- EPA 1065.602-9   
        numerator, denominator = 0.0, 0.0
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            numerator = numerator + ((x - xmean) * (y - ymean))
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            denominator = denominator + ((y - ymean) ** 2)
                
        if np.isnan(numerator/denominator) == True:
          Slope = 1
        else:
          Slope = numerator / denominator 

        # -- Regression Intercept -- EPA 1065.602-10 
        Intercept = (xmean - (Slope * ymean))

        # -- Regression Standard Error of Estimate -- EPA 1065.602-11 
        sumat = 0.0
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            sumat = sumat + ((x - Intercept - (Slope * y)) ** 2)
        see = sumat / (vars(self)[X].size - 2)
        standerror = math.sqrt(see)

        # -- Regression Coefficient of determination -- EPA 1065.602-12
        numerator, denominator = 0.0, 0.0
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            numerator = numerator + ((x - Intercept - (Slope * y)) ** 2)
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            denominator = denominator + ((x - ymean) ** 2)
                
        r2 = 1 - (numerator / denominator)

        self.reg_results[channel]['Slope'] = round(Slope,2)
        self.reg_results[channel]['Intercept'] = round(Intercept,2)
        self.reg_results[channel]['Standard Error'] = round(standerror,2)
        self.reg_results[channel]['Rsquared'] = round(r2,2)


    def _regression_validation(self):

        self.reg_results_bool = {'Torque': { 'Slope': False, 'Intercept': False, 'Standard Error': False, 'Rsquared': False }, 
                                  'Power': { 'Slope': False, 'Intercept': False, 'Standard Error': False, 'Rsquared': False },
                                  'Speed': { 'Slope': False, 'Intercept': False, 'Standard Error': False, 'Rsquared': False }}

        # Cycle-validation criteria for operation over specified duty cycles -- EPA 1065.514 - Table 2
        for parameter in self.reg_results:

            ###### Statistical Criteria for Speed #####
            if parameter == 'Speed':

                # Slope
                if (self.reg_results[parameter]['Slope'] <= 1.03) and (self.reg_results[parameter]['Slope'] >= 0.95):
                    self.reg_results_bool[parameter]['Slope'] = True

                # Intercept
                if (self.reg_results[parameter]['Intercept'] <= 0.1*float(self.Warm_Idle)):
                    self.reg_results_bool[parameter]['Intercept'] = True

                # Standard error
                if self.reg_results[parameter]['Standard Error'] <= 0.05*self.Speed_Max:
                    self.reg_results_bool[parameter]['Standard Error'] = True

                # Coefficient of determination
                if self.reg_results[parameter]['Rsquared'] >= 0.97:
                    self.reg_results_bool[parameter]['Rsquared'] = True

            ###### Statistical Criteria for Torque #####
            if parameter == 'Torque':

                # Slope
                if (self.reg_results[parameter]['Slope'] <= 1.03) and (self.reg_results[parameter]['Slope'] >= 0.83):
                    self.reg_results_bool[parameter]['Slope'] = True
                # Intercept
                if (self.reg_results[parameter]['Intercept'] <= 0.02*self.Torque_Max):
                    self.reg_results_bool[parameter]['Intercept'] = True

                # Standard error
                if self.reg_results[parameter]['Standard Error'] <= 0.1*self.Torque_Max:
                    self.reg_results_bool[parameter]['Standard Error'] = True

                # Coefficient of determination
                if self.reg_results[parameter]['Rsquared'] >= 0.85:
                    self.reg_results_bool[parameter]['Rsquared'] = True

            ###### Statistical Criteria for Power #####
            if parameter == 'Power':

                # Slope
                if (self.reg_results[parameter]['Slope'] <= 1.03) and (self.reg_results[parameter]['Slope'] >= 0.83):
                    self.reg_results_bool[parameter]['Slope'] = True

                # Intercept
                if (self.reg_results[parameter]['Intercept'] <= 0.02*self.Power_Max):
                    self.reg_results_bool[parameter]['Intercept'] = True

                # Standard error
                if self.reg_results[parameter]['Standard Error'] <= 0.1*self.Power_Max:
                    self.reg_results_bool[parameter]['Standard Error'] = True

                # Coefficient of determination
                if self.reg_results[parameter]['Rsquared'] >= 0.91:
                    self.reg_results_bool[parameter]['Rsquared'] = True






