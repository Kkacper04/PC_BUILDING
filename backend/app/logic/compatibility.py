from typing import Dict, Any, Optional
from app.models.components import CPU, Motherboard, RAM, GPU, Case, PSU, CPUCooler
from app.models.enums import FormFactor


# Form factor size hierarchy (larger index = physically larger board)
_FF_SIZE = {
    FormFactor.MINI_ITX: 0,
    FormFactor.MICRO_ATX: 1,
    FormFactor.ATX: 2,
    FormFactor.E_ATX: 3,
}


class CompatibilityChecker:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    
    # CPU socket must match Motherboard socket
    def check_cpu_motherboard(self, cpu: CPU, mobo: Motherboard) -> bool:
        if not cpu.socket or not mobo.socket:
            self.errors.append("Cannot verify CPU-Motherboard compatibility: missing socket data.")
            return False

        if cpu.socket == mobo.socket:
            return True
            
        cpu_sock = cpu.socket.value
        mobo_sock = mobo.socket.value
        self.errors.append(
            f"CPU socket ({cpu_sock}) does not match "
            f"Motherboard socket ({mobo_sock})."
        )
        return False


    # RAM generation & slot count must match Motherboard
    def check_ram_motherboard(self, ram: RAM, mobo: Motherboard) -> bool:
        is_compatible = True

        if not ram.ddr_generation or not mobo.ddr_generation:
            self.errors.append("Cannot verify RAM-Motherboard compatibility: missing DDR generation data.")
            is_compatible = False
        elif ram.ddr_generation != mobo.ddr_generation:
            ram_ddr = ram.ddr_generation.value
            mobo_ddr = mobo.ddr_generation.value
            self.errors.append(
                f"RAM generation ({ram_ddr}) does not match "
                f"Motherboard standard ({mobo_ddr})."
            )
            is_compatible = False

        if ram.modules and mobo.ram_slots and ram.modules > mobo.ram_slots:
            self.errors.append(
                f"RAM has {ram.modules} modules, but the motherboard "
                f"only has {mobo.ram_slots} slots."
            )
            is_compatible = False

        if ram.speed_mhz and mobo.max_ram_speed_mhz and ram.speed_mhz > mobo.max_ram_speed_mhz:
            self.warnings.append(
                f"RAM speed ({ram.speed_mhz} MHz) exceeds Motherboard max "
                f"supported speed ({mobo.max_ram_speed_mhz} MHz). "
                f"RAM will be downclocked."
            )

        return is_compatible

    
    # GPU must physically fit inside the Case
    def check_gpu_case(self, gpu: GPU, pc_case: Case) -> bool:
        if gpu.length_mm <= pc_case.max_gpu_length_mm:
            return True
        self.errors.append(
            f"GPU length ({gpu.length_mm} mm) exceeds Case maximum "
            f"clearance ({pc_case.max_gpu_length_mm} mm)."
        )
        return False

   
    # PSU must supply enough wattage
    def check_power_supply(self, cpu: CPU, gpu: GPU, psu: PSU) -> bool:
        if not cpu.tdp or not gpu.tdp or not psu.wattage:
            self.errors.append("Cannot verify Power Supply: missing TDP or wattage data.")
            return False
            
        # Pylance workaround for SQLAlchemy Optional ints
        c_tdp: int = cpu.tdp
        g_tdp: int = gpu.tdp
        p_watt: int = psu.wattage
            
        consumption = c_tdp + g_tdp + 100  # +100W overhead

        if p_watt >= consumption:
            if p_watt - consumption < 50:
                self.warnings.append(
                    f"PSU wattage ({p_watt}W) is very close to the "
                    f"estimated consumption ({consumption}W). "
                    f"Consider a higher-wattage unit."
                )
            return True
            
        self.errors.append(
            f"PSU wattage ({p_watt}W) is insufficient for estimated "
            f"consumption ({consumption}W)."
        )
        return False

   
    # Motherboard form factor must fit inside the Case
    def check_mobo_case(self, mobo: Motherboard, pc_case: Case) -> bool:
        if not mobo.form_factor:
            self.errors.append("Cannot verify Motherboard-Case compatibility: missing Form Factor data.")
            return False

        ff = mobo.form_factor
        assert ff is not None
        
        # Jeśli obudowa ma zdefiniowaną precyzyjną relację w bazie
        if pc_case.supported_form_factors:
            supported = [supp.form_factor for supp in pc_case.supported_form_factors]
            if ff in supported:
                return True
            else:
                self.errors.append(
                    f"Motherboard form factor ({ff.value}) is not officially supported "
                    f"by this case (Supports: {[s.value for s in supported]})."
                )
                return False

        # Fallback logic jeśli baza jeszcze nie ma wypełnionych relacji
        case_type_upper = (pc_case.case_type or "").upper()
        if "FULL" in case_type_upper or "BIG" in case_type_upper:
            max_ff = FormFactor.E_ATX
        elif "MID" in case_type_upper:
            max_ff = FormFactor.ATX
        elif "MINI" in case_type_upper or "SFF" in case_type_upper or "ITX" in case_type_upper:
            max_ff = FormFactor.MINI_ITX
        elif "MICRO" in case_type_upper:
            max_ff = FormFactor.MICRO_ATX
        else:
            # Default: assume Mid Tower (ATX)
            max_ff = FormFactor.ATX

        mobo_size = _FF_SIZE.get(ff, 2)
        case_max_size = _FF_SIZE.get(max_ff, 2)

        if mobo_size <= case_max_size:
            return True
            
        ff_str = ff.value
        self.errors.append(
            f"Motherboard form factor ({ff_str}) is too large "
            f"for this case type ({pc_case.case_type})."
        )
        return False

    
    #CPU Cooler height must fit inside the Case
    def check_cooler_case(self, cooler: CPUCooler, pc_case: Case) -> bool:
        if cooler.height_mm is None or pc_case.max_cpu_cooler_height_mm is None:
            return True  # Cannot validate without dimensions
        if cooler.height_mm <= pc_case.max_cpu_cooler_height_mm:
            return True
        self.errors.append(
            f"CPU Cooler height ({cooler.height_mm} mm) exceeds Case maximum "
            f"clearance ({pc_case.max_cpu_cooler_height_mm} mm)."
        )
        return False

    # PSU form factor must match Case
    def check_psu_case(self, psu: PSU, pc_case: Case) -> bool:
        if psu.form_factor == pc_case.psu_form_factor:
            return True
        self.errors.append(
            f"PSU form factor ({psu.form_factor.value}) does not match "
            f"Case PSU bay ({pc_case.psu_form_factor.value})."
        )
        return False

    # GPU power connectors vs PSU available connectors
    def check_gpu_psu_connectors(self, gpu: GPU, psu: PSU) -> bool:
        is_compatible = True

        if gpu.pcie_power_12vhpwr and gpu.pcie_power_12vhpwr > 0:
            if not psu.has_12vhpwr or psu.num_12vhpwr < gpu.pcie_power_12vhpwr:
                self.errors.append(
                    f"GPU requires {gpu.pcie_power_12vhpwr} 12VHPWR connector(s), "
                    f"but PSU has {psu.num_12vhpwr}."
                )
                is_compatible = False

        if gpu.pcie_power_8pin and gpu.pcie_power_8pin > 0:
            if psu.pcie_8pin_connectors < gpu.pcie_power_8pin:
                self.errors.append(
                    f"GPU requires {gpu.pcie_power_8pin} PCIe 8-pin connector(s), "
                    f"but PSU only has {psu.pcie_8pin_connectors}."
                )
                is_compatible = False

        return is_compatible

    
    def validate_build(
        self,
        cpu: CPU,
        mobo: Motherboard,
        ram: RAM,
        gpu: GPU,
        pc_case: Case,
        psu: PSU,
        cooler: Optional[CPUCooler] = None,
    ) -> Dict[str, Any]:
        self.errors.clear()
        self.warnings.clear()

        self.check_cpu_motherboard(cpu, mobo)
        self.check_ram_motherboard(ram, mobo)
        self.check_gpu_case(gpu, pc_case)
        self.check_power_supply(cpu, gpu, psu)
        self.check_mobo_case(mobo, pc_case)
        self.check_psu_case(psu, pc_case)
        self.check_gpu_psu_connectors(gpu, psu)

        if cooler:
            self.check_cooler_case(cooler, pc_case)

        return {
            "is_compatible": len(self.errors) == 0,
            "errors": list(self.errors),       # return copies
            "warnings": list(self.warnings),   # to prevent mutation
        }
