from django.db import models
from Ebench.models import Ebench

import pandas as pd
import statsmodels.api as sm
import pandas as pd
import numpy as np
import scipy as sc
import scipy.optimize as opt
import xlsxwriter
import io

class Calculator:

  def __init__(self, DataHandler, MapDict, ReportParams):
        
    self.preparation = Preparation(DataHandler, MapDict)   
    self.calculation = Calculation(self.preparation, MapDict)
    DataHandler, MapDict, ReportParams = None, None, None



class Preparation:

  def __init__(self, DataHandler, MapDict):

    ##### Load Data #####
    self.pre = DataHandler.preZeroSpan.data
    self.post = DataHandler.postZeroSpan.data
    self.test = DataHandler.testData.data
    self.TestType = DataHandler.testData.metaData['test_type']

    ##### CoHigh or COL #####
    if DataHandler.CoHigh:
         self.CO = MapDict['Carbon_Monoxide_High_Dry']
         COString = 'COH'
    else:
         self.CO = MapDict['Carbon_Monoxide_Low_Dry']
         COString = 'COL'

    ##### Prepare Fuel and E-bench data #####
    self.FuelData = self._fuel_data(DataHandler.testData.metaData, MapDict)
    self.EbenchData = self._ebench_data(DataHandler.ebenchData, DataHandler.testData.data,MapDict, COString)               

    ##### Prepare Pre/Post-Data #####
    self.Species = [MapDict['Carbon_Dioxide_Dry'],self.CO,MapDict['Nitrogen_X_Dry'],
                    MapDict['Total_Hydrocarbons_Wet'],MapDict['Methane_Wet']]                  
    self.ZeroSpan = self._zeroSpan(self.pre, self.post, self.Species, self.EbenchData)        

    ##### Prepare Test parameter
    if (self.TestType == 'Transient').bool:
         self.TransientBool = True
    else:
         self.TransientBool = False


  def _fuel_data(self, HeaderData, MapDict):


    ##### Carbon Mass Fraction and Fuel Composition -- CFR 1065.655 #####
    FuelData = pd.DataFrame(data=np.zeros([20,1]), index=['M_C','M_H','M_O','M_S','M_N','M_HC','M_NMHC','M_NOX','M_CO','M_CO2',
                                                           'W_c','W_h','W_o','W_s','W_n','alpha','beta','gamma','delta','xH2Ogas'])

    ## Molar masses ##
    FuelData.M_C = 12.0107 # Molar mass of Carbon
    FuelData.M_H = 1.00794 # Molar mass of Hydrogen
    FuelData.M_O = 15.9994 # Molar mass of Oxygen
    FuelData.M_S = 32.065 # Molar mass of Sulfur
    FuelData.M_N = 14.0067 # Molar mass of atomic Nitrogen
    FuelData.M_HC = 13.875389 # Molar mass of HC
    FuelData.M_NMHC = 13.875389 # Molar mass of NMHC
    FuelData.M_NOX = 46.0055 # Molar mass of NO2
    FuelData.M_CO = 28.0101 # Molar mass of CO
    FuelData.M_CO2 = 44.0095 # Molar mass of CO2

    ## Mass fractions ##   
    FuelData.W_c = float(HeaderData[MapDict['Mass_Fraction_Carbon']])/100 # Carbon mass fraction of fuel
    FuelData.W_h = float(HeaderData[MapDict['Mass_Fraction_Hydrogen']])/100 # Hydrogen mass fraction of fuel
    FuelData.W_o = float(HeaderData[MapDict['Mass_Fraction_Oxygen']])/100 # Oxygen mass fraction of fuel
    FuelData.W_s = 0
    FuelData.W_n = 0
    #FuelData.W_s = headerData[MapDicht['Mass_Fraction_Sulfur']]/10000 in ppm in Header page, the sum of W doesn't equals 1
    #FuelData.W_n = headerData['N_MFN'] not in Header page

    ## Calculation of parameters ##
    FuelData.alpha = (FuelData.W_h*FuelData.M_C)/(FuelData.W_c*FuelData.M_H)
    FuelData.beta = (FuelData.W_o*FuelData.M_C)/(FuelData.W_c*FuelData.M_O)
    FuelData.gamma = (FuelData.W_s*FuelData.M_C)/(FuelData.W_c*FuelData.M_S)
    FuelData.delta = (FuelData.W_n*FuelData.M_C)/(FuelData.W_c*FuelData.M_N)

    FuelData.xH2Ogas = 3.5 # Constant Value does not belong to fuel (water-gas reaction equilibrium coefficient)

    return FuelData


  def _ebench_data(self, ebenchData,TestData,MapDict,COString):    

    EbenchData = pd.DataFrame(data=np.zeros([14,1]),index=['RFPF','CH4_RF','Tchiller','Pchiller','Pamb','Factorchiller',
                                                         'xTHC_THC_FID_init','xCO2intdry','xCO2dildry','Bottle_Concentration_CO2',
                                                         'Bottle_Concentration_CO','Bottle_Concentration_NOX','Bottle_Concentration_THC',
                                                         'Bottle_Concentration_NMHC'])
    ##### Write Ebench-Data #####
    EbenchData.RFPF = ebenchData['RFPF']
    EbenchData.CH4_RF = ebenchData['CH4_RF']
    EbenchData.Tchiller = ebenchData['Tchiller'] + 273.15 # in K      
    EbenchData.Pamb = np.mean(TestData[MapDict['Air_Ambient_Pressure']])*100 # bar --> kPa
    EbenchData.Pchiller = ebenchData['Pchiller'] + EbenchData.Pamb
    EbenchData.xCO2intdry = 0.000375 ## CFR 1065.655
    EbenchData.xCO2dildry = 0.000375 ## CFR 1065.655
    EbenchData.xTHC_THC_FID_init = ebenchData['xTHC[THC_FID]init']
    EbenchData.Factorchiller = (10**(10.79574*(1-(273.16/EbenchData.Tchiller))-5.028*np.log10(EbenchData.Tchiller/273.16)+0.000150475*(1-10**(-8.2969*((EbenchData.Tchiller/273.16)-1)))+0.00042873*(10**(4.76955*(1-(273.16/EbenchData.Tchiller)))-1)-0.2138602))/(EbenchData.Pchiller)

    ##### Bottle Concentrations from Ebench #####
    EbenchData.Bottle_Concentration_CO2 = ebenchData['Bottle_Concentration_CO2']
    EbenchData.Bottle_Concentration_CO = ebenchData['Bottle_Concentration_' + COString]
    EbenchData.Bottle_Concentration_NOX = ebenchData['Bottle_Concentration_NOX']
    EbenchData.Bottle_Concentration_THC = ebenchData['Bottle_Concentration_THC']
    EbenchData.Bottle_Concentration_NMHC =  ebenchData['Bottle_Concentration_NMHC']

    # Clear Variables
    ebenchData, TestData = None, None

    return EbenchData


  def _zeroSpan(self, Pre, Post, Species, Ebench):
      
    ListFactor = [10000,10000,1,1,1]          
    ZeroSpan = pd.DataFrame(data=np.zeros([5,5]),index=['PreZero','PreSpan','PostZero','PostSpan','Chosen'],columns=Species)
    TimeWindow = self._prepare_time_window(Species)

    ##### Chosen-Data From Ebench
    ZeroSpan[Species[0]]['Chosen'] = Ebench.Bottle_Concentration_CO2
    ZeroSpan[Species[1]]['Chosen'] = Ebench.Bottle_Concentration_CO
    ZeroSpan[Species[2]]['Chosen'] = Ebench.Bottle_Concentration_NOX
    ZeroSpan[Species[3]]['Chosen'] = Ebench.Bottle_Concentration_THC
    ZeroSpan[Species[4]]['Chosen'] = Ebench.Bottle_Concentration_NMHC

    ##### Pre Zero/Span #####
    Name = {'Zero':'PreZero','Span':'PreSpan'}
    ZeroSpan = self._prepare_type(ZeroSpan,Species,TimeWindow,Pre,Name)

    ##### Post Zero/Span #####
    Name = {'Zero':'PostZero','Span':'PostSpan'}
    ZeroSpan = self._prepare_type(ZeroSpan,Species,TimeWindow,Post,Name)

    # Clear Variables
    ListFactor, TimeWindow, Name = None, None, None

    return ZeroSpan


  def _prepare_time_window(self,Species):

    ## Species = ['CO2','CO','NOX','THC','CH4'] these are the Species in the array but with the channel names
    TypeTime = ['Zero_start','Zero_end','Span_start','Span_end']
    SpecTime = [0,59,60,119] # Time window for Zero and Span Data
    TimeWindow = pd.DataFrame(data = np.ones([4,5]), columns=Species, index=TypeTime)

    for TimePoint, SpecTime in zip(TypeTime,SpecTime):
      TimeWindow.loc[TimePoint,:] = SpecTime
        
    TimeWindow[Species[0]]['Span_start'] = 120
    TimeWindow[Species[0]]['Span_end'] = 179
    TimeWindow[Species[4]]['Span_start'] = 120
    TimeWindow[Species[4]]['Span_end'] = 179

    # Clear Variables
    Species, TypeTime, SpecTime = None, None, None

    return TimeWindow


  def _prepare_type(self, ZeroSpan, Species, TimeWindow, Data, name): 

    for spec in Species:
      ColumnZero = Data.loc[TimeWindow[spec][0]:TimeWindow[spec][1], spec]
      ColumnZero.index = range(0,len(ColumnZero))
      ColumnSpan = Data.loc[TimeWindow[spec][2]:TimeWindow[spec][3], spec]
      ColumnSpan.index = range(0,len(ColumnSpan))
      
      for i in range(0,len(ColumnZero)):

          if ColumnZero[i]> ZeroSpan[spec]['Chosen']*0.01: # Accetable Range of noise 1%
              ColumnZero = ColumnZero.drop(i)

          if (ColumnSpan[i]< ZeroSpan[spec]['Chosen']*0.98) | (ColumnSpan[i] > ZeroSpan[spec]['Chosen']*1.02): # Acceptable Range of noise +-2%
              ColumnSpan = ColumnSpan.drop(i)

      if (len(ColumnZero)) > 30 and (len(ColumnSpan) > 30): # At least 30 points to calculate the average of Zero and Span

          ZeroSpan[spec][name['Zero']] = abs(ColumnZero.mean())
          ZeroSpan[spec][name['Span']] = abs(ColumnSpan.mean())

      else:

        raise Exception('Not enough data points for average Zero/Span! Minimum : 30')

    # Clear Variables
    ColumnZero, ColumnSpan, spec, Species, TimeWindow, Data, name, i = None, None, None, None, None, None, None, None

    return ZeroSpan        



