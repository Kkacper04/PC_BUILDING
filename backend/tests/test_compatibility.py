
import pytest
from app.logic.compatibility import CompatibilityChecker
from app.models.components import CPU, Motherboard, RAM, GPU, Case, PSU, CPUCooler
from app.models.enums import (
    SocketType, DDRGeneration, PSUFormFactor, FormFactor, CoolerType
)


@pytest.fixture
def checker():
    return CompatibilityChecker()



class TestCpuMotherboard:
    def test_matching_socket(self, checker):
        cpu = CPU(socket=SocketType.AM5, tdp=105, cores=8, threads=16,
                  base_clock_mhz=4000, boost_clock_mhz=5000)
        mobo = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5)

        assert checker.check_cpu_motherboard(cpu, mobo) is True
        assert len(checker.errors) == 0

    def test_mismatched_socket(self, checker):
        cpu = CPU(socket=SocketType.AM5, tdp=105, cores=8, threads=16,
                  base_clock_mhz=4000, boost_clock_mhz=5000)
        mobo = Motherboard(socket=SocketType.LGA1700, ddr_generation=DDRGeneration.DDR5)

        assert checker.check_cpu_motherboard(cpu, mobo) is False
        assert len(checker.errors) == 1
        assert "socket" in checker.errors[0].lower()


class TestRamMotherboard:
    def test_matching_ddr(self, checker):
        ram = RAM(ddr_generation=DDRGeneration.DDR5, modules=2, speed_mhz=6000)
        mobo = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5,
                           ram_slots=4, max_ram_speed_mhz=6400)

        assert checker.check_ram_motherboard(ram, mobo) is True
        assert len(checker.errors) == 0

    def test_mismatched_ddr(self, checker):
        ram = RAM(ddr_generation=DDRGeneration.DDR4, modules=2, speed_mhz=3200)
        mobo = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5,
                           ram_slots=4, max_ram_speed_mhz=6400)

        assert checker.check_ram_motherboard(ram, mobo) is False
        assert "generation" in checker.errors[0].lower()

    def test_too_many_modules(self, checker):
        ram = RAM(ddr_generation=DDRGeneration.DDR5, modules=4, speed_mhz=5600)
        mobo = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5,
                           ram_slots=2, max_ram_speed_mhz=6400)

        assert checker.check_ram_motherboard(ram, mobo) is False
        assert "slots" in checker.errors[0].lower()

    def test_speed_warning(self, checker):
        ram = RAM(ddr_generation=DDRGeneration.DDR5, modules=2, speed_mhz=7200)
        mobo = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5,
                           ram_slots=4, max_ram_speed_mhz=5600)

        assert checker.check_ram_motherboard(ram, mobo) is True  # not an error
        assert len(checker.warnings) == 1
        assert "downclocked" in checker.warnings[0].lower()

class TestGpuCase:
    def test_gpu_fits(self, checker):
        gpu = GPU(length_mm=280, tdp=250, vram_gb=8,
                  base_clock_mhz=1500, boost_clock_mhz=1700)
        case = Case(max_gpu_length_mm=340, max_cpu_cooler_height_mm=160,
                    psu_form_factor=PSUFormFactor.ATX, case_type="Midi Tower")

        assert checker.check_gpu_case(gpu, case) is True

    def test_gpu_too_long(self, checker):
        gpu = GPU(length_mm=360, tdp=250, vram_gb=8,
                  base_clock_mhz=1500, boost_clock_mhz=1700)
        case = Case(max_gpu_length_mm=300, max_cpu_cooler_height_mm=160,
                    psu_form_factor=PSUFormFactor.ATX, case_type="Midi Tower")

        assert checker.check_gpu_case(gpu, case) is False
        assert "exceeds" in checker.errors[0].lower()


