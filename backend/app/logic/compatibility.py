from typing import Dict, Any, Optional
from app.models.components import CPU, Motherboard, RAM, GPU, Case, PSU, CPUCooler, Storage
from app.models.enums import FormFactor, StorageFormFactor


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
    def check_power_supply(self, cpu: CPU, gpu: Optional[GPU], psu: PSU) -> bool:
        if not cpu.tdp or not psu.wattage:
            self.errors.append("Cannot verify Power Supply: missing TDP or wattage data.")
            return False
        
        c_tdp: int = cpu.tdp
        p_watt: int = psu.wattage
        
        # GPU TDP: use actual TDP, fall back to recommended_psu_wattage * 0.4, or 0 for iGPU
        g_tdp: int = 0
        if gpu:
            if gpu.tdp:
                g_tdp = gpu.tdp
            elif gpu.recommended_psu_wattage:
                g_tdp = int(gpu.recommended_psu_wattage * 0.4)
                self.warnings.append(
                    f"GPU TDP unknown, estimating ~{g_tdp}W from recommended PSU wattage."
                )
            
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
        mobo_size = _FF_SIZE.get(ff, 2)
        
        # Use DB relation if available — with hierarchical check (smaller always fits)
        if pc_case.supported_form_factors:
            supported = [supp.form_factor for supp in pc_case.supported_form_factors]
            max_supported_size = max(_FF_SIZE.get(s, 0) for s in supported)
            if mobo_size <= max_supported_size:
                return True
            else:
                self.errors.append(
                    f"Motherboard form factor ({ff.value}) is too large "
                    f"for this case (max supported: {[s.value for s in supported]})."
                )
                return False

        # Fallback: guess from case_type string
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
            max_ff = FormFactor.ATX

        case_max_size = _FF_SIZE.get(max_ff, 2)

        if mobo_size <= case_max_size:
            return True
            
        self.errors.append(
            f"Motherboard form factor ({ff.value}) is too large "
            f"for this case type ({pc_case.case_type})."
        )
        return False

    
    # CPU Cooler clearance check — air cooler height OR AIO radiator size
    def check_cooler_case(self, cooler: CPUCooler, pc_case: Case) -> bool:
        is_compatible = True
        
        # Air cooler: check tower height
        if cooler.height_mm is not None and pc_case.max_cpu_cooler_height_mm is not None:
            if cooler.height_mm > pc_case.max_cpu_cooler_height_mm:
                self.errors.append(
                    f"CPU Cooler height ({cooler.height_mm} mm) exceeds Case maximum "
                    f"clearance ({pc_case.max_cpu_cooler_height_mm} mm)."
                )
                is_compatible = False
                
        # AIO: check radiator size vs case radiator support
        if cooler.radiator_size_mm is not None and pc_case.max_radiator_mm is not None:
            if cooler.radiator_size_mm > pc_case.max_radiator_mm:
                self.errors.append(
                    f"AIO radiator ({cooler.radiator_size_mm}mm) exceeds Case maximum "
                    f"radiator support ({pc_case.max_radiator_mm}mm)."
                )
                is_compatible = False
        elif cooler.radiator_size_mm is not None and pc_case.max_radiator_mm is None:
            self.warnings.append(
                "Case radiator support data is missing. Cannot verify AIO compatibility."
            )
                
        return is_compatible
    
    
    # CPU Cooler must support CPU socket and handle its TDP
    def check_cooler_cpu(self, cooler: CPUCooler, cpu: CPU) -> bool:
        is_compatible = True
        
        # Socket compatibility
        if cpu.socket and cooler.supported_sockets:
            supported = [s.socket for s in cooler.supported_sockets]
            if cpu.socket not in supported:
                socket_str = cpu.socket.value
                self.errors.append(
                    f"CPU Cooler does not support socket {socket_str}. "
                    f"Supported: {[s.value for s in supported]}."
                )
                is_compatible = False
        
        # TDP rating
        if cpu.tdp and cooler.max_tdp:
            if cpu.tdp > cooler.max_tdp:
                self.errors.append(
                    f"CPU TDP ({cpu.tdp}W) exceeds Cooler maximum rating ({cooler.max_tdp}W)."
                )
                is_compatible = False
            elif cpu.tdp > cooler.max_tdp * 0.9:
                self.warnings.append(
                    f"CPU TDP ({cpu.tdp}W) is very close to Cooler maximum ({cooler.max_tdp}W). "
                    f"May result in thermal throttling under sustained load."
                )
                
        return is_compatible


    # PSU form factor must match Case
    def check_psu_case(self, psu: PSU, pc_case: Case) -> bool:
        if psu.form_factor == pc_case.psu_form_factor:
            return True
        psu_ff = getattr(psu.form_factor, 'value', str(psu.form_factor))
        case_ff = getattr(pc_case.psu_form_factor, 'value', str(pc_case.psu_form_factor))
        self.errors.append(
            f"PSU form factor ({psu_ff}) does not match "
            f"Case PSU bay ({case_ff})."
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

    

    # 1. Missing Video Output Check
    def check_display_output(self, cpu: CPU, gpu: Optional[GPU]) -> bool:
        if gpu is not None:
            return True
        # If no GPU, CPU must have integrated graphics
        if cpu.integrated_graphics and cpu.integrated_graphics.lower() != "brak":
            return True
        
        self.errors.append(
            f"No video output! The selected CPU ({cpu.name}) does not have integrated graphics. "
            f"You must add a dedicated GPU, otherwise the PC will not display anything."
        )
        return False

    # 2. Storage vs Motherboard
    def check_storage_motherboard(self, storage: Storage, mobo: Motherboard) -> bool:
        is_compatible = True
        
        # Check M.2 NVMe vs Motherboard M.2 slots
        if storage.form_factor in [StorageFormFactor.M2_2280, StorageFormFactor.M2_2230]:
            if mobo.m2_slots == 0:
                self.errors.append(
                    f"Selected storage is M.2 ({storage.form_factor.value}), "
                    f"but the Motherboard has no M.2 slots."
                )
                is_compatible = False
        
        # Check SATA vs Motherboard SATA ports
        elif storage.form_factor in [StorageFormFactor.INCH_2_5, StorageFormFactor.INCH_3_5]:
            if mobo.sata_ports == 0:
                self.errors.append(
                    f"Selected storage is SATA ({storage.form_factor.value}), "
                    f"but the Motherboard has no SATA ports."
                )
                is_compatible = False
                
        return is_compatible

    def validate_build(
        self,
        cpu: CPU,
        mobo: Motherboard,
        ram: RAM,
        gpu: Optional[GPU],
        pc_case: Case,
        psu: PSU,
        cooler: Optional[CPUCooler] = None,
        storage: Optional[Storage] = None,
    ) -> Dict[str, Any]:
        self.errors.clear()
        self.warnings.clear()

        self.check_cpu_motherboard(cpu, mobo)
        self.check_ram_motherboard(ram, mobo)
        self.check_display_output(cpu, gpu)
        
        if storage:
            self.check_storage_motherboard(storage, mobo)
        
        if gpu:
            self.check_gpu_case(gpu, pc_case)
            self.check_gpu_psu_connectors(gpu, psu)
            
        self.check_power_supply(cpu, gpu, psu)
        self.check_mobo_case(mobo, pc_case)
        self.check_psu_case(psu, pc_case)

        if cooler:
            self.check_cooler_case(cooler, pc_case)
            self.check_cooler_cpu(cooler, cpu)

        return {
            "is_compatible": len(self.errors) == 0,
            "errors": list(self.errors),       # return copies
            "warnings": list(self.warnings),   # to prevent mutation
        }
