from django.db import models

# Create your models here.


class DelayPrep:    

	def __init__(self, data, mapDict):
		self.data = data
		self.mapDict = mapDict


		def create_windows(self):
			pctChange = self.data[self.mapDict['Engine_Torque']].pct_change()
			fiveLargest = pctChange.nlargest(5)

			delaySpecies = [ self.data[self.mapDict['Air_Flow_Rate']], self.data[self.mapDict['Nitrogen_X_Dry']], self.data[self.mapDict['Methane_Wet']], self.data[self.mapDict['Oxygen_Dry']]]

			



















