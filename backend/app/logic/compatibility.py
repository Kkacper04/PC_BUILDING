from typing import List, Dict, Any
from app.models.components import CPU, Motherboard, RAM, GPU, Case, PSU

class CompatibilityChecker:
    
    
    def __init__(self):
        self.errors = []
        self.warnings = []

    def check_cpu_motherboard(self, cpu: CPU, mobo: Motherboard) -> bool:
       
        if cpu.socket == mobo.socket:
            return True
        else:
            self.errors.append(f"CPU socket ({cpu.socket.value}) does not match Motherboard socket ({mobo.socket.value}).")
            return False

    def check_ram_motherboard(self, ram: RAM, mobo: Motherboard) -> bool:
        is_compatible = True

        if ram.ddr_generation != mobo.ddr_generation:
            self.errors.append(f"RAM generation ({ram.ddr_generation.value}) does not match Motherboard standard ({mobo.ddr_generation.value}).")
            is_compatible = False

        if ram.modules > mobo.ram_slots:
            self.errors.append(f"RAM has {ram.modules} modules, but the motherboard only has {mobo.ram_slots} slots.")
            is_compatible = False
            
        if ram.speed_mhz > mobo.max_ram_speed_mhz:
            self.warnings.append(f"RAM speed ({ram.speed_mhz} MHz) exceeds Motherboard max supported speed ({mobo.max_ram_speed_mhz} MHz).")

        return is_compatible

    def check_gpu_case(self, gpu: GPU, pc_case: Case) -> bool:
        if gpu.length_mm <= pc_case.max_gpu_length_mm:
            return True
        else:
            self.errors.append(f"GPU length ({gpu.length_mm} mm) exceeds Case maximum clearance ({pc_case.max_gpu_length_mm} mm).")
            return False

    def check_power_supply(self, cpu: CPU, gpu: GPU, psu: PSU) -> bool:
        consumption = cpu.tdp + gpu.tdp + 100
        
        if psu.wattage >= consumption:
            if psu.wattage - consumption < 50:
                self.warnings.append(f"PSU wattage ({psu.wattage}W) is very close to the estimated consumption ({consumption}W).")
            return True
        else:
            self.errors.append(f"PSU wattage ({psu.wattage}W) is insufficient for estimated consumption ({consumption}W).")
            return False

    def validate_build(self, cpu: CPU, mobo: Motherboard, ram: RAM, gpu: GPU, pc_case: Case, psu: PSU) -> Dict[str, Any]:
        self.errors.clear()
        self.warnings.clear()

        self.check_cpu_motherboard(cpu, mobo)
        self.check_ram_motherboard(ram, mobo)
        self.check_gpu_case(gpu, pc_case)
        self.check_power_supply(cpu, gpu, psu)
        
        return {
            "is_compatible": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings
        }
