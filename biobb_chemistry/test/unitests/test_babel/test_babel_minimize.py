from biobb_common.tools import test_fixtures as fx
from biobb_chemistry.babel.babel_minimize import BabelMinimize


class TestBabelMinimize():
    def setUp(self):
        fx.test_setup(self,'babel_minimize')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_minimize(self):
        BabelMinimize(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_path'])
        assert fx.equal(self.paths['output_path'], self.paths['ref_output_babel_path'])