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
    self.all_files_loaded = False
    self.file_type_string = None
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
      self.file_type_string = raw_data[:1]['CycleState1065'][0] # Reads the filetype out of header page
    else:
      raise Exception("MetaData missing CycleState1065, cannot detect cycle state in %s" (data_file.file))

    ##### Create FileClass #####
    if self.file_type_string == 'FULL':
      file_type = FullLoad(data_file)

    elif self.file_type_string == 'PRE':
      file_type = ZeroSpan(data_file)

    elif self.file_type_string == 'MAIN':
      self.cycle_attr = self._load_cycle_attr(self.cycle_attr, raw_data[:1], self.cycles_data)
      file_type = TestData(data_file, self.cycle_attr['CycleType'])

    elif self.file_type_string == 'POST':
      file_type = ZeroSpan(data_file)

    ##### Load File #####
    [master_meta_data, master_file_name] = file_type.load_data(raw_data, self.master_meta_data, self.master_file_name, self.master_dict, self.channel_data)
    setattr(self,self.file_dict[file_type_string], file_type)

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
      
      if len(self.ebenches.filter(ebench_id=self.cycle_attr['EbenchID'])) == 0:
        raise Exception("Cannot find associated Ebench in database, please contact Emissions group")
      else:
        self.ebench_data = self._load_ebench(self.ebenches.filter(ebench_id=self.cycle_attr['EbenchID'])[0].history, self.test_data.time_stamp)
      
      ##### Check Channel-Ranges of all files #####
      self.channel_data = self._set_channel_data()
      for file in attrs:
        vars(self)[File].check_ranges(self.channel_data, file)###SOMETHING STRANGE HERE 


  def _set_channel_data(self):
    
    ##### Lists of ChannelNames and BottleNames #####
    species = ['Carbon_Dioxide_Dry', 'Carbon_Monoxide_High_Dry', 'Nitrogen_X_Dry', 'Total_Hydrocarbons_Wet', 'Methane_Wet']
    bottles = ['Bottle_Concentration_CO2', 'Bottle_Concentration_CO', 'Bottle_Concentration_NOX', 'Bottle_Concentration_THC', 'Bottle_Concentration_NMHC']      

    ##### Change maximum Range-Values of Species to 110% of Bottle-Concentration #####
    for spec, bottle in zip(species, bottles):
      self.channel_data[spec]['maximum_value'] = self.ebench_data[bottle]

    return self.channel_data


  def _create_master_dict(self, attrs):

    master_dict = self.test_data.map_dict
    master_dict.update(self.pre_zero_span.map_dict) # test_data.map_dict is changed as well
    master_dict = self._set_CO(self.test_data.data, master_dict)

    return master_dict


  def _set_CO(self, data, master_dict):

    ##### CO-Strings for master_dict #####
    col = 'Carbon_Monoxide_Low_Dry'
    coh = 'Carbon_Monoxide_High_Dry'
    co = 'Carbon_Monoxide_Dry'

    ##### Load Min- Compare/Value for COL #####
    min_value = self.channel_data[col]['minimum_value']
    min_compare = np.nanmin(data[master_dict[col]])[0]

    ##### Check whether minimum out of Range #####
    if (min_compare < float(min_value)) == True:
      master_dict[co] = master_dict[coh]
    else:
      master_dict[co] = master_dict[col]
  
    del master_dict[col]
    del master_dict[coh]

    # Clear Variables
    col, coh, co, min_value, min_compare = None, None, None, None, None

    return master_dict


  def _load_ebench(self, ebenches, time_stamp):

    ############### HARD CODED TIMESTAMP #######################
    time_stamp = time.time()
    ############################################################

    ebench_data = {}    
    for ebench_set in ebenches.values():
      if ebench_set['history_date'].timestamp() < time_stamp :

        ebench_data['RFPF'] = ebench_set['CH4_Penetration_Factor']
        ebench_data['CH4_RF'] = ebench_set['CH4_Response_Factor']
        ebench_data['Tchiller'] = ebench_set['Thermal_Chiller_Dewpoint']
        ebench_data['Pchiller'] = ebench_set['Thermal_Absolute_Pressure']
        ebench_data['xTHC[THC_FID]init'] = ebench_set['THC_Initial_Contamination']
        ebench_data['Bottle_Concentration_CO2'] = ebench_set['Bottle_Concentration_CO2']/10000 # ppm --> %
        if 'COH' in self.master_dict['Carbon_Monoxide_Dry']:##ASK ANTON WHAT IS GOING ON HERE!!!!!
          ebench_data['Bottle_Concentration_CO'] = ebench_set['Bottle_Concentration_COH']/10000 # ppm --> %
        else:
          ebench_data['Bottle_Concentration_CO'] = ebench_set['Bottle_Concentration_COL']
        ebench_data['Bottle_Concentration_NOX'] = ebench_set['Bottle_Concentration_NOX']
        ebench_data['Bottle_Concentration_THC'] = ebench_set['Bottle_Concentration_THC']
        ebench_data['Bottle_Concentration_NMHC'] =  ebench_set['Bottle_Concentration_NMHC']
        break
    self.ebenches = None

    return ebench_data   


  def _check_time_stamp(self, pre_ts, test_ts, post_ts, test_length):

    init_string = 'Timestamp-Check Failed ! : '
    if (test_ts - pre_ts) < 0:
      init_string = init_string + 'Timestamp of Pre-ZeroSpan is after the Test. '    
    if (post_ts - test_ts) < 0:
      init_string = init_string + 'Timestamp of Post-ZeroSpan is before the Test. '
    if (post_ts - test_ts) > 2 * test_length: 
      init_string = init_string + 'Timestamp of Post-ZeroSpan is too late. '
    if (test_ts - pre_ts) > test_length:
      init_string = init_string + 'Timestamp of Pre-ZeroSpan is too early. '

    if init_string != 'Timestamp-Check Failed ! : ':
      raise Exception (init_string)


