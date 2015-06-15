from django.db import models
import simplejson as json
import pandas as pd
import numpy as np
# Create your models here.


class DelayPrep:    


        def __init__(self, data, mapDict, coHigh):

                self.data = data
                self.mapDict = mapDict
                self.coHigh = coHigh

                self.delaySpecies = pd.DataFrame.from_items([('Air_Flow_Rate', self.data[self.mapDict['Air_Flow_Rate']]),('Nitrogen_X_Dry',self.data[self.mapDict['Nitrogen_X_Dry']]),
                ('Total_Hydrocarbons_Wet',self.data[self.mapDict['Total_Hydrocarbons_Wet']]), 
                ('Methane_Wet',self.data[self.mapDict['Methane_Wet']]),('Oxygen_Dry',self.data[self.mapDict['Oxygen_Dry']]), ('Nitrogen_Monoxide_Dry',self.data[self.mapDict['Nitrogen_Monoxide_Dry']]),
                ('Carbon_Dioxide_Dry',self.data[self.mapDict['Carbon_Dioxide_Dry']]),('Engine_Torque',self.data[self.mapDict['Engine_Torque']])])


                if(self.coHigh == False):
                        self.delaySpecies['Carbon_Monoxide_Low_Dry'] = self.data[self.mapDict['Carbon_Monoxide_Low_Dry']]
                else:
                        self.delaySpecies['Carbon_Monoxide_High_Dry'] = self.data[self.mapDict['Carbon_Monoxide_High_Dry']]


                

                

        def create_windows(self):

                pctChange = self.data[self.mapDict['Engine_Torque']].diff()
                largest = pctChange.nlargest(3)
                                
                low = largest.index[1] - 100
                high = largest.index[1] + 100                

                #torq = pd.Series(torqWindow, name="Torque") 


#                import ipdb; ipdb.set_trace()

                self.delaySpecies = self.delaySpecies[low:high]

                self.delaySpecies = (self.delaySpecies - self.delaySpecies.mean()) / (self.delaySpecies.max() - self.delaySpecies.min())
                
                #self.delaySpecies = self.delaySpecies.apply(lambda x: x/x.loc[x.abs().idxmax()].astype(np.float64))
                self.js = self.delaySpecies.to_json()

                return self.js


                #jsonDict = { "torque": torqWindow}

                # for species in self.delaySpecies:
        
                #         specWindow = species[low.values[0]:high.values[0]]
                #         jsonDict[species.name] = specWindow.to_json()
                        



                