class Calculation:

    def __init__(self, Preparation, MapDict):

        if Preparation.TransientBool == True:
             self._transient_calculation(Preparation, MapDict)
             self.result = self._result()             
        else:
             self._steady_state_calculation(Preparation, MapDict)


    def _transient_calculation(self, Preparation, MapDict):

        Species = Preparation.Species
        ZeroSpan = Preparation.ZeroSpan
        DataUn = pd.DataFrame()
        DataCor = pd.DataFrame()

        ##### Drif-uncorrected Calc #####
        [DataUn, self.ArraySumUn] = self._inner_calc(Preparation, DataUn, Species)

        ##### Drift-corrected Calc #####
        PreparationDrift = Preparation
        PreparationDrift.test = self._drift_correction(DataUn, ZeroSpan, Preparation.test, Species)
        [DataCor, self.ArraySumCor] = self._inner_calc(PreparationDrift, DataCor, Species)  
        [self.ArraySumCorWon, self.U_BPOW_Factor] = self._remove_negatives(DataCor, Preparation.test, MapDict)

        self.ArraySum = [self.ArraySumUn, self.ArraySumCor, self.ArraySumCorWon]
        self.Data = [Preparation.test, DataUn, DataCor]

        # Clear Variables
        Species, ZeroSpan, DataUn, DataCor = None, None, None, None


    def _steady_state_calculation(self, Preparation):

        ## Calculate steady state Cycle
        pass


    def _inner_calc(self, Preparation, Data, Species):

        ##### Load Data #####
        TestData = Preparation.test
        Ebench = Preparation.EbenchData
        Fuel = Preparation.FuelData 

        ##### Steps of calculation #####
        Data = self._unit_conversion(Data, TestData, Species)
        Data = self._prepare_iteration(Data, TestData, Ebench)
        Data = self._iteration(Data, Fuel, Ebench)
        [Data, ArraySum] = self._rest_calculation(Data, Fuel)

        # Clear Variables
        Preparation, Species, TestData, Ebench, Fuel = None, None, None, None, None

        return Data, ArraySum


    def _unit_conversion(self, Data, TestData, Species):

        # Species
        Data["E_CO2D2"] = TestData[Species[0]]*10000 # % --> ppm
        Data[Species[1]] = TestData[Species[1]]*10000 # % --> ppm
        Data["E_NOXD2"] = TestData.E_NOXD2 # in ppm
        Data["E_THCW2"] = TestData.E_THCW2 # in ppm        

        Data["xCH4wet"] = TestData[Species[4]]/1000000 # ppm --> mol/mol
        Data["xCO2meas"] = Data.E_CO2D2/1000000 # ppm --> mol/mol
        Data["xCOmeas"] = Data.get(Species[1])/1000000 # ppm --> mol/mol
        Data["xNOxmeas"] = Data.E_NOXD2/1000000 # ppm --> mol/mol
        Data["xTHCmeas"] = Data.E_THCW2/1000000 # ppm --> mol/mol

        # Flows
        Data["mfuel"] = TestData.M_FRFUEL*1000/3600 # kg/h --> g/s
        Data["Molar Flow Wet"] = TestData.C_FRAIRWS*1000/3600 # kg/h --> g/s
        Data["Intake Air flow"] = Data.get("Molar Flow Wet")/28.96 # g/sec --> mol/sec

        # Rest
        Data["BARO Press"] = TestData.P_INLET*10000 # bar --> Pa
        Data["T_INLET"] = TestData.T_INLET + 273.15 # °C --> K

        # Clear Variables
        TestData, Species = None, None

        return Data


    def _prepare_iteration(self, Data, TestData, Ebench):    

        # Intake
        Data["pH2O @ inlet"] = 10**(10.79574*(1-(273.16/(Data.T_INLET)))-5.028*np.log10((Data.T_INLET)/273.16)+0.000150475*(1-10**(-8.2969*(((Data.T_INLET)/273.16)-1)))+0.00042873*(10**(4.76955*(1-(273.16/(Data.T_INLET))))-1)-0.2138602)
        Data["xH2O"] = TestData.M_RELHUM*Data.get("pH2O @ inlet")/(Data.get("BARO Press"))
        Data["xH2Oint"] = Data.xH2O
        Data["Mmix"] = 28.96559*(1-Data.xH2O)+18.01528*Data.xH2O
        Data["nint (Intake Air Flow)"] = Data.get("Molar Flow Wet")/Data.Mmix
        Data["xH2Ointdry"] = Data.xH2Oint/(1-Data.xH2Oint)
        Data["xCO2int"] = Ebench.xCO2intdry/(1+Data.xH2Ointdry)
        Data["xO2int"] = ((0.20982-Ebench.xCO2intdry)/(1+Data.xH2Ointdry))

        # Dilution
        Data["xH2Odil"] = Data.xH2O 
        Data["xH2Odildry"] = Data.xH2Odil/(1-Data.xH2Odil)
        Data["xCO2dil"] = Ebench.xCO2dildry/(1+Data.xH2Odildry)

        # Rest
        Data["xTHC[THC_FID]cor"] = Data.E_THCW2-Ebench.xTHC_THC_FID_init
        Data["xNO2meas"] = Data.xNOxmeas*0 # NO2 not measured
        Data["xNOmeas"] = Data.xNOxmeas*1
        Data["xTHCwet"] = Data.xTHCmeas
        Data["xNMHCwet"] = (Data.xTHCwet-Data.xCH4wet*Ebench.CH4_RF)/(1-Ebench.RFPF*Ebench.CH4_RF)        

        # Clear Variables
        TestData, Ebench = None, None

        return Data


    def _iteration(self, Data, Fuel, Ebench):   

        def function_iteration(variables):

            ###### Channels in Formulas #####

            #A = xdil/exh -- G
            #B = xH2Oexh -- H
            #C = xCcombdry -- I
            #D = xH2Oexhdry -- J
            #E = xdil/exhdry -- K
            #F = xint/exhdry -- L
            #G = xraw/exhdry -- M
            #H = xH2OCOmeas -- AC
            #I = xH2OTHCmeas -- AD
            #J = xH2ONOxmeas -- AE
            #K = xH2ONO2meas -- AF
            #L = xH2OCO2meas -- AH
            #M = xCOdry -- AI
            #N = xTHCdry -- AJ
            #O = xNOxdry -- AK
            #P = xNO2dry -- AL
            #Q = xCO2dry -- AN
            #R = xH2dry -- AO 
            
            # Unknown Variables
            (A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R) = variables
                
            # Known Variables
            S = Data.xCO2dil[i]
            T = Data.xCO2int[i]
            U = Fuel.alpha
            V = Data.xH2Odil[i]
            W = Data.xH2Oint[i]
            X = Data.xO2int[i]
            Y = Fuel.beta
            Z = Fuel.gamma
            AA = Fuel.delta
            AB = Data.xCOmeas[i]
            AC = Data.xTHCmeas[i]
            AD = Data.xNOxmeas[i]
            AE = Data.xNO2meas[i]
            AF = Fuel.xH2Ogas
            AG = Data.xCO2meas[i]
            
            # Equations to solve
            eq1 = 1-(G/(1+D))-A
            eq2 = D/(1+D)-B
            eq3 = Q+(M)+(N)-(S*E)-(T*F)-C
            eq4 = ((U/2)*(C-N))+V*E+W*F-R-D 
            eq5 = A/(1-B)-E
            eq6 = (1/(2*X))*(((U/2)-Y+2+(2*Z))*(C-N)-(M-O-(2*P)+R))-F
            eq7 = 0.5*(((U/2)+Y+AA)*(C-N)+((2*N)+M-P+R))+F-G
            eq8 = AB/(1-H)-M ## Reference: CFR 1065.659
            eq10 = AC/(1-I)-N ## Reference: CFR 1065.659
            eq11 = B-I
            eq12 = AD/(1-J)-O ## Reference: CFR 1065.659
            eq14 = AE/(1-K)-P ## Reference: CFR 1065.659
            eq16 = (M*(D-V*E))/(AF*(Q-S*E))-R ## Reference: CFR 1065.659
            eq17 = AG/(1-L)-Q ## Reference: CFR 1065.659
            
            if Mode==0:
                eq9 = Ebench.Factorchiller-H    
                eq13 = Ebench.Factorchiller-J
                eq15 = Ebench.Factorchiller-K
                eq18 = Ebench.Factorchiller-L
            else:
                eq9 = B-H    
                eq13 = B-J
                eq15 = B-K
                eq18 = B-L
            
            return [eq1,eq2,eq3,eq4,eq5,eq6,eq7,eq8,eq9,eq10,eq11,eq12,eq13,eq14,eq15,eq16,eq17,eq18]

        i = 0
        Mode = 0
        ResultList = np.zeros((len(Data),18))     

        while i < len(Data)-1:
            i +=1  
            g = 0.5 # First guess for iteration start

            Solution = opt.fsolve(function_iteration,(g,g,g,g,g,g,g,g,g,g,g,g,g,g,g,g,g,g))
            
            if Solution[2]<Ebench.Factorchiller:
                Mode = 1 # Different Calculation with mode 1 or 0
                Solution = opt.fsolve(function_iteration,(g,g,g,g,g,g,g,g,g,g,g,g,g,g,g,g,g,g))
                Mode = 0
            ResultList[:][i] = Solution

        Iteration = pd.DataFrame(ResultList,columns =['xdil/exh','xH2Oexh','xCcombdry','xH2Oexhdry','xdil/exhdry','xint/exhdry',
                                                      'xraw/exhdry','xH2OCOmeas','xH2OTHCmeas','xH2ONOxmeas','xH2ONO2meas','xH2OCO2meas',
                                                      'xCOdry','xTHCdry','xNOxdry','xNO2dry','xCO2dry','xH2dry'])
        Data = pd.concat([Data,Iteration],axis=1)

        # Clear Variables
        Iteration, Mode, ResultList, g, Solution = None, None, None, None, None

        return Data


    def _rest_calculation(self, Data, Fuel):   

        # Dry Emissions
        Data["xH2ONOmeas"] = Data.xH2ONO2meas
        Data["xNOdry"] = Data.xNOmeas/(1-Data.xH2ONOmeas) ## Reference: CFR 1065.659
        Data["xCO2dry"] = Data.xCO2meas/(1-Data.xH2OCO2meas) ## Reference: CFR 1065.659
        Data["xH2dry"] = (Data.xCOdry*(Data.xH2Oexhdry-Data.xH2Odil*Data.get("xdil/exhdry")))/(Fuel.xH2Ogas*(Data.xCO2dry-Data.xCO2dil*Data.get("xdil/exhdry")))

        # Wet Emissions
        Data["xCOwet"] = Data.xCOmeas*((1-Data.xH2Oexh)/(1-Data.xH2OCOmeas))
        Data['xNOxwet'] = Data.xNOxmeas*((1-Data.xH2Oexh)/(1-Data.xH2ONOxmeas))
        Data["xNO2wet"] = Data.xNO2meas*((1-Data.xH2Oexh)/(1-Data.xH2ONO2meas))
        Data["xNOwet"] = Data.xNOmeas*((1-Data.xH2Oexh)/(1-Data.xH2ONOmeas))
        Data["xCO2wet"] = Data.xCO2meas*((1-Data.xH2Oexh)/(1-Data.xH2OCO2meas))
        Data["xNOxcorrwet"] = Data.xNOxwet*(18.84 *Data.xH2O + 0.68094) ## Reference: CFR 1065.670 !!!!!@!@!@@!??? Change the value to take from json

        # Masses of emissions
        Data["nexh"] = Data.get("nint (Intake Air Flow)")/(1+((Data.get("xint/exhdry")-Data.get("xraw/exhdry"))/(1+Data.xH2Oexhdry)))
        Data["Mass_THC"] = Data.xTHCwet*Data.nexh*Fuel.M_HC
        Data["Mass_CO"] = Data.xCOwet*Data.nexh*Fuel.M_CO
        Data["Mass_NOx"] = Data.xNOxcorrwet*Data.nexh*Fuel.M_NOX
        Data["Mass_CO2"] = Data.xCO2wet*Data.nexh*Fuel.M_CO2
        Data["Mass_NMHC"] = Data.xNMHCwet*Data.nexh*Fuel.M_NMHC

        # Emissions in total
        ArraySum = {'CO2':Data.Mass_CO2.sum(),'CO':Data.Mass_CO.sum(),'NOx':Data.Mass_NOx.sum(),'THC':Data.Mass_THC.sum(),'NMHC':Data.Mass_NMHC.sum()}

        # Clear Variables
        Fuel = None, None, None, None, None, None

        return Data, ArraySum


    def _drift_correction(self, DataUn, ZeroSpan, TestData, Species):

        ## Correct Raw-Emissions ##
        TestData['E_CO2D2'] = ZeroSpan.E_CO2D2['Chosen']*((2*DataUn.E_CO2D2)-(ZeroSpan.E_CO2D2['PreZero']+ZeroSpan.E_CO2D2['PostZero']))/((ZeroSpan.E_CO2D2['PreSpan']+ZeroSpan.E_CO2D2['PostSpan'])-(ZeroSpan.E_CO2D2['PreZero']+ZeroSpan.E_CO2D2['PostZero']))/10000 # in % because of later calculation
        TestData[Species[1]] = ZeroSpan[Species[1]]['Chosen']*((2*DataUn.get(Species[1]))-(ZeroSpan[Species[1]]['PreZero']+ZeroSpan[Species[1]]['PostZero']))/((ZeroSpan[Species[1]]['PreSpan']+ZeroSpan[Species[1]]['PostSpan'])-(ZeroSpan[Species[1]]['PreZero']+ZeroSpan[Species[1]]['PostZero']))/10000 # in % because of later calculation
        TestData['E_NOXD2'] = ZeroSpan.E_NOXD2['Chosen']*((2*TestData.E_NOXD2)-(ZeroSpan.E_NOXD2['PreZero']+ZeroSpan.E_NOXD2['PostZero']))/((ZeroSpan.E_NOXD2['PreSpan']+ZeroSpan.E_NOXD2['PostSpan'])-(ZeroSpan.E_NOXD2['PreZero']+ZeroSpan.E_NOXD2['PostZero']))
        TestData['E_THCW2'] = ZeroSpan.E_THCW2['Chosen']*((2*DataUn.get('xTHC[THC_FID]cor'))-(ZeroSpan.E_THCW2['PreZero']+ZeroSpan.E_THCW2['PostZero']))/((ZeroSpan.E_THCW2['PreSpan']+ZeroSpan.E_THCW2['PostSpan'])-(ZeroSpan.E_THCW2['PreZero']+ZeroSpan.E_THCW2['PostZero']))
        TestData['E_CH4W2'] = ZeroSpan.E_CH4W2['Chosen']*((2*TestData.E_CH4W2)-(ZeroSpan.E_CH4W2['PreZero']+ZeroSpan.E_CH4W2['PostZero']))/((ZeroSpan.E_CH4W2['PreSpan']+ZeroSpan.E_CH4W2['PostSpan'])-(ZeroSpan.E_CH4W2['PreZero']+ZeroSpan.E_CH4W2['PostZero']))

        # Clear Variables
        DataUn, ZeroSpan, Species = None, None, None

        return TestData

    def _remove_negatives(self, Data, DataRaw, MapDict):

        # Emissions and Engine Power in total (Negative Values removed)
        Data.Mass_CO2[np.where(Data.Mass_CO2<0)[0]] = 0          
        Data.Mass_CO[np.where(Data.Mass_CO<0)[0]] = 0
        Data.Mass_NOx[np.where(Data.Mass_NOx<0)[0]] = 0      
        Data.Mass_THC[np.where(Data.Mass_THC<0)[0]] = 0
        Data.Mass_NMHC[np.where(Data.Mass_NMHC<0)[0]] = 0
        U_BPOW_Factor = DataRaw[MapDict['Engine_Power']].drop(np.where(DataRaw[MapDict['Engine_Power']]<0)[0]).sum(skipna=True)/(3600*0.746)

        ArraySumCorWon = {'CO2':Data.Mass_CO2.sum(),'CO':Data.Mass_CO.sum(),'NOx':Data.Mass_NOx.sum(),
                         'THC':Data.Mass_THC.sum(),'NMHC':Data.Mass_NMHC.sum()}

        # Clear Variables
        MapDict, DataRaw, i = None, None, None

        return ArraySumCorWon, U_BPOW_Factor


    def _result(self):

        ##### Load Data #####
        Species = ['CO2','CO','NOx','THC','NMHC'] 

        ##### Create DataFrames #####
        DF = pd.DataFrame()
        DF['Species'] = Species
        DF['Units'] = ['g/ghphr','g/ghphr','g/ghphr','g/ghphr','g/ghphr']
        DF['Test'] = np.zeros([5,1])
        DF['Total'] =  np.zeros([5,1])
        self.DriftUncorrected, self.DriftCorrected, self.Final = DF.copy(), DF.copy(), DF.copy()
        DF = None

        for i in range(0,len(Species)):
            self.DriftUncorrected['Test'][i] = self.ArraySumUn[Species[i]]/self.U_BPOW_Factor
            self.DriftUncorrected['Total'][i] = self.ArraySumUn[Species[i]]
            self.DriftCorrected['Test'][i] = self.ArraySumCor[Species[i]]/self.U_BPOW_Factor
            self.DriftCorrected['Total'][i] = self.ArraySumCor[Species[i]]
            self.Final['Test'][i] = self.ArraySumCorWon[Species[i]]/self.U_BPOW_Factor
            self.Final['Total'][i] = self.ArraySumCorWon[Species[i]]

        self.result = [self.DriftUncorrected.to_json(), self.DriftCorrected.to_json(), self.Final.to_json()]

        return self.result



