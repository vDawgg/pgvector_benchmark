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

### SUT INSTANCE
resource "google_compute_instance" "SUT" {
  name         = "pgvector-sut"
  machine_type = "e2-standard-2"

  boot_disk {
    initialize_params {
      size  = 80
      image = "ubuntu-2004-focal-v20231101"
    }
  }
  metadata_startup_script = file("./startup_sut.sh")


  network_interface {
    network = google_compute_network.vpc_network.id
    access_config {
      # Include this section to give the VM an external IP address
    }
  }
}

### BENCHMARK CLIENT INSTANCE
resource "google_compute_instance" "client" {
  name         = "pgvector-client"
  machine_type = "e2-standard-2"

  service_account {
    email  = "default"
    scopes = ["cloud-platform"]
  }

  boot_disk {
    initialize_params {
      image = "ubuntu-2004-focal-v20231101"
      size  = 80
    }
  }
  metadata_startup_script = file("./startup_client.sh")


  network_interface {
    network = google_compute_network.vpc_network.id
    access_config {
      # Include this section to give the VM an external IP address
    }
  }
}
