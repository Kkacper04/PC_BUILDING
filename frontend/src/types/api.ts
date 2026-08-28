export interface ComponentBase {
  id: number;
  brand: string;
  model: string;
  name: string;
  price: number;
  image_url: string | null;
}

export interface CPUResponse extends ComponentBase {
  socket: string | null;
  cores: number;
  threads: number;
  base_clock_mhz: number;
  boost_clock_mhz: number;
  tdp: number;
  l3_cache_mb: number | null;
  supports_ddr4: boolean;
  supports_ddr5: boolean;
  integrated_graphics: string | null;
  benchmark_score: number;
}

export interface GPUResponse extends ComponentBase {
  chip_manufacturer: string;
  gpu_chip: string | null;
  vram_gb: number;
  vram_type: string;
  base_clock_mhz: number;
  boost_clock_mhz: number;
  memory_bus_width: number | null;
  length_mm: number;
  width_slots: number | null;
  tdp: number | null;
  recommended_psu_wattage: number;
  benchmark_score: number;
}

export interface MotherboardResponse extends ComponentBase {
  socket: string | null;
  chipset: string | null;
  form_factor: string | null;
  ddr_generation: string;
  ram_slots: number;
  max_ram_speed_mhz: number;
  max_ram_capacity_gb: number;
  m2_slots: number;
  sata_ports: number;
  has_wifi: boolean;
  has_bluetooth: boolean;
}

export interface RAMResponse extends ComponentBase {
  ddr_generation: string;
  speed_mhz: number;
  total_capacity_gb: number;
  modules: number;
  capacity_per_module_gb: number;
  cas_latency: number | null;
  voltage: number | null;
}

export interface PSUResponse extends ComponentBase {
  wattage: number;
  efficiency_rating: string;
  modular_type: string;
  form_factor: string;
  pcie_8pin_connectors: number;
  has_12vhpwr: boolean;
  num_12vhpwr: number;
}

export interface CaseResponse extends ComponentBase {
  case_type: string;
  max_gpu_length_mm: number;
  max_cpu_cooler_height_mm: number;
  drive_bays_35: number;
  drive_bays_25: number;
  height_mm: number | null;
  width_mm: number | null;
  length_mm: number | null;
  has_tempered_glass: boolean;
  front_io_usb_c: boolean;
  psu_form_factor: string;
}

export interface StorageResponse extends ComponentBase {
  storage_type: string;
  form_factor: string;
  interface: string;
  capacity_gb: number;
  read_speed_mbps: number | null;
  write_speed_mbps: number | null;
  nand_type: string | null;
  tbw: number | null;
}

export interface CPUCoolerResponse extends ComponentBase {
  cooler_type: string;
  height_mm: number | null;
  radiator_size_mm: number | null;
  fan_count: number;
  fan_size_mm: number | null;
  max_tdp: number;
  max_noise_dba: number | null;
  has_rgb: boolean;
}

export interface BuildValidationRequest {
  cpu_id: number;
  motherboard_id: number;
  ram_id: number;
  gpu_id?: number | null;
  case_id: number;
  psu_id: number;
  cooler_id?: number | null;
}

export interface CompatibilityReport {
  is_compatible: boolean;
  errors: string[];
  warnings: string[];
}

export interface SSDRecommendation {
  id: number;
  name: string;
  brand: string;
  price: number;
  capacity_gb: number;
  read_speed_mbps: number | null;
  value_score: number;
}

export type ComponentType =
  | 'cpu'
  | 'gpu'
  | 'motherboard'
  | 'ram'
  | 'psu'
  | 'case'
  | 'cooler'
  | 'storage';

export type AnyComponent =
  | CPUResponse
  | GPUResponse
  | MotherboardResponse
  | RAMResponse
  | PSUResponse
  | CaseResponse
  | StorageResponse
  | CPUCoolerResponse;

export interface CPUQueryParams {
  brand?: string;
  socket?: string;
  limit?: number;
  offset?: number;
}

export interface GPUQueryParams {
  brand?: string;
  min_vram?: number;
  limit?: number;
  offset?: number;
}

export interface MotherboardQueryParams {
  socket?: string;
  form_factor?: string;
  limit?: number;
  offset?: number;
}

export interface RAMQueryParams {
  ddr?: string;
  limit?: number;
  offset?: number;
}

export interface PSUQueryParams {
  min_wattage?: number;
  limit?: number;
  offset?: number;
}

export interface CaseQueryParams {
  limit?: number;
  offset?: number;
}

export interface CoolerQueryParams {
  cooler_type?: string;
  min_tdp?: number;
  limit?: number;
  offset?: number;
}

export interface StorageQueryParams {
  min_capacity?: number;
  limit?: number;
  offset?: number;
}

export interface SSDRecommendParams {
  budget?: number;
  use_case?: string;
}
