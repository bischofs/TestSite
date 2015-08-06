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

      
  def _load_cycle_attr(self, cycle_attr, meta_data, cycles_data):


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
      self._check_time_stamp(self.pre_zero_span.time_stamp, self.test_data.time_stamp, self.post_zero_span.time_stamp, len(self.test_data.data))

      ##### Create MaterDict, Set Co-Channel, Load E-Bench-Data #####
      self.master_dict = self._create_master_dict(attrs)
      
      if len(self.ebenches.filter(EbenchID=self.cycle_attr['EbenchID'])) == 0:
        raise Exception("Cannot find associated Ebench in database, please contact Emissions group")
      else:
        self.ebenchData = self._load_ebench(self.ebenches.filter(EbenchID=self.cycle_attr['EbenchID'])[0].history, self.test_data.time_stamp)
      
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

    master_dict = self.test_data.map_dict
    master_dict.update(self.pre_zero_span.map_dict) # test_data.map_dict is changed as well

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


  def _load_ebench(self, Ebenches, time_stamp):

    ############### HARD CODED TIMESTAMP #######################
    time_stamp = time.time()
    ############################################################

    ebenchData = {}    
    for EbenchSet in Ebenches.values():
      if EbenchSet['history_date'].timestamp() < time_stamp :

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
      
    self.map_dict = {}
    self.logDict = {}

    self.data_file = data_file
    self.fileName = data_file.name
    self.file_type = self.__class__.__name__
    self.time_stamp = None


  def load_data(self, raw_data, master_meta_data, master_file_name, master_dict, channel_data):

    ##### Load Spec-File, Metadata, Data, Units #####
    self.data = raw_data
    [self.metaData, master_meta_data, master_file_name] = self._load_metadata(self.data, self.fileName, master_meta_data, master_file_name, channel_data)
    [self.data, self.units] = self._load_data_units(self.data)
    self.time_stamp = self._load_timestamp(self.data)
    self.map_dict = self._create_map_dict(channel_data)

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


  def _create_map_dict(self, channel_data):

    map_dict = {}
      
    for channel in channel_data.items():
      if channel[1]['files'].__contains__(self.file_type):
        if channel[1]['header_data'] == False:
          if (channel[1]['multiple_benches'] == True):
            self._create_map_dict_util(channel[0], channel[1]['channel_names'], True, channel[1]['optional'], self.data, self.fileName, map_dict)
          else:
            self._create_map_dict_util(channel[0], channel[1]['channel_names'], False, channel[1]['optional'], self.data, self.fileName, map_dict)
        else:
          self._create_map_dict_util(channel[0], channel[1]['channel_names'], False, channel[1]['optional'], self.metaData, self.fileName, map_dict)            
          

    # Clear Variables
    channel = None

    return map_dict


  def _create_map_dict_util(self, channel, channelNames, multipleBenches, optional, data, fileName, map_dict):   

    ##### For Loop through all entries of of map_dict        
    for name in channelNames:
      if name in data.columns:
        map_dict[channel] = name
        return map_dict
    else:
      if optional == False:
        raise Exception("Cannot find %s channel %s in file %s" % (channel.replace("_"," "), channelNames, fileName))   

    # Clear Variables
    name = None                      
               

  def _check_units(self, channel_data):

    for channel in self.map_dict:
      unit = channel_data[channel]['unit']
      if channel_data[channel]['header_data'] == False:
        booleanCond = self.units[self.map_dict[channel]].str.contains(unit)

        if not (booleanCond.any()):
          self.logDict['error'] = "%s units are not in %s" % (self.map_dict[channel], unit)          
          raise Exception("%s units are not in %s" % (self.map_dict[channel], unit))


  def check_ranges(self, channel_data, File):

    for channel in self.map_dict:       
      if channel != 'Carbon_Monoxide_Dry':

        ##### Read Max/Min-Vaues from json-file #####
        maxValue = channel_data[channel]['maximum_value']
        minValue = channel_data[channel]['minimum_value']

        ##### Load Values from Data #####
        if channel_data[channel]['header_data'] == False:
          maxCompare = np.nanmax(self.data[self.map_dict[channel]])[0]
          minCompare = np.nanmin(self.data[self.map_dict[channel]])[0]

        ##### Load Values from Metadata #####
        else:
          maxCompare = float(self.metaData[self.map_dict[channel]][0])
          minCompare = float(self.metaData[self.map_dict[channel]][0])

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

    self.logDict['error'] = "%s is %s of %s %s in %s" % (self.map_dict[channel], ErrorString, str(Value), channel_data[channel]['unit'], File)
    raise Exception ("%s is %s of %s %s in %s" % (self.map_dict[channel], ErrorString, str(Value), channel_data[channel]['unit'], File))



