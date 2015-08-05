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

    self.results_log = {'Regression': {},'Regression_bool': {},
                        'Data Alignment': {'Array':{'NOx':0,'CH4':0,'THC':0,'CO':0,'CO2':0,'NO':0,'MFRAIR':0,'N2O':0,'CH2O':0,'NH3':0},
                        'Data':pd.DataFrame()}, 'Calculation': {}, 'Report':{}}
    self.file_dict = {'FULL': 'full_load', 'PRE':'pre_zero_span','MAIN':'test_data','POST':'post_zero_span'}
    self.cycles_data = pd.read_json("cycles.json").Cycles
    self.channel_data = pd.read_json("spec.json").Species
    self.ebenches = Ebench.objects.all()
    self.master_meta_data = pd.DataFrame()
    self.master_file_name = None
    self.File = None
    self.all_files_loaded = False
    self.do_calculation = True
    self.master_dict = {}
    self.cycle_attr = {}
    self.log = {}

  def import_data(self, data_file):   

    ##### Prepare DataHandler and File #####
    self._clear_all_files_loaded()
   
    try:
      raw_data = pd.read_csv(data_file, names=range(1,500), encoding='windows-1258')
      raw_data.columns = raw_data.loc[0].values
      raw_data = raw_data[1:]
      raw_data = raw_data.dropna(how="all", axis=(1))
      raw_data.index = range(0,len(raw_data))
    except:
      raise Exception("Problem parsing data in file %s" (data_file.file))

    if('CycleState1065'in raw_data.columns.values):
      self.File = raw_data[:1]['CycleState1065'][0] # Reads the filetype out of header page
    else:
      raise Exception("MetaData missing CycleState1065, cannot detect cycle state in %s" (data_file.file))


    ##### Create FileClass #####
    if self.File == 'FULL':
      file_type = FullLoad(data_file)

    elif self.File == 'PRE':
      file_type = ZeroSpan(data_file)

    elif self.File == 'MAIN':
      self.cycle_attr = self._load_cycle_attr(self.cycle_attr, raw_data[:1], self.cycles_data)
      file_type = TestData(data_file, self.cycle_attr['CycleType'])

    elif self.File == 'POST':
      file_type = ZeroSpan(data_file)

    ##### Load File #####
    [masterMetaData, masterFileName] = file_type.load_data(raw_data, self.master_meta_data, self.master_file_name, self.master_dict, self.channel_data)
    setattr(self,self.file_dict[self.File], file_type)

    ##### Set MasterFile #####
    if (self.master_file_name == None):
      self.master_file_name = master_file_name
      self.master_meta_data = master_meta_data 

    ##### Finish Upload #####
    self._check_all_files_loaded()


  def _clear_all_files_loaded(self):

  ##### Clears all Data and resets the Datahandler when 5th file is uploaded #####
    if(self.all_files_loaded == True):
      del self.test_data, self.pre_zero_span, self.post_zero_span, self.full_load
      self.__init__()

      
  def _load_cycle_attr(self, cycle_attr, meta_data, CyclesData):


    cycle = meta_data['CycleType1065'][0]
    cycle_attr['Cycle'] = cycle
    cycle_attr['EbenchID'] = meta_data['EbenchID'][0]
    cycle_attr['Name'] = cycles_data[Cycle]['Name']    
    cycle_attr['Engine'] = cycles_data[Cycle]['Engine']
    cycle_attr['CycleType'] = cycles_data[Cycle]['CycleType']
    if(cycle_attr['CycleType'] == 'Transient'):
      cycle_attr['CycleLength'] = cycles_data[Cycle]['CycleLength']
    cycle_attr['Fuel'] = cycles_data[Cycle]['Fuel']
    cycle_attr['FactorMult'] = cycles_data[Cycle]['NOxFactorMult']
    cycle_attr['FactorAdd'] = cycles_data[Cycle]['NOxFactorAdd']
      

    return cycle_attr


  def _check_all_files_loaded(self):

    ##### Checks whether all files are uploaded #####
    attrs = ['full_load', 'post_zero_span', 'pre_zero_span', 'test_data']        

    for attr in attrs:

      if not hasattr(self, attr):
        self.all_files_loaded = False
        break

    else:
      self.all_files_loaded = True
      ##### Check Timestamps of Files
      self._check_time_stamp(self.pre_zero_span.TimeStamp, self.test_data.TimeStamp, self.post_zero_span.TimeStamp, len(self.test_data.data))

      ##### Create MaterDict, Set Co-Channel, Load E-Bench-Data #####
      self.master_dict = self._create_master_dict(attrs)
      
      if len(self.ebenches.filter(EbenchID=self.cycle_attr['EbenchID'])) == 0:
        raise Exception("Cannot find associated Ebench in database, please contact Emissions group")
      else:
        self.ebenchData = self._load_ebench(self.ebenches.filter(EbenchID=self.cycle_attr['EbenchID'])[0].history, self.test_data.TimeStamp)
      
      ##### Check Channel-Ranges of all files #####
      self.channel_data = self._set_channel_data()
      for File in attrs:
        vars(self)[File].check_ranges(self.channel_data, File)      


  def _set_channel_data(self):
    
    ##### Lists of ChannelNames and BottleNames #####
    ListSpecies = ['Carbon_Dioxide_Dry', 'Carbon_Monoxide_High_Dry', 'Nitrogen_X_Dry', 'Total_Hydrocarbons_Wet', 'Methane_Wet']
    ListBottles = ['Bottle_Concentration_CO2', 'Bottle_Concentration_CO', 'Bottle_Concentration_NOX', 'Bottle_Concentration_THC', 'Bottle_Concentration_NMHC']      

    ##### Change maximum Range-Values of Species to 110% of Bottle-Concentration #####
    for spec, bottle in zip(ListSpecies, ListBottles):
      self.channel_data[spec]['maximum_value'] = self.ebenchData[bottle]

    return self.channel_data

  def _create_master_dict(self, attrs):

    master_dict = self.test_data.mapDict
    master_dict.update(self.pre_zero_span.mapDict) # test_data.mapDict is changed as well

    master_dict = self._set_CO(self.test_data.data, master_dict)


    return master_dict


  def _set_CO(self, data, master_dict):

    ##### CO-Strings for master_dict #####
    COL = 'Carbon_Monoxide_Low_Dry'
    COH = 'Carbon_Monoxide_High_Dry'
    CO = 'Carbon_Monoxide_Dry'

    ##### Load Min- Compare/Value for COL #####
    minValue = self.channel_data[COL]['minimum_value']
    minCompare = np.nanmin(data[master_dict[COL]])[0]

    ##### Check whether minimum out of Range #####
    if (minCompare < float(minValue)) == True:
      master_dict[CO] = master_dict[COH]
    else:
      master_dict[CO] = master_dict[COL]
  
    del master_dict[COL]
    del master_dict[COH]

    # Clear Variables
    COl, COH, CO, minValue, minCompare = None, None, None, None, None

    return master_dict


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
        if 'COH' in self.master_dict['Carbon_Monoxide_Dry']:
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

  def __init__(self, data_file):
      
    self.mapDict = {}
    self.logDict = {}

    self.data_file = data_file
    self.fileName = data_file.name
    self.file_type = self.__class__.__name__
    self.TimeStamp = None


  def load_data(self, raw_data, master_meta_data, master_file_name, master_dict, channel_data):

    ##### Load Spec-File, Metadata, Data, Units #####
    self.data = raw_data
    [self.metaData, master_meta_data, master_file_name] = self._load_metadata(self.data, self.fileName, master_meta_data, master_file_name, channel_data)
    [self.data, self.units] = self._load_data_units(self.data)
    self.TimeStamp = self._load_timestamp(self.data)
    self.mapDict = self._create_mapDict(channel_data)

    ##### Perform Checks on Data #####
    self._check_metadata(self.metaData, self.fileName, master_meta_data, master_file_name) 
    self._check_units(channel_data)

    return master_meta_data, master_file_name


  def _load_metadata(self, data, FileName, master_meta_data, master_file_name, channel_data):

    metaData = data[:1].dropna(how="all",axis=(1)) # Drop Zero-Columns

    ##### Loop through all entries of channel_data in the header page #####
    for channel in channel_data.items():
      if channel[1]['header_data'] == True:
        for channelName in channel[1]['channel_names']:
          if channelName in metaData.columns:
            self.logDict['info'] = "Meta-Data read from import file %s" % self.fileName
                     
          else:
            self.logDict['warning'] = "Meta-Data missing in import file %s" % self.fileName
            raise Exception("Cannot find %s channel in header data of file %s" % (channelName, self.fileName))

    if master_file_name == None:

      master_meta_data = metaData
      master_file_name = FileName                

    return metaData, master_meta_data, master_file_name  


  def _load_data_units(self, raw_data):

      self.data.columns = raw_data.loc[1].values
      self.data = raw_data[2:]
      units = raw_data[2:3]
      self.data = self.data.dropna(how="all",axis=(1)) # Drop Zero-Columns
      self.data = (self.data.convert_objects(convert_numeric=True)).dropna() # Convert and drop NA
      self.data.index = range(0,len(self.data))

      return self.data, units


  def _load_timestamp(self, Data):
    try:
      return time.mktime(datetime.datetime.strptime(Data['Date'][0] + ' ' + Data['Time'][0], "%m/%d/%Y %H:%M:%S.%f").timetuple())
    except :
      raise Exception('The file is not raw data. Please upload raw data from LabCentral.')
    


  def _check_metadata(self, meta_data, FileName, master_meta_data, master_file_name):

    SkipList = ['N_TR','no_run','Comment1','Comment2','Proj#', 'N_TQ', 'CycleCondition1065','CycleState1065', 'N_FLAG2'] # Remove CycleCondition later e.g COS = Coldstart

    ##### Compare Metadata with Master-meta_data #####
    for ChannelName in meta_data:
      if ChannelName not in SkipList:
          if (not str(master_meta_data[ChannelName][0]) == str(meta_data[ChannelName][0])):
            try:
              if (not float(master_meta_data[ChannelName][0]) == float(meta_data[ChannelName][0])):
                raise Exception("%s in file %s is not the same as in file %s" % (ChannelName, FileName, master_file_name))
            except:
              raise Exception("%s in file %s is not the same as in file %s" % (ChannelName, FileName, master_file_name))


    ChannelName, SkipList = None, None


  def _create_mapDict(self, channel_data):

    mapDict = {}
      
    for channel in channel_data.items():
      if channel[1]['files'].__contains__(self.file_type):
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
               

  def _check_units(self, channel_data):

    for channel in self.mapDict:
      unit = channel_data[channel]['unit']
      if channel_data[channel]['header_data'] == False:
        booleanCond = self.units[self.mapDict[channel]].str.contains(unit)

        if not (booleanCond.any()):
          self.logDict['error'] = "%s units are not in %s" % (self.mapDict[channel], unit)          
          raise Exception("%s units are not in %s" % (self.mapDict[channel], unit))


  def check_ranges(self, channel_data, File):

    for channel in self.mapDict:       
      if channel != 'Carbon_Monoxide_Dry':

        ##### Read Max/Min-Vaues from json-file #####
        maxValue = channel_data[channel]['maximum_value']
        minValue = channel_data[channel]['minimum_value']

        ##### Load Values from Data #####
        if channel_data[channel]['header_data'] == False:
          maxCompare = np.nanmax(self.data[self.mapDict[channel]])[0]
          minCompare = np.nanmin(self.data[self.mapDict[channel]])[0]

        ##### Load Values from Metadata #####
        else:
          maxCompare = float(self.metaData[self.mapDict[channel]][0])
          minCompare = float(self.metaData[self.mapDict[channel]][0])

        ##### Check whether maximum out of Range #####
        if (maxCompare > float(maxValue)) == True:
          self._output_oor(channel, maxValue, 'above required maximum', channel_data, File)       

        ##### Check whether minimum out of Range #####
        if (minCompare < float(minValue)) == True:
          self._output_oor(channel, minValue, 'below required minimum', channel_data, File)

    # Clear Variables
    channel, maxValue, minValue, maxCompare, minCompare = None, None, None, None, None

  # oor = Out of Range
  def _output_oor(self, channel, Value, ErrorString, channel_data, File):   

    self.logDict['error'] = "%s is %s of %s %s in %s" % (self.mapDict[channel], ErrorString, str(Value), channel_data[channel]['unit'], File)
    raise Exception ("%s is %s of %s %s in %s" % (self.mapDict[channel], ErrorString, str(Value), channel_data[channel]['unit'], File))