class Data:


  def __init__(self, data_file):
      
    self.map_dict = {}
    self.logDict = {}

    self.data_file = data_file
    self.file_name = data_file.name
    self.file_type = self.__class__.__name__
    self.time_stamp = None


  def load_data(self, raw_data, master_meta_data, master_file_name, master_dict, channel_data):

    ##### Load Spec-File, Metadata, Data, Units #####
    self.data = raw_data
    [self.meta_data, master_meta_data, master_file_name] = self._load_metadata(self.data, self.file_name, master_meta_data, master_file_name, channel_data)
    [self.data, self.units] = self._load_data_units(self.data)
    self.time_stamp = self._load_timestamp(self.data)
    self.map_dict = self._create_map_dict(channel_data)

    ##### Perform Checks on Data #####
    self._check_metadata(self.meta_data, self.file_name, master_meta_data, master_file_name) 
    self._check_units(channel_data)

    return master_meta_data, master_file_name


  def _load_metadata(self, data, file_name, master_meta_data, master_file_name, channel_data):

    meta_data = data[:1].dropna(how="all",axis=(1)) # Drop Zero-Columns

    ##### Loop through all entries of channel_data in the header page #####
    for channel in channel_data.items():
      if channel[1]['header_data'] == True:
        for channel_name in channel[1]['channel_names']:
          if channel_name in meta_data.columns:
            self.logDict['info'] = "Meta-Data read from import file %s" % self.file_name
          else:
            self.logDict['warning'] = "Meta-Data missing in import file %s" % self.file_name
            raise Exception("Cannot find %s channel in header data of file %s" % (channel_name, self.file_name))

    if master_file_name == None:

      master_meta_data = meta_data
      master_file_name = file_name                

    return meta_data, master_meta_data, master_file_name  


  def _load_data_units(self, raw_data):

      self.data.columns = raw_data.loc[1].values
      self.data = raw_data[2:]
      units = raw_data[2:3]
      self.data = self.data.dropna(how="all",axis=(1)) # Drop Zero-Columns
      self.data = (self.data.convert_objects(convert_numeric=True)).dropna() # Convert and drop NA
      self.data.index = range(0,len(self.data))

      return self.data, units


  def _load_timestamp(self, data):

    try:
      return time.mktime(datetime.datetime.strptime(data['Date'][0] + ' ' + data['Time'][0], "%m/%d/%Y %H:%M:%S.%f").timetuple())
    except :
      raise Exception('The file is not raw data. Please upload raw data from LabCentral.')
    

  def _check_metadata(self, meta_data, FileName, master_meta_data, master_file_name):

    skip = ['N_TR','no_run','Comment1','Comment2','Proj#', 'N_TQ', 'CycleCondition1065','CycleState1065', 'N_FLAG2'] # Remove CycleCondition later e.g COS = Coldstart

    ##### Compare Metadata with Master-meta_data #####
    for channel_name in meta_data:
      if channel_name not in skip:
          if (not str(master_meta_data[channel_name][0]) == str(meta_data[channel_name][0])):
            try:
              if (not float(master_meta_data[channel_name][0]) == float(meta_data[channel_name][0])):
                raise Exception("%s in file %s is not the same as in file %s" % (channel_name, file_name, master_file_name))
            except:
              raise Exception("%s in file %s is not the same as in file %s" % (channel_name, file_name, master_file_name))


    channel_name, skip = None, None


  def _create_map_dict(self, channel_data):

    map_dict = {}
      
    for channel in channel_data.items():
      if channel[1]['files'].__contains__(self.file_type):
        if channel[1]['header_data'] == False:
          if (channel[1]['multiple_benches'] == True):
            self._create_map_dict_util(channel[0], channel[1]['channel_names'], True, channel[1]['optional'], self.data, self.file_name, map_dict)
          else:
            self._create_map_dict_util(channel[0], channel[1]['channel_names'], False, channel[1]['optional'], self.data, self.file_name, map_dict)
        else:
          self._create_map_dict_util(channel[0], channel[1]['channel_names'], False, channel[1]['optional'], self.metaData, self.file_name, map_dict)            
          

    # Clear Variables
    channel = None

    return map_dict


  def _create_map_dict_util(self, channel, channel_names, optional, data, file_name, map_dict):   

    ##### For Loop through all entries of of map_dict        
    for name in channel_names:
      if name in data.columns:
        map_dict[channel] = name
        return map_dict
    else:
      if optional == False:
        raise Exception("Cannot find %s channel %s in file %s" % (channel.replace("_"," "), channel_names, file_name))   
    # Clear Variables
    name = None                      
               

  def _check_units(self, channel_data):

    for channel in self.map_dict:
      unit = channel_data[channel]['unit']
      if channel_data[channel]['header_data'] == False:
        boolean_cond = self.units[self.map_dict[channel]].str.contains(unit)

        if not (boolean_cond.any()):
          self.logDict['error'] = "%s units are not in %s" % (self.map_dict[channel], unit)          
          raise Exception("%s units are not in %s" % (self.map_dict[channel], unit))


  def check_ranges(self, channel_data, file_name):

    for channel in self.map_dict:       
      if channel != 'Carbon_Monoxide_Dry':

        ##### Read Max/Min-Vaues from json-file #####
        max_value = channel_data[channel]['maximum_value']
        min_value = channel_data[channel]['minimum_value']

        ##### Load Values from Data #####
        if channel_data[channel]['header_data'] == False:
          max_compare = np.nanmax(self.data[self.map_dict[channel]])[0]
          min_compare = np.nanmin(self.data[self.map_dict[channel]])[0]

        ##### Load Values from Metadata #####
        else:
          max_compare = float(self.meta_data[self.map_dict[channel]][0])
          min_compare = float(self.meta_data[self.map_dict[channel]][0])

        ##### Check whether maximum out of Range #####
        if (max_compare > float(max_value)) == True:
          self._output_oor(channel, max_value, 'above required maximum', channel_data, file_name)       

        ##### Check whether minimum out of Range #####
        if (min_compare < float(min_value)) == True:
          self._output_oor(channel, min_value, 'below required minimum', channel_data, file_name)

    # Clear Variables
    channel, max_value, min_value, max_compare, min_compare = None, None, None, None, None


  # oor = Out of Range
  def _output_oor(self, channel, value, error_string, channel_data, file_name):   

    self.logDict['error'] = "%s is %s of %s %s in %s" % (self.map_dict[channel], error_string, str(value), channel_data[channel]['unit'], file_name)
    raise Exception ("%s is %s of %s %s in %s" % (self.map_dict[channel], error_string, str(value), channel_data[channel]['unit'], file_name))



