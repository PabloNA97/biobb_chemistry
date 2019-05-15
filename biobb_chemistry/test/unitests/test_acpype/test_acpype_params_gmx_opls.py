from biobb_common.tools import test_fixtures as fx
from biobb_chemistry.acpype.acpype_params_gmx_opls import AcpypeParamsGMXOPLS


class TestAcpypeParamsGMXOPLS():
    def setUp(self):
        fx.test_setup(self,'acpype_params_gmx_opls')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_params_gmx_opls(self):
        AcpypeParamsGMXOPLS(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_path_itp'])
        assert fx.not_empty(self.paths['output_path_top'])
        assert fx.equal(self.paths['output_path_itp'], self.paths['ref_output_acpype_path_itp'])
        assert fx.equal(self.paths['output_path_top'], self.paths['ref_output_acpype_path_top'])