class FullLoad(Data):

  def __init__(self, data_file):
    super().__init__(data_file)


class ZeroSpan(Data):

  def __init__(self, data_file):
    super().__init__(data_file)


  def _create_map_dict(self, channel_data):

    self.Channel = self._bench_channel(channel_data)
    return super()._create_map_dict(channel_data)


  def _create_map_dict_util(self, channel, channelNames, multipleBenches, optional, data, fileName, map_dict):

    ##### Write used Ebench-Channel #####
    for name in channelNames:
      if name in data.columns:
        if multipleBenches == True:
          map_dict[channel] =  name + self.Channel
        else:
          map_dict[channel] =  name
        return map_dict
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

    for channel in self.map_dict:       
      if channel != 'Carbon_Monoxide_Dry':

        ##### Read Max/Min-Vaues from json-file #####
        maxValue = channel_data[channel]['maximum_value'] * 1.05 # Span can go 5% over the Bottle Concentration
        minValue = channel_data[channel]['maximum_value'] * -0.05 # Span can go 5% over the Bottle Concentration

        ##### Load Values from Data #####
        maxCompare = np.nanmax(self.data[self.map_dict[channel]])[0]
        minCompare = np.nanmin(self.data[self.map_dict[channel]])[0]

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
    
    def __init__(self, test_data, map_dict, full_load, warm_idle, filter_choice):

      ##### Load Data #####
      self._filter_choice = filter_choice
      self._data = test_data.data
      self._data_full = Fullload.data
      self._data_full.index = range(0,len(self.data_full))
      self._data.index = range(0,len(self.data))
      self._map_dict = map_dict

      ##### Define Variables #####     
      self._throttle = self.data[self.map_dict['Commanded__throttle']]
      self._torque_demand = self.data[self.map_dict['Commanded_Torque']]
      self._torque_engine = self.data[self.map_dict['Engine_Torque']] 
      self._speed_demand = self.data[self.map_dict['Commanded_Speed']]
      self._speed_engine = self.data[self.map_dict['Engine_Speed']]
      self._power_demand = (self.data[self.map_dict['Commanded_Torque']] * self.data[self.map_dict['Commanded_Speed']] / 9.5488) / 1000
      self._power_engine = self.data[self.map_dict['Engine_Power']]
      self.data = None

      ##### Maximum of Speed, Torque, Power and warm idle #####
      self._speed_max = np.nanmax(self.data_full[self.map_dict['Engine_Speed']])[0]
      self._torque_max = np.nanmax(self.data_full[self.map_dict['Engine_Torque']])[0]
      self._power_max = np.nanmax(self.data_full[self.map_dict['Engine_Power']])[0]
      self._warm_idle = Warmidle[0]
      self.data_full = None
        
      ##### Index of Maximum and Minimum _throttle #####
      self.Index_Min = np.where([self._throttle==np.nanmin(self._throttle)[0]])[1]
      self.Index_Max = np.where([self._throttle==np.nanmax(self._throttle)[0]])[1]


      ##### Drop Lists #####
      self._torque_drop = []
      self._speed_drop = []
      self._power_drop = []

      self._data_dict = {'Torque': ['_torque_demand', '_torque_engine'],
                         'Power': ['_power_demand', '_power_engine'], 
                         'Speed': ['_speed_demand', '_speed_engine']}

      if (self.filter_choice != 0):
        self._pre_regression_filter(self.filter_choice)        
      self._regression()
      self._regression_validation()
        
    def _pre_regression_filter(self, filter_choice):

      for i in self.Index_Min:
            
        ##### Check Minimum _throttle ##### -- Table 1 EPA 1065.514
        if (self._torque_demand[i])<0 and \
           (filter_choice == 1):
              
          self._torque_drop.append(i)
          self._power_drop.append(i)                  
                
        if (self._torque_demand[i]==0) and \
           (self._speed_demand[i]==0) and \
           ((self._torque_engine[i]-0.02*self._torque_max)<self._torque_engine[i]) and \
           (self._torque_engine[i]<(self._torque_engine[i]+0.02*self._torque_max)) and \
           (filter_choice == 2):
               
          self._speed_drop.append(i)
          self._power_drop.append(i)
                
        if (self._torque_engine[i]>self._torque_demand[i]) and \
           ((self._torque_engine[i]<(self._torque_engine[i]+0.02*self._torque_max)) | (self._torque_engine[i]<(self._torque_engine[i]-0.02*self._torque_max))) and \
           (filter_choice == 3):
              
          self._torque_drop.append(i)
          self._power_drop.append(i)
                
        if (self._speed_engine[i]>self._speed_demand[i]) and \
           (self._speed_engine[i]<self._speed_demand[i]*1.02) and \
           (filter_choice == 4):
          self._speed_drop.append(i)
          self._power_drop.append(i)
            
      for j in self.Index_Max:
        ##### Check Maximum _throttle ##### -- Table 1 EPA 1065.514                
        if (self._torque_engine[j]<self._torque_demand[j]) and \
           (self._torque_engine[j]>(self._torque_engine[j]-0.02*self._torque_max)) and \
           (filter_choice == 5):
          
          self._torque_drop.append(j)
          self._power_drop.append(j)

        if (self._speed_engine[j]<self._speed_demand[j]) and \
           (self._speed_engine[j]>self._speed_demand[j]*0.98) and \
           (filter_choice == 6):
          
          self._speed_drop.append(j)
          self._power_drop.append(j)                    

        ##### Omitting the Data #####
        self._speed_engine = self._speed_engine.drop(self._speed_drop)
        self._speed_demand = self._speed_demand.drop(self._speed_drop)
        self._torque_engine = self._torque_engine.drop(self._torque_drop)
        self._torque_demand = self._torque_demand.drop(self._torque_drop)
        self._power_engine = self._power_engine.drop(self._power_drop)
        self._power_demand = self._power_demand.drop(self._power_drop)            

        ##### Reindexing the data #####
        self._torque_engine.index = range(0,len(self._torque_engine))
        self._torque_demand.index = range(0,len(self._torque_demand))
        self._speed_engine.index = range(0,len(self._speed_engine))
        self._speed_demand.index = range(0,len(self._speed_demand))
        self._power_engine.index = range(0,len(self._power_engine))
        self._power_demand.index = range(0,len(self._power_demand))

        ##### Cleaning Variables #####
        self._throttle, self.Index_Min = None, None
        self._torque_drop, self._speed_drop, self._power_drop = None, None, None
       

    def _regression(self):
        
        self.reg_results = {'Torque': { 'Slope': " ", 'Intercept': " ", 'Standard Error': " ", 'Rsquared': " " },
                            'Power': { 'Slope': " ", 'Intercept': " ", 'Standard Error': " ", 'Rsquared': " " }, 
                            'Speed': { 'Slope': " ", 'Intercept': " ", 'Standard Error': " ", 'Rsquared': " " }}
        
        for channel in self._data_dict.items():
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
                
        if np.isnan(numerator / denominator) == True:
          slope = 1
        else:
          slope = _numerator / denominator 

        # -- Regression Intercept -- EPA 1065.602-10 
        intercept = (_xmean - (_slope * _ymean))

        # -- Regression Standard Error of Estimate -- EPA 1065.602-11 
        sumat = 0.0
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            sumat = sumat + ((x - intercept - (slope * y)) ** 2)
        see = _sumat / (vars(self)[X].size - 2)
        standerror = math.sqrt(see)

        # -- Regression Coefficient of determination -- EPA 1065.602-12
        numerator, denominator = 0.0, 0.0
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            numerator = numerator + ((x - intercept - (slope * y)) ** 2)
        for x, y in zip(vars(self)[X], vars(self)[Y]):
            denominator = denominator + ((x - ymean) ** 2)
                
        r2 = 1 - (numerator / denominator)

        self.reg_results[channel]['Slope'] = round(slope, 2)
        self.reg_results[channel]['Intercept'] = round(intercept, 2)
        self.reg_results[channel]['Standard Error'] = round(standerror, 2)
        self.reg_results[channel]['Rsquared'] = round(r2, 2)


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
                if (self.reg_results[parameter]['Intercept'] <= 0.1*float(self._warm_idle)):
                    self.reg_results_bool[parameter]['Intercept'] = True

                # Standard error
                if self.reg_results[parameter]['Standard Error'] <= 0.05*self._speed_max:
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
                if (self.reg_results[parameter]['Intercept'] <= 0.02*self._torque_max):
                    self.reg_results_bool[parameter]['Intercept'] = True

                # Standard error
                if self.reg_results[parameter]['Standard Error'] <= 0.1*self._torque_max:
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
                if (self.reg_results[parameter]['Intercept'] <= 0.02*self._power_max):
                    self.reg_results_bool[parameter]['Intercept'] = True

                # Standard error
                if self.reg_results[parameter]['Standard Error'] <= 0.1*self._power_max:
                    self.reg_results_bool[parameter]['Standard Error'] = True

                # Coefficient of determination
                if self.reg_results[parameter]['Rsquared'] >= 0.91:
                    self.reg_results_bool[parameter]['Rsquared'] = True