class FullLoad(Data):

  def __init__(self, data_file):
    super().__init__(data_file)


class ZeroSpan(Data):

  def __init__(self, data_file):
    super().__init__(data_file)


  def _create_map_dict(self, channel_data):

    self.channel = self._bench_channel(channel_data)
    return super()._create_map_dict(channel_data)


  def _create_map_dict_util(self, channel, channel_names, multiple_benches, optional, data, file_name, map_dict):

    ##### Write used Ebench-Channel #####
    for name in channel_names:
      if name in data.columns:
        if multiple_benches == True:
          map_dict[channel] =  name + self.channel
        else:
          map_dict[channel] =  name
        return map_dict
    else:
      if optional == False:
        raise Exception("Cannot find %s channel %s in file %s" % (channel.replace("_"," "), channel_names, file_name))   

    # Clear Variables
    name = None


  def _bench_channel(self, channel_data):

    bench_list = {}

    ##### Scrape Species-List to identify Ebench-Channel #####
    for channel in channel_data.items():
      if channel[1]['multiple_benches'] == True:
        bench_list[channel[0]] = channel[1]['channel_names'][0]       

    ##### Set Ebench-Channel by percentage Change of Data during ZeroSpan #####
    for channel in bench_list.values():
      max_pct_change = np.nanmax(abs(self.data[channel]).pct_change())[0]
      if max_pct_change < 0.9:
        return '2'
    else:
        return ''    


  def check_ranges(self, channel_data, file_name):

    for channel in self.map_dict:       
      if channel != 'Carbon_Monoxide_Dry':

        ##### Read Max/Min-Vaues from json-file #####
        max_value = channel_data[channel]['maximum_value'] * 1.05 # Span can go 5% over the Bottle Concentration
        min_value = channel_data[channel]['maximum_value'] * -0.05 # Span can go 5% over the Bottle Concentration

        ##### Load Values from Data #####
        max_compare = np.nanmax(self.data[self.map_dict[channel]])[0]
        min_compare = np.nanmin(self.data[self.map_dict[channel]])[0]

        ##### Check whether maximum out of Range #####
        if (max_compare > float(max_value)) == True:
          self._output_oor(channel, max_value, 'above required maximum', channel_data, file_name)       

        ##### Check whether minimum out of Range #####
        if (min_compare < float(min_value)) == True:
          self._output_oor(channel, min_value, 'below required minimum', channel_data, file_name)

    # Clear Variables
    channel, max_value, min_value, max_compare, min_compare = None, None, None, None, None        



