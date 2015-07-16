from django.db import models
import simplejson as json
import pandas as pd
import numpy as np
import copy
# Create your models here.


class DelayPrep:    


    def __init__(self, Results, Data, mapDict):

        if Results['Data'].empty:    
            self.DelayArray = {'NOx':0,'CH4':0,'THC':0,'CO':0,'CO2':0,'O2':0,'NO':0,'MFRAIR':0}
            self.Copy = copy.deepcopy(Data)
            self.data = Data
            
        else:
            self.DelayArray = Results['Array']
            self.data = copy.deepcopy(Results['Data'])   

        self.mapDict = mapDict

        self.delaySpecies = pd.DataFrame.from_items([('Air_Flow_Rate', self.data[self.mapDict['Air_Flow_Rate']]),
                                                     ('Nitrogen_X_Dry',self.data[self.mapDict['Nitrogen_X_Dry']]),
                                                     ('Total_Hydrocarbons_Wet',self.data[self.mapDict['Total_Hydrocarbons_Wet']]), 
                                                     ('Methane_Wet',self.data[self.mapDict['Methane_Wet']]),
                                                     ('Oxygen_Dry',self.data[self.mapDict['Oxygen_Dry']]),
                                                     ('Nitrogen_Monoxide_Dry',self.data[self.mapDict['Nitrogen_Monoxide_Dry']]),
                                                     ('Carbon_Dioxide_Dry',self.data[self.mapDict['Carbon_Dioxide_Dry']]),
                                                     ('Engine_Torque',self.data[self.mapDict['Engine_Torque']]),
                                                     ('Carbon_Monoxide_Dry',self.data[self.mapDict['Carbon_Monoxide_Dry']])])
        
        

    def create_windows(self):
            
        pctChange = self.data[self.mapDict['Engine_Torque']].diff()
        largest = pctChange.nlargest(3)
        
        low = largest.index[1] - 100
        high = largest.index[1] + 100                
        
        self.delaySpecies = self.delaySpecies[low:high]

        self.delaySpecies = (self.delaySpecies - self.delaySpecies.mean()) / (self.delaySpecies.max() - self.delaySpecies.min())
        self.js = self.delaySpecies.to_json()

        self.js = {'DelaySpecies':self.js, 'Array':self.DelayArray}
        return self.js




class DelaySubmit:

    def __init__(self, Data, MasterDict, DelayArray):

        self.Data = Data

        ChannelList = ['Air_Flow_Rate','Nitrogen_X_Dry','Total_Hydrocarbons_Wet','Methane_Wet','Oxygen_Dry','Nitrogen_Monoxide_Dry','Carbon_Dioxide_Dry','Carbon_Monoxide_Dry']
        AbbrList = ['MFRAIR','NOx','THC','CH4','O2','NO','CO2','CO']

        for Channel, Abbr in zip(ChannelList,AbbrList):
            self.Data[[MasterDict[Channel]]] = self.Data[[MasterDict[Channel]]].shift(-1*DelayArray[Abbr])
            self.Data[[MasterDict[Channel]]] = self.Data[[MasterDict[Channel]]].fillna(self.Data[[MasterDict[Channel]]].irow(-1))

        self.Data = self.Data.ix[:len(self.Data)-29]