class FullLoad(Data):

  def __init__(self, data_file):
    super().__init__(data_file)


class ZeroSpan(Data):

  def __init__(self, data_file):
    super().__init__(data_file)


  def _create_mapDict(self, channel_data):

    self.Channel = self._bench_channel(channel_data)
    return super()._create_mapDict(channel_data)


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


  def _bench_channel(self, channel_data):

    BenchList = {}

    ##### Scrape Species-List to identify Ebench-Channel #####
    for channel in channel_data.items():
      if channel[1]['multiple_benches'] == True:
        BenchList[channel[0]] = channel[1]['channel_names'][0]       

    ##### Set Ebench-Channel by percentage Change of Data during ZeroSpan #####
    for channel in BenchList.values():
      MaxPctChange = np.nanmax(abs(self.data[channel]).pct_change())[0]
      if MaxPctChange < 0.9:
        return '2'
    else:
        return ''    


  def check_ranges(self, channel_data, File):

    for channel in self.mapDict:       
      if channel != 'Carbon_Monoxide_Dry':

        ##### Read Max/Min-Vaues from json-file #####
        maxValue = channel_data[channel]['maximum_value'] * 1.05 # Span can go 5% over the Bottle Concentration
        minValue = channel_data[channel]['maximum_value'] * -0.05 # Span can go 5% over the Bottle Concentration

        ##### Load Values from Data #####
        maxCompare = np.nanmax(self.data[self.mapDict[channel]])[0]
        minCompare = np.nanmin(self.data[self.mapDict[channel]])[0]

        ##### Check whether maximum out of Range #####
        if (maxCompare > float(maxValue)) == True:
          self._output_oor(channel, maxValue, 'above required maximum', channel_data, File)       

        ##### Check whether minimum out of Range #####
        if (minCompare < float(minValue)) == True:
          self._output_oor(channel, minValue, 'below required minimum', channel_data, File)

    # Clear Variables
    channel, maxValue, minValue, maxCompare, minCompare = None, None, None, None, None        



class TestData(Data):

  def __init__(self, data_file, CycleType):
    super().__init__(data_file)
    self.CycleType = CycleType


  def _load_data_units(self, raw_data):

    [data, units] = super()._load_data_units(raw_data)

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
          slope = 1
        else:
          slope = numerator / denominator 

        # -- Regression Intercept -- EPA 1065.602-10 
        Intercept = (xmean - (slope * ymean))

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