class Report:

    def __init__(self, DataHandler, MapDict, CalculatorLog, DelayArray, output):

        ###### Load Variables #####
        self.output = output
        #Test, Uncorrected, Corrected = Calculator.Data
        ArraySumUn, ArraySumCor, ArraySumCorWon = CalculatorLog['Array']
        self.DriftUncorrected, self.DriftCorrected, self.Final = CalculatorLog['Results']
        Species = ['CO2','CO','NOx','THC','NMHC']  

        ###### Preparation of Excel-File #####        
        self.file = self._preparation_excel_file(self.output)

        ##### Write Emissions in Report ######
        self.sheet = self._write_emissions(self.sheet, self.DriftUncorrected, self.DriftCorrected, self.Final, ArraySumUn, ArraySumCor, ArraySumCorWon, Species)
        self.sheet = self._write_first_page(self.sheet, DataHandler.resultsLog, CalculatorLog['ZeroSpan'], DelayArray)
        ##### Write Data according to choosen options #####
        #self.sheet2 = self._write_dataframe(self.sheet2, Test)
        #self.sheet3 = self._write_dataframe(self.sheet3, Uncorrected)
        #self.sheet4 = self._write_dataframe(self.sheet4, Corrected)

        self.file.close()


    def _preparation_excel_file(self, output):

        file = xlsxwriter.Workbook(output, {'in_memory':True})
        self.sheet = file.add_worksheet('Emissions_Calculations')
        #self.sheet2 = file.add_worksheet('Raw Data')
        #self.sheet3 = file.add_worksheet('Drift-uncorrected Data')
        #self.sheet4 = file.add_worksheet('Drift-corrected Data')

        return file

    def _write_emissions(self, sheet, DriftUncorrected, DriftCorrected, Final, ArraySumUn, ArraySumCor, ArraySumCorWon, Species):

        Type = ['Drift-uncorrected', 'Drift-corrected', 'Final']
        TypeNum = [19, 10 , 1]
        DataList = [DriftUncorrected, DriftCorrected, Final]
        ArrayList = [ArraySumUn, ArraySumCor, ArraySumCorWon]     

        ##### Prepare Formats #####
        self.dark_grey = self.file.add_format({'fg_color':'#696969','bold':1,'border': 1})
        self.bright_grey = self.file.add_format({'fg_color':'#A9A9A9', 'bold':1,'border': 1})
        self.border = self.file.add_format({'border':1})
        self.green = self.file.add_format({'fg_color':'#5EFB6E','border': 1})
        self.red = self.file.add_format({'fg_color':'#F75D59','border': 1})        
        self.merge = self.file.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': '#C71585','font_color':'white'})
        
        for [text, index, Data, Array] in zip(Type, TypeNum, DataList, ArrayList):
            
            ##### Write Data to File #####
            Data = pd.read_json(Data)
            sheet.merge_range('J'+str(index) + ':L'+str(index), text +' Emissions', self.merge)
            sheet.write('J'+str(index+1),'Species',self.dark_grey)
            sheet.write('K'+str(index+1),'Units',self.dark_grey)
            sheet.write('L'+str(index+1),'Test',self.dark_grey)
            sheet.write_column('J'+str(index+2),Data.Species,self.bright_grey)
            sheet.write_column('K'+str(index+2),Data.Units,self.bright_grey)
            where_are_NaNs = np.isnan(Data.Test)
            Data.Test[where_are_NaNs] = 99999
            sheet.write_column('L'+str(index+2),np.round(Data.get('Test'),3),self.border)

            ##### Emissions Total Mass #####
            sheet.write('N'+str(index), 'Emissions Mass', self.bright_grey)
            sheet.write('N'+str(index+1),'Total',self.bright_grey)
            sheet.write_column('N'+str(index+2), np.round(Data.get('Total'),3), self.border)

        return sheet


    def _write_first_page(self, sheet, ResultsLog, ZeroSpan, DelayArray):

        Regression = ResultsLog['Regression'][0]
        OmitChoice = ResultsLog['Regression'][1]
        Regression_bool = ResultsLog['Regression_bool']
        Delay = ResultsLog['Data Alignment']

        TypeList = ['Power', 'Speed', 'Torque']
        Letters = ['B','C','D']
        ResultsList = ['Intercept', 'Rsquared', 'Slope', 'Standard Error']
        sheet.write_row('B2',TypeList,self.dark_grey)
        sheet.write('A2','Parameter',self.dark_grey)
        sheet.merge_range('A7:B7','Omit Choice :',self.bright_grey)
        if OmitChoice == 0:
            text = 'W/o omit'
        elif OmitChoice == 1:
            text = 'Omit 1 (Power & Torque)'
        elif OmitChoice == 2:
            text = 'Omit 2 (Power & Speed)'
        elif OmitChoice == 3:
            text = 'Omit 3.1 (Power & Torque)'
        elif OmitChoice == 4:
            text = 'Omit 3.2 (Power & Speed)'
        elif OmitChoice == 5:
            text = 'OOmit 4.1 (Power & Torque)'  
        elif OmitChoice == 6:
            text = 'Omit 4.2 (Power & Speed)'
        sheet.merge_range('C7:D7',text,self.border)                                            


        sheet.merge_range('A1:D1','Regression', self.merge)
        for Type, letter in zip(TypeList, Letters):
            for result, index2 in zip(ResultsList, range(1,len(ResultsList)+1)):
                if Regression_bool[Type][result] == True:
                    sheet.write(letter+str(index2+2),Regression[Type][result],self.green)
                    sheet.write('A'+str(index2+2),result,self.bright_grey)
                else:
                    sheet.write(letter+str(index2+2),Regression[Type][result],self.red)
                    sheet.write('A'+str(index2+2),result,self.bright_grey)

        import ipdb
        ipdb.set_trace()
        sheet.merge_range('A10:C10','Data Alignment', self.merge)
        Species = ['CO2','CO','NOx','THC','NMHC']
        sheet.write_row('A11:C11',['Species','Units','Delay'],self.dark_grey)
        sheet.write_column('A12',Species,self.bright_grey)
        sheet.write_column('B12',['seconds','seconds','seconds','seconds','seconds',],self.bright_grey)
        #for spec, index in DelayArray
        sheet.write('C12',5,self.border)
        sheet.write('C13',4,self.border)
        sheet.write('C14',8,self.border)
        sheet.write('C15',7,self.border)
        sheet.write('C16',3,self.border)


        ZeroSpan = pd.read_json(ZeroSpan)
        Species = ZeroSpan.columns.values
        Letters = ['C','D','E','F','G']
        TypeList = ['Chosen','PreZero','PostZero','PreSpan','PostSpan']
        sheet.merge_range('A19:G19','Zero/Span - Table', self.merge)
        sheet.write('A20','Species',self.dark_grey)
        sheet.write('B20','Units',self.dark_grey)
        sheet.write_row('C20:G20',TypeList,self.dark_grey)
        for Type, letter in zip(TypeList, Letters):
            for spec, index in zip(Species,range(1,len(Species)+1)):
                if ZeroSpan[spec][Type] > 100:
                    sheet.write('B'+str(index+20),'ppm',self.bright_grey)
                else:
                    sheet.write('B'+str(index+20),'%',self.bright_grey)
                sheet.write(letter+str(index+20), np.round(ZeroSpan[spec][Type],2),self.border)
                sheet.write('A'+str(index+20), spec,self.bright_grey)

    def _write_dataframe(self, Sheet, Data):

        for i in range(0,len(Data.columns)):
            Sheet.write(0,i,Data.columns[i])
            Sheet.write_column(1,i,Data[Data.columns[i]])

        return Sheet

