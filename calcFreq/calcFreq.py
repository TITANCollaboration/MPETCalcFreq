#import sys
#sys.path.append("/home/mpet/Aaron/TitanMidasScripts/pythonmidas/")

import pythonmidas.pythonmidas as Midas
import pkg_resources
import re
import math


class calcFreq():
    def __init__(self):
        ### Load the Mass Excess Data
        f = pkg_resources.resource_string(__name__,
                                          'data/NUBASE2012_formatted.dat')

        # Take the 3rd and 4th columns were the 3rd coumn is the element name
        # and the 4th column is the mass excess in keV.
        self.data = []
        for line in f[:-1].split('\n'):
            temp = line.split()
            self.data.append([temp[2], float(temp[3]), float(temp[4])])

        ### Load the electron binding energies
        f = pkg_resources.resource_string(__name__,
                                          'data/ElectronBindingEnergies.dat')
        self.electronBE = []
        for line in f[:-1].split('\n'):
            self.electronBE.append(map(float, line.split()))

        self.elemDict = {'H': 1,
                         'He': 2,
                         'Li': 3,
                         'Be': 4,
                         'B': 5,
                         'C': 6,
                         'N': 7,
                         'O': 8,
                         'F': 9,
                         'Ne': 10,
                         'Na': 11,
                         'Mg': 12,
                         'Al': 13,
                         'Si': 14,
                         'P': 15,
                         'S': 16,
                         'Cl': 17,
                         'Ar': 18,
                         'K': 19,
                         'Ca': 20,
                         'Sc': 21,
                         'Ti': 22,
                         'V': 23,
                         'Cr': 24,
                         'Mn': 25,
                         'Fe': 26,
                         'Co': 27,
                         'Ni': 28,
                         'Cu': 29,
                         'Zn': 30,
                         'Ga': 31,
                         'Ge': 32,
                         'As': 33,
                         'Se': 34,
                         'Br': 35,
                         'Kr': 36,
                         'Rb': 37,
                         'Sr': 38,
                         'Y': 39,
                         'Zr': 40,
                         'Nb': 41,
                         'Mo': 42,
                         'Tc': 43,
                         'Ru': 44,
                         'Rh': 45,
                         'Pd': 46,
                         'Ag': 47,
                         'Cd': 48,
                         'In': 49,
                         'Sn': 50,
                         'Sb': 51,
                         'Te': 52,
                         'I': 53,
                         'Xe': 54,
                         'Cs': 55,
                         'Ba': 56,
                         'La': 57,
                         'Ce': 58,
                         'Pr': 59,
                         'Nd': 60,
                         'Pm': 61,
                         'Sm': 62,
                         'Eu': 63,
                         'Gd': 64,
                         'Tb': 65,
                         'Dy': 66,
                         'Ho': 67,
                         'Er': 68,
                         'Tm': 69,
                         'Yb': 70,
                         'Lu': 71,
                         'Hf': 72,
                         'Ta': 73,
                         'W': 74,
                         'Re': 75,
                         'Os': 76,
                         'Ir': 77,
                         'Pt': 78,
                         'Au': 79,
                         'Hg': 80,
                         'Tl': 81,
                         'Pb': 82,
                         'Bi': 83,
                         'Po': 84,
                         'At': 85,
                         'Rn': 86,
                         'Fr': 87,
                         'Ra': 88,
                         'Ac': 89,
                         'Th': 90,
                         'Pa': 91,
                         'U': 92,
                         'Np': 93,
                         'Pu': 94,
                         'Am': 95,
                         'Cm': 96,
                         'Bk': 97,
                         'Cf': 98,
                         'Es': 99,
                         'Fm': 100,
                         'Md': 101,
                         'No': 102,
                         'Lr': 103,
                         'Rf': 104,
                         'Db': 105,
                         'Sg': 106,
                         'Bh': 107,
                         'Hs': 108,
                         'Mt': 109,
                         'Ds': 110,
                         'Rg': 111,
                         'Cp': 112,
                         'Uut': 113,
                         'Uuq': 114,
                         'Uup': 115,
                         'Uuh': 116,
                         'Uus': 117,
                         'Uuo': 118,
                         }

        self.me = 510.998928
        self.amu = 931494.061

    def getReference(self):
        '''Get the RF calibration from the ODB'''

        self.refname = Midas.varget("/Experiment/Variables/" +
                                    "MPET RF Calibration/Reference Ion")
        self.reffreq = float(Midas.varget("/Experiment/Variables/" +
                                          "MPET RF Calibration/" +
                                          "Reference Frequency"))
        self.refcharge = float(Midas.varget("/Experiment/Variables/" +
                                            "MPET RF Calibration/" +
                                            "Reference Charge"))
        self.refmagnetron = float(Midas.varget("/Experiment/Variables/" +
                                               "MPET RF Calibration/" +
                                               "FreqMinus (Hz)"))
        try:
            self.reffreqerr = float(Midas.varget("/Experiment/Variables/" +
                                                 "MPET RF Calibration/" +
                                                 "Reference Frequency Error"))
        except:
            self.reffreqerr = 0.0

    def BE(self, Z, q):
        '''Sum the electron binding energies from neutral to the charge
        state of the ion.'''
        Z = int(Z)
        q = int(q)
        result = sum(self.electronBE[Z - 1][:q]) / 1000.
        return result

    def splitInput(self, name):
        '''Split the given string on any colons present.'''
        result = name.split(":")
        return result

    def getAtomicMass(self, name):
        '''Get mass excess of the given element in the standard eva format'''

        # The first regex gets the A of the species, the second finds the
        # element
        #elem = re.findall('\\d+', name)[1] + re.search('\\D+', name).group(0)
        elem = re.findall('\\d+', name)[1] + "".join(re.findall('\\D+', name))

        # Search the NUBASE data to find the element
        for tempelem in self.data:
            if tempelem[0] == elem:
                # If a match, get the mass excess and error
                ME = tempelem[1]
                MEerr = tempelem[2]
                break

        # Get mass number
        A = float(re.findall('\\d+', name)[1])

        return ((A * self.amu + ME), MEerr)

    def getIonicMass(self, name, q):
        '''Take a eva formated element name and charge q,
        and return the mass of the ion in keV.

        This also returns the ionic mass of isomers, if the
        isomer is listed in the AME.
        '''
        names = self.splitInput(name)

        temp1 = [re.findall('\\d+', x) for x in names]
        temp2 = [re.findall('\\D+', x) for x in names]

        elemList = []
        for i in range(len(temp1)):
            # If an isomer is present in the name, and if the element
            # name is 1 character (K, S, etc.), then prepend an 'x' to
            # the isomer label. Needed for NUBASE file lookup.
            # Otherwise, no isomer label is present, and append
            # an empty string.
            if len(temp2[i]) == 2 and len(temp2[i][0]) == 1:
                temp2[i][1] = "x" + temp2[i][1]
            if len(temp2[i]) == 1:
                temp2[i].append("")

            elemList.append([temp1[i][0], temp1[i][1],
                             temp2[i][0], temp2[i][1]])

        mass = [float(x[0]) * self.getAtomicMass(x[0] + x[2] + x[1] + x[3])[0]
                for x in elemList]
        print mass
        mass = sum(mass) - self.me * q
        print mass

        # Correct for the binding energy.
        # If ion is a molecule, perform no correction
        if len(elemList) > 1 or q < 1 or (len(elemList) == 2
                                          and elemList[0] > 1):
            return mass
        else:
            return mass + self.BE(self.elemDict[elemList[0][2]], q)

    def getIonicMassErr(self, name, q):
        '''Take a eva formated element name and charge q,
        and return the mass of the ion in keV.

        This also returns the ionic mass of isomers, if the
        isomer is listed in the AME.
        '''
        names = self.splitInput(name)

        temp1 = [re.findall('\\d+', x) for x in names]
        temp2 = [re.findall('\\D+', x) for x in names]

        elemList = []
        for i in range(len(temp1)):
            # If an isomer is present in the name, and if the element
            # name is 1 character (K, S, etc.), then prepend an 'x' to
            # the isomer label. Needed for NUBASE file lookup.
            # Otherwise, no isomer label is present, and append
            # an empty string.
            if len(temp2[i]) == 2 and len(temp2[i][0]) == 1:
                temp2[i][1] = "x" + temp2[i][1]
            if len(temp2[i]) == 1:
                temp2[i].append("")

            elemList.append([temp1[i][0], temp1[i][1],
                             temp2[i][0], temp2[i][1]])

        mass = [float(x[0]) * self.getAtomicMass(x[0] + x[2] + x[1] + x[3])[1]
                for x in elemList]
        print mass
        mass = sum(mass)
        print mass

        return mass

    def getFreqErr(self, name, q):
        mass = self.getIonicMass(name, q)
        merr = self.getIonicMassErr(name, q)
        # freq = self.getFreqC(name, q)
        refmass = self.getIonicMass(self.refname, self.refcharge)
        rmerr = self.getIonicMassErr(self.refname, self.refcharge)

        parErrRef = (q * rmerr * self.reffreq / (self.refcharge * mass)) ** 2
        parErrInt = (q * refmass * merr * self.reffreq
                     / (self.refcharge * mass ** 2)) ** 2
        parErrFreq = (q * refmass * self.reffreqerr
                      / (self.refcharge * mass)) ** 2

        return math.sqrt(parErrRef + parErrInt + parErrFreq)

    def getFreqC(self, name, q):
        mass = self.getIonicMass(name, q)
        refmass = self.getIonicMass(self.refname, self.refcharge)
        return self.reffreq * (refmass / self.refcharge) * (q / mass)

    def getFreqP(self, name, q):
        freqc = self.getFreqC(name, q)
        return freqc - self.refmagnetron

    def dipole_frequencies(self, name):
        freqP = self.calc_frequency(name, self.getFreqP)
        return freqP

    def cyclotron_frequencies(self, name):
        freqC = self.calc_frequency(name, self.getFreqC)
        return freqC

    def calc_frequency(self, name, func):
        names = self.parseInput(name)
        freqs = map(lambda x: func(x[0], float(x[1])), names)
        return freqs

    def calc_freqerr(self, name):
        names = self.parseInput(name)
        freqerrs = map(lambda x: self.getFreqErr(x[0], float(x[1])), names)
        return freqerrs

    def parseInput(self, name):
        """
        Parse input from the CalcFreq MIDAS page.

        Expect a string with delimeters of ';' or ','.

        The string format is "ELEM1 q, ELEM2 q2, .....", where ELEM1 and ELEM2
        are in the standard eva format for single ions or molecules. The charge
        'q' can be written as a single integer (e.g. 1) or with the sign of the
        charge (e.g. '1+'). The '+' is replaced with an empty string.
        """
        names = name.replace('+', '')
        names = re.split(';|,', names)
        names = [x.lstrip().split() for x in names]
        return names
