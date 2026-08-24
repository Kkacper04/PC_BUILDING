import pytest
from app.logic.compatibility import CompatibilityChecker
from app.models.components import CPU, Motherboard, RAM, GPU, Case, PSU
from app.models.enums import SocketType, DDRGeneration, PSUFormFactor

@pytest.fixture
def checker():
    return CompatibilityChecker()

def test_cpu_motherboard_compatibility(checker):
    # GIVEN
    cpu_am5 = CPU(socket=SocketType.AM5, tdp=105, cores=8, threads=16, base_clock_mhz=4000, boost_clock_mhz=5000)
    mobo_am5 = Motherboard(socket=SocketType.AM5, ddr_generation=DDRGeneration.DDR5)
    mobo_lga1700 = Motherboard(socket=SocketType.LGA1700, ddr_generation=DDRGeneration.DDR5)

    # WHEN & THEN
    assert checker.check_cpu_motherboard(cpu_am5, mobo_am5) == True
    assert len(checker.errors) == 0

    # WHEN & THEN
    assert checker.check_cpu_motherboard(cpu_am5, mobo_lga1700) == False
    assert len(checker.errors) == 1
    assert "socket" in checker.errors[0].lower()

def test_gpu_case_clearance(checker):
    # GIVEN
    gpu = GPU(length_mm=320, tdp=250, vram_gb=8, base_clock_mhz=1500, boost_clock_mhz=1700)
    pc_case = Case(max_gpu_length_mm=300, psu_form_factor=PSUFormFactor.ATX)

    # WHEN
    result = checker.check_gpu_case(gpu, pc_case)

    # THEN
    assert result == False
    assert len(checker.errors) == 1
    assert "exceeds case maximum clearance" in checker.errors[0].lower()

def test_power_supply_wattage(checker):
    # GIVEN
    cpu = CPU(tdp=105, socket=SocketType.AM5, cores=8, threads=16, base_clock_mhz=4000, boost_clock_mhz=5000)
    gpu = GPU(tdp=320, length_mm=300, vram_gb=8, base_clock_mhz=1500, boost_clock_mhz=1700)
    
    psu_weak = PSU(wattage=500, form_factor=PSUFormFactor.ATX)
    psu_strong = PSU(wattage=850, form_factor=PSUFormFactor.ATX)
    psu_tight = PSU(wattage=550, form_factor=PSUFormFactor.ATX)

    # too week power suply
    assert checker.check_power_supply(cpu, gpu, psu_weak) == False
    assert len(checker.errors) == 1

    checker.errors.clear()

    # strong ps
    assert checker.check_power_supply(cpu, gpu, psu_strong) == True
    assert len(checker.errors) == 0
    assert len(checker.warnings) == 0

    # ps: required 525W, delivered ma 550W -> margin < 50W
    assert checker.check_power_supply(cpu, gpu, psu_tight) == True
    assert len(checker.warnings) == 1
    assert "very close" in checker.warnings[0].lower()
