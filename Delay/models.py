from django.db import models
import simplejson as json
import pandas as pd
import numpy as np
# Create your models here.


class DelayPrep:    


        def __init__(self, data, mapDict):

                self.data = data
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
                
                #torq = pd.Series(torqWindow, name="Torque") 

                
                self.delaySpecies = self.delaySpecies[low:high]

                self.delaySpecies = (self.delaySpecies - self.delaySpecies.mean()) / (self.delaySpecies.max() - self.delaySpecies.min())
                
                #self.delaySpecies = self.delaySpecies.apply(lambda x: x/x.loc[x.abs().idxmax()].astype(np.float64))
                self.js = self.delaySpecies.to_json()

                return self.js

                #jsonDict = { "torque": torqWindow}

                # for species in self.delaySpecies:
        
                #         specWindow = species[low.values[0]:high.values[0]]
                #         jsonDict[species.name] = specWindow.to_json()


class DelaySubmit:

    def __init__(self, Data, MasterDict, DelayArray):

        self.MapDict = MasterDict
        self.Data = Data
        self.Array = DelayArray      

        ChannelList = ['Air_Flow_Rate','Nitrogen_X_Dry','Total_Hydrocarbons_Wet','Methane_Wet','Oxygen_Dry','Nitrogen_Monoxide_Dry','Carbon_Dioxide_Dry','Carbon_Monoxide_Dry']
        AbbrList = ['MFRAIR','NOx','THC','CH4','O2','NO','CO2','CO']

        for Channel, Abbr in zip(ChannelList,AbbrList):
            self.Data[[self.MapDict[Channel]]] = self.Data[[self.MapDict[Channel]]].shift(-1*self.Array[Abbr])
            self.Data[[self.MapDict[Channel]]] = self.Data[[self.MapDict[Channel]]].fillna(self.Data[[self.MapDict[Channel]]].irow(-1))

        self.Data = self.Data.ix[:len(self.Data)-29]

