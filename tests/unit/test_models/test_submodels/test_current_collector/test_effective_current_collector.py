#
# Tests for the Effective Current Collector Resistance models
#
import pybamm
import unittest
import numpy as np


class TestEffectiveResistance1D(unittest.TestCase):
    def test_well_posed(self):
        model = pybamm.current_collector.EffectiveResistance1D()
        model.check_well_posedness()

    def test_default_geometry(self):
        model = pybamm.current_collector.EffectiveResistance1D()
        self.assertIsInstance(model.default_geometry, pybamm.Geometry)
        self.assertTrue("current collector" in model.default_geometry)
        self.assertNotIn("negative electrode", model.default_geometry)

    def test_default_solver(self):
        model = pybamm.current_collector.EffectiveResistance1D()
        self.assertIsInstance(model.default_solver, pybamm.CasadiAlgebraicSolver)


class TestEffectiveResistance2D(unittest.TestCase):
    def test_well_posed(self):
        model = pybamm.current_collector.EffectiveResistance2D()
        model.check_well_posedness()

    def test_default_geometry(self):
        model = pybamm.current_collector.EffectiveResistance2D()
        self.assertIsInstance(model.default_geometry, pybamm.Geometry)
        self.assertTrue("current collector" in model.default_geometry)
        self.assertNotIn("negative electrode", model.default_geometry)

    def test_default_solver(self):
        model = pybamm.current_collector.EffectiveResistance2D()
        self.assertIsInstance(model.default_solver, pybamm.CasadiAlgebraicSolver)


class TestAlternativeEffectiveResistance2D(unittest.TestCase):
    def test_well_posed(self):
        model = pybamm.current_collector.AlternativeEffectiveResistance2D()
        model.check_well_posedness()

    def test_default_geometry(self):
        model = pybamm.current_collector.AlternativeEffectiveResistance2D()
        self.assertIsInstance(model.default_geometry, pybamm.Geometry)
        self.assertTrue("current collector" in model.default_geometry)
        self.assertNotIn("negative electrode", model.default_geometry)

    def test_default_solver(self):
        model = pybamm.current_collector.AlternativeEffectiveResistance2D()
        self.assertIsInstance(model.default_solver, pybamm.CasadiAlgebraicSolver)


class TestEffectiveResistancePotentials(unittest.TestCase):
    def test_get_processed_potentials(self):
        # solve cheap SPM to test processed potentials (think of an alternative test?)
        models = [
            pybamm.lithium_ion.SPM(),
            pybamm.current_collector.EffectiveResistance1D(),
            # pybamm.current_collector.EffectiveResistance2D(),
            # pybamm.current_collector.AlternativeEffectiveResistance2D(),
        ]
        var = pybamm.standard_spatial_vars
        var_pts = {
            var.x_n: 5,
            var.x_s: 5,
            var.x_p: 5,
            var.r_n: 5,
            var.r_p: 5,
            var.y: 5,
            var.z: 5,
        }
        param = models[0].default_parameter_values
        meshes = [None] * len(models)
        for i, model in enumerate(models):
            param.process_model(model)
            geometry = model.default_geometry
            param.process_geometry(geometry)
            meshes[i] = pybamm.Mesh(geometry, model.default_submesh_types, var_pts)
            disc = pybamm.Discretisation(meshes[i], model.default_spatial_methods)
            disc.process_model(model)
        t_eval = np.linspace(0, 100, 10)
        solution_1D = models[0].default_solver.solve(models[0], t_eval)
        # Process SPM V and I
        V = solution_1D["Terminal voltage"]
        I = solution_1D["Total current density"]

        # Test potential can be constructed and evaluated without raising error
        # for each current collector model
        for model in models[1:]:
            solution = model.default_solver.solve(model)
            potentials = model.get_processed_potentials(solution, param, V, I)
            pts = np.array([0.1, 0.5, 0.9])
            for var, processed_var in potentials.items():
                if isinstance(model, pybamm.current_collector.EffectiveResistance1D):
                    processed_var(t=solution_1D.t[5], z=pts)
                else:
                    processed_var(t=solution_1D.t[5], y=pts, z=pts)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    pybamm.settings.debug_mode = True
    unittest.main()
