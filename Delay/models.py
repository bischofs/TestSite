from django.db import models
import simplejson as json
import pandas as pd
import numpy as np
import copy
# Create your models here.


class DelayPrep:    


    def __init__(self, Results, Data, MapDict):

        if Results['Data'].empty:    

            self.DelayArray = {'NOx':0,'CH4':0,'THC':0,'CO':0,'CO2':0,'O2':0,'NO':0,'MFRAIR':0}

            if "Nitrous_Oxide_Wet" in MapDict:
                self.DelayArray.update({'N2O':0})
            if "Formaldehyde_Wet" in MapDict:
                self.DelayArray.update({'CH2O':0})
            if "Ammonia_Wet" in MapDict:
                self.DelayArray.update({'NH3':0})        
                  
            self.Copy = copy.deepcopy(Data)
            self.data = Data
            
        else:
            self.DelayArray = Results['Array']
            self.data = copy.deepcopy(Results['Data'])   

        self.MapDict = MapDict

        self.delaySpecies = pd.DataFrame.from_items([('Air_Flow_Rate', self.data[self.MapDict['Air_Flow_Rate']]),
                                                     ('Nitrogen_X_Dry',self.data[self.MapDict['Nitrogen_X_Dry']]),
                                                     ('Total_Hydrocarbons_Wet',self.data[self.MapDict['Total_Hydrocarbons_Wet']]), 
                                                     ('Methane_Wet',self.data[self.MapDict['Methane_Wet']]),
                                                     ('Oxygen_Dry',self.data[self.MapDict['Oxygen_Dry']]),
                                                     ('Nitrogen_Monoxide_Dry',self.data[self.MapDict['Nitrogen_Monoxide_Dry']]),
                                                     ('Carbon_Dioxide_Dry',self.data[self.MapDict['Carbon_Dioxide_Dry']]),
                                                     ('Engine_Torque',self.data[self.MapDict['Engine_Torque']]),
                                                     ('Carbon_Monoxide_Dry',self.data[self.MapDict['Carbon_Monoxide_Dry']])])

        if "Nitrous_Oxide_Wet" in MapDict:
            self.delaySpecies['Nitrous_Oxide_Wet'] = self.data[self.MapDict['Nitrous_Oxide_Wet']]
        if "Formaldehyde_Wet" in MapDict:
            self.delaySpecies['Formaldehyde_Wet'] = self.data[self.MapDict['Formaldehyde_Wet']]
        if "Ammonia_Wet" in MapDict:
            self.delaySpecies['Ammonia_Wet'] = self.data[self.MapDict['Ammonia_Wet']]


    def create_windows(self):
            
        pctChange = self.data[self.MapDict['Engine_Torque']].diff()
        largest = pctChange.nlargest(3)
        
        low = largest.index[1] - 100
        high = largest.index[1] + 100                
        
        self.delaySpecies = self.delaySpecies[low:high]

        self.delaySpecies = (self.delaySpecies - self.delaySpecies.mean()) / (self.delaySpecies.max() - self.delaySpecies.min())
        self.js = self.delaySpecies.to_json()

        self.js = {'DelaySpecies':self.js, 'Array':self.DelayArray}
        return self.js




class DelaySubmit:

    def __init__(self, Data, MapDict, DelayArray, CycleLength):

        self.Data = Data

        ChannelList = ['Nitrogen_X_Dry','Methane_Wet','Total_Hydrocarbons_Wet','Carbon_Monoxide_Dry','Carbon_Dioxide_Dry','Oxygen_Dry','Nitrogen_Monoxide_Dry','Air_Flow_Rate']

        if "Nitrous_Oxide_Wet" in MapDict:
            ChannelList.append("Nitrous_Oxide_Wet")
        if "Formaldehyde_Wet" in MapDict:
            ChannelList.append("Formaldehyde_Wet")
        if "Ammonia_Wet" in MapDict:
            ChannelList.append("Ammonia_Wet")         

        for Channel, Abbr in zip(ChannelList,DelayArray):
            self.Data[[MapDict[Channel]]] = self.Data[[MapDict[Channel]]].shift(-1*DelayArray[Abbr])
            self.Data[[MapDict[Channel]]] = self.Data[[MapDict[Channel]]].fillna(self.Data[[MapDict[Channel]]].irow(-1))
        self.Data = self.Data.ix[:CycleLength-1]