class TestData(Data):


  def __init__(self, data_file, cycle_type):
    super().__init__(data_file)
    self.cycle_type = cycle_type


  def _load_data_units(self, raw_data):

    [data, units] = super()._load_data_units(raw_data)

    if self.cycle_type == 'Steady State':
      data = self._load_steady_state(data)

    return data, units


  def _load_steady_state(self, data):

    torque_71_6 = max(data['N_CERTTRQ']) # Torque channel will be changed
    data_steady = data[data['N_CERTMODE'].isin(pd.Series(data['N_CERTMODE'].astype(int)).unique())] # Choose Data where Channel N_CERTMODE is int
    data_steady = data_steady[data_steady['N_CERTMODE']>0]

    ##### Write Torque in original TorqueChannel (same for Speed)
    data_steady['UDPi_TorqueDemand'][data_steady['N_CERTMODE'] == 1] = torque_71_6/0.716
    data_steady.index = range(0,len(data_steady))
    data_steady.Date[0] = data.Date[0]
    data_steady.Time[0] = data.Time[0]

    # Clear Variables
    Torque71_6r, Date, Time = None, None, None #ASK ANTON ABOUT THIS

    return data_steady   



class CycleValidator:
    
    def __init__(self, test_data, map_dict, full_load, warm_idle, filter_choice):

      ##### Load Data #####
      self.filter_choice = filter_choice
      self._data = test_data.data
      self._data_full = Fullload.data
      self._data_full.index = range(0,len(self.data_full))
      self._data.index = range(0,len(self.data))
      self._map_dict = map_dict

      ##### Define Variables #####     
      self._throttle = self._data[self._map_dict['Commanded__throttle']]
      self._torque_demand = self._data[self._map_dict['Commanded_Torque']]
      self._torque_engine = self._data[self._map_dict['Engine_Torque']] 
      self._speed_demand = self._data[self._map_dict['Commanded_Speed']]
      self._speed_engine = self._data[self._map_dict['Engine_Speed']]
      self._power_demand = (self._data[self._map_dict['Commanded_Torque']] * self._data[self._map_dict['Commanded_Speed']] / 9.5488) / 1000
      self._power_engine = self._data[self._map_dict['Engine_Power']]
      self._data = None

      ##### Maximum of Speed, Torque, Power and warm idle #####
      self._speed_max = np.nanmax(self._data_full[self._map_dict['Engine_Speed']])[0]
      self._torque_max = np.nanmax(self._data_full[self._map_dict['Engine_Torque']])[0]
      self._power_max = np.nanmax(self._data_full[self._map_dict['Engine_Power']])[0]
      self._warm_idle = warm_idle[0]
      self._data_full = None
        
      ##### Index of Maximum and Minimum _throttle #####
      self._index_min = np.where([self._throttle==np.nanmin(self._throttle)[0]])[1]
      self._index_max = np.where([self._throttle==np.nanmax(self._throttle)[0]])[1]


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

      for i in self._index_min:
            
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
        self._throttle, self._index_Min = None, None
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
          slope = numerator / denominator 

        # -- Regression Intercept -- EPA 1065.602-10 
        intercept = (xmean - (slope * ymean))

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






