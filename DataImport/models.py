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

    self.resultsLog = {'Regression': {},'Regression_bool': {},
                        'Data Alignment': {'Array':{'NOx':0,'CH4':0,'THC':0,'CO':0,'CO2':0,'NO':0,'MFRAIR':0,'N2O':0,'CH2O':0,'NH3':0},
                        'Data':pd.DataFrame()}, 'Calculation': {}, 'Report':{}}
    self.fileDict = {'FULL': 'fullLoad', 'PRE':'preZeroSpan','MAIN':'testData','POST':'postZeroSpan'}
    self.CyclesData = pd.read_json("cycles.json").Cycles
    self.ChannelData = pd.read_json("spec.json").Species
    self.ebenches = Ebench.objects.all()
    self.masterMetaData = pd.DataFrame()
    self.masterFileName = None
    self.File = None
    self.allFilesLoaded = False
    self.DoCalculation = True
    self.masterDict = {}
    self.CycleAttr = {}
    self.log = {}

  def import_data(self, dataFile):   


    ##### Prepare DataHandler and File #####
    self._clear_all_files_loaded()
    RawData = pd.read_csv(dataFile, encoding='windows-1258')
    self.File = RawData[:1]['CycleState1065'][0] # Reads the filetype out of header page

    ##### Create FileClass #####
    if self.File == 'FULL':
      fileType = FullLoad(dataFile)

    elif self.File == 'PRE':
      fileType = ZeroSpan(dataFile)

    elif self.File == 'MAIN':
      self.CycleAttr = self._load_cycle_attr(self.CycleAttr, RawData[:1], self.CyclesData)
      fileType = TestData(dataFile, self.CycleAttr['CycleType'])

    elif self.File == 'POST':
      fileType = ZeroSpan(dataFile)

    ##### Load File #####
    [masterMetaData, masterFileName] = fileType.load_data(RawData, self.masterMetaData, self.masterFileName, self.masterDict, self.ChannelData)
    setattr(self,self.fileDict[self.File],fileType)

    ##### Set MasterFile #####
    if (self.masterFileName == None):
      self.masterFileName = masterFileName
      self.masterMetaData = masterMetaData 

    ##### Finish Upload #####
    self._check_all_files_loaded()


  def _clear_all_files_loaded(self):

  ##### Clears all Data and resets the Datahandler when 5th file is uploaded #####
    if(self.allFilesLoaded == True):
      del self.testData, self.preZeroSpan, self.postZeroSpan, self.fullLoad
      self.__init__()

      
  def _load_cycle_attr(self, CycleAttr, MetaData, CyclesData):

    Cycle = MetaData['CycleType1065'][0]
    CycleAttr['Cycle'] = Cycle
    CycleAttr['EbenchID'] = MetaData['EbenchID'][0]
    CycleAttr['Name'] = CyclesData[Cycle]['Name']    
    CycleAttr['Engine'] = CyclesData[Cycle]['Engine']
    CycleAttr['CycleType'] = CyclesData[Cycle]['CycleType']
    if CycleAttr['CycleType'] == 'Transient':
      CycleAttr['CycleLength'] = CyclesData[Cycle]['CycleLength']
    CycleAttr['Fuel'] = CyclesData[Cycle]['Fuel']
    CycleAttr['FactorMult'] = CyclesData[Cycle]['NOxFactorMult']
    CycleAttr['FactorAdd'] = CyclesData[Cycle]['NOxFactorAdd']

    return CycleAttr


  def _check_all_files_loaded(self):

    ##### Checks whether all files are uploaded #####
    attrs = ['fullLoad', 'postZeroSpan', 'preZeroSpan', 'testData']        

    for attr in attrs:

      if not hasattr(self, attr):
        self.allFilesLoaded = False
        break

    else:
      self.allFilesLoaded = True
      ##### Check Timestamps of Files
      self._check_time_stamp(self.preZeroSpan.TimeStamp, self.testData.TimeStamp, self.postZeroSpan.TimeStamp, len(self.testData.data))

      ##### Create MaterDict, Set Co-Channel, Load E-Bench-Data #####
      self.masterDict = self._create_master_dict(attrs)
      
      if len(self.ebenches.filter(EbenchID=self.CycleAttr['EbenchID'])) == 0:
        raise Exception("Cannot find associated Ebench in database, please contact Emissions group")
      else:
        self.ebenchData = self._load_ebench(self.ebenches.filter(EbenchID=self.CycleAttr['EbenchID'])[0].history, self.testData.TimeStamp)
      
      ##### Check Channel-Ranges of all files #####
      self.ChannelData = self._set_channel_data()
      for File in attrs:
        vars(self)[File].check_ranges(self.ChannelData)      


  def _set_channel_data(self):
    
    ##### Lists of ChannelNames and BottleNames #####
    ListSpecies = ['Carbon_Dioxide_Dry', 'Carbon_Monoxide_High_Dry', 'Nitrogen_X_Dry', 'Total_Hydrocarbons_Wet', 'Methane_Wet']
    ListBottles = ['Bottle_Concentration_CO2', 'Bottle_Concentration_CO', 'Bottle_Concentration_NOX', 'Bottle_Concentration_THC', 'Bottle_Concentration_NMHC']      

    ##### Change maximum Range-Values of Species to 110% of Bottle-Concentration #####
    for spec, bottle in zip(ListSpecies, ListBottles):
      self.ChannelData[spec]['maximum_value'] = self.ebenchData[bottle]

    return self.ChannelData

  def _create_master_dict(self, attrs):

    masterDict = self.testData.mapDict
    masterDict.update(self.preZeroSpan.mapDict) # testData.mapDict is changed as well

    masterDict = self._set_CO(self.testData.data, masterDict)


    return masterDict


  def _set_CO(self, data, masterDict):

    ##### CO-Strings for masterDict #####
    COL = 'Carbon_Monoxide_Low_Dry'
    COH = 'Carbon_Monoxide_High_Dry'
    CO = 'Carbon_Monoxide_Dry'

    ##### Load Min- Compare/Value for COL #####
    minValue = self.ChannelData[COL]['minimum_value']
    minCompare = np.nanmin(data[masterDict[COL]])[0]

    ##### Check whether minimum out of Range #####
    if (minCompare < float(minValue)) == True:
      masterDict[CO] = masterDict[COH]
    else:
      masterDict[CO] = masterDict[COL]
  
    del masterDict[COL]
    del masterDict[COH]

    # Clear Variables
    COl, COH, CO, minValue, minCompare = None, None, None, None, None

    return masterDict


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
        ebenchData['Bottle_Concentration_CO2'] = EbenchSet['Bottle_Concentration_CO2']/10000 # ppm --> %
        if 'COH' in self.masterDict['Carbon_Monoxide_Dry']:
          ebenchData['Bottle_Concentration_CO'] = EbenchSet['Bottle_Concentration_COH']/10000 # ppm --> %
        else:
          ebenchData['Bottle_Concentration_CO'] = EbenchSet['Bottle_Concentration_COL']
        ebenchData['Bottle_Concentration_NOX'] = EbenchSet['Bottle_Concentration_NOX']
        ebenchData['Bottle_Concentration_THC'] = EbenchSet['Bottle_Concentration_THC']
        ebenchData['Bottle_Concentration_NMHC'] =  EbenchSet['Bottle_Concentration_NMHC']
        break

    self.ebenches = None

    return ebenchData   


  def _check_time_stamp(self,TsPre,TsTest,TsPost,TestLength):

    String = 'Timestamp-Check Failed ! : '
    if (TsTest - TsPre) < 0:
      String = String + 'Timestamp of Pre-ZeroSpan is after the Test. '    
    if (TsPost - TsTest) < 0:
      String = String + 'Timestamp of Post-ZeroSpan is before the Test. '
    if (TsPost - TsTest) > 2*TestLength: 
      String = String + 'Timestamp of Post-ZeroSpan is too late. '
    if (TsTest - TsPre) > TestLength:
      String = String + 'Timestamp of Pre-ZeroSpan is too early. '

    if String != 'Timestamp-Check Failed ! : ':
      raise Exception (String)



