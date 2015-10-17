#import sys
#sys.path.append("/home/mpet/Aaron/TitanMidasScripts/pythonmidas/")

import pythonmidas.pythonmidas as Midas
import pkg_resources
import re


class calcFreq():
    def __init__(self):
        #self.data = loadtxt("/home/mpet/Aaron/TitanMidasScripts/" +
        #               "ElectronBindingData/NUBASE2012_formatted.dat",
        #               usecols=[2, 3], dtype=object)
        #f = open("/home/mpet/Aaron/TitanMidasScripts/" +
        #         "ElectronBindingData/NUBASE2012_formatted.dat")
        #f = open("data/NUBASE2012_formatted.dat")
        f = pkg_resources.resource_string(__name__,
                                          'data/NUBASE2012_formatted.dat')
        self.data = []
        #for line in f:
        for line in f[:-1].split('\n'):
            temp = line.split()
            self.data.append([temp[2], float(temp[3])])
        #f.close()

        #f = open("/home/mpet/Aaron/TitanMidasScripts/" +
        #         "ElectronBindingData/ElectronBindingEnergies.dat")
        #f = open("data/ElectronBindingEnergies.dat")
        f = pkg_resources.resource_string(__name__,
                                          'data/ElectronBindingEnergies.dat')
        self.electronBE = []
        #for line in f:
        for line in f[:-1].split('\n'):
            self.electronBE.append(map(float, line.split()))
        #f.close()

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

    def BE(self, Z, q):
        #result = sum(self.electronBE[Z-1, 0:q-1])/1000.
        Z = int(Z)
        q = int(q)
        result = sum(self.electronBE[Z - 1][:q]) / 1000.
        return result

    def splitInput(self, name):
        result = name.split(":")
        return result

    def getAtomicMass(self, name):
        # Get mass excess
        elem = re.findall('\\d+', name)[1] + re.search('\\D+', name).group(0)
        #ME = float(self.data[self.data[:, 0]==elem][0, 1])
        for tempelem in self.data:
            if tempelem[0] == elem:
                ME = tempelem[1]
                break

        # Get mass number
        A = float(re.findall('\\d+', name)[1])

        return (A * self.amu + ME)

    def getIonicMass(self, name, q):
        names = self.splitInput(name)
        #elemList = hstack(([re.findall('\\d+', x) for x in names],
        #                   [re.findall('\\D+', x) for x in names]))
        temp1 = [re.findall('\\d+', x) for x in names]
        temp2 = [re.findall('\\D+', x) for x in names]
        elemList = []
        for i in range(len(temp1)):
            elemList.append([temp1[i][0], temp1[i][1], temp2[i][0]])

        mass = [float(x[0]) * self.getAtomicMass(x[0] + x[2] + x[1])
                for x in elemList]
        mass = sum(mass) - self.me * q

        # Correct for the binding energy.
        # If ion is a molecule, perform no correction
        if len(elemList) > 1 or q < 1 or (len(elemList) == 2
                                          and elemList[0] > 1):
            return mass
        else:
            return mass + self.BE(self.elemDict[elemList[0][2]], q)

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
