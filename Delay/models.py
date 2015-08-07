from django.db import models
import simplejson as json
import pandas as pd
import numpy as np
import copy
# Create your models here.


class DelayPrep:    

    def __init__(self, results, data, map_dict):

        if results['Data'].empty:    
            self.delays = {'NOx':0,'CH4':0,'THC':0,'CO':0,'CO2':0,'NO':0,'MFRAIR':0}

            if "Nitrous_Oxide_Wet" in map_dict:
                self.delays.update({'N2O':0})
            if "Formaldehyde_Wet" in map_dict:
                self.delays.update({'CH2O':0})
            if "Ammonia_Wet" in map_dict:
                self.delays.update({'NH3':0})        
                  
            self.copy = copy.deepcopy(Data)
            self.data = data
            
        else:
            self.delays = results['Array']
            self.data = copy.deepcopy(results['Data'])   

        self.map_dict = map_dict
        self.delay_species = pd.DataFrame.from_items([('Air_Flow_Rate', self.data[self.map_dict['Air_Flow_Rate']]),
                                                     ('Nitrogen_X_Dry',self.data[self.map_dict['Nitrogen_X_Dry']]),
                                                     ('Total_Hydrocarbons_Wet',self.data[self.map_dict['Total_Hydrocarbons_Wet']]), 
                                                     ('Methane_Wet',self.data[self.map_dict['Methane_Wet']]),
                                                     ('Nitrogen_Monoxide_Dry',self.data[self.map_dict['Nitrogen_Monoxide_Dry']]),
                                                     ('Carbon_Dioxide_Dry',self.data[self.map_dict['Carbon_Dioxide_Dry']]),
                                                     ('Engine_Torque',self.data[self.map_dict['Engine_Torque']]),
                                                     ('Carbon_Monoxide_Dry',self.data[self.map_dict['Carbon_Monoxide_Dry']])])

        if "Nitrous_Oxide_Wet" in map_dict:
            self.delay_species['Nitrous_Oxide_Wet'] = self.data[self.map_dict['Nitrous_Oxide_Wet']]
        if "Formaldehyde_Wet" in map_dict:
            self.delay_species['Formaldehyde_Wet'] = self.data[self.map_dict['Formaldehyde_Wet']]
        if "Ammonia_Wet" in map_dict:
            self.delay_species['Ammonia_Wet'] = self.data[self.map_dict['Ammonia_Wet']]


    def create_windows(self):
            
        pct_change = self.data[self.map_dict['Engine_Torque']].diff()
        largest = pct_change.nlargest(3)
        
        low = largest.index[1] - 100
        high = largest.index[1] + 100                
        
        self.delay_species = self.delay_species[low:high]

        self.delay_species = (self.delay_species - self.delay_species.mean()) / (self.delay_species.max() - self.delay_species.min())
        self.js = self.delay_species.to_json()

        self.js = {'DelaySpecies':self.js, 'Array':self.delays}
        return self.js




class DelaySubmit:

    def __init__(self, data, map_dict, delays, CycleLength):

        self.data = data

        channel_list = {'NOx':'Nitrogen_X_Dry','CH4':'Methane_Wet','THC':'Total_Hydrocarbons_Wet','CO':'Carbon_Monoxide_Dry',
                       'CO2':'Carbon_Dioxide_Dry','NO':'Nitrogen_Monoxide_Dry','MFRAIR':'Air_Flow_Rate'}

        if "Nitrous_Oxide_Wet" in map_dict:
            channel_list['N2O'] = "Nitrous_Oxide_Wet"
        else:
            del delays['N2O']
        if "Formaldehyde_Wet" in map_dict:
            channel_list['CH2O'] = "Formaldehyde_Wet"
        else:
            del delays['CH2O']
        if "Ammonia_Wet" in map_dict:
            channel_list['NH3'] = "Ammonia_Wet" 
        else:
            del delays['NH3']        

        for channel in delays:
            self.data[[map_dict[channel_list[channel]]]] = self.data[[map_dict[channel_list[channel]]]].shift(-1*delays[channel])
            self.data[[map_dict[channel_list[channel]]]] = self.data[[map_dict[channel_list[channel]]]].fillna(self.data[[map_dict[channel_list[channel]]]].irow(-1))
        self.data = self.data.ix[:CycleLength-1]