class TestPowerSupply:
    def test_sufficient_psu(self, checker):
        cpu = CPU(socket=SocketType.AM5, tdp=105, cores=8, threads=16,
                  base_clock_mhz=4000, boost_clock_mhz=5000)
        gpu = GPU(tdp=320, length_mm=300, vram_gb=12,
                  base_clock_mhz=1500, boost_clock_mhz=1700)
        psu = PSU(wattage=850, form_factor=PSUFormFactor.ATX)

        assert checker.check_power_supply(cpu, gpu, psu) is True
        assert len(checker.errors) == 0
        assert len(checker.warnings) == 0

    def test_insufficient_psu(self, checker):
        cpu = CPU(socket=SocketType.AM5, tdp=105, cores=8, threads=16,
                  base_clock_mhz=4000, boost_clock_mhz=5000)
        gpu = GPU(tdp=320, length_mm=300, vram_gb=12,
                  base_clock_mhz=1500, boost_clock_mhz=1700)
        psu = PSU(wattage=450, form_factor=PSUFormFactor.ATX)

        assert checker.check_power_supply(cpu, gpu, psu) is False
        assert "insufficient" in checker.errors[0].lower()

    def test_tight_margin_warning(self, checker):
        cpu = CPU(socket=SocketType.AM5, tdp=105, cores=8, threads=16,
                  base_clock_mhz=4000, boost_clock_mhz=5000)
        gpu = GPU(tdp=320, length_mm=300, vram_gb=12,
                  base_clock_mhz=1500, boost_clock_mhz=1700)
        # consumption = 105 + 320 + 100 = 525W, margin = 25W < 50W
        psu = PSU(wattage=550, form_factor=PSUFormFactor.ATX)

        assert checker.check_power_supply(cpu, gpu, psu) is True
        assert len(checker.warnings) == 1
        assert "very close" in checker.warnings[0].lower()



class TestMoboCase:
    def test_atx_in_mid_tower(self, checker):
        mobo = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5,
                           form_factor=FormFactor.ATX)
        case = Case(case_type="Midi Tower", max_gpu_length_mm=340,
                    max_cpu_cooler_height_mm=160, psu_form_factor=PSUFormFactor.ATX)

        assert checker.check_mobo_case(mobo, case) is True

    def test_atx_in_mini_itx_case(self, checker):
        mobo = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5,
                           form_factor=FormFactor.ATX)
        case = Case(case_type="Mini Tower", max_gpu_length_mm=300,
                    max_cpu_cooler_height_mm=130, psu_form_factor=PSUFormFactor.SFX)

        assert checker.check_mobo_case(mobo, case) is False
        assert "too large" in checker.errors[0].lower()


class TestCoolerCase:
    def test_cooler_fits(self, checker):
        cooler = CPUCooler(cooler_type=CoolerType.AIR, height_mm=155, max_tdp=220)
        case = Case(case_type="Midi Tower", max_gpu_length_mm=340,
                    max_cpu_cooler_height_mm=165, psu_form_factor=PSUFormFactor.ATX)

        assert checker.check_cooler_case(cooler, case) is True

    def test_cooler_too_tall(self, checker):
        cooler = CPUCooler(cooler_type=CoolerType.AIR, height_mm=170, max_tdp=220)
        case = Case(case_type="Midi Tower", max_gpu_length_mm=340,
                    max_cpu_cooler_height_mm=155, psu_form_factor=PSUFormFactor.ATX)

        assert checker.check_cooler_case(cooler, case) is False
        assert "cooler height" in checker.errors[0].lower()


class TestPsuCase:
    def test_matching_psu_form_factor(self, checker):
        psu = PSU(wattage=750, form_factor=PSUFormFactor.ATX)
        case = Case(case_type="Midi Tower", max_gpu_length_mm=340,
                    max_cpu_cooler_height_mm=165, psu_form_factor=PSUFormFactor.ATX)

        assert checker.check_psu_case(psu, case) is True

    def test_atx_psu_in_sfx_case(self, checker):
        psu = PSU(wattage=750, form_factor=PSUFormFactor.ATX)
        case = Case(case_type="Mini Tower", max_gpu_length_mm=300,
                    max_cpu_cooler_height_mm=130, psu_form_factor=PSUFormFactor.SFX)

        assert checker.check_psu_case(psu, case) is False
        assert "psu form factor" in checker.errors[0].lower()


