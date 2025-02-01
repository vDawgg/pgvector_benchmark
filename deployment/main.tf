variable "run_number" {
  type = string
  nullable = false
}

variable "project_id" {
  type = string
  nullable = false
}

variable "zone" {
  type = string
  nullable = false
}

variable "region" {
  type = string
  nullable = false
}

variable "indexing_method" {
  type = string
  nullable = false
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

### NETWORK
resource "google_compute_network" "vpc_network" {
  name                    = "benchmark-network-${var.indexing_method}-${var.run_number}"
  auto_create_subnetworks = true
}

### FIREWALL
resource "google_compute_firewall" "all" {
  name = "allow-all-${var.indexing_method}-${var.run_number}"
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  network       = google_compute_network.vpc_network.id
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_router" "nat_router" {
  name    = "benchmark-nat-router-${var.indexing_method}-${var.run_number}"
  network = google_compute_network.vpc_network.id
  region  = var.region
}

resource "google_compute_router_nat" "nat_config" {
  name                       = "benchmark-nat-${var.indexing_method}-${var.run_number}"
  router                     = google_compute_router.nat_router.name
  region                     = var.region
  nat_ip_allocate_option     = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

### SUT INSTANCE
resource "google_compute_instance" "SUT" {
  name         = "pgvector-sut-${var.indexing_method}-${var.run_number}"
  machine_type = "e2-highcpu-8"

  service_account {
    email  = "default"
    scopes = ["cloud-platform"]
  }

  boot_disk {
    initialize_params {
      size  = 40
      image = "ubuntu-2004-focal-v20231101"
    }
  }
  metadata_startup_script = file("./startup_sut.sh")


  network_interface {
    network = google_compute_network.vpc_network.id
  }
}

### BENCHMARK CLIENT INSTANCE
resource "google_compute_instance" "client" {
  name         = "pgvector-client-${var.indexing_method}-${var.run_number}"
  machine_type = "e2-standard-4"

  service_account {
    email  = "default"
    scopes = ["cloud-platform"]
  }

  boot_disk {
    initialize_params {
      image = "ubuntu-2004-focal-v20231101"
      size  = 40
    }
  }
  metadata_startup_script = file("./startup_client.sh")


  network_interface {
    network = google_compute_network.vpc_network.id
  }
}
