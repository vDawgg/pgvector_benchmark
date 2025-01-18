provider "google" {
  project = "benchmark-446021" # TODO: Parameterize this!
  region  = "europe-west3"
  zone    = "europe-west3-c"
}

### NETWORK
resource "google_compute_network" "vpc_network" {
  name                    = "demo-benchmark-network"
  auto_create_subnetworks = true
}

### FIREWALL
resource "google_compute_firewall" "all" {
  name = "allow-all"
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  network       = google_compute_network.vpc_network.id
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_router" "nat_router" {
  name    = "benchmark-nat-router"
  network = google_compute_network.vpc_network.id
  region  = "europe-west3"
}

resource "google_compute_router_nat" "nat_config" {
  name                       = "benchmark-nat"
  router                     = google_compute_router.nat_router.name
  region                     = "europe-west3"
  nat_ip_allocate_option     = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

### SUT INSTANCE
resource "google_compute_instance" "SUT" {
  name         = "pgvector-sut"
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
  name         = "pgvector-client"
  machine_type = "e2-highcpu-4"

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
