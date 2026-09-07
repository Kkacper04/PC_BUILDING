import type { CPUResponse, MotherboardResponse, RAMResponse, GPUResponse, CaseResponse, StorageResponse, CPUCoolerResponse } from '../types/api';

export type CompatibilityStatus = 'COMPATIBLE' | 'INCOMPATIBLE' | 'NEUTRAL';

interface CurrentBuild {
    cpu?: CPUResponse | null;
    motherboard?: MotherboardResponse | null;
    ram?: RAMResponse | null;
    gpu?: GPUResponse | null;
    pcCase?: CaseResponse | null; 
    storage?: StorageResponse | null;
    cooler?: CPUCoolerResponse | null;
}

export const checkComponentCompatibility = (
    item: any, 
    category: string,
    currentBuild: CurrentBuild
): CompatibilityStatus => {
    const cat = category.toUpperCase();

    if (cat === 'CPU') {
        if (currentBuild.motherboard) {
            return item.socket === currentBuild.motherboard.socket ? 'COMPATIBLE' : 'INCOMPATIBLE';
        }
    }

    if (cat === 'MOTHERBOARD') {
        let isValid = true;
        let hasCondition = false;

        if (currentBuild.cpu) {
            hasCondition = true;
            if (item.socket !== currentBuild.cpu.socket) isValid = false;
        }
        if (currentBuild.ram) {
            hasCondition = true;
            if (item.ddr_generation !== currentBuild.ram.ddr_generation) isValid = false;
            if (currentBuild.ram.total_capacity_gb > item.max_ram_capacity_gb) isValid = false;
        }
        if (currentBuild.storage) {
            hasCondition = true;
            const isM2 = currentBuild.storage.form_factor?.includes("M.2") ?? false;
            if (isM2 && item.m2_slots === 0) isValid = false;
            if (!isM2 && item.sata_ports === 0) isValid = false;
        }

        if (hasCondition) return isValid ? 'COMPATIBLE' : 'INCOMPATIBLE';
    }
    if (cat === 'RAM') {
        if (currentBuild.motherboard) {
            const isDdrMatch = item.ddr_generation === currentBuild.motherboard.ddr_generation;
            const isCapacityOk = item.total_capacity_gb <= currentBuild.motherboard.max_ram_capacity_gb;
            
            return (isDdrMatch && isCapacityOk) ? 'COMPATIBLE' : 'INCOMPATIBLE';
        }
    }

    if (cat === 'GPU') {
        if (currentBuild.pcCase) {
            return item.length_mm <= currentBuild.pcCase.max_gpu_length_mm ? 'COMPATIBLE' : 'INCOMPATIBLE';
        }
         else if (currentBuild.motherboard) {
            return 'COMPATIBLE';
        }
    }

    if (cat === 'CASE') {
        let isValid = true;
        let hasCondition = false;

        if (currentBuild.gpu) {
            hasCondition = true;
            if (currentBuild.gpu.length_mm > item.max_gpu_length_mm) isValid = false;
        }
        if (currentBuild.cooler && currentBuild.cooler.height_mm) {
            hasCondition = true;
            if (currentBuild.cooler.height_mm > item.max_cpu_cooler_height_mm) isValid = false;
        }

        if (hasCondition) return isValid ? 'COMPATIBLE' : 'INCOMPATIBLE';
    }
    if (cat === 'STORAGE') {
        if (currentBuild.motherboard) {
            const isM2 = item.form_factor?.includes("M.2") ?? false;
            if (isM2 && currentBuild.motherboard.m2_slots === 0) return 'INCOMPATIBLE';
            if (!isM2 && currentBuild.motherboard.sata_ports === 0) return 'INCOMPATIBLE';
            return 'COMPATIBLE';
        }
    }
    if (cat === 'COOLER' || cat === 'CPU_COOLER') {
        if (currentBuild.pcCase && item.height_mm) {
            return item.height_mm <= currentBuild.pcCase.max_cpu_cooler_height_mm ? 'COMPATIBLE' : 'INCOMPATIBLE';
        }
    }
    if (cat === 'PSU' || cat === 'POWER SUPPLY') {
        if (currentBuild.motherboard) {   
            return 'COMPATIBLE';
        }
    }

    return 'NEUTRAL';
}