from django.db import models
import simplejson as json
import pandas as pd
import numpy as np
import copy
# Create your models here.


class DelayPrep:    

    def __init__(self, results, Data, map_dict):

        if results['Data'].empty:    
            self.DelayArray = {'NOx':0,'CH4':0,'THC':0,'CO':0,'CO2':0,'NO':0,'MFRAIR':0}

            if "Nitrous_Oxide_Wet" in map_dict:
                self.DelayArray.update({'N2O':0})
            if "Formaldehyde_Wet" in map_dict:
                self.DelayArray.update({'CH2O':0})
            if "Ammonia_Wet" in map_dict:
                self.DelayArray.update({'NH3':0})        
                  
            self.Copy = copy.deepcopy(Data)
            self.data = Data
            
        else:
            self.DelayArray = results['Array']
            self.data = copy.deepcopy(results['Data'])   

        self.map_dict = map_dict
        self.delaySpecies = pd.DataFrame.from_items([('Air_Flow_Rate', self.data[self.map_dict['Air_Flow_Rate']]),
                                                     ('Nitrogen_X_Dry',self.data[self.map_dict['Nitrogen_X_Dry']]),
                                                     ('Total_Hydrocarbons_Wet',self.data[self.map_dict['Total_Hydrocarbons_Wet']]), 
                                                     ('Methane_Wet',self.data[self.map_dict['Methane_Wet']]),
                                                     ('Nitrogen_Monoxide_Dry',self.data[self.map_dict['Nitrogen_Monoxide_Dry']]),
                                                     ('Carbon_Dioxide_Dry',self.data[self.map_dict['Carbon_Dioxide_Dry']]),
                                                     ('Engine_Torque',self.data[self.map_dict['Engine_Torque']]),
                                                     ('Carbon_Monoxide_Dry',self.data[self.map_dict['Carbon_Monoxide_Dry']])])

        if "Nitrous_Oxide_Wet" in map_dict:
            self.delaySpecies['Nitrous_Oxide_Wet'] = self.data[self.map_dict['Nitrous_Oxide_Wet']]
        if "Formaldehyde_Wet" in map_dict:
            self.delaySpecies['Formaldehyde_Wet'] = self.data[self.map_dict['Formaldehyde_Wet']]
        if "Ammonia_Wet" in map_dict:
            self.delaySpecies['Ammonia_Wet'] = self.data[self.map_dict['Ammonia_Wet']]


    def create_windows(self):
            
        pctChange = self.data[self.map_dict['Engine_Torque']].diff()
        largest = pctChange.nlargest(3)
        
        low = largest.index[1] - 100
        high = largest.index[1] + 100                
        
        self.delaySpecies = self.delaySpecies[low:high]

        self.delaySpecies = (self.delaySpecies - self.delaySpecies.mean()) / (self.delaySpecies.max() - self.delaySpecies.min())
        self.js = self.delaySpecies.to_json()

        self.js = {'DelaySpecies':self.js, 'Array':self.DelayArray}
        return self.js




class DelaySubmit:

    def __init__(self, Data, map_dict, DelayArray, CycleLength):

        self.Data = Data

        ChannelList = {'NOx':'Nitrogen_X_Dry','CH4':'Methane_Wet','THC':'Total_Hydrocarbons_Wet','CO':'Carbon_Monoxide_Dry',
                       'CO2':'Carbon_Dioxide_Dry','NO':'Nitrogen_Monoxide_Dry','MFRAIR':'Air_Flow_Rate'}

        if "Nitrous_Oxide_Wet" in map_dict:
            ChannelList['N2O'] = "Nitrous_Oxide_Wet"
        else:
            del DelayArray['N2O']
        if "Formaldehyde_Wet" in map_dict:
            ChannelList['CH2O'] = "Formaldehyde_Wet"
        else:
            del DelayArray['CH2O']
        if "Ammonia_Wet" in map_dict:
            ChannelList['NH3'] = "Ammonia_Wet" 
        else:
            del DelayArray['NH3']        

        for Channel in DelayArray:
            self.Data[[map_dict[ChannelList[Channel]]]] = self.Data[[map_dict[ChannelList[Channel]]]].shift(-1*DelayArray[Channel])
            self.Data[[map_dict[ChannelList[Channel]]]] = self.Data[[map_dict[ChannelList[Channel]]]].fillna(self.Data[[map_dict[ChannelList[Channel]]]].irow(-1))
        self.Data = self.Data.ix[:CycleLength-1]