class Data:

  def __init__(self, dataFile):
      
    self.mapDict = {}
    self.logDict = {}

    self.dataFile = dataFile
    self.fileName = dataFile.name
    self.fileType = self.__class__.__name__
    self.TimeStamp = None


  def load_data(self, RawData, masterMetaData, masterFileName, masterDict, ChannelData):

    ##### Load Spec-File, Metadata, Data, Units #####
    self.data = RawData
    [self.metaData, masterMetaData, masterFileName] = self._load_metadata(self.data, self.fileName, masterMetaData, masterFileName, ChannelData)
    [self.data, self.units] = self._load_data_units(self.data)
    self.TimeStamp = self._load_timestamp(self.data)
    self.mapDict = self._create_mapDict(ChannelData)

    ##### Perform Checks on Data #####
    self._check_metadata(self.metaData, self.fileName, masterMetaData, masterFileName) 
    self._check_units(ChannelData)

    return masterMetaData, masterFileName


  def _load_metadata(self, data, FileName, masterMetaData, masterFileName, ChannelData):

    metaData = data[:1].dropna(how="all",axis=(1)) # Drop Zero-Columns

    ##### Loop through all entries of ChannelData in the header page #####
    for channel in ChannelData.items():
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
      self.data = self.data.dropna(how="all",axis=(1)) # Drop Zero-Columns
      self.data = (self.data.convert_objects(convert_numeric=True)).dropna() # Convert and drop NA
      self.data.index = range(0,len(self.data))

      return self.data, units


  def _load_timestamp(self, Data):
    return time.mktime(datetime.datetime.strptime(Data['Date'][0] + ' ' + Data['Time'][0], "%m/%d/%Y %H:%M:%S.%f").timetuple())


  def _check_metadata(self, MetaData, FileName, masterMetaData, masterFileName):

    SkipList = ['N_TR','no_run','Comment1','Comment2','Proj#', 'N_TQ', 'CycleCondition1065','CycleState1065', 'N_FLAG2'] # Remove CycleCondition later e.g COS = Coldstart

    ##### Compare Metadata with Master-MetaData #####
    for ChannelName in MetaData:
      if ChannelName not in SkipList:
          if (not str(masterMetaData[ChannelName][0]) == str(MetaData[ChannelName][0])):
            try:
              if (not float(masterMetaData[ChannelName][0]) == float(MetaData[ChannelName][0])):
                raise Exception("%s in file %s is not the same as in file %s" % (ChannelName, FileName, masterFileName))
            except:
              raise Exception("%s in file %s is not the same as in file %s" % (ChannelName, FileName, masterFileName))


    ChannelName, SkipList = None, None


  def _create_mapDict(self, ChannelData):

    mapDict = {}
      
    for channel in ChannelData.items():
      if channel[1]['files'].__contains__(self.fileType):
        if channel[1]['header_data'] == False:
          if (channel[1]['multiple_benches'] == True):
            self._create_mapDict_util(channel[0], channel[1]['channel_names'], True, channel[1]['optional'], self.data, self.fileName, mapDict)
          else:
            self._create_mapDict_util(channel[0], channel[1]['channel_names'], False, channel[1]['optional'], self.data, self.fileName, mapDict)
        else:
          self._create_mapDict_util(channel[0], channel[1]['channel_names'], False, channel[1]['optional'], self.metaData, self.fileName, mapDict)            
          

    # Clear Variables
    channel = None

    return mapDict


  def _create_mapDict_util(self, channel, channelNames, multipleBenches, optional, data, fileName, mapDict):   

    ##### For Loop through all entries of of mapDict        
    for name in channelNames:
      if name in data.columns:
        mapDict[channel] = name
        return mapDict
    else:
      if optional == False:
        raise Exception("Cannot find %s channel %s in file %s" % (channel.replace("_"," "), channelNames, fileName))   

    # Clear Variables
    name = None                      
               

  def _check_units(self, ChannelData):

    for channel in self.mapDict:
      unit = ChannelData[channel]['unit']
      if ChannelData[channel]['header_data'] == False:
        booleanCond = self.units[self.mapDict[channel]].str.contains(unit)

        if not (booleanCond.any()):
          self.logDict['error'] = "%s units are not in %s" % (self.mapDict[channel], unit)          
          raise Exception("%s units are not in %s" % (self.mapDict[channel], unit))


  def check_ranges(self, ChannelData):

    for channel in self.mapDict:       
      if channel != 'Carbon_Monoxide_Dry':

        ##### Read Max/Min-Vaues from json-file #####
        maxValue = ChannelData[channel]['maximum_value']
        minValue = ChannelData[channel]['minimum_value']

        ##### Load Values from Data #####
        if ChannelData[channel]['header_data'] == False:
          maxCompare = np.nanmax(self.data[self.mapDict[channel]])[0]
          minCompare = np.nanmin(self.data[self.mapDict[channel]])[0]

        ##### Load Values from Metadata #####
        else:
          maxCompare = float(self.metaData[self.mapDict[channel]][0])
          minCompare = float(self.metaData[self.mapDict[channel]][0])

        ##### Check whether maximum out of Range #####
        if (maxCompare > float(maxValue)) == True:
          self._output_oor(channel, maxValue, 'above required maximum', ChannelData)       

        ##### Check whether minimum out of Range #####
        if (minCompare < float(minValue)) == True:
          self._output_oor(channel, minValue, 'below required minimum', ChannelData)

    # Clear Variables
    channel, maxValue, minValue, maxCompare, minCompare = None, None, None, None, None

  # oor = Out of Range
  def _output_oor(self, channel, Value, ErrorString, ChannelData):   

    self.logDict['error'] = "%s is %s of %s %s" % (self.mapDict[channel], ErrorString, str(Value), ChannelData[channel]['unit'])
    raise Exception ("%s is %s of %s %s" % (self.mapDict[channel], ErrorString, str(Value), ChannelData[channel]['unit']))



