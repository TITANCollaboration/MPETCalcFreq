import mock
from unittest import TestCase
import calcFreq.calcFreq as CF


@mock.patch('calcFreq.calcFreq.Midas')
class calcFreq_tests(TestCase):
    def test_init(self, mock_Midas):
        mycf = CF.calcFreq()

        self.assertEqual(len(mycf.elemDict), 118)

    def test_getReference(self, mock_Midas):
        mycf = CF.calcFreq()

        mock_Midas.varget.side_effect = ["ion1", "1000000", "1", "1000"]

        mycf.getReference()

        self.assertEqual(mock_Midas.varget.call_count, 4)
        self.assertEqual(mycf.refname, "ion1")
        self.assertEqual(mycf.reffreq, 1000000.0)
        self.assertEqual(mycf.refcharge, 1.0)
        self.assertEqual(mycf.refmagnetron, 1000.0)

    def test_BE(self, mock_Midas):
        mycf = CF.calcFreq()

        result = mycf.BE(1, 1)
        expected = 13.59844 / 1000.0

        self.assertEqual(result, expected)

        result = mycf.BE(2, 2)
        expected = (23.44309 + 54.41776) / 1000.0
        self.assertEqual(result, expected)

        result = mycf.BE(118, 3)
        expected = (5.89095 + 14.66149 + 25.79251) / 1000.0

        self.assertEqual(result, expected)

    def test_splitInput(self, mock_Midas):
        mycf = CF.calcFreq()
        name = "1H1:1H2"

        result = mycf.splitInput(name)
        expected = ["1H1", "1H2"]

        self.assertEqual(result, expected)

    def test_getAtomicMass(self, mock_Midas):
        mycf = CF.calcFreq()

        mycf.data = [["1H", 1000],
                     ["2H", 2000],
                     ["3H", 3000]]
        mycf.amu = 1.0

        result = mycf.getAtomicMass("1H1")
        expected = 1 * 1.0 + 1000.0

        self.assertEqual(result, expected)

        result = mycf.getAtomicMass("1H3")
        expected = 3 * 1.0 + 3000.0

        self.assertEqual(result, expected)

    def test_getIonicMass(self, mock_Midas):
        mycf = CF.calcFreq()
        mycf.me = 500.0
        mycf.getAtomicMass = mock.MagicMock(return_value=1000.0)
        mycf.BE = mock.MagicMock(return_value=1)

        result = mycf.getIonicMass("1H2", 1)
        expected = 1000.0 - 500.0 + 1

        self.assertEqual(result, expected)
        mycf.getAtomicMass.assert_called_once_with("1H2")
        mycf.BE.assert_called_once_with(1, 1)

        mycf.getAtomicMass.reset_mock()
        mycf.BE.reset_mock()
        mycf.getAtomicMass = mock.MagicMock(return_value=1000.0)
        mycf.BE = mock.MagicMock(return_value=1)

        result = mycf.getIonicMass("1H2:4C12", 1)
        expected = 5 * 1000.0 - 500.0

        self.assertEqual(result, expected)
        mycf.getAtomicMass.assert_has_calls([mock.call("1H2"),
                                             mock.call("4C12")])
        mycf.BE.assert_not_called()

        mycf.getAtomicMass.reset_mock()
        mycf.BE.reset_mock()
        mycf.getAtomicMass = mock.MagicMock(return_value=1000.0)
        mycf.BE = mock.MagicMock(return_value=1)

        result = mycf.getIonicMass("1Rb74", 20)
        expected = 1000.0 - 20 * 500.0 + 1

        self.assertEqual(result, expected)
        mycf.getAtomicMass.assert_called_once_with("1Rb74")
        mycf.BE.assert_called_once_with(37, 20)

    def test_getFreqC(self, mock_Midas):
        mycf = CF.calcFreq()
        mycf.getIonicMass = mock.MagicMock(return_value=1000.0)
        mycf.reffreq = 1000000.0
        mycf.refname = "1C12"
        mycf.refcharge = 1

        result = mycf.getFreqC("1H1", 1)
        expected = 1000000.0 * (1000.0 / 1) * (1 / 1000.0)

        self.assertEqual(result, expected)
        mycf.getIonicMass.assert_has_calls([mock.call("1H1", 1),
                                            mock.call("1C12", 1)])

    def test_getFreqP(self, mock_Midas):
        mycf = CF.calcFreq()
        mycf.getFreqC = mock.MagicMock(return_value=1000.0)
        mycf.refmagnetron = 10.0

        result = mycf.getFreqP("1C12", 1)
        expected = 1000.0 - 10.0

        self.assertEqual(result, expected)
        mycf.getFreqC.assert_called_once_with("1C12", 1)

    def test_dipole_frequencies(self, mock_Midas):
        mycf = CF.calcFreq()
        mycf.calc_frequency = mock.MagicMock(return_value=1.0)

        result = mycf.dipole_frequencies("1C12")
        expected = 1.0

        self.assertEqual(result, expected)
        mycf.calc_frequency.assert_called_once_with("1C12", mycf.getFreqP)

    def test_cyclotron_frequencies(self, mock_Midas):
        mycf = CF.calcFreq()
        mycf.calc_frequency = mock.MagicMock(return_value=1.0)

        result = mycf.cyclotron_frequencies("1C12")
        expected = 1.0

        self.assertEqual(result, expected)
        mycf.calc_frequency.assert_called_once_with("1C12", mycf.getFreqC)

    def test_calc_frequency(self, mock_Midas):
        mycf = CF.calcFreq()

        def myfunc(name, q):
            return q * 1.0

        result = mycf.calc_frequency("1H1 1, 1C12 2, 2C12:4H1 3", myfunc)
        expected = [1.0, 2.0, 3.0]

        self.assertEqual(result, expected)

    def test_parseInput(self, mock_Midas):
        mycf = CF.calcFreq()

        name = "1H1 1"
        result = mycf.parseInput(name)
        expected = [["1H1", "1"]]

        self.assertEqual(result, expected)

        name = "1H1 1, 1C12 2+     ,     1Ca40 10; 1C12:1O16 1, 1H2 1"
        result = mycf.parseInput(name)
        expected = [["1H1", "1"], ["1C12", "2"], ["1Ca40", "10"],
                    ["1C12:1O16", "1"], ["1H2", "1"]]

        self.assertEqual(result, expected)
