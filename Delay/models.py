from django.db import models
import simplejson as json
import pandas as pd
# Create your models here.


class DelayPrep:    


        def __init__(self, data, mapDict, coHigh):

                self.data = data
                self.mapDict = mapDict
                self.coHigh = coHigh

                self.delaySpecies = pd.DataFrame.from_items([('Air_Flow_Rate', self.data[self.mapDict['Air_Flow_Rate']]),('Nitrogen_X_Dry',self.data[self.mapDict['Nitrogen_X_Dry']]), 
                ('Methane_Wet',self.data[self.mapDict['Methane_Wet']]),('Oxygen_Dry',self.data[self.mapDict['Oxygen_Dry']]), ('Nitrogen_Monoxide_Dry',self.data[self.mapDict['Nitrogen_Monoxide_Dry']]),
                ('Carbon_Dioxide_Dry',self.data[self.mapDict['Carbon_Dioxide_Dry']])])


                if(self.coHigh == False):
                        self.delaySpecies['Carbon_Monoxide_Low_Dry'] = self.data[self.mapDict['Carbon_Monoxide_Low_Dry']]
                else:
                        self.delaySpecies['Carbon_Monoxide_Low_Dry'] = self.data[self.mapDict['Carbon_Monoxide_Low_Dry']]


                self.js = self.delaySpecies.to_json()

                

        def create_windows(self):

                pctChange = self.data[self.mapDict['Engine_Torque']].pct_change()
                largest = pctChange.nlargest(1)
                                
                low = largest.index - 10
                high = largest.index + 10                

                #torq = pd.Series(torqWindow, name="Torque") 
                
                #import ipdb; ipdb.set_trace()
                return self.js


                #jsonDict = { "torque": torqWindow}

                # for species in self.delaySpecies:
        
                #         specWindow = species[low.values[0]:high.values[0]]
                #         jsonDict[species.name] = specWindow.to_json()
                        



                