class FullLoad(Data):

  def __init__(self, dataFile):
    super().__init__(dataFile)


class ZeroSpan(Data):

  def __init__(self, dataFile):
    super().__init__(dataFile)


  def _create_mapDict(self, ChannelData):

    self.Channel = self._bench_channel(ChannelData)
    return super()._create_mapDict(ChannelData)


  def _create_mapDict_util(self, channel, channelNames, multipleBenches, optional, data, fileName, mapDict):

    ##### Write used Ebench-Channel #####
    for name in channelNames:
      if name in data.columns:
        if multipleBenches == True:
          mapDict[channel] =  name + self.Channel
        else:
          mapDict[channel] =  name
        return mapDict
    else:
      if optional == False:
        raise Exception("Cannot find %s channel %s in file %s" % (channel.replace("_"," "), channelNames, fileName))   

    # Clear Variables
    name = None


  def _bench_channel(self, ChannelData):

    BenchList = {}

    ##### Scrape Species-List to identify Ebench-Channel #####
    for channel in ChannelData.items():
      if channel[1]['multiple_benches'] == True:
        BenchList[channel[0]] = channel[1]['channel_names'][0]       

    ##### Set Ebench-Channel by percentage Change of Data during ZeroSpan #####
    for channel in BenchList.values():
      MaxPctChange = np.nanmax(abs(self.data[channel]).pct_change())[0]
      if MaxPctChange < 0.9:
        return '2'
    else:
        return ''    


  def check_ranges(self, ChannelData):

    for channel in self.mapDict:       
      if channel != 'Carbon_Monoxide_Dry':

        ##### Read Max/Min-Vaues from json-file #####
        maxValue = ChannelData[channel]['maximum_value'] * 1.05 # Span can go 5% over the Bottle Concentration
        minValue = ChannelData[channel]['maximum_value'] * -0.05 # Span can go 5% over the Bottle Concentration

        ##### Load Values from Data #####
        maxCompare = np.nanmax(self.data[self.mapDict[channel]])[0]
        minCompare = np.nanmin(self.data[self.mapDict[channel]])[0]

        ##### Check whether maximum out of Range #####
        if (maxCompare > float(maxValue)) == True:
          self._output_oor(channel, maxValue, 'above required maximum', ChannelData)       

        ##### Check whether minimum out of Range #####
        if (minCompare < float(minValue)) == True:
          self._output_oor(channel, minValue, 'below required minimum', ChannelData)

    # Clear Variables
    channel, maxValue, minValue, maxCompare, minCompare = None, None, None, None, None        



class TestData(Data):

  def __init__(self, dataFile, CycleType):
    super().__init__(dataFile)
    self.CycleType = CycleType


  def _load_data_units(self, RawData):

    [data, units] = super()._load_data_units(RawData)

    if self.CycleType == 'Steady State':
      data = self._load_steady_state(data)

    return data, units


  def _load_steady_state(self, Data):

    Torque71_6 = max(Data['N_CERTTRQ']) # Torque channel will be changed
    DataSteady = Data[Data['N_CERTMODE'].isin(pd.Series(Data['N_CERTMODE'].astype(int)).unique())] # Choose Data where Channel N_CERTMODE is int
    DataSteady = DataSteady[DataSteady['N_CERTMODE']>0]

    ##### Write Torque in original TorqueChannel (same for Speed)
    DataSteady['UDPi_TorqueDemand'][DataSteady['N_CERTMODE'] == 1] = Torque71_6/0.716
    DataSteady.index = range(0,len(DataSteady))
    DataSteady.Date[0] = Data.Date[0]
    DataSteady.Time[0] = Data.Time[0]

    # Clear Variables
    Torque71_6r, Date, Time = None, None, None

    return DataSteady   



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