class TestGpuPsuConnectors:
    def test_gpu_needs_12vhpwr_psu_has_it(self, checker):
        gpu = GPU(tdp=350, length_mm=320, vram_gb=16,
                  base_clock_mhz=2000, boost_clock_mhz=2500,
                  pcie_power_12vhpwr=1, pcie_power_8pin=0)
        psu = PSU(wattage=850, form_factor=PSUFormFactor.ATX,
                  has_12vhpwr=True, num_12vhpwr=1)

        assert checker.check_gpu_psu_connectors(gpu, psu) is True

    def test_gpu_needs_12vhpwr_psu_missing(self, checker):
        gpu = GPU(tdp=350, length_mm=320, vram_gb=16,
                  base_clock_mhz=2000, boost_clock_mhz=2500,
                  pcie_power_12vhpwr=1, pcie_power_8pin=0)
        psu = PSU(wattage=850, form_factor=PSUFormFactor.ATX,
                  has_12vhpwr=False, num_12vhpwr=0)

        assert checker.check_gpu_psu_connectors(gpu, psu) is False
        assert "12vhpwr" in checker.errors[0].lower()


class TestValidateBuild:
    def test_fully_compatible_build(self, checker):
        cpu = CPU(socket=SocketType.AM5, tdp=105, cores=8, threads=16,
                  base_clock_mhz=4000, boost_clock_mhz=5000)
        mobo = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5,
                           form_factor=FormFactor.ATX, ram_slots=4, max_ram_speed_mhz=6400)
        ram = RAM(ddr_generation=DDRGeneration.DDR5, modules=2, speed_mhz=6000)
        gpu = GPU(tdp=250, length_mm=310, vram_gb=12,
                  base_clock_mhz=1800, boost_clock_mhz=2300,
                  pcie_power_8pin=2, pcie_power_12vhpwr=0)
        case = Case(case_type="Midi Tower", max_gpu_length_mm=340,
                    max_cpu_cooler_height_mm=165, psu_form_factor=PSUFormFactor.ATX)
        psu = PSU(wattage=750, form_factor=PSUFormFactor.ATX,
                  pcie_8pin_connectors=4, has_12vhpwr=False, num_12vhpwr=0)

        result = checker.validate_build(cpu, mobo, ram, gpu, case, psu)

        assert result["is_compatible"] is True
        assert len(result["errors"]) == 0

    def test_incompatible_build_multiple_errors(self, checker):
        cpu = CPU(socket=SocketType.AM5, tdp=170, cores=16, threads=32,
                  base_clock_mhz=4200, boost_clock_mhz=5700)
        mobo = Motherboard(socket=SocketType.LGA1700, ddr_generation=DDRGeneration.DDR4,
                           form_factor=FormFactor.ATX, ram_slots=4, max_ram_speed_mhz=3200)
        ram = RAM(ddr_generation=DDRGeneration.DDR5, modules=2, speed_mhz=6000)
        gpu = GPU(tdp=350, length_mm=360, vram_gb=24,
                  base_clock_mhz=2000, boost_clock_mhz=2600,
                  pcie_power_12vhpwr=1, pcie_power_8pin=0)
        case = Case(case_type="Mini Tower", max_gpu_length_mm=300,
                    max_cpu_cooler_height_mm=130, psu_form_factor=PSUFormFactor.SFX)
        psu = PSU(wattage=500, form_factor=PSUFormFactor.ATX,
                  pcie_8pin_connectors=2, has_12vhpwr=False, num_12vhpwr=0)

        result = checker.validate_build(cpu, mobo, ram, gpu, case, psu)

        assert result["is_compatible"] is False
        # Should have multiple errors: socket, DDR, GPU length, PSU wattage,
        # mobo form factor, PSU form factor, GPU 12VHPWR connector
        assert len(result["errors"]) >= 5
